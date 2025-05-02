#!/usr/bin/env python3
"""
Database initialization script that creates all tables defined in models.py
"""
import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the SQLAlchemy models and Base
from src.database.models import Base

def init_db():
    """Initialize the database with all models defined in models.py"""
    # Load environment variables
    load_dotenv()

    # Get database URL from environment or use default
    db_url = os.getenv("DATABASE_URL", "mysql+pymysql://root:ImKundan@localhost:3306/warehouse_vision")
    
    print(f"Connecting to database at: {db_url}")
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Create all tables
        Base.metadata.create_all(engine)
        
        print("Database tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        return False

if __name__ == "__main__":
    # Allow database URL to be passed as command line argument
    if len(sys.argv) > 1:
        os.environ["DATABASE_URL"] = sys.argv[1]
    
    success = init_db()
    sys.exit(0 if success else 1)