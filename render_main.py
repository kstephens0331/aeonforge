#!/usr/bin/env python3
"""
Ultra-simple Render deployment
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create simple FastAPI app
app = FastAPI(title="Aeonforge Render", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Aeonforge deployed successfully on Render!",
        "status": "success",
        "version": "1.0.0",
        "platform": "Render"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "render"}

@app.get("/test")
async def test():
    return {"message": "API is working!", "platform": "render"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Aeonforge on Render port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)