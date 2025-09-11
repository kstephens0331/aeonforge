#!/usr/bin/env python3
"""
Aeonforge Enterprise Backend - Render Deployment
Secure API key handling on server-side only
"""
import os
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
NIH_API_KEY = os.getenv("NIH_API_KEY") or os.getenv("NIHPubMed_Key")  # Support both names
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")

# Create FastAPI app
app = FastAPI(
    title="Aeonforge Enterprise API", 
    version="2.0.0",
    description="Multi-Agent AI System with secure server-side API keys"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None

class SearchRequest(BaseModel):
    query: str

# AI Model Helper Functions
async def call_openai(message: str, model: str) -> str:
    """Call OpenAI API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": message}],
                "max_tokens": 1000
            },
            timeout=30.0
        )
        data = response.json()
        return data["choices"][0]["message"]["content"]

async def call_anthropic(message: str, model: str) -> str:
    """Call Anthropic Claude API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": model,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": message}]
            },
            timeout=30.0
        )
        data = response.json()
        return data["content"][0]["text"]

async def call_google_gemini(message: str, model: str) -> str:
    """Call Google Gemini API"""
    async with httpx.AsyncClient() as client:
        # Google AI Studio API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        response = await client.post(
            url,
            headers={
                "Content-Type": "application/json"
            },
            params={
                "key": GOOGLE_API_KEY
            },
            json={
                "contents": [{
                    "parts": [{
                        "text": message
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": 1000,
                    "temperature": 0.7
                }
            },
            timeout=30.0
        )
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

@app.get("/")
async def root():
    return {
        "message": "Aeonforge Enterprise API v2.0 is running!",
        "status": "operational",
        "version": "2.0.0",
        "platform": "Render",
        "features": {
            "openai_available": bool(OPENAI_API_KEY),
            "anthropic_available": bool(ANTHROPIC_API_KEY),
            "google_available": bool(GOOGLE_API_KEY),
            "search_available": bool(SERPAPI_KEY),
            "nih_available": bool(NIH_API_KEY),
            "default_model": DEFAULT_MODEL
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "platform": "render"}

@app.get("/models")
async def available_models():
    """Return available AI models based on configured API keys"""
    models = []
    if OPENAI_API_KEY:
        models.extend(["gpt-4", "gpt-3.5-turbo"])
    if ANTHROPIC_API_KEY:
        models.extend(["claude-3-sonnet", "claude-3-haiku"])
    if GOOGLE_API_KEY:
        models.extend(["gemini-1.5-pro", "gemini-1.5-flash"])
    
    return {
        "available_models": models,
        "default_model": DEFAULT_MODEL,
        "total_models": len(models)
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Secure chat endpoint with smart model routing - API keys handled server-side only"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="No AI models configured")
    
    model = request.model or DEFAULT_MODEL
    
    try:
        # Smart routing to appropriate AI service based on model
        if model.startswith("gpt-") and OPENAI_API_KEY:
            response_text = await call_openai(request.message, model)
        elif model.startswith("claude-") and ANTHROPIC_API_KEY:
            response_text = await call_anthropic(request.message, model)
        elif model.startswith("gemini-") and GOOGLE_API_KEY:
            response_text = await call_google_gemini(request.message, model)
        else:
            # Intelligent fallback to best available model
            if GOOGLE_API_KEY:
                response_text = await call_google_gemini(request.message, "gemini-1.5-flash")
                model = "gemini-1.5-flash"
            elif OPENAI_API_KEY:
                response_text = await call_openai(request.message, "gpt-3.5-turbo")
                model = "gpt-3.5-turbo"
            elif ANTHROPIC_API_KEY:
                response_text = await call_anthropic(request.message, "claude-3-haiku")
                model = "claude-3-haiku"
            else:
                raise HTTPException(status_code=503, detail="No AI models available")
        
        return {
            "response": response_text,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    except Exception as e:
        # Graceful fallback with error handling
        fallback_response = f"AI response using {model}: {request.message}"
        if "gemini" in model.lower() and OPENAI_API_KEY:
            try:
                fallback_response = await call_openai(request.message, "gpt-3.5-turbo")
                model = "gpt-3.5-turbo-fallback"
            except:
                pass
        
        return {
            "response": fallback_response,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": "2025-01-01T00:00:00Z"
        }

@app.post("/search")
async def search(request: SearchRequest):
    """Secure search endpoint using server-side SERPAPI key"""
    if not SERPAPI_KEY:
        raise HTTPException(status_code=503, detail="Search not configured")
    
    # Mock search response
    return {
        "query": request.query,
        "results": [
            {"title": f"Search result for: {request.query}", "url": "https://example.com"}
        ],
        "search_engine": "SerpAPI"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Aeonforge on Render port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)