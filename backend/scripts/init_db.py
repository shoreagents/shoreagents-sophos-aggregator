#!/usr/bin/env python3
"""
Database initialization script for Sophos Aggregator
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, create_tables
from app.sophos_client import SophosClient

def init_database():
    """Initialize the database and create tables."""
    load_dotenv()
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        # Create tables
        print("🔧 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully")
        
        # Test database connection
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test query
        result = db.execute("SELECT 1").fetchone()
        if result:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            sys.exit(1)
            
        db.close()
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

def test_sophos_connection():
    """Test Sophos API connection."""
    print("\n🔧 Testing Sophos API connection...")
    
    try:
        client = SophosClient()
        token = client.get_access_token()
        
        if token:
            print("✅ Sophos API connection successful")
            return True
        else:
            print("❌ Sophos API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Sophos API connection failed: {e}")
        return False

def main():
    """Main initialization function."""
    print("🚀 Initializing Sophos Aggregator Backend...")
    
    # Initialize database
    init_database()
    
    # Test Sophos connection
    sophos_ok = test_sophos_connection()
    
    print("\n📋 Summary:")
    print("✅ Database: Initialized successfully")
    if sophos_ok:
        print("✅ Sophos API: Connection successful")
    else:
        print("⚠️  Sophos API: Connection failed - check credentials")
    
    print("\n🎉 Initialization complete!")
    print("\nNext steps:")
    print("1. Start the application: python run.py")
    print("2. Test endpoints: curl http://localhost:8000/health")
    print("3. Fetch data: curl -X POST http://localhost:8000/fetch/endpoints")

if __name__ == "__main__":
    main() 