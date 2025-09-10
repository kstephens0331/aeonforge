"""
Database configuration and models for Aeonforge
Supports both local PostgreSQL and Supabase
"""

import os
import asyncpg
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, LargeBinary
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import uuid

# Database configuration - Railway automatically provides DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL (local development), use local PostgreSQL
if not DATABASE_URL:
    DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/aeonforge"
else:
    # Railway provides postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Add asyncpg if not present
    if "postgresql://" in DATABASE_URL and "+asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_archived = Column(Boolean, default=False)
    chat_settings = Column(JSON, default=dict)  # Chat-specific settings and context

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    message_type = Column(String(50), default='text')  # 'text', 'image', 'file', 'tool_result'
    metadata = Column(JSON, default=dict)  # Additional message data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String(100))  # Which AI model was used
    tokens_used = Column(Integer, default=0)

class ChatMemory(Base):
    __tablename__ = "chat_memory"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, nullable=False)
    memory_type = Column(String(50), nullable=False)  # 'context', 'summary', 'facts', 'preferences'
    content = Column(Text, nullable=False)
    importance = Column(Integer, default=1)  # 1-10 importance scale
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))  # Optional expiration

class FileAttachment(Base):
    __tablename__ = "file_attachments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(500))  # Path in storage system
    file_data = Column(LargeBinary)  # Direct storage in PostgreSQL if small
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Database dependency
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Database initialization
async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully")

# Database utilities
async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str):
    """Create a new user"""
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def create_chat(db: AsyncSession, user_id: str, title: str):
    """Create a new chat for a user"""
    chat = Chat(
        user_id=user_id,
        title=title
    )
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat

async def add_message(db: AsyncSession, chat_id: str, user_id: str, content: str, role: str, model_used: str = None):
    """Add a message to a chat"""
    message = Message(
        chat_id=chat_id,
        user_id=user_id,
        content=content,
        role=role,
        model_used=model_used
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def add_chat_memory(db: AsyncSession, chat_id: str, memory_type: str, content: str, importance: int = 1):
    """Add memory item to chat context"""
    memory = ChatMemory(
        chat_id=chat_id,
        memory_type=memory_type,
        content=content,
        importance=importance
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    return memory

async def get_chat_messages(db: AsyncSession, chat_id: str, limit: int = 100):
    """Get messages for a chat"""
    from sqlalchemy import select
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

async def get_chat_memory(db: AsyncSession, chat_id: str, memory_types: list = None):
    """Get chat memory for context"""
    from sqlalchemy import select
    query = select(ChatMemory).where(ChatMemory.chat_id == chat_id)
    
    if memory_types:
        query = query.where(ChatMemory.memory_type.in_(memory_types))
    
    query = query.order_by(ChatMemory.importance.desc(), ChatMemory.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_user_chats(db: AsyncSession, user_id: str):
    """Get all chats for a user"""
    from sqlalchemy import select
    result = await db.execute(
        select(Chat)
        .where(Chat.user_id == user_id)
        .where(Chat.is_archived == False)
        .order_by(Chat.updated_at.desc())
    )
    return result.scalars().all()