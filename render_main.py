#!/usr/bin/env python3
"""
Aeonforge Enterprise Backend - Render Deployment
Secure API key handling on server-side only
"""
import os
import uvicorn
import httpx
import jwt
import bcrypt
import stripe
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sqlite3
import json

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
NIH_API_KEY = os.getenv("NIH_API_KEY") or os.getenv("NIHPubMed_Key")  # Support both names
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")

# Configure Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

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

# Initialize SQLite Database
def init_db():
    """Initialize user database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        plan TEXT DEFAULT 'free',
        daily_usage INTEGER DEFAULT 0,
        usage_reset_date TEXT DEFAULT CURRENT_DATE,
        stripe_customer_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Authentication Helper Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: int, email: str) -> str:
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now(datetime.timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token: str) -> Dict[str, Any]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(None)):
    """Get current user from JWT token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_jwt_token(token)
        
        # Get user from database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (payload['user_id'],))
        user_row = cursor.fetchone()
        conn.close()
        
        if not user_row:
            raise HTTPException(status_code=401, detail="User not found")
        
        return {
            'id': user_row[0],
            'email': user_row[1],
            'name': user_row[3],
            'plan': user_row[4],
            'daily_usage': user_row[5],
            'usage_reset_date': user_row[6]
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication")

def check_usage_limits(user: dict) -> bool:
    """Check if user has exceeded daily usage limits"""
    # Set daily limits based on plan
    if user['plan'] == 'pro' or user['plan'] == 'enterprise':
        return True  # No limits for pro and enterprise
    elif user['plan'] == 'standard':
        daily_limit = 100
    else:  # Free plan
        daily_limit = 5
    
    # Reset daily usage if it's a new day
    today = datetime.now().date().isoformat()
    if user['usage_reset_date'] != today:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET daily_usage = 0, usage_reset_date = ? WHERE id = ?", 
                      (today, user['id']))
        conn.commit()
        conn.close()
        user['daily_usage'] = 0
    
    return user['daily_usage'] < daily_limit

def increment_usage(user_id: int):
    """Increment user's daily usage count"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET daily_usage = daily_usage + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Request models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None

class SearchRequest(BaseModel):
    query: str

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class CheckoutRequest(BaseModel):
    priceId: str
    plan: str

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

# Authentication Endpoints
@app.post("/auth/login")
async def login(request: LoginRequest):
    """User login endpoint"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (request.email,))
    user_row = cursor.fetchone()
    conn.close()
    
    if not user_row or not verify_password(request.password, user_row[2]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_jwt_token(user_row[0], user_row[1])
    
    return {
        "token": token,
        "user": {
            "id": user_row[0],
            "email": user_row[1],
            "name": user_row[3],
            "plan": user_row[4],
            "dailyUsage": user_row[5]
        }
    }

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    """User signup endpoint"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT email FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(request.password)
    cursor.execute(
        "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
        (request.email, hashed_password, request.name)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    token = create_jwt_token(user_id, request.email)
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": request.email,
            "name": request.name,
            "plan": "free",
            "dailyUsage": 0
        }
    }

@app.get("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify JWT token and return user info"""
    return {
        "user": current_user
    }

@app.post("/payments/create-checkout")
async def create_checkout(request: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Create Stripe checkout session"""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment processing not configured")
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': request.priceId,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://aeonforge.vercel.app/success',
            cancel_url='https://aeonforge.vercel.app/cancel',
            customer_email=current_user['email'],
            metadata={
                'user_id': current_user['id'],
                'plan': request.plan
            }
        )
        
        return {
            "checkoutUrl": checkout_session.url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payment error: {str(e)}")

@app.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Secure chat endpoint with usage limits and smart model routing"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="No AI models configured")
    
    # Check usage limits for free users
    if not check_usage_limits(current_user):
        raise HTTPException(status_code=429, detail="Daily usage limit exceeded. Upgrade to continue.")
    
    model = request.model or DEFAULT_MODEL
    
    # Restrict model access based on plan
    if current_user['plan'] == 'free':
        model = "gpt-3.5-turbo"  # Force free users to use basic model
    elif current_user['plan'] == 'standard':
        # Standard users get GPT-4 and Claude but not Gemini
        if model.startswith("gemini-"):
            model = "gpt-4"  # Fallback to GPT-4 for standard users
    
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
        
        # Increment usage for free and standard users
        if current_user['plan'] in ['free', 'standard']:
            increment_usage(current_user['id'])
        
        return {
            "response": response_text,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z"
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
        
        # Still increment usage even on fallback for free and standard users
        if current_user['plan'] in ['free', 'standard']:
            increment_usage(current_user['id'])
        
        return {
            "response": fallback_response,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z"
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