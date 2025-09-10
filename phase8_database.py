"""
Aeonforge Phase 8 - Advanced Database Integration
PostgreSQL, Redis, Vector Database Integration with AI-Enhanced Data Management
"""

import os
import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import logging

# Database imports
ADVANCED_DB_AVAILABLE = True
try:
    import asyncpg
except ImportError:
    print("Warning: asyncpg not available - using fallback to aiosqlite")
    ADVANCED_DB_AVAILABLE = False

try:
    import redis.asyncio as redis
except ImportError:
    print("Warning: redis not available - caching disabled")
    redis = None

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
    from sqlalchemy import String, DateTime, Text, Integer, Boolean, JSON
except ImportError as e:
    print(f"Warning: SQLAlchemy not available: {e}")
    ADVANCED_DB_AVAILABLE = False
    # Create fallback classes
    class DeclarativeBase:
        pass
    class Mapped:
        pass
    def mapped_column(*args, **kwargs):
        pass

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("Warning: ChromaDB not available - vector search disabled")
    chromadb = None

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    postgresql_url: str = "postgresql+asyncpg://aeonforge:password@localhost:5432/aeonforge"
    redis_url: str = "redis://localhost:6379"
    vector_db_path: str = "./vector_db"
    enable_vector_search: bool = True
    enable_caching: bool = True
    backup_enabled: bool = True

class Base(DeclarativeBase):
    """SQLAlchemy base class"""
    pass

