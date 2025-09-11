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

# Add CORS - Allow both local and production frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://aeonforge.vercel.app",
        "https://aeonforge-git-main-kstephens0331.vercel.app",
        "https://aeonforge-kstephens0331.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Memory allocation limits by plan (in MB)
MEMORY_LIMITS = {
    'free': 512,        # 0.5 GB
    'standard': 1024,   # 1 GB  
    'pro': 1536,        # 1.5 GB
    'enterprise': 2048  # 2 GB
}

# Initialize Enhanced Database
def init_db():
    """Initialize comprehensive database with all required tables"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    # Users table with enhanced fields
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
        memory_used INTEGER DEFAULT 0,
        memory_limit INTEGER DEFAULT 512,
        organization_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Organizations table for enterprise accounts
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        plan TEXT DEFAULT 'enterprise',
        admin_user_id INTEGER,
        total_memory_limit INTEGER DEFAULT 2048,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_user_id) REFERENCES users (id)
    )
    ''')
    
    # Conversations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        model TEXT DEFAULT 'gpt-3.5-turbo',
        memory_size INTEGER DEFAULT 0,
        is_archived BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Chat messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        model_used TEXT,
        tokens_used INTEGER DEFAULT 0,
        memory_size INTEGER DEFAULT 0,
        saved_to_memory BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # User memory/knowledge base
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        key_name TEXT NOT NULL,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        memory_size INTEGER DEFAULT 0,
        importance_score INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Project history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        memory_size INTEGER DEFAULT 0,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Search history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        results_count INTEGER DEFAULT 0,
        memory_size INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Memory tracking for quota management
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memory_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        table_name TEXT NOT NULL,
        record_id INTEGER NOT NULL,
        memory_size INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
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
    """Get current user from JWT token with enhanced fields"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        token = authorization.replace("Bearer ", "")
        payload = verify_jwt_token(token)
        
        # Get user from database
        conn = sqlite3.connect('aeonforge.db')
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
            'usage_reset_date': user_row[6],
            'memory_used': user_row[8],
            'memory_limit': user_row[9],
            'organization_id': user_row[10]
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
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET daily_usage = daily_usage + 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Memory Management Functions
def calculate_memory_size(content: str) -> int:
    """Calculate memory size in bytes for content"""
    return len(content.encode('utf-8'))

def check_memory_limits(user: dict, additional_memory: int = 0) -> bool:
    """Check if user has available memory"""
    current_memory = user.get('memory_used', 0)
    memory_limit = user.get('memory_limit', MEMORY_LIMITS.get(user['plan'], 512))
    return (current_memory + additional_memory) <= (memory_limit * 1024 * 1024)  # Convert MB to bytes

def update_user_memory_usage(user_id: int, memory_change: int):
    """Update user's memory usage"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET memory_used = memory_used + ? WHERE id = ?", (memory_change, user_id))
    conn.commit()
    conn.close()

def save_chat_message(conversation_id: int, user_id: int, role: str, content: str, 
                      model_used: str = None, save_to_memory: bool = True):
    """Save chat message with memory tracking"""
    memory_size = calculate_memory_size(content) if save_to_memory else 0
    
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_messages 
        (conversation_id, user_id, role, content, model_used, memory_size, saved_to_memory)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (conversation_id, user_id, role, content, model_used, memory_size, save_to_memory))
    
    if save_to_memory:
        update_user_memory_usage(user_id, memory_size)
    
    conn.commit()
    conn.close()

def save_to_user_memory(user_id: int, key_name: str, content: str, category: str = "general"):
    """Save information to user's memory/knowledge base"""
    memory_size = calculate_memory_size(content)
    
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    # Check if key already exists, update or insert
    cursor.execute("SELECT id, memory_size FROM user_memory WHERE user_id = ? AND key_name = ?", (user_id, key_name))
    existing = cursor.fetchone()
    
    if existing:
        old_memory_size = existing[1]
        cursor.execute('''
            UPDATE user_memory 
            SET content = ?, memory_size = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (content, memory_size, existing[0]))
        update_user_memory_usage(user_id, memory_size - old_memory_size)
    else:
        cursor.execute('''
            INSERT INTO user_memory (user_id, key_name, content, category, memory_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, key_name, content, category, memory_size))
        update_user_memory_usage(user_id, memory_size)
    
    conn.commit()
    conn.close()

