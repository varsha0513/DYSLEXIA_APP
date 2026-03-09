"""
Test database connection
Verify that PostgreSQL is properly configured
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    exit(1)

print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print(f"✅ PostgreSQL is running and accessible")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Now test importing the models and creating tables
try:
    from database import Base, engine, init_db
    print("✅ Successfully imported database configuration")
    
    # Initialize tables
    init_db()
    print("✅ Successfully created all database tables")
    
except Exception as e:
    print(f"❌ Failed to create tables: {e}")
    exit(1)

print("\n🎉 All tests passed! Database is ready to use.")
