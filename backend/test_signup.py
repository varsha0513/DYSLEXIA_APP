"""
Test signup API endpoint
"""
import requests
import json

try:
    # Test signup
    signup_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "age": 25
    }
    
    print("[*] Testing POST /auth/signup...")
    response = requests.post(
        "http://localhost:8000/auth/signup",
        json=signup_data,
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("[OK] Signup successful!")
        data = response.json()
        print(f"User ID: {data.get('user_id')}")
        print(f"Token: {data.get('access_token')[:20]}...")
    else:
        print(f"[ERROR] Signup failed with status {response.status_code}")
        
except Exception as e:
    print(f"[ERROR] Request failed: {e}")