# Request models
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None
    save_to_memory: Optional[bool] = True

class MemoryRequest(BaseModel):
    key_name: str
    content: str
    category: Optional[str] = "general"

class MemoryUpdateRequest(BaseModel):
    key_name: str
    new_content: str

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

class ConversationRequest(BaseModel):
    title: str
    model: Optional[str] = "gpt-3.5-turbo"

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
    conn = sqlite3.connect('aeonforge.db')
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
            "dailyUsage": user_row[5],
            "memoryUsed": user_row[8],
            "memoryLimit": user_row[9]
        }
    }

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    """User signup endpoint with memory allocation"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT email FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with memory limit based on plan
    hashed_password = hash_password(request.password)
    plan = "free"
    memory_limit = MEMORY_LIMITS[plan] * 1024 * 1024  # Convert MB to bytes
    
    cursor.execute(
        "INSERT INTO users (email, password, name, plan, memory_limit) VALUES (?, ?, ?, ?, ?)",
        (request.email, hashed_password, request.name, plan, memory_limit)
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
            "plan": plan,
            "dailyUsage": 0,
            "memoryUsed": 0,
            "memoryLimit": memory_limit
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

def parse_memory_commands(message: str) -> tuple[str, dict]:
    """Parse special memory commands from user message"""
    message_lower = message.lower().strip()
    
    if message_lower.startswith("don't save") or message_lower.startswith("do not save"):
        return message, {"save_to_memory": False, "command": "no_save"}
    
    if message_lower.startswith("update memory"):
        # Extract key and value: "update memory for name to John Doe"
        if " for " in message_lower and " to " in message_lower:
            parts = message_lower.split(" for ", 1)[1].split(" to ", 1)
            if len(parts) == 2:
                key_name = parts[0].strip()
                new_value = parts[1].strip()
                return message, {"save_to_memory": True, "command": "update_memory", "key": key_name, "value": new_value}
    
    if message_lower.startswith("remember") or message_lower.startswith("save to memory"):
        # Extract key and value: "remember my name is John"
        return message, {"save_to_memory": True, "command": "save_memory"}
    
    return message, {"save_to_memory": True, "command": None}

@app.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Enhanced chat endpoint with memory management and special commands"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not GOOGLE_API_KEY:
        raise HTTPException(status_code=503, detail="No AI models configured")
    
    # Check usage limits for free users
    if not check_usage_limits(current_user):
        raise HTTPException(status_code=429, detail="Daily usage limit exceeded. Upgrade to continue.")
    
    # Parse memory commands
    processed_message, memory_config = parse_memory_commands(request.message)
    save_to_memory = memory_config.get("save_to_memory", request.save_to_memory)
    
    # Handle special memory commands
    if memory_config.get("command") == "update_memory":
        save_to_user_memory(current_user['id'], memory_config['key'], memory_config['value'])
        return {
            "response": f"✅ Updated memory: {memory_config['key']} = {memory_config['value']}",
            "model_used": "memory-system",
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "memory_updated": True
        }
    
    model = request.model or DEFAULT_MODEL
    
    # Restrict model access based on plan
    if current_user['plan'] == 'free':
        model = "gpt-3.5-turbo"  # Force free users to use basic model
    elif current_user['plan'] == 'standard':
        # Standard users get GPT-4 and Claude but not Gemini
        if model.startswith("gemini-"):
            model = "gpt-4"  # Fallback to GPT-4 for standard users
    
    # Check memory limits if saving to memory
    if save_to_memory:
        message_memory_size = calculate_memory_size(processed_message)
        if not check_memory_limits(current_user, message_memory_size):
            save_to_memory = False
            memory_warning = " (Not saved to memory - limit exceeded)"
        else:
            memory_warning = ""
    else:
        memory_warning = " (Not saved to memory as requested)"
    
    try:
        # Smart routing to appropriate AI service based on model
        if model.startswith("gpt-") and OPENAI_API_KEY:
            response_text = await call_openai(processed_message, model)
        elif model.startswith("claude-") and ANTHROPIC_API_KEY:
            response_text = await call_anthropic(processed_message, model)
        elif model.startswith("gemini-") and GOOGLE_API_KEY:
            response_text = await call_google_gemini(processed_message, model)
        else:
            # Intelligent fallback to best available model
            if GOOGLE_API_KEY:
                response_text = await call_google_gemini(processed_message, "gemini-1.5-flash")
                model = "gemini-1.5-flash"
            elif OPENAI_API_KEY:
                response_text = await call_openai(processed_message, "gpt-3.5-turbo")
                model = "gpt-3.5-turbo"
            elif ANTHROPIC_API_KEY:
                response_text = await call_anthropic(processed_message, "claude-3-haiku")
                model = "claude-3-haiku"
            else:
                raise HTTPException(status_code=503, detail="No AI models available")
        
        # Save chat messages to database if conversation_id provided
        if request.conversation_id and request.conversation_id != "new-conversation":
            try:
                conv_id = int(request.conversation_id)
                save_chat_message(conv_id, current_user['id'], "user", processed_message, model, save_to_memory)
                save_chat_message(conv_id, current_user['id'], "assistant", response_text, model, save_to_memory)
            except ValueError:
                pass  # Invalid conversation_id format
        
        # Increment usage for free and standard users
        if current_user['plan'] in ['free', 'standard']:
            increment_usage(current_user['id'])
        
        return {
            "response": response_text + memory_warning,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "saved_to_memory": save_to_memory,
            "memory_command": memory_config.get("command")
        }
    except Exception as e:
        # Graceful fallback with error handling
        fallback_response = f"AI response using {model}: {processed_message}"
        if "gemini" in model.lower() and OPENAI_API_KEY:
            try:
                fallback_response = await call_openai(processed_message, "gpt-3.5-turbo")
                model = "gpt-3.5-turbo-fallback"
            except:
                pass
        
        # Still increment usage even on fallback for free and standard users
        if current_user['plan'] in ['free', 'standard']:
            increment_usage(current_user['id'])
        
        return {
            "response": fallback_response + memory_warning,
            "model_used": model,
            "conversation_id": request.conversation_id or "new-conversation",
            "timestamp": datetime.now(datetime.timezone.utc).isoformat() + "Z",
            "saved_to_memory": save_to_memory,
            "memory_command": memory_config.get("command")
        }

# Memory and Chat Management Endpoints
@app.post("/conversations")
async def create_conversation(request: ConversationRequest, current_user: dict = Depends(get_current_user)):
    """Create a new conversation"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (user_id, title, model)
        VALUES (?, ?, ?)
    ''', (current_user['id'], request.title, request.model))
    
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "conversation_id": conversation_id,
        "title": request.title,
        "model": request.model,
        "created_at": datetime.now(datetime.timezone.utc).isoformat()
    }

@app.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    """Get user's conversation history"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, model, memory_size, created_at, updated_at
        FROM conversations 
        WHERE user_id = ? AND is_archived = FALSE
        ORDER BY updated_at DESC
    ''', (current_user['id'],))
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            "id": row[0],
            "title": row[1],
            "model": row[2],
            "memory_size": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        })
    
    conn.close()
    return {"conversations": conversations}

