# 🚂 Updated Railway Deployment Instructions for Aeonforge

## 📋 Prerequisites
- Railway account: https://railway.app
- Railway CLI installed: `npm install -g @railway/cli`
- GitHub repository: https://github.com/kstephens0331/aeonforge

---

## 🚀 Step 1: Install and Login to Railway

```bash
# Install Railway CLI (if not already installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Verify login
railway whoami
```

---

## 🚀 Step 2: Create Railway Project and Services

```bash
# Navigate to your project
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"

# Create new Railway project
railway new

# Create backend service
railway service create backend

# Create frontend service  
railway service create frontend

# List services to verify
railway services
```

---

## 🚀 Step 3: Deploy Backend Service

```bash
# Switch to backend service
railway service backend

# Connect to GitHub repository
railway connect

# Set environment variables for backend
railway vars set ENVIRONMENT=production
railway vars set DEBUG=false
railway vars set PORT=8000

# Add PostgreSQL database
railway add postgresql

# Add Redis cache
railway add redis

# Set API keys (replace with your actual keys)
railway vars set OPENAI_API_KEY="your_openai_api_key_here"
railway vars set GEMINI_API_KEY="your_gemini_api_key_here"
railway vars set SERPAPI_KEY="your_serpapi_key_here"
railway vars set NIH_PUBMED_KEY="your_nih_pubmed_key_here"

# Set Supabase variables
railway vars set SUPABASE_URL="https://your-project.supabase.co"
railway vars set SUPABASE_ANON_KEY="your_supabase_anon_key"
railway vars set SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_key"

# Deploy backend
railway up --service backend
```

---

## 🚀 Step 4: Configure Backend for Production

Create a `railway.json` file in the `backend/` directory:

```json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

Create a `Procfile` in the `backend/` directory:

```
web: python main.py
worker: python ../system_health_checks/comprehensive_inspection_system.py
```

---

## 🚀 Step 5: Deploy Frontend Service

```bash
# Switch to frontend service
railway service frontend

# Set build configuration
railway vars set BUILD_COMMAND="cd frontend && npm install && npm run build"
railway vars set START_COMMAND="cd frontend && npm run preview"
railway vars set INSTALL_COMMAND="npm install"

# Set backend URL (get this from your backend deployment)
railway vars set VITE_API_URL="https://your-backend-url.railway.app"

# Deploy frontend
railway up --service frontend
```

---

## 🚀 Step 6: Configure Custom Domain (Optional)

```bash
# Add custom domain to backend
railway domain add api.yourdomain.com --service backend

# Add custom domain to frontend  
railway domain add yourdomain.com --service frontend

# DNS configuration will be provided by Railway
```

---

## 🚀 Step 7: Set Up Environment-Specific Deployments

### Production Environment
```bash
# Configure production scaling
railway vars set --env production REPLICAS=3
railway vars set --env production MEMORY_LIMIT=2GB
railway vars set --env production CPU_LIMIT=1000m
railway vars set --env production AUTO_SCALE=true
```

### Staging Environment
```bash
# Create staging environment
railway env create staging

# Configure staging
railway vars set --env staging ENVIRONMENT=staging
railway vars set --env staging DEBUG=true
railway vars set --env staging REPLICAS=1
```

---

## 🔧 Step 8: Database Setup and Migrations

```bash
# Connect to your Railway PostgreSQL database
railway connect postgresql

# Run database migrations (when in database shell)
\c railway  # Connect to railway database

# Create tables using the schema from deployment/supabase/schema.sql
# Copy and paste the SQL commands from that file
```

---

## 📊 Step 9: Monitoring and Logs

```bash
# View service logs
railway logs --service backend

# Monitor deployments
railway status

# Check resource usage
railway metrics --service backend

# View environment variables
railway vars --service backend
```

---

## 🚀 Step 10: Automated Deployments

Create `.railway/deploy.yml` for automated deployments:

```yaml
version: 2
services:
  backend:
    build:
      buildCommand: pip install -r requirements.txt
      startCommand: python main.py
    healthcheck:
      path: /health
      timeout: 10s
    env:
      PORT: 8000
      
  frontend:
    build:
      buildCommand: cd frontend && npm install && npm run build
      startCommand: cd frontend && npm run preview
    env:
      PORT: 3000
```

---

## 🔑 Required Environment Variables

### Backend Service:
```bash
# Core
ENVIRONMENT=production
DEBUG=false
PORT=8000

# AI APIs
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
SERPAPI_KEY=your_serpapi_key
NIH_PUBMED_KEY=your_nih_key

# Database (automatically set by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Security
JWT_SECRET_KEY=your_jwt_secret_32_chars_minimum
CORS_ORIGINS=http://localhost:3000,https://your-frontend.railway.app
```

### Frontend Service:
```bash
# Build settings
NODE_ENV=production
VITE_API_URL=https://your-backend.railway.app
```

---

## 🔄 Deployment Commands Summary

```bash
# Full deployment process
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"

# Backend deployment
railway service backend
railway up

# Frontend deployment  
railway service frontend
railway up

# Check status
railway status

# View logs
railway logs --follow
```

---

## 🌐 Expected URLs After Deployment

- **Backend API**: `https://backend-production-xxxx.railway.app`
- **Frontend App**: `https://frontend-production-xxxx.railway.app`  
- **Health Check**: `https://backend-production-xxxx.railway.app/health`
- **API Docs**: `https://backend-production-xxxx.railway.app/docs`

---

## 🚨 Troubleshooting

### Build Failures:
```bash
# Check logs
railway logs --service backend

# Rebuild service
railway redeploy --service backend
```

### Environment Issues:
```bash
# List all variables
railway vars

# Update specific variable
railway vars set VARIABLE_NAME=new_value
```

### Database Connection Issues:
```bash
# Test database connection
railway connect postgresql

# Check database URL
railway vars | grep DATABASE_URL
```

---

## 💡 Pro Tips

1. **Use Railway Templates**: Start with a template for faster setup
2. **Environment Variables**: Always use Railway's built-in environment management
3. **Monitoring**: Set up Railway's monitoring for production deployments
4. **Scaling**: Use Railway's auto-scaling for production workloads
5. **Backups**: Set up automated database backups in production

---

**🎯 Your Aeonforge system will be fully deployed on Railway with:**
- ✅ Backend API with multi-model AI integration
- ✅ Frontend React application  
- ✅ PostgreSQL + Redis databases
- ✅ Auto-scaling and monitoring
- ✅ Custom domains (optional)
- ✅ Automated deployments from GitHub