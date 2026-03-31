#!/usr/bin/env python3
"""Test authentication setup"""
import sys
import os

print("[TEST] Starting authentication diagnostics...\n")

# Test 1: Import auth utilities
print("[1] Testing auth utilities import...")
try:
    from auth_utils import hash_password, verify_password, validate_email, validate_password
    print("    ✓ Auth utilities imported successfully")
except Exception as e:
    print(f"    ✗ Failed to import auth utilities: {e}")
    sys.exit(1)

# Test 2: Import schemas
print("[2] Testing schemas import...")
try:
    from schemas import UserSignUp, UserLogin, UserCreate, LoginResponse, UserResponse
    print("    ✓ Schemas imported successfully")
except Exception as e:
    print(f"    ✗ Failed to import schemas: {e}")
    sys.exit(1)

# Test 3: Import database
print("[3] Testing database import...")
try:
    from database import init_db, get_db, SessionLocal, engine
    print("    ✓ Database module imported successfully")
except Exception as e:
    print(f"    ✗ Failed to import database: {e}")
    sys.exit(1)

# Test 4: Import models  
print("[4] Testing models import...")
try:
    from models import User
    print("    ✓ Models imported successfully")
except Exception as e:
    print(f"    ✗ Failed to import models: {e}")
    sys.exit(1)

# Test 5: Import CRUD
print("[5] Testing CRUD import...")
try:
    from crud import UserCRUD
    print("    ✓ CRUD imported successfully")
except Exception as e:
    print(f"    ✗ Failed to import CRUD: {e}")
    sys.exit(1)

# Test 6: Test password hashing
print("[6] Testing password hashing...")
try:
    pwd = 'Demo123'
    hashed = hash_password(pwd)
    verified = verify_password(pwd, hashed)
    if verified:
        print(f"    ✓ Password hashing and verification works")
    else:
        print(f"    ✗ Password verification failed")
        sys.exit(1)
except Exception as e:
    print(f"    ✗ Error in password hashing: {e}")
    sys.exit(1)

# Test 7: Test database connection
print("[7] Testing database connection...")
try:
    # Try to connect without initializing tables
    connection = engine.connect()
    connection.close()
    print(f"    ✓ Database connection established")
except Exception as e:
    print(f"    ✗ Database connection failed: {e}")
    print(f"       Make sure PostgreSQL is running at localhost:5432")
    print(f"       DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    sys.exit(1)

# Test 8: Test database initialization
print("[8] Testing database initialization...")
try:
    init_db()
    print(f"    ✓ Database tables initialized")
except Exception as e:
    print(f"    ✗ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Test UserCRUD with database
print("[9] Testing UserCRUD operations...")
try:
    db = SessionLocal()
    user_crud = UserCRUD(db)
    
    # Test creating a user
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="Test123"
    )
    
    # First check if user already exists
    existing = user_crud.get_by_email("test@example.com")
    if existing:
        user_crud.delete_user(existing.id)
        print("    (Deleted existing test user)")
    
    user = user_crud.create_user_with_password(user_create)
    print(f"    ✓ User created: {user.username} (ID: {user.id})")
    
    # Test retrieving user
    retrieved = user_crud.get_by_email("test@example.com")
    if retrieved and retrieved.id == user.id:
        print(f"    ✓ User retrieved successfully")
    else:
        print(f"    ✗ User retrieval failed")
        sys.exit(1)
    
    # Clean up
    user_crud.delete_user(user.id)
    print(f"    ✓ Test user cleaned up")
    
    db.close()
except Exception as e:
    print(f"    ✗ UserCRUD test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓✓✓ All diagnostics passed! ✓✓✓")
print("\nThe backend authentication system is properly configured.")
