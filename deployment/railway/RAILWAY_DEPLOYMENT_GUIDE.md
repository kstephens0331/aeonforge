# Aeonforge Railway Deployment Guide

## 🎯 Overview

Complete guide for deploying Aeonforge to Railway with auto-scaling, environment management, and continuous deployment from GitHub.

## 📋 Pre-Deployment Setup

### 1. Install Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Verify installation
railway --version

# Login to Railway
railway login
```

### 2. Prepare Project for Railway
```bash
cd "C:\Users\usmc3\OneDrive\Documents\Stephens Code Programs\Aeonforge"

# Create Railway-specific configuration files
mkdir -p railway/

# Create nixpacks.toml for build configuration
cat > nixpacks.toml << 'EOF'
[phases.build]
nixPkgs = ["python39", "nodejs-18_x", "postgresql"]
cmds = ["pip install -r requirements.txt"]

[phases.start]
cmd = "python backend/main.py"

[variables]
PORT = "8000"
PYTHONPATH = "/app"
EOF

# Create Procfile for process definition
cat > Procfile << 'EOF'
web: cd backend && python main.py
worker: python system_health_checks/comprehensive_inspection_system.py
EOF
```

## 🚀 Railway Deployment Commands

### Step 1: Initialize Railway Project
```bash
# Create new Railway project
railway new aeonforge

# Or link to existing project
railway link

# Set up environment
railway environment
```

### Step 2: Configure Environment Variables
```bash
# Set production environment variables
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set PORT=8000

# Database configuration (Railway PostgreSQL)
railway add postgresql
# This automatically sets DATABASE_URL

# Redis cache
railway add redis
# This automatically sets REDIS_URL

# API Keys (set your actual keys)
railway variables set OPENAI_API_KEY="your_openai_key_here"
railway variables set GEMINI_API_KEY="your_gemini_key_here"
railway variables set SERPAPI_KEY="your_serpapi_key_here"
railway variables set NIH_PUBMED_KEY="your_nih_key_here"

# Supabase integration
railway variables set SUPABASE_URL="https://your-project.supabase.co"
railway variables set SUPABASE_ANON_KEY="your_supabase_anon_key"
railway variables set SUPABASE_SERVICE_ROLE_KEY="your_supabase_service_key"

# Frontend configuration
railway variables set FRONTEND_URL="https://your-frontend-domain.railway.app"
railway variables set BACKEND_URL="https://your-backend-domain.railway.app"

# Health monitoring
railway variables set HEALTH_CHECK_ENABLED=true
railway variables set HEALTH_CHECK_INTERVAL=300  # 5 minutes
```

### Step 3: Create Railway Configuration Files
```bash
# Create railway.json for deployment configuration
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python backend/main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  },
  "environments": {
    "production": {
      "variables": {
        "ENVIRONMENT": "production",
        "DEBUG": "false"
      }
    },
    "staging": {
      "variables": {
        "ENVIRONMENT": "staging", 
        "DEBUG": "true"
      }
    }
  }
}
EOF

# Create requirements.txt optimized for production
cat > requirements-railway.txt << 'EOF'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Database
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy==2.0.23

# AI Integration
openai==1.3.7
google-generativeai==0.3.2
ollama==0.1.7

# Multi-agent Framework
autogen==0.2.0
langchain==0.0.340

# Web Tools
requests==2.31.0
beautifulsoup4==4.12.2
aiohttp==3.9.1

# Data Processing
pandas==2.1.4
numpy==1.25.2
python-multipart==0.0.6

# System Monitoring
psutil==5.9.6

# Payment Processing
stripe==7.8.0

# Environment Management
python-dotenv==1.0.0

# CORS and Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Logging and Monitoring
structlog==23.2.0

# Testing (dev dependencies)
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
EOF

# Use optimized requirements for Railway
cp requirements-railway.txt requirements.txt
```

### Step 4: Create Health Check Endpoint
```python
# File: railway/health_check.py

import os
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter
from typing import Dict, Any

# Add to your FastAPI backend
router = APIRouter()

