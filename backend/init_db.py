#!/usr/bin/env python3

"""
Database initialization script for Idea Shaper
Creates all necessary tables with the correct schema
"""

from database import create_tables, engine, Base
from sqlalchemy import text

def init_database():
    """Initialize the database with all tables"""
    print("Creating database tables...")
    
    # Drop all tables first (if they exist)
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")
    
    # Verify tables were created
    with engine.connect() as conn:
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in result]
        print(f"Created tables: {tables}")

if __name__ == "__main__":
    init_database()