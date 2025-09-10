# Aeonforge Phase 3 - Deployment Guide

This guide covers deploying Aeonforge to production with Railway (backend) and Vercel (frontend).

## Prerequisites

- GitHub account
- Railway account (railway.app)
- Vercel account (vercel.com)
- SerpAPI key (serpapi.com)

## Local Testing First

Before deployment, test the fixed system locally:

1. **Start Backend**:
   ```bash
   start_backend.bat
   # Should start at http://localhost:8000
   ```

2. **Start Frontend**:
   ```bash
   start_frontend.bat
   # Should start at http://localhost:3000
   ```

3. **Test the Web Scraper Project**:
   - Open http://localhost:3000
   - Enter your SerpAPI key
   - Type: "Create a Python web scraper for product prices"
   - Click "1 - Approve" when prompted
   - Verify it creates real files in `web_scraper_project/`

## Deployment Steps

### 1. GitHub Repository Setup

```bash
# Initialize Git repository
git init
git add .
git commit -m "Initial Aeonforge Phase 3 commit"

# Create GitHub repository and push
# (Replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/aeonforge.git
git branch -M main
git push -u origin main
```

### 2. Backend Deployment (Railway)

1. **Go to Railway.app**
2. **Create New Project** → **Deploy from GitHub repo**
3. **Select your Aeonforge repository**
4. **Configure Service**:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
   - Add any required environment variables
6. **Deploy** - Railway will auto-deploy
7. **Note the Railway URL** (e.g., `https://aeonforge-backend-production.up.railway.app`)

### 3. Frontend Deployment (Vercel)

1. **Go to Vercel.com**
2. **New Project** → **Import Git Repository**
3. **Select your Aeonforge repository**
4. **Configure Project**:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Environment Variables**:
   - `VITE_API_BASE_URL`: Your Railway backend URL
6. **Deploy** - Vercel will auto-deploy
7. **Note the Vercel URL** (e.g., `https://aeonforge.vercel.app`)

### 4. Update CORS Configuration

After deployment, update backend CORS to include your Vercel domain:

```python
# In backend/main.py, update allow_origins:
allow_origins=[
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "https://your-aeonforge-app.vercel.app"  # Add your actual Vercel URL
]
```

## Testing Production Deployment

1. **Open your Vercel URL**
2. **Enter your SerpAPI key**
3. **Test the web scraper project**:
   - Type: "Create a Python web scraper for product prices"
   - Approve the request
   - Verify the system creates files and provides detailed responses

## Troubleshooting

### Backend Issues
- Check Railway logs for Python errors
- Verify all dependencies in `requirements.txt`
- Ensure environment variables are set

### Frontend Issues
- Check Vercel function logs
- Verify `VITE_API_BASE_URL` environment variable
- Check browser console for CORS errors

### CORS Issues
- Update backend `allow_origins` with exact Vercel URL
- Ensure Railway backend is accessible

## Production URLs

After deployment, you'll have:
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/docs`

## Environment Variables Required

**Backend (Railway)**:
- `SERPAPI_KEY` (optional - can be provided via frontend)

**Frontend (Vercel)**:
- `VITE_API_BASE_URL` (your Railway backend URL)

## Security Notes

- API keys are handled securely via frontend input
- No sensitive data is stored in repositories
- CORS is configured for specific domains only