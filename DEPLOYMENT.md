# Railway Deployment Guide

## Files needed for Railway deployment:

### Backend (Python/FastAPI):
- `requirements.txt` - Python dependencies
- `Procfile` - Process file for Railway
- `railway.json` - Railway configuration
- `runtime.txt` - Python version specification
- `api_endpoints.py` - Main API file
- `data/database_manager.py` - Database management
- `signals/` - Signal processing modules
- `models/` - Data models

### Frontend (React/Vite):
Deploy separately on Vercel or Netlify:
- `pulse-frontend/` - React application
- Update API URLs in frontend to use Railway backend URL

## Railway Setup Steps:

1. **Create Railway account** at https://railway.app
2. **Connect GitHub repository** (push your code to GitHub first)
3. **Create new project** in Railway
4. **Add service** - select your repository
5. **Railway will automatically detect** Python and use the Procfile
6. **Set environment variables** if needed:
   - `PORT` (automatically set by Railway)
   - Any API keys or database URLs

## Frontend Deployment (Vercel):

1. **Push frontend to GitHub** (separate repo or subfolder)
2. **Connect to Vercel** at https://vercel.com
3. **Import project** from GitHub
4. **Update API URLs** in frontend code:
   ```javascript
   // Change from:
   const API_BASE = 'http://localhost:8004';
   // To:
   const API_BASE = 'https://your-railway-app.railway.app';
   ```

## Important Notes:

- **Database**: Railway provides PostgreSQL, but your current SQLite will work for testing
- **Environment**: Railway automatically handles Python environment
- **Scaling**: Railway can auto-scale based on traffic
- **Monitoring**: Railway provides logs and metrics
- **Custom Domain**: You can add custom domains in Railway settings

## Current Status:
✅ Backend ready for Railway
✅ Frontend ready for Vercel
✅ CORS configured for production
✅ All dependencies specified
