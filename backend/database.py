"""
Database Configuration and Connection
PostgreSQL setup with SQLAlchemy ORM
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://dyslexia_user:12Varsh%400513@localhost:5432/dyslexia_db"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see SQL queries
    pool_pre_ping=True,  # Test connections before using
    poolclass=NullPool  # Disable connection pooling for simplicity
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session
    Usage: def my_endpoint(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this once at startup
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Drop all tables - use with caution!
    """
    Base.metadata.drop_all(bind=engine)