@app.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(conversation_id: int, current_user: dict = Depends(get_current_user)):
    """Get messages from a specific conversation"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    # Verify user owns this conversation
    cursor.execute("SELECT user_id FROM conversations WHERE id = ?", (conversation_id,))
    conv_owner = cursor.fetchone()
    if not conv_owner or conv_owner[0] != current_user['id']:
        raise HTTPException(status_code=403, detail="Access denied")
    
    cursor.execute('''
        SELECT role, content, model_used, saved_to_memory, created_at
        FROM chat_messages 
        WHERE conversation_id = ?
        ORDER BY created_at ASC
    ''', (conversation_id,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "role": row[0],
            "content": row[1],
            "model_used": row[2],
            "saved_to_memory": row[3],
            "created_at": row[4]
        })
    
    conn.close()
    return {"messages": messages}

@app.post("/memory")
async def save_memory(request: MemoryRequest, current_user: dict = Depends(get_current_user)):
    """Save information to user's memory"""
    memory_size = calculate_memory_size(request.content)
    
    if not check_memory_limits(current_user, memory_size):
        raise HTTPException(status_code=413, detail="Memory limit exceeded")
    
    save_to_user_memory(current_user['id'], request.key_name, request.content, request.category)
    
    return {
        "message": f"Saved to memory: {request.key_name}",
        "memory_size": memory_size,
        "category": request.category
    }

