"""
Setup script for Aeonforge PostgreSQL database
This script helps set up either local PostgreSQL or Supabase connection
"""

import asyncio
import os
import sys

# Add the api directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.database import init_database, AsyncSessionLocal, create_user, create_chat

async def setup_database():
    """Initialize database and create sample data"""
    print("🔧 Setting up Aeonforge database...")
    
    try:
        # Initialize database tables
        await init_database()
        print("✅ Database tables created successfully")
        
        # Create a sample user
        async with AsyncSessionLocal() as db:
            try:
                sample_user = await create_user(
                    db, 
                    username="demo_user", 
                    email="demo@aeonforge.com",
                    hashed_password="hashed_demo_password"
                )
                print(f"✅ Sample user created: {sample_user.username}")
                
                # Create a sample chat
                sample_chat = await create_chat(
                    db, 
                    user_id=sample_user.id,
                    title="Welcome Chat"
                )
                print(f"✅ Sample chat created: {sample_chat.title}")
                
            except Exception as e:
                print(f"ℹ️  Sample data may already exist: {e}")
        
        print("\n🎉 Database setup completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Make sure PostgreSQL is running locally (port 5432)")
        print("2. Database: aeonforge")
        print("3. Username: postgres")
        print("4. Password: password")
        print("\n🚀 You can now start the API server!")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure PostgreSQL is installed and running")
        print("2. Create database 'aeonforge'")
        print("3. Check connection string in database.py")
        print("4. Install requirements: pip install -r api/requirements.txt")

def get_database_info():
    """Display database configuration information"""
    print("🗃️  Aeonforge Database Configuration")
    print("=" * 50)
    print("Default Local PostgreSQL:")
    print("  Host: localhost")
    print("  Port: 5432")
    print("  Database: aeonforge")
    print("  Username: postgres")
    print("  Password: password")
    print("  Connection: postgresql+asyncpg://postgres:password@localhost:5432/aeonforge")
    print("\nFor Supabase:")
    print("  Set DATABASE_URL environment variable")
    print("  Format: postgresql+asyncpg://user:pass@host:5432/dbname")
    print("\nFeatures:")
    print("  ✅ User Management")
    print("  ✅ Chat Storage")
    print("  ✅ Message History")
    print("  ✅ Chat-Specific Memory")
    print("  ✅ File Attachments")
    print("  ✅ Context Awareness")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "info":
        get_database_info()
    else:
        asyncio.run(setup_database())