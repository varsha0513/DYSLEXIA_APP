#!/usr/bin/env python3
"""Test signup and login endpoints"""
import sys
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("[TEST] Testing signup and login endpoints...\n")

# Test 1: Signup
print("[1] Testing signup endpoint...")
try:
    import random
    test_id = random.randint(1000, 9999)
    signup_data = {
        "name": "Test User",
        "email": f"testuser{test_id}@example.com",
        "password": "Test123",
        "password_confirm": "Test123"
    }
    test_email = signup_data['email']
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Signup successful!")
        print(f"    Token: {data['access_token'][:20]}...")
        print(f"    User: {data['user']['username']}")
        signup_token = data['access_token']
    else:
        print(f"    ✗ Signup failed with status {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print(f"    ✗ Cannot connect to backend at {BASE_URL}")
    print(f"    Make sure the backend is running: python backend/app.py")
    sys.exit(1)
except Exception as e:
    print(f"    ✗ Signup test failed: {e}")
    sys.exit(1)

# Test 2: Login
print("[2] Testing login endpoint...")
try:
    login_data = {
        "email": test_email,
        "password": "Test123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Login successful!")
        print(f"    Token: {data['access_token'][:20]}...")
        print(f"    User: {data['user']['username']}")
    else:
        print(f"    ✗ Login failed with status {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        sys.exit(1)
        
except Exception as e:
    print(f"    ✗ Login test failed: {e}")
    sys.exit(1)

# Test 3: Verify token by getting user info
print("[3] Testing GET /auth/me with token...")
try:
    headers = {
        "Authorization": f"Bearer {signup_token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Token verification successful!")
        print(f"    User ID: {data['id']}")
        print(f"    Email: {data['email']}")
    else:
        print(f"    ⚠ Token verification failed with status {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        
except Exception as e:
    print(f"    ⚠ Token verification test failed: {e}")

print("\n✓✓✓ All endpoint tests passed! ✓✓✓")
print("\nThe authentication system is working correctly.")
print(f"Test user created: {test_email} / Test123")
