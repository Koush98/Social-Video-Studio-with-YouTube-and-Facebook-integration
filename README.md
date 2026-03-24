# 🚀 Social Video Studio

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, professional web application for uploading videos to multiple social media platforms simultaneously. Currently supports **YouTube** with **Facebook** integration ready for business verification.

![Social Video Studio](https://img.shields.io/badge/Social-Video%20Studio-ff0000?style=for-the-badge)

## ✨ Features

- 📺 **YouTube Upload** - Full support with metadata, scheduling, and privacy settings
- 📘 **Facebook Integration** - UI ready (requires Meta Business Verification for video uploads)
- 🎨 **Modern UI** - Glass-morphism design with drag-and-drop file upload
- ⏰ **Scheduling** - Schedule videos for later publication on each platform independently
- 🔐 **Secure OAuth** - PKCE-based authentication for enhanced security
- 📱 **Responsive** - Works on desktop, tablet, and mobile devices
- ⚡ **FastAPI Backend** - High-performance async Python backend

## 🎯 Platform Support

| Platform | Upload | Scheduling | Status |
|----------|--------|------------|--------|
| YouTube | ✅ | ✅ | Fully Functional |
| Facebook | ⚠️ | ⚠️ | Requires Business Verification |

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Cloud account (for YouTube API)
- Facebook Developer account (optional, for Facebook uploads)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/social-video-studio.git
cd social-video-studio
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Set Up Google OAuth (YouTube)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 credentials** (Web application)
5. Add authorized redirect URI: `http://localhost:8000/callback`
6. Download `client_secrets.json` and place it in the project root

### 5. Run the Application

```bash
python main.py
```

Visit `http://localhost:8000` in your browser.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Facebook App (optional)
FB_APP_ID=your_facebook_app_id
FB_APP_SECRET=your_facebook_app_secret

# Application
APP_URL=http://localhost:8000
SESSION_SECRET=your_random_secret_key
```

### Facebook Setup (Optional)

To enable Facebook video uploads:

1. Create a Facebook app at [developers.facebook.com](https://developers.facebook.com/)
2. Select **Consumer** app type (NOT Business)
3. Add **Facebook Login** product
4. Add your redirect URI: `http://localhost:8000/fb-callback`
5. Complete **Business Verification** (required for video upload permissions)
6. Request **Advanced Access** for `pages_manage_posts` and `publish_video`

## 🚢 Deployment

### Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables in Render Dashboard
5. Add your Render domain to Google OAuth redirect URIs

### Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

1. Click the button above or:
2. Create new project from GitHub repo
3. Add environment variables
4. Deploy!

### Manual Deployment

```bash
# Production dependencies
pip install -r requirements.txt

# Set production environment variables
export APP_URL=https://your-domain.com
export SESSION_SECRET=your-production-secret

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📁 Project Structure

```
social-video-studio/
├── main.py                 # FastAPI backend
├── index.html             # Frontend application
├── client_secrets.json    # Google OAuth credentials (not in git)
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment configuration
└── README.md             # This file
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Authentication**: OAuth 2.0 with PKCE
- **APIs**: YouTube Data API v3, Facebook Graph API
- **Styling**: Custom CSS with glass-morphism design
- **Icons**: Font Awesome

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Google API Client](https://github.com/googleapis/google-api-python-client) - YouTube API integration
- [Font Awesome](https://fontawesome.com/) - Beautiful icons

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/social-video-studio](https://github.com/yourusername/social-video-studio)

---

⭐ Star this repo if you find it helpful!
