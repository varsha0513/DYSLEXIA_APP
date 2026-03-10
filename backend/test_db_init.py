"""
Test database initialization and table creation
"""

from database import init_db, Base, engine
from models import User, Assessment, AssessmentResult, PronunciationAttempt, PronunciationCheck, ProgressHistory, SpeedTrainerSession, ChunkReadingSession
import sqlalchemy

print("✅ All imports successful!")
print(f"📊 SQLAlchemy version: {sqlalchemy.__version__}")
print()

print("🔨 Creating database tables...")
try:
    init_db()
    print("✅ Database tables created successfully!")
    print()
    
    # List created tables
    inspector = sqlalchemy.inspect(engine)
    tables = inspector.get_table_names()
    print("📋 Created tables:")
    for table in sorted(tables):
        print(f"   ✓ {table}")
    print()
    print(f"Total tables: {len(tables)}")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
    import traceback
    traceback.print_exc()
