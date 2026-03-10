"""
View database contents
"""

from database import SessionLocal, engine
from models import User, Assessment, AssessmentResult
from sqlalchemy import text

print("=" * 70)
print("📊 DYSLEXIA APP DATABASE VIEWER")
print("=" * 70)
print()

db = SessionLocal()

try:
    # Check users
    print("1️⃣ USERS TABLE")
    print("-" * 70)
    users = db.query(User).all()
    if users:
        print(f"   Found {len(users)} user(s):")
        for user in users:
            print(f"   • ID: {user.id} | Username: {user.username} | Email: {user.email} | Age: {user.age}")
    else:
        print("   ❌ No users yet (will be created on first assessment)")
    print()

    # Check assessments
    print("2️⃣ ASSESSMENTS TABLE")
    print("-" * 70)
    assessments = db.query(Assessment).all()
    if assessments:
        print(f"   Found {len(assessments)} assessment(s):")
        for assessment in assessments:
            print(f"   • ID: {assessment.id} | User: {assessment.user_id} | Date: {assessment.created_at}")
    else:
        print("   ❌ No assessments yet")
    print()

    # Check results
    print("3️⃣ ASSESSMENT RESULTS TABLE")
    print("-" * 70)
    results = db.query(AssessmentResult).all()
    if results:
        print(f"   Found {len(results)} result(s):")
        for result in results:
            print(f"   • Assessment: {result.assessment_id}")
            print(f"     - Accuracy: {result.accuracy_percent:.1f}%")
            print(f"     - WPM: {result.wpm:.1f}")
            print(f"     - Risk Level: {result.risk_level}")
    else:
        print("   ❌ No results yet")
    print()

    # Show raw table info
    print("4️⃣ DATABASE STATISTICS")
    print("-" * 70)
    with engine.connect() as conn:
        # Count records in all tables
        tables = ['users', 'assessments', 'assessment_results', 'pronunciation_attempts', 
                  'pronunciation_checks', 'progress_history', 'speed_trainer_sessions', 
                  'chunk_reading_sessions']
        
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            status = "✓" if count > 0 else "○"
            print(f"   {status} {table}: {count} records")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print()
print("=" * 70)
print("💡 TIP: Run an assessment to populate the database!")
print("=" * 70)
