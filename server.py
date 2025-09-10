"""
Minimal FastAPI server for Railway deployment testing
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Aeonforge Backend", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Aeonforge Backend is running on Railway!"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend is running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API test successful",
        "backend_url": os.getenv("RAILWAY_PUBLIC_DOMAIN", "unknown"),
        "port": os.getenv("PORT", "8000")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)