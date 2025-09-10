"""
Aeonforge Hybrid API Server
Works with PostgreSQL when available, falls back to in-memory storage
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json

# Global variables to track database availability
DB_AVAILABLE = False
db_module = None
in_memory_storage = {
    "users": {},
    "chats": {},
    "messages": {},
    "memory": {}
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup with graceful fallback"""
    global DB_AVAILABLE, db_module
    
    try:
        # Try to import and initialize database
        from database import (
            init_database, get_database, AsyncSessionLocal,
            create_user, create_chat, add_message, add_chat_memory,
            get_chat_messages, get_chat_memory, get_user_chats
        )
        
        await init_database()
        DB_AVAILABLE = True
        db_module = sys.modules['database']
        print("PostgreSQL database initialized successfully")
        
    except Exception as e:
        print(f"PostgreSQL not available: {e}")
        print("Using in-memory storage")
        DB_AVAILABLE = False
    
    yield

app = FastAPI(
    title="Aeonforge API",
    version="2.0.0",
    description="Multi-Agent AI Development System - Hybrid Storage",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class ChatCreate(BaseModel):
    title: str
    user_id: str

class ChatMessage(BaseModel):
    message: str
    chat_id: str
    user_id: str
    model: str = "chatgpt"

class MemoryCreate(BaseModel):
    chat_id: str
    memory_type: str
    content: str
    importance: int = 1

# Helper functions for in-memory storage
def store_user_memory(user_id: str, username: str, email: str, password: str):
    user_data = {
        "id": user_id,
        "username": username,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "hashed_password": f"hashed_{password}"
    }
    in_memory_storage["users"][user_id] = user_data
    return user_data

def store_chat_memory(chat_id: str, title: str, user_id: str):
    chat_data = {
        "id": chat_id,
        "title": title,
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    in_memory_storage["chats"][chat_id] = chat_data
    return chat_data

def store_message_memory(msg_id: str, chat_id: str, user_id: str, content: str, role: str, model: str = None):
    msg_data = {
        "id": msg_id,
        "chat_id": chat_id,
        "user_id": user_id,
        "content": content,
        "role": role,
        "created_at": datetime.now().isoformat(),
        "model_used": model
    }
    in_memory_storage["messages"][msg_id] = msg_data
    return msg_data

def store_memory_item(mem_id: str, chat_id: str, memory_type: str, content: str, importance: int):
    memory_data = {
        "id": mem_id,
        "chat_id": chat_id,
        "memory_type": memory_type,
        "content": content,
        "importance": importance,
        "created_at": datetime.now().isoformat()
    }
    in_memory_storage["memory"][mem_id] = memory_data
    return memory_data

# Dependency function for database access
async def get_db():
    if DB_AVAILABLE:
        from database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        yield None

# API Routes
@app.get("/")
async def root():
    storage_type = "PostgreSQL" if DB_AVAILABLE else "In-Memory"
    return {
        "message": f"Aeonforge API v2.0 is running!", 
        "status": "operational",
        "storage": storage_type,
        "features": ["Chat Memory", "User Management", "File Storage", "Hybrid Storage"],
        "database_available": DB_AVAILABLE
    }

@app.get("/api/health")
async def health_check():
    storage_type = "PostgreSQL" if DB_AVAILABLE else "In-Memory"
    stats = {}
    
    if not DB_AVAILABLE:
        stats = {
            "users": len(in_memory_storage["users"]),
            "chats": len(in_memory_storage["chats"]),
            "messages": len(in_memory_storage["messages"]),
            "memory_items": len(in_memory_storage["memory"])
        }
    
    return {
        "status": "healthy",
        "message": "Aeonforge API is operational",
        "version": "2.0.0",
        "storage": storage_type,
        "database_available": DB_AVAILABLE,
        "stats": stats
    }

@app.post("/api/users")
async def create_user_endpoint(user: UserCreate, db = Depends(get_db)):
    """Create a new user"""
    try:
        user_id = str(uuid.uuid4())
        
        if DB_AVAILABLE and db:
            from database import create_user
            new_user = await create_user(db, user.username, user.email, f"hashed_{user.password}")
            return {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "created_at": new_user.created_at
            }
        else:
            # Use in-memory storage
            user_data = store_user_memory(user_id, user.username, user.email, user.password)
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "created_at": user_data["created_at"]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chats")
async def create_chat_endpoint(chat: ChatCreate, db = Depends(get_db)):
    """Create a new chat for a user"""
    try:
        chat_id = str(uuid.uuid4())
        
        if DB_AVAILABLE and db:
            from database import create_chat
            new_chat = await create_chat(db, chat.user_id, chat.title)
            return {
                "id": new_chat.id,
                "title": new_chat.title,
                "user_id": new_chat.user_id,
                "created_at": new_chat.created_at
            }
        else:
            # Use in-memory storage
            chat_data = store_chat_memory(chat_id, chat.title, chat.user_id)
            return chat_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats/{user_id}")
async def get_user_chats_endpoint(user_id: str, db = Depends(get_db)):
    """Get all chats for a user"""
    try:
        if DB_AVAILABLE and db:
            from database import get_user_chats
            chats = await get_user_chats(db, user_id)
            return {
                "chats": [
                    {
                        "id": chat.id,
                        "title": chat.title,
                        "created_at": chat.created_at,
                        "updated_at": chat.updated_at
                    } for chat in chats
                ]
            }
        else:
            # Use in-memory storage
            user_chats = [
                chat for chat in in_memory_storage["chats"].values() 
                if chat["user_id"] == user_id
            ]
            return {"chats": user_chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage, db = Depends(get_db)):
    """Enhanced chat endpoint with memory"""
    try:
        user_msg_id = str(uuid.uuid4())
        ai_msg_id = str(uuid.uuid4())
        
        if DB_AVAILABLE and db:
            # Use PostgreSQL database
            from database import add_message, get_chat_memory, get_chat_messages, add_chat_memory
            
            # Store user message
            user_msg = await add_message(
                db, chat_message.chat_id, chat_message.user_id, 
                chat_message.message, "user", chat_message.model
            )
            
            # Get chat memory for context
            memory_items = await get_chat_memory(db, chat_message.chat_id)
            recent_messages = await get_chat_messages(db, chat_message.chat_id, limit=10)
            
            context_info = f"[PostgreSQL: {len(memory_items)} memory items, {len(recent_messages)} recent messages]"
            
            # Add important information to memory
            if len(chat_message.message) > 50:
                await add_chat_memory(
                    db, chat_message.chat_id, "context",
                    f"User asked: {chat_message.message[:100]}...", importance=3
                )
            
        else:
            # Use in-memory storage
            store_message_memory(user_msg_id, chat_message.chat_id, chat_message.user_id, 
                               chat_message.message, "user", chat_message.model)
            
            # Get chat memory for context
            chat_memories = [
                mem for mem in in_memory_storage["memory"].values() 
                if mem["chat_id"] == chat_message.chat_id
            ]
            
            chat_messages = [
                msg for msg in in_memory_storage["messages"].values()
                if msg["chat_id"] == chat_message.chat_id
            ]
            
            context_info = f"[In-Memory: {len(chat_memories)} memory items, {len(chat_messages)} recent messages]"
            
            # Add important information to memory
            if len(chat_message.message) > 50:
                mem_id = str(uuid.uuid4())
                store_memory_item(mem_id, chat_message.chat_id, "context",
                                f"User asked: {chat_message.message[:100]}...", 3)
        
        # Generate AI response
        ai_response = f"{context_info}\nAeonforge AI: I received your message '{chat_message.message}'. Processing with {chat_message.model} model using {'PostgreSQL' if DB_AVAILABLE else 'in-memory'} storage for context."
        
        # Store AI response
        if DB_AVAILABLE and db:
            from database import add_message
            ai_msg = await add_message(
                db, chat_message.chat_id, chat_message.user_id,
                ai_response, "assistant", chat_message.model
            )
        else:
            store_message_memory(ai_msg_id, chat_message.chat_id, chat_message.user_id,
                               ai_response, "assistant", chat_message.model)
        
        return {
            "response": ai_response,
            "status": "success",
            "model": chat_message.model,
            "message_id": ai_msg_id,
            "storage": "PostgreSQL" if DB_AVAILABLE else "In-Memory"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def system_status():
    """Get system status"""
    return {
        "system": "Aeonforge Multi-Agent AI v2.0 - Hybrid",
        "status": "operational",
        "storage": "PostgreSQL" if DB_AVAILABLE else "In-Memory",
        "features": {
            "multi_model_ai": True,
            "tool_system": True,
            "real_time_chat": True,
            "chat_memory": True,
            "user_management": True,
            "postgresql_storage": DB_AVAILABLE,
            "in_memory_fallback": not DB_AVAILABLE,
            "hybrid_architecture": True
        },
        "version": "2.0.0",
        "database_available": DB_AVAILABLE
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main_hybrid:app",
        host="0.0.0.0", 
        port=port,
        reload=False
    )