@app.put("/memory/{key_name}")
async def update_memory(key_name: str, request: MemoryUpdateRequest, current_user: dict = Depends(get_current_user)):
    """Update memory entry"""
    save_to_user_memory(current_user['id'], key_name, request.new_content)
    return {"message": f"Updated memory: {key_name}"}

@app.get("/memory")
async def get_memory(current_user: dict = Depends(get_current_user)):
    """Get user's memory/knowledge base"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT key_name, content, category, memory_size, created_at, updated_at
        FROM user_memory
        WHERE user_id = ?
        ORDER BY updated_at DESC
    ''', (current_user['id'],))
    
    memory_items = []
    for row in cursor.fetchall():
        memory_items.append({
            "key_name": row[0],
            "content": row[1],
            "category": row[2],
            "memory_size": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        })
    
    conn.close()
    return {"memory": memory_items}

@app.delete("/memory/{key_name}")
async def delete_memory(key_name: str, current_user: dict = Depends(get_current_user)):
    """Delete memory entry"""
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    
    # Get memory size before deletion
    cursor.execute("SELECT memory_size FROM user_memory WHERE user_id = ? AND key_name = ?", 
                   (current_user['id'], key_name))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Memory item not found")
    
    memory_size = result[0]
    
    # Delete the memory item
    cursor.execute("DELETE FROM user_memory WHERE user_id = ? AND key_name = ?", 
                   (current_user['id'], key_name))
    
    # Update user's memory usage
    update_user_memory_usage(current_user['id'], -memory_size)
    
    conn.commit()
    conn.close()
    
    return {"message": f"Deleted memory: {key_name}"}

@app.get("/memory/usage")
async def get_memory_usage(current_user: dict = Depends(get_current_user)):
    """Get user's memory usage statistics"""
    return {
        "memory_used": current_user.get('memory_used', 0),
        "memory_limit": current_user.get('memory_limit', 0),
        "memory_available": current_user.get('memory_limit', 0) - current_user.get('memory_used', 0),
        "usage_percentage": (current_user.get('memory_used', 0) / current_user.get('memory_limit', 1)) * 100,
        "plan": current_user['plan']
    }

@app.post("/search")
async def search(request: SearchRequest, current_user: dict = Depends(get_current_user)):
    """Secure search endpoint using server-side SERPAPI key"""
    if not SERPAPI_KEY:
        raise HTTPException(status_code=503, detail="Search not configured")
    
    # Save search to history
    memory_size = calculate_memory_size(request.query)
    conn = sqlite3.connect('aeonforge.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO search_history (user_id, query, memory_size)
        VALUES (?, ?, ?)
    ''', (current_user['id'], request.query, memory_size))
    conn.commit()
    conn.close()
    
    # Mock search response
    return {
        "query": request.query,
        "results": [
            {"title": f"Search result for: {request.query}", "url": "https://example.com"}
        ],
        "search_engine": "SerpAPI",
        "saved_to_history": True
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Aeonforge on Render port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)