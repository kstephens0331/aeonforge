#!/usr/bin/env python3
"""
PostgreSQL Database Setup for AeonForge
Creates all required tables for the memory management system
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in environment variables.")
    print("Please update your .env file with the correct DATABASE_URL")
    print("Example: DATABASE_URL=postgresql://user:password@host:port/database")
    exit(1)

if "YOUR_PASSWORD_HERE" in DATABASE_URL:
    print("Please replace 'YOUR_PASSWORD_HERE' in your .env file with the actual PostgreSQL password from Render")
    exit(1)

def create_tables():
    """Create all required tables for AeonForge"""
    
    print("Setting up AeonForge PostgreSQL Database...")
    
    try:
        # Connect to PostgreSQL with SSL settings for Render
        import ssl
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor,
            sslmode='require'
        )
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # 1. Users table with memory management
        print("Creating users table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            name VARCHAR(255) NOT NULL,
            plan VARCHAR(50) DEFAULT 'free',
            daily_usage INTEGER DEFAULT 0,
            usage_reset_date DATE DEFAULT CURRENT_DATE,
            stripe_customer_id VARCHAR(255),
            memory_used BIGINT DEFAULT 0,
            memory_limit BIGINT DEFAULT 536870912, -- 0.5 GB for free plan
            organization_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 2. Organizations table for enterprise accounts
        print("Creating organizations table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            plan VARCHAR(50) DEFAULT 'enterprise',
            admin_user_id INTEGER,
            total_memory_limit BIGINT DEFAULT 2147483648,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_user_id) REFERENCES users (id)
        )
        ''')
        
        # 3. Conversations table
        print("Creating conversations table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title VARCHAR(500) NOT NULL,
            model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
            memory_size BIGINT DEFAULT 0,
            is_archived BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 4. Chat messages table
        print("Creating chat_messages table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            model_used VARCHAR(100),
            tokens_used INTEGER DEFAULT 0,
            memory_size BIGINT DEFAULT 0,
            saved_to_memory BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 5. User memory/knowledge base
        print("Creating user_memory table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_memory (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            key_name VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(100) DEFAULT 'general',
            memory_size BIGINT DEFAULT 0,
            importance_score INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 6. Projects table
        print("Creating projects table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50) DEFAULT 'active',
            memory_size BIGINT DEFAULT 0,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 7. Search history table
        print("Creating search_history table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            query VARCHAR(1000) NOT NULL,
            results_count INTEGER DEFAULT 0,
            memory_size BIGINT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # 8. Memory usage tracking
        print("Creating memory_usage table...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_usage (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            table_name VARCHAR(100) NOT NULL,
            record_id INTEGER NOT NULL,
            memory_size BIGINT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create indexes for better performance
        print("Creating indexes for performance...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages(conversation_id);",
            "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_memory_user_id ON user_memory(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_memory_key_name ON user_memory(user_id, key_name);",
            "CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_memory_usage_user_id ON memory_usage(user_id);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Commit all changes
        conn.commit()
        
        print("\nDatabase setup complete!")
        print("\nCreated tables:")
        print("   - users (with memory management)")
        print("   - organizations (enterprise support)")
        print("   - conversations (chat history)")
        print("   - chat_messages (message storage)")
        print("   - user_memory (knowledge base)")
        print("   - projects (project tracking)")
        print("   - search_history (search tracking)")
        print("   - memory_usage (quota management)")
        print("\nPerformance indexes created")
        print("\nReady for AeonForge deployment!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
            print("Database connection closed")
    
    return True

def verify_tables():
    """Verify all tables were created successfully"""
    try:
        conn = psycopg2.connect(
            DATABASE_URL,
            cursor_factory=RealDictCursor,
            sslmode='require'
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = [row['table_name'] for row in cursor.fetchall()]
        
        expected_tables = [
            'users', 'organizations', 'conversations', 'chat_messages',
            'user_memory', 'projects', 'search_history', 'memory_usage'
        ]
        
        print("\nVerification Results:")
        for table in expected_tables:
            if table in tables:
                print(f"   OK: {table}")
            else:
                print(f"   MISSING: {table}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error verifying tables: {e}")
        return False

if __name__ == "__main__":
    print("AeonForge PostgreSQL Database Setup")
    print("=" * 50)
    
    if create_tables():
        verify_tables()
        print("\nDatabase is ready for production deployment!")
    else:
        print("\nSetup failed. Please check the error messages above.")