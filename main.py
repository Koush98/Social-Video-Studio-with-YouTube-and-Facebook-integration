import os
import time
import json
import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Facebook App Configuration
FB_APP_ID = os.getenv("FB_APP_ID", "YOUR_FB_APP_ID")
FB_APP_SECRET = os.getenv("FB_APP_SECRET", "YOUR_FB_APP_SECRET")
APP_URL = os.getenv("APP_URL", "http://localhost:8000")
FB_REDIRECT_URI = f"{APP_URL}/fb-callback"

app = FastAPI()

# Session middleware for PKCE verifier storage
session_secret = os.getenv("SESSION_SECRET", secrets.token_hex(32))
app.add_middleware(SessionMiddleware, secret_key=session_secret)

# Allow frontend to talk to backend
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def serve_index():
    return FileResponse("index.html")

# Google OAuth Configuration
CLIENT_SECRETS_FILE = "client_secrets.json"

# For production: Load from environment variable if file doesn't exist
GOOGLE_CLIENT_SECRETS_JSON = os.getenv("GOOGLE_CLIENT_SECRETS_JSON", "")

user_creds = {}  # Stores YouTube credentials
fb_creds = {}    # Stores Facebook credentials

# Create client_secrets.json from environment variable if provided
if GOOGLE_CLIENT_SECRETS_JSON and not os.path.exists(CLIENT_SECRETS_FILE):
    with open(CLIENT_SECRETS_FILE, 'w') as f:
        f.write(GOOGLE_CLIENT_SECRETS_JSON)

async def save_temp_file(file: UploadFile):
    """Save uploaded file temporarily"""
    temp_name = f"upload_{file.filename}"
    with open(temp_name, "wb") as f:
        f.write(await file.read())
    return temp_name

def cleanup_temp_file(temp_name: str):
    """Clean up temp file with retry logic"""
    for _ in range(5):
        try:
            if os.path.exists(temp_name):
                os.remove(temp_name)
            break
        except PermissionError:
            time.sleep(0.3)

@app.post("/upload/youtube")
async def upload_youtube(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
    platform: str = Form("{}")
):
    if 'auth' not in user_creds:
        raise HTTPException(401, "Please connect YouTube account first")
    
    import json
    platform_data = json.loads(platform)
    
    temp_name = await save_temp_file(file)
    
    try:
        creds = user_creds['auth']
        if creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        youtube = build("youtube", "v3", credentials=creds)
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags.split(",") if tags else [],
                "categoryId": platform_data.get('category_id', '22')
            },
            "status": {
                "privacyStatus": platform_data.get('privacy_status', 'public'),
                "selfDeclaredMadeForKids": platform_data.get('made_for_kids', False)
            }
        }
        
        # Handle scheduling
        schedule = platform_data.get('schedule')
        if schedule:
            body["status"]["publishAt"] = schedule
            body["status"]["privacyStatus"] = "private"
        
        media = MediaFileUpload(temp_name, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
        
        media._fd.close()
        cleanup_temp_file(temp_name)
        
        return {"video_id": response["id"], "status": "Uploaded Successfully"}
        
    except Exception as e:
        cleanup_temp_file(temp_name)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fb-login")
def fb_login(request: Request):
    """Initiate Facebook OAuth flow with basic scopes"""
    # Check if using placeholder credentials
    if FB_APP_ID == "YOUR_FB_APP_ID" or FB_APP_ID == "4163755660558792":
        return {
            "error": "Facebook App not configured",
            "message": "Please update FB_APP_ID and FB_APP_SECRET in main.py with your Facebook App credentials",
            "instructions": [
                "1. Go to https://developers.facebook.com/",
                "2. Create a new app (Consumer type, not Business)",
                "3. Add Facebook Login product",
                "4. Add http://localhost:8000/fb-callback to Valid OAuth Redirect URIs",
                "5. Copy App ID and App Secret to main.py"
            ]
        }
    
    # Generate state for security
    state = secrets.token_urlsafe(32)
    request.session['fb_state'] = state
    
    # Use basic scopes that don't require business verification
    # Note: These scopes only allow reading pages, not posting
    # To enable posting, you need Advanced Access (requires business verification)
    fb_auth_url = (
        f"https://www.facebook.com/v18.0/dialog/oauth?"
        f"client_id={FB_APP_ID}&"
        f"redirect_uri={FB_REDIRECT_URI}&"
        f"state={state}&"
        f"scope=pages_read_engagement,pages_show_list"
    )
    return RedirectResponse(fb_auth_url)

@app.get("/fb-callback")
def fb_callback(request: Request, code: str, state: str):
    """Handle Facebook OAuth callback"""
    # Verify state
    if state != request.session.get('fb_state'):
        return {"error": "Invalid state parameter"}
    
    # Exchange code for access token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "redirect_uri": FB_REDIRECT_URI,
        "code": code
    }
    
    response = requests.get(token_url, params=params)
    if response.status_code != 200:
        return {"error": "Failed to get access token", "details": response.text}
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    
    # Get user's pages
    pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
    pages_response = requests.get(pages_url)
    
    if pages_response.status_code != 200:
        return {"error": "Failed to get pages", "details": pages_response.text}
    
    pages = pages_response.json().get('data', [])
    if not pages:
        return {"error": "No Facebook pages found. You need to be an admin of a Facebook Page to upload videos."}
    
    # Store first page's access token (you can enhance this to let user select page)
    page = pages[0]
    fb_creds['auth'] = {
        'page_access_token': page['access_token'],
        'page_id': page['id'],
        'page_name': page['name']
    }
    
    # Auto-redirect back to main app
    return RedirectResponse(f"{APP_URL}/?auth=success&platform=facebook")

@app.post("/upload/facebook")
async def upload_facebook(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(""),
    platform: str = Form("{}")
):
    """Upload video to Facebook Page - Requires Advanced Access"""
    if 'auth' not in fb_creds:
        raise HTTPException(401, "Please connect Facebook account first")
    
    # Check if we have the required permissions
    # Basic scopes don't allow video uploads
    raise HTTPException(
        status_code=403,
        detail="Facebook video upload requires Advanced Access permissions (pages_manage_posts, publish_video) which need business verification. "
               "YouTube upload is fully functional. To enable Facebook: "
               "1. Complete Business Verification in your Facebook app, or "
               "2. Request Advanced Access for required permissions in App Review."
    )

@app.get("/login")
def login(request: Request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
        redirect_uri=f"{APP_URL}/callback"
    )
    auth_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline"
    )
    # Store the flow's code_verifier in session
    request.session['code_verifier'] = flow.code_verifier
    request.session['state'] = state
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(request: Request, code: str, state: str):
    # Retrieve code_verifier from session
    code_verifier = request.session.get('code_verifier')
    if not code_verifier:
        return {"error": "Session expired. Please try logging in again."}
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
        redirect_uri="http://localhost:8000/callback",
        state=state
    )
    # Restore the code_verifier
    flow.code_verifier = code_verifier
    # Disable scope check since Google may return additional scopes
    flow.oauth2session.scope = None
    flow.fetch_token(code=code)
    user_creds['auth'] = flow.credentials
    # Auto-redirect back to main app
    return RedirectResponse(f"{APP_URL}/?auth=success&platform=youtube")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)