@router.get("/health")
async def health_check():
    """Railway health check endpoint"""
    try:
        # Quick system checks
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0",
            "services": {}
        }
        
        # Check database connection
        try:
            import psycopg2
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                conn = psycopg2.connect(db_url)
                conn.close()
                health_status["services"]["database"] = "healthy"
            else:
                health_status["services"]["database"] = "not_configured"
        except Exception as e:
            health_status["services"]["database"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check Redis connection
        try:
            import redis
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                r = redis.from_url(redis_url)
                r.ping()
                health_status["services"]["redis"] = "healthy"
            else:
                health_status["services"]["redis"] = "not_configured"
        except Exception as e:
            health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        
        # Check tool system
        try:
            from tools.natural_language import UniversalTranslator
            health_status["services"]["tools"] = "healthy"
        except Exception as e:
            health_status["services"]["tools"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check for monitoring"""
    try:
        # Run quick status check
        from system_health_checks.quick_status_check import QuickStatusChecker
        
        checker = QuickStatusChecker()
        status_data, exit_code = checker.run_quick_check()
        
        return {
            "railway_health": await health_check(),
            "system_health": status_data,
            "overall_status": "healthy" if exit_code == 0 else "degraded"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
```

### Step 5: Setup GitHub Integration
```bash
# Connect Railway to your GitHub repository
railway connect

# Set up automatic deployments
railway deploy --detach

# Configure deployment triggers
cat > .railway/triggers.json << 'EOF'
{
  "triggers": [
    {
      "branch": "main",
      "environment": "production",
      "checkSuites": true
    },
    {
      "branch": "develop", 
      "environment": "staging",
      "checkSuites": true
    }
  ]
}
EOF
```

### Step 6: Create Multi-Service Architecture
```bash
# Deploy backend service
railway up

# Add frontend service (if separate)
railway add --name aeonforge-frontend

# Add worker service for background tasks
railway add --name aeonforge-worker

# Add scheduled health checks
railway add --name aeonforge-health-monitor
```

### Step 7: Configure Custom Domains (Optional)
```bash
# Add custom domain to your Railway service
railway domain add yourdomain.com

# Configure SSL (automatic with Railway)
# DNS settings will be provided by Railway
```

## 🔧 Advanced Railway Configuration

### Multi-Service Setup

#### Backend Service (main API)
```bash
# Railway backend configuration
cat > railway-backend.json << 'EOF'
{
  "build": {
    "builder": "nixpacks",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100
  }
}
EOF
```

#### Worker Service (background tasks)
```bash
# Railway worker configuration  
cat > railway-worker.json << 'EOF'
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python -m celery worker -A backend.celery_app --loglevel=info",
    "healthcheckPath": null
  }
}
EOF
```

#### Scheduled Jobs
```bash
# Railway cron job configuration
cat > railway-scheduler.json << 'EOF'
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python -m celery beat -A backend.celery_app --loglevel=info"
  },
  "cron": [
    {
      "schedule": "0 */6 * * *",
      "command": "python system_health_checks/comprehensive_inspection_system.py"
    },
    {
      "schedule": "*/15 * * * *", 
      "command": "python system_health_checks/quick_status_check.py"
    }
  ]
}
EOF
```

### Environment-Specific Configurations

#### Production Environment
```bash
# Production-specific variables
railway variables set --environment production REPLICAS=3
railway variables set --environment production MEMORY_LIMIT=2GB
railway variables set --environment production CPU_LIMIT=1000m
railway variables set --environment production AUTO_SCALE=true
railway variables set --environment production MIN_REPLICAS=2
railway variables set --environment production MAX_REPLICAS=10
```

#### Staging Environment  
```bash
# Staging-specific variables
railway variables set --environment staging REPLICAS=1
railway variables set --environment staging MEMORY_LIMIT=1GB
railway variables set --environment staging CPU_LIMIT=500m
railway variables set --environment staging AUTO_SCALE=false
```

### Monitoring and Logging Setup
```bash
# Enable Railway monitoring
railway logs --follow

# Configure log levels
railway variables set LOG_LEVEL=INFO
railway variables set STRUCTURED_LOGGING=true

# Set up alerting (Railway Pro feature)
railway alerts add --type deployment_failed
railway alerts add --type high_cpu_usage --threshold 80
railway alerts add --type high_memory_usage --threshold 85
```

## 📊 Monitoring and Observability

### Railway Metrics Dashboard
```bash
# View service metrics
railway status

# Monitor resource usage
railway metrics

# Check deployment history
railway deployments

# View logs
railway logs --tail 100
```

### Custom Monitoring Setup
```python
# File: railway/monitoring.py

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any

class RailwayMonitoring:
    """Custom monitoring for Railway deployment"""
    
    def __init__(self):
        self.railway_token = os.getenv("RAILWAY_TOKEN")
        self.project_id = os.getenv("RAILWAY_PROJECT_ID")
        self.environment = os.getenv("ENVIRONMENT", "production")
    
    async def send_health_metrics(self, metrics: Dict[str, Any]):
        """Send custom health metrics to monitoring service"""
        try:
            # Send to your monitoring service (DataDog, New Relic, etc.)
            monitoring_webhook = os.getenv("MONITORING_WEBHOOK_URL")
            
            if monitoring_webhook:
                payload = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "environment": self.environment,
                    "service": "aeonforge",
                    "metrics": metrics
                }
                
                response = requests.post(monitoring_webhook, json=payload)
                return response.status_code == 200
                
        except Exception as e:
            print(f"Failed to send metrics: {e}")
            return False
    
    async def check_service_health(self):
        """Check all service health endpoints"""
        services = [
            f"{os.getenv('BACKEND_URL')}/health",
            f"{os.getenv('BACKEND_URL')}/health/detailed"
        ]
        
        health_results = {}
        
        for service_url in services:
            try:
                response = requests.get(service_url, timeout=10)
                health_results[service_url] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "data": response.json() if response.headers.get('content-type') == 'application/json' else None
                }
            except Exception as e:
                health_results[service_url] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_results
```

### Auto-scaling Configuration
```bash
# Configure auto-scaling policies
railway variables set RAILWAY_AUTOSCALE_ENABLED=true
railway variables set RAILWAY_AUTOSCALE_MIN_REPLICAS=2
railway variables set RAILWAY_AUTOSCALE_MAX_REPLICAS=10
railway variables set RAILWAY_AUTOSCALE_TARGET_CPU=70
railway variables set RAILWAY_AUTOSCALE_TARGET_MEMORY=80
```

## 🚀 Deployment Automation

### GitHub Actions Integration
```yaml
# File: .github/workflows/railway-deploy.yml

name: Railway Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Railway CLI
      run: |
        npm install -g @railway/cli
    
    - name: Deploy to Railway
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
      run: |
        railway deploy --detach
    
    - name: Run health check
      run: |
        sleep 30  # Wait for deployment
        curl -f ${{ secrets.RAILWAY_HEALTH_URL }}/health || exit 1
    
    - name: Notify deployment status
      if: always()
      run: |
        # Send notification to Slack, Discord, etc.
        echo "Deployment completed"
```

### Database Migrations
```bash
# Set up database migration on Railway
railway run python -c "
import psycopg2
import os

# Connect to Railway database
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Run migrations
with open('deployment/supabase/schema.sql', 'r') as f:
    cur.execute(f.read())

conn.commit()
conn.close()
print('Database migration completed')
"

# Register tools in database
railway run python deployment/supabase/tool_registration.py
```

## 📋 Railway Deployment Checklist

### Pre-deployment:
- [ ] Railway account created and CLI installed
- [ ] GitHub repository connected
- [ ] Environment variables configured
- [ ] Database services added
- [ ] Health check endpoints implemented

### Deployment:
- [ ] Services deployed successfully
- [ ] Auto-scaling configured
- [ ] Custom domains set up (if needed)
- [ ] Monitoring and alerting enabled

### Post-deployment:
- [ ] Health checks passing
- [ ] Database migrations applied
- [ ] Tool registration completed
- [ ] Performance monitoring active
- [ ] Backup and disaster recovery tested

## 🔄 Maintenance and Updates

### Rolling Updates
```bash
# Deploy new version with zero downtime
railway deploy --strategy rolling

# Rollback if needed
railway rollback

# Check deployment status
railway status
```

### Scaling Operations
```bash
# Manual scaling
railway scale --replicas 5

# Update resource limits
railway variables set MEMORY_LIMIT=4GB
railway variables set CPU_LIMIT=2000m
```

### Backup and Recovery
```bash
# Backup database
railway run pg_dump $DATABASE_URL > backup.sql

# Restore database
railway run psql $DATABASE_URL < backup.sql
```

---

**Railway Project**: `https://railway.app/project/YOUR_PROJECT_ID`  
**Production URL**: `https://your-service.railway.app`  
**Monitoring**: Railway dashboard + custom monitoring  
**Auto-scaling**: Enabled with smart policies  
**CI/CD**: Automated deployment from GitHub