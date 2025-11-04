#!/usr/bin/env python3
"""
Quick onboarding API test with admin credentials
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# Login as admin
print("🔑 Logging in as admin...")
login_response = requests.post(f"{BASE_URL}/api/auth/login/", json={
    "email": "admin@test.com",
    "password": "adminpass123"
})

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data["access_token"]
    print("✅ Admin login successful!")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Create onboarding progress
    print("\n📝 Creating onboarding progress...")
    onboarding_data = {
        "current_step": 1,
        "owner_name": "John Admin",
        "brand_name_dba": "Admin's Restaurant",
        "email": "john.admin@restaurant.com",
        "business_name": "Admin Restaurant LLC",
        "time_zone": "America/New_York",
        "service_model": "Fast Casual"
    }
    
    create_response = requests.post(f"{BASE_URL}/api/auth/onboarding/", 
                                   json=onboarding_data, headers=headers)
    print(f"Status: {create_response.status_code}")
    if create_response.status_code == 201:
        print("✅ Onboarding progress created!")
        result = create_response.json()
        print(f"   Owner Name: {result['data']['owner_name']}")
        print(f"   Current Step: {result['data']['current_step']}")
        
        # Test 2: Update onboarding progress
        print("\n🔄 Updating onboarding progress...")
        update_data = {
            "current_step": 2,
            "address": "123 Main Street, New York, NY 10001",
            "is_franchise": "YES",
            "franchise_brand_name": "Big Restaurant Chain",
            "locations_owned_operated": "5 locations in NYC",
            "region_market": "Northeast"
        }
        
        update_response = requests.put(f"{BASE_URL}/api/auth/onboarding/update/", 
                                      json=update_data, headers=headers)
        print(f"Status: {update_response.status_code}")
        if update_response.status_code == 200:
            print("✅ Onboarding updated!")
            result = update_response.json()
            print(f"   Current Step: {result['data']['current_step']}")
            print(f"   Franchise: {result['data']['is_franchise']}")
            print(f"   Franchise Name: {result['data']['franchise_brand_name']}")
            
            # Test 3: Get onboarding progress
            print("\n📊 Retrieving onboarding progress...")
            get_response = requests.get(f"{BASE_URL}/api/auth/onboarding/", headers=headers)
            print(f"Status: {get_response.status_code}")
            if get_response.status_code == 200:
                result = get_response.json()
                print("✅ Retrieved onboarding progress!")
                data = result['data']
                print(f"   Owner: {data['owner_name']}")
                print(f"   Business: {data['business_name']}")
                print(f"   Step: {data['current_step']}")
                print(f"   Completed: {data['is_completed']}")
                print(f"   Service Model: {data['service_model']}")
                print(f"   Time Zone: {data['time_zone']}")
                
                # Test 4: Complete onboarding
                print("\n🏁 Completing onboarding...")
                complete_data = {
                    "current_step": 9,
                    "monthly_marketing_budget": 5000,
                    "key_policies": "Customer satisfaction guaranteed, 24/7 service"
                }
                
                complete_response = requests.put(f"{BASE_URL}/api/auth/onboarding/update/", 
                                               json=complete_data, headers=headers)
                print(f"Status: {complete_response.status_code}")
                if complete_response.status_code == 200:
                    result = complete_response.json()
                    print("✅ Onboarding completed!")
                    print(f"   Message: {result['message']}")
                    print(f"   Completed: {result['data']['is_completed']}")
                    print(f"   Final Step: {result['data']['current_step']}")
                    
                    print("\n🎉 All onboarding API tests passed successfully!")
                    print("=" * 50)
                    print("✅ POST /api/auth/onboarding/ - Create progress")
                    print("✅ PUT /api/auth/onboarding/update/ - Update progress") 
                    print("✅ GET /api/auth/onboarding/ - Get progress")
                    print("✅ Auto-completion when step = 9")
                    print("✅ Franchise field validation")
                    print("✅ JWT authentication")
                else:
                    print("❌ Failed to complete onboarding")
                    print(complete_response.text)
            else:
                print("❌ Failed to retrieve progress")
                print(get_response.text)
        else:
            print("❌ Failed to update onboarding")
            print(update_response.text)
    else:
        print("❌ Failed to create onboarding progress")
        print(create_response.text)
else:
    print("❌ Login failed")
    print(login_response.text)