#!/usr/bin/env python3
"""
Test the new GET onboarding endpoint
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

# Login as admin to get token
print("🔑 Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/api/auth/login/", json={
    "email": "admin@test.com",
    "password": "adminpass123"
})

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Test the new GET endpoint
    print("\n📊 Testing GET /api/auth/onboarding/get/...")
    get_response = requests.get(f"{BASE_URL}/api/auth/onboarding/get/", headers=headers)
    
    print(f"Status Code: {get_response.status_code}")
    
    if get_response.status_code == 200:
        result = get_response.json()
        print("✅ GET endpoint working!")
        print(f"Message: {result['message']}")
        
        data = result['data']
        print("\n📋 Current Onboarding Data:")
        print(f"   Owner: {data['owner_name']}")
        print(f"   Business: {data['business_name']}")
        print(f"   Current Step: {data['current_step']}")
        print(f"   Completed: {data['is_completed']}")
        print(f"   Service Model: {data['service_model']}")
        print(f"   Time Zone: {data['time_zone']}")
        print(f"   Franchise: {data['is_franchise']}")
        if data['is_franchise'] == 'YES':
            print(f"   Franchise Name: {data['franchise_brand_name']}")
        
    elif get_response.status_code == 404:
        result = get_response.json()
        print("ℹ️  No onboarding progress found (expected if no data exists)")
        print(f"Message: {result['message']}")
        
    else:
        print("❌ GET endpoint failed")
        print(f"Response: {get_response.text}")

else:
    print("❌ Login failed")
    print(f"Response: {login_response.text}")

print("\n🎯 All 3 onboarding endpoints now available:")
print("   POST /api/auth/onboarding/ - Create new progress")
print("   GET  /api/auth/onboarding/get/ - Retrieve current progress")
print("   PUT  /api/auth/onboarding/update/ - Update existing progress")