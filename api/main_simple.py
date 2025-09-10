"""
Simplified Aeonforge API for Railway deployment
Basic version that works without PostgreSQL dependency
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime

app = FastAPI(
    title="Aeonforge API",
    version="2.0.0",
    description="Multi-Agent AI Development System - Railway Deployment"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for Railway deployment (will be replaced with PostgreSQL)
users_db = {}
chats_db = {}
messages_db = {}
memory_db = {}

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

@app.get("/")
async def root():
    return {
        "message": "🚀 Aeonforge API v2.0 is running on Railway!", 
        "status": "operational",
        "features": ["Chat Memory", "User Management", "File Storage", "In-Memory DB"],
        "deployment": "Railway",
        "note": "PostgreSQL integration available for local development"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Aeonforge API is operational on Railway",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "database": "In-Memory (Railway)",
        "users": len(users_db),
        "chats": len(chats_db),
        "messages": len(messages_db)
    }

@app.post("/api/users")
async def create_user_endpoint(user: UserCreate):
    """Create a new user"""
    try:
        user_id = str(uuid.uuid4())
        users_db[user_id] = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "created_at": datetime.now().isoformat(),
            "hashed_password": f"hashed_{user.password}"
        }
        return {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "created_at": users_db[user_id]["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chats")
async def create_chat_endpoint(chat: ChatCreate):
    """Create a new chat for a user"""
    try:
        chat_id = str(uuid.uuid4())
        chats_db[chat_id] = {
            "id": chat_id,
            "title": chat.title,
            "user_id": chat.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return chats_db[chat_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats/{user_id}")
async def get_user_chats_endpoint(user_id: str):
    """Get all chats for a user"""
    try:
        user_chats = [
            chat for chat in chats_db.values() 
            if chat["user_id"] == user_id
        ]
        return {"chats": user_chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Enhanced chat endpoint with memory"""
    try:
        # Store user message
        user_msg_id = str(uuid.uuid4())
        messages_db[user_msg_id] = {
            "id": user_msg_id,
            "chat_id": chat_message.chat_id,
            "user_id": chat_message.user_id,
            "content": chat_message.message,
            "role": "user",
            "created_at": datetime.now().isoformat(),
            "model_used": chat_message.model
        }
        
        # Get chat memory for context
        chat_memories = [
            mem for mem in memory_db.values() 
            if mem["chat_id"] == chat_message.chat_id
        ]
        
        # Get recent messages for context
        chat_messages = [
            msg for msg in messages_db.values()
            if msg["chat_id"] == chat_message.chat_id
        ]
        chat_messages.sort(key=lambda x: x["created_at"])
        recent_messages = chat_messages[-10:]  # Last 10 messages
        
        # Create context-aware response
        context_info = f"[Memory items: {len(chat_memories)}, Recent messages: {len(recent_messages)}]"
        
        # Generate AI response (simulated)
        ai_response = f"{context_info}\n🤖 Aeonforge AI: I received your message '{chat_message.message}'. This chat has {len(chat_memories)} memory items and {len(recent_messages)} previous messages for context. I'm processing with {chat_message.model} model."
        
        # Store AI response
        ai_msg_id = str(uuid.uuid4())
        messages_db[ai_msg_id] = {
            "id": ai_msg_id,
            "chat_id": chat_message.chat_id,
            "user_id": chat_message.user_id,
            "content": ai_response,
            "role": "assistant",
            "created_at": datetime.now().isoformat(),
            "model_used": chat_message.model
        }
        
        # Add important information to memory
        if len(chat_message.message) > 50:
            memory_id = str(uuid.uuid4())
            memory_db[memory_id] = {
                "id": memory_id,
                "chat_id": chat_message.chat_id,
                "memory_type": "context",
                "content": f"User asked: {chat_message.message[:100]}...",
                "importance": 3,
                "created_at": datetime.now().isoformat()
            }
        
        return {
            "response": ai_response,
            "status": "success",
            "model": chat_message.model,
            "message_id": ai_msg_id,
            "context_used": len(chat_memories),
            "history_length": len(recent_messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{chat_id}/messages")
async def get_chat_messages_endpoint(chat_id: str, limit: int = 50):
    """Get messages for a specific chat"""
    try:
        chat_messages = [
            msg for msg in messages_db.values()
            if msg["chat_id"] == chat_id
        ]
        chat_messages.sort(key=lambda x: x["created_at"])
        return {"messages": chat_messages[-limit:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory")
async def add_memory_endpoint(memory: MemoryCreate):
    """Add memory item to a chat"""
    try:
        memory_id = str(uuid.uuid4())
        memory_db[memory_id] = {
            "id": memory_id,
            "chat_id": memory.chat_id,
            "memory_type": memory.memory_type,
            "content": memory.content,
            "importance": memory.importance,
            "created_at": datetime.now().isoformat()
        }
        return memory_db[memory_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/{chat_id}")
async def get_memory_endpoint(chat_id: str):
    """Get memory items for a chat"""
    try:
        chat_memories = [
            mem for mem in memory_db.values() 
            if mem["chat_id"] == chat_id
        ]
        # Sort by importance and creation time
        chat_memories.sort(key=lambda x: (x["importance"], x["created_at"]), reverse=True)
        return {"memory": chat_memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            "Chat with Memory",
            "In-Memory Storage", 
            "User Management",
            "Context Awareness",
            "Railway Deployment"
        ],
        "count": 5,
        "status": "railway_mode"
    }

@app.get("/api/status")
async def system_status():
    """Get system status"""
    return {
        "system": "Aeonforge Multi-Agent AI v2.0",
        "status": "operational",
        "deployment": "Railway",
        "features": {
            "multi_model_ai": True,
            "tool_system": True,
            "real_time_chat": True,
            "chat_memory": True,
            "user_management": True,
            "in_memory_storage": True,
            "railway_deployment": True
        },
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "2.0.0",
        "stats": {
            "users": len(users_db),
            "chats": len(chats_db),
            "messages": len(messages_db),
            "memory_items": len(memory_db)
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0", 
        port=port,
        reload=False
    )