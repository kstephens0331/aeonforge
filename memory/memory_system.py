"""
Aeonforge Memory System - Persistent Memory and Project Management
Maintains comprehensive memory across sessions with project-specific contexts
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import pickle
import threading
from collections import defaultdict

@dataclass
class ConversationEntry:
    """Single conversation entry"""
    id: str
    session_id: str
    project_id: Optional[str]
    timestamp: datetime
    user_message: str
    assistant_response: str
    context_tags: List[str]
    files_referenced: List[str]
    tools_used: List[str]
    metadata: Dict[str, Any]

@dataclass
class ProjectContext:
    """Project-specific context and instructions"""
    id: str
    name: str
    description: str
    base_path: str
    instructions: str
    custom_rules: List[str]
    file_patterns: List[str]  # Files that belong to this project
    knowledge_base: Dict[str, Any]
    active_sessions: List[str]
    created_at: datetime
    last_accessed: datetime
    metadata: Dict[str, Any]

@dataclass
class KnowledgeItem:
    """Individual piece of knowledge"""
    id: str
    content: str
    category: str
    tags: List[str]
    source: str  # 'conversation', 'file', 'manual'
    confidence: float
    created_at: datetime
    last_accessed: datetime
    access_count: int
    related_items: List[str]

@dataclass
class SessionContext:
    """Current session context"""
    id: str
    project_id: Optional[str]
    start_time: datetime
    last_activity: datetime
    conversation_count: int
    active_files: Set[str]
    working_directory: str
    phase_states: Dict[str, Any]
    temporary_context: Dict[str, Any]

class MemorySystem:
    """Comprehensive memory system for Aeonforge"""
    
    def __init__(self, data_dir: str = "memory_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Database setup
        self.db_path = self.data_dir / "memory.db"
        self.knowledge_db_path = self.data_dir / "knowledge.db"
        
        # Current session
        self.current_session: Optional[SessionContext] = None
        self.current_project: Optional[ProjectContext] = None
        
        # Memory caches
        self.conversation_cache: Dict[str, ConversationEntry] = {}
        self.project_cache: Dict[str, ProjectContext] = {}
        self.knowledge_cache: Dict[str, KnowledgeItem] = {}
        
        # Threading
        self.lock = threading.RLock()
        
        # Initialize databases
        self._init_databases()
        
        # Start new session
        self._start_new_session()
    
    def _init_databases(self):
        """Initialize memory databases"""
        # Main memory database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                project_id TEXT,
                timestamp TIMESTAMP NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                context_tags TEXT,
                files_referenced TEXT,
                tools_used TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                base_path TEXT NOT NULL,
                instructions TEXT,
                custom_rules TEXT,
                file_patterns TEXT,
                knowledge_base TEXT,
                active_sessions TEXT,
                created_at TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP NOT NULL,
                metadata TEXT
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                project_id TEXT,
                start_time TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                conversation_count INTEGER DEFAULT 0,
                active_files TEXT,
                working_directory TEXT,
                phase_states TEXT,
                temporary_context TEXT
            )
        """)
        
        # Indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_session ON conversations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_project ON conversations(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_path ON projects(base_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_project ON sessions(project_id)")
        
        conn.commit()
        conn.close()
        
        # Knowledge database
        conn = sqlite3.connect(str(self.knowledge_db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,
                source TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP NOT NULL,
                access_count INTEGER DEFAULT 0,
                related_items TEXT,
                content_hash TEXT,
                project_id TEXT
            )
        """)
        
        # Full-text search for knowledge
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                id, content, category, tags, source
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_items(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_items(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_hash ON knowledge_items(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_project ON knowledge_items(project_id)")
        
        conn.commit()
        conn.close()
    
    def _start_new_session(self):
        """Start a new session"""
        session_id = str(uuid.uuid4())
        
        self.current_session = SessionContext(
            id=session_id,
            project_id=None,
            start_time=datetime.now(),
            last_activity=datetime.now(),
            conversation_count=0,
            active_files=set(),
            working_directory=str(Path.cwd()),
            phase_states={},
            temporary_context={}
        )
        
        self._save_session()
    
    def remember_conversation(self, user_message: str, assistant_response: str, 
                            context_tags: List[str] = None, files_referenced: List[str] = None,
                            tools_used: List[str] = None, metadata: Dict[str, Any] = None):
        """Store a conversation in memory"""
        if not self.current_session:
            self._start_new_session()
        
        conversation_id = str(uuid.uuid4())
        entry = ConversationEntry(
            id=conversation_id,
            session_id=self.current_session.id,
            project_id=self.current_project.id if self.current_project else None,
            timestamp=datetime.now(),
            user_message=user_message,
            assistant_response=assistant_response,
            context_tags=context_tags or [],
            files_referenced=files_referenced or [],
            tools_used=tools_used or [],
            metadata=metadata or {}
        )
        
        with self.lock:
            # Store in cache
            self.conversation_cache[conversation_id] = entry
            
            # Store in database
            self._save_conversation(entry)
            
            # Update session
            self.current_session.conversation_count += 1
            self.current_session.last_activity = datetime.now()
            
            if files_referenced:
                self.current_session.active_files.update(files_referenced)
            
            self._save_session()
            
            # Extract knowledge from conversation
            self._extract_knowledge(entry)
        
        return conversation_id
    
    def _save_conversation(self, entry: ConversationEntry):
        """Save conversation to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations 
            (id, session_id, project_id, timestamp, user_message, assistant_response,
             context_tags, files_referenced, tools_used, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.session_id,
            entry.project_id,
            entry.timestamp.isoformat(),
            entry.user_message,
            entry.assistant_response,
            json.dumps(entry.context_tags),
            json.dumps(entry.files_referenced),
            json.dumps(entry.tools_used),
            json.dumps(entry.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_session(self):
        """Save current session to database"""
        if not self.current_session:
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions
            (id, project_id, start_time, last_activity, conversation_count,
             active_files, working_directory, phase_states, temporary_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.current_session.id,
            self.current_session.project_id,
            self.current_session.start_time.isoformat(),
            self.current_session.last_activity.isoformat(),
            self.current_session.conversation_count,
            json.dumps(list(self.current_session.active_files)),
            self.current_session.working_directory,
            json.dumps(self.current_session.phase_states),
            json.dumps(self.current_session.temporary_context)
        ))
        
        conn.commit()
        conn.close()
    
    def create_project(self, name: str, base_path: str, description: str = "",
                      instructions: str = "", custom_rules: List[str] = None,
                      file_patterns: List[str] = None) -> str:
        """Create a new project context"""
        project_id = str(uuid.uuid4())
        
        project = ProjectContext(
            id=project_id,
            name=name,
            description=description,
            base_path=str(Path(base_path).absolute()),
            instructions=instructions,
            custom_rules=custom_rules or [],
            file_patterns=file_patterns or ["**/*"],
            knowledge_base={},
            active_sessions=[],
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            metadata={}
        )
        
        with self.lock:
            self.project_cache[project_id] = project
            self._save_project(project)
        
        return project_id
    
    def _save_project(self, project: ProjectContext):
        """Save project to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO projects
            (id, name, description, base_path, instructions, custom_rules,
             file_patterns, knowledge_base, active_sessions, created_at,
             last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.id,
            project.name,
            project.description,
            project.base_path,
            project.instructions,
            json.dumps(project.custom_rules),
            json.dumps(project.file_patterns),
            json.dumps(project.knowledge_base),
            json.dumps(project.active_sessions),
            project.created_at.isoformat(),
            project.last_accessed.isoformat(),
            json.dumps(project.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def switch_to_project(self, project_id: str) -> bool:
        """Switch current context to a project"""
        project = self._load_project(project_id)
        if not project:
            return False
        
        with self.lock:
            self.current_project = project
            
            # Update session
            if self.current_session:
                self.current_session.project_id = project_id
                self.current_session.working_directory = project.base_path
                self._save_session()
            
            # Update project access
            project.last_accessed = datetime.now()
            if self.current_session and self.current_session.id not in project.active_sessions:
                project.active_sessions.append(self.current_session.id)
            
            self._save_project(project)
        
        return True
    
    def _load_project(self, project_id: str) -> Optional[ProjectContext]:
        """Load project from cache or database"""
        if project_id in self.project_cache:
            return self.project_cache[project_id]
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))
        
        project = ProjectContext(
            id=data['id'],
            name=data['name'],
            description=data['description'] or "",
            base_path=data['base_path'],
            instructions=data['instructions'] or "",
            custom_rules=json.loads(data['custom_rules'] or '[]'),
            file_patterns=json.loads(data['file_patterns'] or '["**/*"]'),
            knowledge_base=json.loads(data['knowledge_base'] or '{}'),
            active_sessions=json.loads(data['active_sessions'] or '[]'),
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            metadata=json.loads(data['metadata'] or '{}')
        )
        
        self.project_cache[project_id] = project
        return project
    
    def get_project_by_path(self, file_path: str) -> Optional[ProjectContext]:
        """Find project that contains the given file path"""
        file_path = str(Path(file_path).absolute())
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects ORDER BY LENGTH(base_path) DESC")
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            base_path = row[3]  # base_path column
            if file_path.startswith(base_path):
                project_id = row[0]  # id column
                return self._load_project(project_id)
        
        return None
    
    def _extract_knowledge(self, entry: ConversationEntry):
        """Extract knowledge from conversation"""
        # Extract file references
        for file_path in entry.files_referenced:
            self._add_knowledge(
                content=f"File referenced: {file_path}",
                category="file_reference",
                tags=["file", "reference"],
                source="conversation",
                confidence=0.8
            )
        
        # Extract tool usage patterns
        for tool in entry.tools_used:
            self._add_knowledge(
                content=f"Tool used: {tool}",
                category="tool_usage",
                tags=["tool", "usage"],
                source="conversation",
                confidence=0.7
            )
        
        # Extract code snippets (simple detection)
        if "```" in entry.assistant_response:
            self._add_knowledge(
                content=entry.assistant_response,
                category="code_snippet",
                tags=["code", "example"],
                source="conversation",
                confidence=0.9
            )
        
        # Extract instructions and rules
        if any(keyword in entry.user_message.lower() for keyword in 
               ["remember", "always", "never", "rule", "instruction"]):
            self._add_knowledge(
                content=entry.user_message,
                category="instruction",
                tags=["instruction", "rule"],
                source="conversation",
                confidence=0.95
            )
    
    def _add_knowledge(self, content: str, category: str, tags: List[str],
                      source: str, confidence: float = 1.0):
        """Add knowledge item"""
        # Create content hash to avoid duplicates
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        conn = sqlite3.connect(str(self.knowledge_db_path))
        cursor = conn.cursor()
        
        # Check if already exists
        cursor.execute("SELECT id FROM knowledge_items WHERE content_hash = ?", (content_hash,))
        if cursor.fetchone():
            conn.close()
            return
        
        knowledge_id = str(uuid.uuid4())
        
        knowledge = KnowledgeItem(
            id=knowledge_id,
            content=content,
            category=category,
            tags=tags,
            source=source,
            confidence=confidence,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            related_items=[]
        )
        
        # Store in database
        cursor.execute("""
            INSERT INTO knowledge_items
            (id, content, category, tags, source, confidence, created_at,
             last_accessed, access_count, related_items, content_hash, project_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            knowledge.id,
            knowledge.content,
            knowledge.category,
            json.dumps(knowledge.tags),
            knowledge.source,
            knowledge.confidence,
            knowledge.created_at.isoformat(),
            knowledge.last_accessed.isoformat(),
            knowledge.access_count,
            json.dumps(knowledge.related_items),
            content_hash,
            self.current_project.id if self.current_project else None
        ))
        
        # Add to FTS index
        cursor.execute("""
            INSERT INTO knowledge_fts (id, content, category, tags, source)
            VALUES (?, ?, ?, ?, ?)
        """, (
            knowledge.id,
            knowledge.content,
            knowledge.category,
            ' '.join(knowledge.tags),
            knowledge.source
        ))
        
        conn.commit()
        conn.close()
        
        self.knowledge_cache[knowledge_id] = knowledge
    
    def search_memory(self, query: str, category: str = None, 
                     project_only: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
        """Search through memory and knowledge"""
        results = []
        
        # Search conversations
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        conv_query = """
            SELECT id, user_message, assistant_response, timestamp, context_tags
            FROM conversations
            WHERE (user_message LIKE ? OR assistant_response LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]
        
        if project_only and self.current_project:
            conv_query += " AND project_id = ?"
            params.append(self.current_project.id)
        
        conv_query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(conv_query, params)
        
        for row in cursor.fetchall():
            results.append({
                'type': 'conversation',
                'id': row[0],
                'user_message': row[1][:200] + "..." if len(row[1]) > 200 else row[1],
                'assistant_response': row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                'timestamp': row[3],
                'relevance': 'high'
            })
        
        conn.close()
        
        # Search knowledge base
        conn = sqlite3.connect(str(self.knowledge_db_path))
        cursor = conn.cursor()
        
        knowledge_query = "SELECT * FROM knowledge_fts WHERE knowledge_fts MATCH ?"
        k_params = [query]
        
        if category:
            knowledge_query += " AND category = ?"
            k_params.append(category)
        
        knowledge_query += " LIMIT ?"
        k_params.append(limit)
        
        cursor.execute(knowledge_query, k_params)
        
        for row in cursor.fetchall():
            # Get full details
            cursor.execute("SELECT * FROM knowledge_items WHERE id = ?", (row[0],))
            full_row = cursor.fetchone()
            
            if full_row:
                results.append({
                    'type': 'knowledge',
                    'id': full_row[0],
                    'content': full_row[1][:200] + "..." if len(full_row[1]) > 200 else full_row[1],
                    'category': full_row[2],
                    'tags': json.loads(full_row[3]),
                    'source': full_row[4],
                    'confidence': full_row[5],
                    'relevance': 'medium'
                })
        
        conn.close()
        
        return results
    
    def get_context_for_current_session(self) -> Dict[str, Any]:
        """Get relevant context for current session"""
        context = {
            'session': asdict(self.current_session) if self.current_session else None,
            'project': asdict(self.current_project) if self.current_project else None,
            'recent_conversations': [],
            'relevant_knowledge': [],
            'active_files': list(self.current_session.active_files) if self.current_session else [],
            'phase_states': self.current_session.phase_states if self.current_session else {}
        }
        
        if self.current_session:
            # Get recent conversations
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_message, assistant_response, timestamp, context_tags
                FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (self.current_session.id,))
            
            for row in cursor.fetchall():
                context['recent_conversations'].append({
                    'user_message': row[0],
                    'assistant_response': row[1],
                    'timestamp': row[2],
                    'tags': json.loads(row[3]) if row[3] else []
                })
            
            conn.close()
        
        return context
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, base_path, last_accessed, 
                   (SELECT COUNT(*) FROM conversations WHERE project_id = projects.id) as conversation_count
            FROM projects
            ORDER BY last_accessed DESC
        """)
        
        projects = []
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'base_path': row[3],
                'last_accessed': row[4],
                'conversation_count': row[5]
            })
        
        conn.close()
        return projects
    
    def update_project_instructions(self, project_id: str, instructions: str, 
                                  custom_rules: List[str] = None):
        """Update project instructions"""
        project = self._load_project(project_id)
        if not project:
            return False
        
        project.instructions = instructions
        if custom_rules is not None:
            project.custom_rules = custom_rules
        
        self._save_project(project)
        return True
    
    def get_project_instructions(self, project_id: str = None) -> Dict[str, Any]:
        """Get project-specific instructions"""
        project_id = project_id or (self.current_project.id if self.current_project else None)
        if not project_id:
            return {}
        
        project = self._load_project(project_id)
        if not project:
            return {}
        
        return {
            'instructions': project.instructions,
            'custom_rules': project.custom_rules,
            'project_name': project.name,
            'base_path': project.base_path
        }
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old conversation data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Archive old conversations
        cursor.execute("""
            DELETE FROM conversations 
            WHERE timestamp < ? AND session_id NOT IN (
                SELECT id FROM sessions WHERE last_activity > ?
            )
        """, (cutoff_date.isoformat(), cutoff_date.isoformat()))
        
        deleted_conversations = cursor.rowcount
        
        # Clean up old sessions
        cursor.execute("""
            DELETE FROM sessions 
            WHERE last_activity < ?
        """, (cutoff_date.isoformat(),))
        
        deleted_sessions = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        # Clean knowledge cache
        self.knowledge_cache.clear()
        self.conversation_cache.clear()
        
        return {
            'deleted_conversations': deleted_conversations,
            'deleted_sessions': deleted_sessions
        }

def main():
    """Test the memory system"""
    memory = MemorySystem()
    
    # Create a test project
    project_id = memory.create_project(
        name="Test Project",
        base_path="/path/to/project",
        description="A test project for the memory system",
        instructions="Always use TypeScript. Follow strict coding standards.",
        custom_rules=["Use async/await", "Include comprehensive tests"]
    )
    
    # Switch to project
    memory.switch_to_project(project_id)
    
    # Remember some conversations
    memory.remember_conversation(
        user_message="Create a new React component",
        assistant_response="I'll create a TypeScript React component for you...",
        context_tags=["react", "typescript"],
        files_referenced=["src/components/NewComponent.tsx"],
        tools_used=["Write", "Edit"]
    )
    
    # Search memory
    results = memory.search_memory("React component")
    print(f"Found {len(results)} results")
    
    # Get context
    context = memory.get_context_for_current_session()
    print(f"Current context: {context}")

if __name__ == "__main__":
    main()