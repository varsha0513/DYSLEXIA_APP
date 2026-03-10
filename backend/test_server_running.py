"""
Test if the Dyslexia API server is running
"""

import requests
import time
import json

print("⏳ Waiting for server to start...")
time.sleep(3)

try:
    print("🔍 Testing API endpoints...")
    print()
    
    # Test 1: Root endpoint
    print("1️⃣ Testing GET / ...")
    response = requests.get("http://127.0.0.1:8000/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📋 API Name: {data.get('name')}")
        print(f"   📌 Version: {data.get('version')}")
        print(f"   🟢 Status: {data.get('status')}")
    else:
        print(f"   ❌ Status: {response.status_code}")
    
    print()
    
    # Test 2: Health endpoint
    print("2️⃣ Testing GET /health ...")
    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   🟢 Status: {data.get('status')}")
        print(f"   🎤 Model: {data.get('model')}")
    else:
        print(f"   ❌ Status: {response.status_code}")
    
    print()
    print("=" * 70)
    print("✅ SERVER IS RUNNING SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("🌐 API is available at: http://127.0.0.1:8000")
    print("📚 Interactive docs: http://127.0.0.1:8000/docs")
    print("🔧 ReDoc docs: http://127.0.0.1:8000/redoc")
    print()
    print("🎯 Key endpoints:")
    print("   POST /assess - Assessment with audio")
    print("   POST /assess-text - Assessment with text")
    print("   POST /tts/word - Generate pronunciation")
    print("   POST /pronunciation/check - Check pronunciation")
    print()
    
except requests.exceptions.ConnectionError:
    print("   ❌ Could not connect to server")
    print("   Make sure the server is still running!")
except requests.exceptions.Timeout:
    print("   ❌ Server request timed out")
except Exception as e:
    print(f"   ❌ Error: {e}")