class Project(Base):
    """Project data model"""
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settings: Mapped[Optional[Dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Conversation(Base):
    """Conversation data model"""
    __tablename__ = "conversations"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(255))
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    conv_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

class Message(Base):
    """Message data model"""
    __tablename__ = "messages"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    msg_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

class CodeGeneration(Base):
    """Code generation history"""
    __tablename__ = "code_generations"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    request: Mapped[str] = mapped_column(Text, nullable=False)
    generated_code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    code_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

class AdvancedDatabaseManager:
    """Advanced database management system"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.engine = None
        self.session_factory = None
        self.redis_client = None
        self.vector_db = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize all database connections"""
        if not ADVANCED_DB_AVAILABLE:
            logger.warning("Advanced database features not available")
            return False
            
        try:
            # Initialize PostgreSQL
            await self._init_postgresql()
            
            # Initialize Redis
            await self._init_redis()
            
            # Initialize Vector Database
            await self._init_vector_db()
            
            self._initialized = True
            logger.info("Advanced database system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            return False
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            self.engine = create_async_engine(
                self.config.postgresql_url,
                echo=False,
                pool_size=10,
                max_overflow=20
            )
            
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                
            logger.info("PostgreSQL initialized")
            
        except Exception as e:
            logger.error(f"PostgreSQL initialization failed: {e}")
            # Fallback to SQLite for development
            sqlite_url = "sqlite+aiosqlite:///./aeonforge.db"
            self.engine = create_async_engine(sqlite_url, echo=False)
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Fallback to SQLite database")
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        if not self.config.enable_caching:
            return
            
        try:
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info("Redis initialized")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_client = None
    
    async def _init_vector_db(self):
        """Initialize Vector Database (ChromaDB)"""
        if not self.config.enable_vector_search:
            return
            
        try:
            os.makedirs(self.config.vector_db_path, exist_ok=True)
            self.vector_db = chromadb.PersistentClient(path=self.config.vector_db_path)
            
            # Create collections
            try:
                self.code_collection = self.vector_db.get_collection("code_snippets")
            except:
                self.code_collection = self.vector_db.create_collection("code_snippets")
                
            try:
                self.docs_collection = self.vector_db.get_collection("documentation")
            except:
                self.docs_collection = self.vector_db.create_collection("documentation")
                
            logger.info("Vector database initialized")
        except Exception as e:
            logger.warning(f"Vector database not available: {e}")
            self.vector_db = None
    
    @asynccontextmanager
    async def get_session(self):
        """Get database session"""
        if not self._initialized:
            await self.initialize()
            
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_project(self, name: str, description: str, owner_id: str, settings: Dict = None) -> str:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        
        async with self.get_session() as session:
            project = Project(
                id=project_id,
                name=name,
                description=description,
                owner_id=owner_id,
                settings=settings or {}
            )
            session.add(project)
            await session.commit()
            
        # Cache project data
        await self._cache_project(project_id, {
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "created_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Created project: {project_id}")
        return project_id
    
    async def get_project(self, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        # Try cache first
        cached = await self._get_cached_project(project_id)
        if cached:
            return cached
            
        async with self.get_session() as session:
            result = await session.get(Project, project_id)
            if result:
                project_data = {
                    "id": result.id,
                    "name": result.name,
                    "description": result.description,
                    "owner_id": result.owner_id,
                    "created_at": result.created_at.isoformat(),
                    "updated_at": result.updated_at.isoformat(),
                    "settings": result.settings,
                    "is_active": result.is_active
                }
                await self._cache_project(project_id, project_data)
                return project_data
                
        return None
    
    async def create_conversation(self, user_id: str, title: str, project_id: str = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        
        async with self.get_session() as session:
            conversation = Conversation(
                id=conversation_id,
                project_id=project_id,
                user_id=user_id,
                title=title
            )
            session.add(conversation)
            await session.commit()
            
        logger.info(f"Created conversation: {conversation_id}")
        return conversation_id
    
    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Dict = None) -> str:
        """Add message to conversation"""
        message_id = str(uuid.uuid4())
        
        async with self.get_session() as session:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                metadata=metadata or {}
            )
            session.add(message)
            await session.commit()
            
        # Store in vector database for semantic search
        await self._store_message_vector(message_id, content, role)
        
        return message_id
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation message history"""
        async with self.get_session() as session:
            from sqlalchemy import select
            
            stmt = select(Message).where(
                Message.conversation_id == conversation_id
            ).order_by(Message.timestamp.desc()).limit(limit)
            
            result = await session.execute(stmt)
            messages = result.scalars().all()
            
            return [{
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            } for msg in reversed(messages)]
    
    async def store_code_generation(self, project_id: str, user_id: str, request: str, 
                                  generated_code: str, language: str, metadata: Dict = None) -> str:
        """Store code generation history"""
        generation_id = str(uuid.uuid4())
        
        async with self.get_session() as session:
            code_gen = CodeGeneration(
                id=generation_id,
                project_id=project_id,
                user_id=user_id,
                request=request,
                generated_code=generated_code,
                language=language,
                metadata=metadata or {}
            )
            session.add(code_gen)
            await session.commit()
            
        # Store in vector database for code search
        await self._store_code_vector(generation_id, generated_code, language, request)
        
        return generation_id
    
    async def search_similar_code(self, query: str, language: str = None, limit: int = 10) -> List[Dict]:
        """Search for similar code using vector similarity"""
        if not self.vector_db:
            return []
            
        try:
            results = self.code_collection.query(
                query_texts=[query],
                n_results=limit,
                where={"language": language} if language else None
            )
            
            similar_code = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                similar_code.append({
                    "id": results["ids"][0][i],
                    "code": doc,
                    "language": metadata.get("language"),
                    "request": metadata.get("request"),
                    "similarity": results["distances"][0][i] if "distances" in results else 0.0
                })
                
            return similar_code
            
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return []
    
    async def search_conversations(self, query: str, user_id: str = None, limit: int = 10) -> List[Dict]:
        """Search conversations using vector similarity"""
        if not self.vector_db:
            return []
            
        try:
            where_clause = {}
            if user_id:
                where_clause["user_id"] = user_id
                
            results = self.docs_collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause if where_clause else None
            )
            
            conversations = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                conversations.append({
                    "message_id": results["ids"][0][i],
                    "content": doc,
                    "role": metadata.get("role"),
                    "conversation_id": metadata.get("conversation_id"),
                    "similarity": results["distances"][0][i] if "distances" in results else 0.0
                })
                
            return conversations
            
        except Exception as e:
            logger.error(f"Conversation search failed: {e}")
            return []
    
    async def _cache_project(self, project_id: str, data: Dict):
        """Cache project data in Redis"""
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"project:{project_id}", 
                    3600, 
                    json.dumps(data, default=str)
                )
            except Exception as e:
                logger.warning(f"Cache failed: {e}")
    
    async def _get_cached_project(self, project_id: str) -> Optional[Dict]:
        """Get cached project data"""
        if self.redis_client:
            try:
                cached = await self.redis_client.get(f"project:{project_id}")
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        return None
    
    async def _store_message_vector(self, message_id: str, content: str, role: str):
        """Store message in vector database"""
        if self.vector_db:
            try:
                self.docs_collection.add(
                    documents=[content],
                    metadatas=[{"role": role, "type": "message"}],
                    ids=[message_id]
                )
            except Exception as e:
                logger.warning(f"Vector storage failed: {e}")
    
    async def _store_code_vector(self, generation_id: str, code: str, language: str, request: str):
        """Store code in vector database"""
        if self.vector_db:
            try:
                self.code_collection.add(
                    documents=[code],
                    metadatas=[{
                        "language": language,
                        "request": request,
                        "type": "code_generation"
                    }],
                    ids=[generation_id]
                )
            except Exception as e:
                logger.warning(f"Code vector storage failed: {e}")
    
    async def get_analytics(self, project_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics"""
        analytics = {
            "total_projects": 0,
            "total_conversations": 0,
            "total_messages": 0,
            "total_code_generations": 0,
            "daily_activity": [],
            "popular_languages": {},
            "user_activity": {}
        }
        
        async with self.get_session() as session:
            from sqlalchemy import func, select
            
            # Get basic counts
            projects_count = await session.execute(select(func.count(Project.id)))
            analytics["total_projects"] = projects_count.scalar()
            
            conversations_count = await session.execute(select(func.count(Conversation.id)))
            analytics["total_conversations"] = conversations_count.scalar()
            
            messages_count = await session.execute(select(func.count(Message.id)))
            analytics["total_messages"] = messages_count.scalar()
            
            code_count = await session.execute(select(func.count(CodeGeneration.id)))
            analytics["total_code_generations"] = code_count.scalar()
            
            # Get language popularity
            lang_query = select(
                CodeGeneration.language,
                func.count(CodeGeneration.id).label('count')
            ).group_by(CodeGeneration.language)
            
            lang_result = await session.execute(lang_query)
            for row in lang_result:
                analytics["popular_languages"][row.language] = row.count
        
        return analytics
    
    async def cleanup(self):
        """Cleanup database connections"""
        if self.redis_client:
            await self.redis_client.close()
            
        if self.engine:
            await self.engine.dispose()
            
        logger.info("Database connections cleaned up")

# Global database manager instance
db_manager = AdvancedDatabaseManager()

async def get_database_manager() -> AdvancedDatabaseManager:
    """Get the global database manager instance"""
    if not db_manager._initialized:
        await db_manager.initialize()
    return db_manager

# Async context manager for database operations
@asynccontextmanager
async def database_session():
    """Context manager for database operations"""
    manager = await get_database_manager()
    async with manager.get_session() as session:
        yield session

# Export main classes and functions
__all__ = [
    'AdvancedDatabaseManager',
    'DatabaseConfig',
    'Project',
    'Conversation', 
    'Message',
    'CodeGeneration',
    'get_database_manager',
    'database_session',
    'db_manager'
]

if __name__ == "__main__":
    # Test the database system
    async def test_database():
        config = DatabaseConfig()
        manager = AdvancedDatabaseManager(config)
        
        # Initialize
        success = await manager.initialize()
        if success:
            print("Database system initialized successfully!")
            
            # Test project creation
            project_id = await manager.create_project(
                name="Test Project",
                description="A test project for Phase 8",
                owner_id="user_123"
            )
            print(f"Created project: {project_id}")
            
            # Test conversation
            conv_id = await manager.create_conversation(
                user_id="user_123",
                title="Test Conversation",
                project_id=project_id
            )
            print(f"Created conversation: {conv_id}")
            
            # Test message
            msg_id = await manager.add_message(
                conversation_id=conv_id,
                role="user",
                content="Hello, this is a test message!"
            )
            print(f"Added message: {msg_id}")
            
            # Test code generation storage
            code_id = await manager.store_code_generation(
                project_id=project_id,
                user_id="user_123",
                request="Create a hello world function",
                generated_code="def hello_world():\n    print('Hello, World!')",
                language="python"
            )
            print(f"Stored code generation: {code_id}")
            
            # Test analytics
            analytics = await manager.get_analytics()
            print("Analytics:", analytics)
            
        else:
            print("Database initialization failed")
            
        await manager.cleanup()
    
    # Run test
    asyncio.run(test_database())