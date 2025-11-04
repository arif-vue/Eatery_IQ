#!/usr/bin/env python
"""
Test script for Onboarding API endpoints
This script demonstrates how to use the onboarding API endpoints.
"""

import requests
import json
import os

# Base URL for your Django application
BASE_URL = "http://127.0.0.1:8000"

# Test data
test_user = {
    "email": "testuser@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "role": "operator",
    "full_name": "Test User",
    "business_name": "Test Restaurant"
}

# Sample onboarding data for testing
sample_onboarding_data = {
    "current_step": 1,
    # Onboarding 1: Account Setup
    "owner_name": "John Doe",
    "brand_name_dba": "Doe's Delicious Diner",
    "email": "john.doe@restaurant.com",
    
    # Onboarding 2: Business Location
    "business_name": "Doe's Restaurant LLC",
    "address": "123 Main Street, Anytown, USA 12345",
    "time_zone": "America/New_York",
    "service_model": "Fast Casual",
    
    # Onboarding 3: Franchise & Brand
    "is_franchise": "NO",
    
    # Onboarding 5: Sales & Baseline
    "estimated_instore_sales_last_month": 25000,
    "estimated_online_3p_sales_last_month": 8000,
    "estimated_instore_sales_last_12_months": 300000,
    "estimated_online_3p_sales_last_12_months": 96000,
    
    # Onboarding 6: Labor & Staff
    "foh_employees": "5 full-time, 3 part-time",
    "boh_employees": "3 full-time, 2 part-time", 
    "pay_cadence": "Bi-weekly",
    
    # Onboarding 8: Marketing & Policies
    "monthly_marketing_budget": 2000,
    "key_policies": "No refunds after 30 minutes, 15% gratuity for groups of 8+",
}

class OnboardingAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def register_user(self):
        """Register a test user"""
        print("\n🔵 Registering test user...")
        url = f"{BASE_URL}/api/auth/register/"
        
        response = self.session.post(url, json=test_user)
        if response.status_code == 201:
            print("✅ User registered successfully!")
            return response.json()
        else:
            print(f"❌ Registration failed: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return None
    
    def login_user(self):
        """Login with test user"""
        print("\n🔵 Logging in...")
        url = f"{BASE_URL}/api/auth/login/"
        
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        response = self.session.post(url, json=login_data)
        if response.status_code == 200:
            result = response.json()
            self.token = result["data"]["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ Login successful!")
            return result
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.json())
            return None
    
    def create_onboarding_progress(self):
        """Test POST /api/auth/onboarding/"""
        print("\n🔵 Creating onboarding progress...")
        url = f"{BASE_URL}/api/auth/onboarding/"
        
        response = self.session.post(url, json=sample_onboarding_data)
        if response.status_code == 201:
            print("✅ Onboarding progress created successfully!")
            return response.json()
        else:
            print(f"❌ Creation failed: {response.status_code}")
            print(response.json())
            return None
    
    def get_onboarding_progress(self):
        """Test GET /api/auth/onboarding/"""
        print("\n🔵 Retrieving onboarding progress...")
        url = f"{BASE_URL}/api/auth/onboarding/"
        
        response = self.session.get(url)
        if response.status_code == 200:
            print("✅ Onboarding progress retrieved successfully!")
            return response.json()
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            print(response.json())
            return None
    
    def update_onboarding_progress(self):
        """Test PUT /api/auth/onboarding/update/"""
        print("\n🔵 Updating onboarding progress...")
        url = f"{BASE_URL}/api/auth/onboarding/update/"
        
        # Update data to move to step 3 with franchise info
        update_data = {
            "current_step": 3,
            "is_franchise": "YES",
            "franchise_brand_name": "Big Chain Restaurant",
            "locations_owned_operated": "3 locations",
            "region_market": "Northeast Region",
            "menu_url": "https://example.com/menu.pdf"
        }
        
        response = self.session.put(url, json=update_data)
        if response.status_code == 200: 
            print("✅ Onboarding progress updated successfully!")
            return response.json()
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(response.json())
            return None
    
    def complete_onboarding(self):
        """Test completing onboarding (step 9)"""
        print("\n🔵 Completing onboarding...")
        url = f"{BASE_URL}/api/auth/onboarding/update/"
        
        # Final update to complete onboarding
        completion_data = {
            "current_step": 9,
            "is_completed": True
        }
        
        response = self.session.put(url, json=completion_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Onboarding completed successfully!")
            if "Congratulations" in result.get("message", ""):
                print("🎉 Completion message received!")
            return result
        else:
            print(f"❌ Completion failed: {response.status_code}")
            print(response.json())
            return None
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Starting Onboarding API Tests...")
        print("=" * 50)
        
        # Step 1: Register user
        if not self.register_user():
            return False
        
        # Step 2: Login
        if not self.login_user():
            return False
        
        # Step 3: Create onboarding progress
        if not self.create_onboarding_progress():
            return False
        
        # Step 4: Get onboarding progress
        progress = self.get_onboarding_progress()
        if progress:
            print(f"📊 Current Step: {progress['data']['current_step']}")
            print(f"📊 Completed: {progress['data']['is_completed']}")
        
        # Step 5: Update onboarding progress
        if not self.update_onboarding_progress():
            return False
        
        # Step 6: Complete onboarding
        if not self.complete_onboarding():
            return False
        
        # Step 7: Final check
        final_progress = self.get_onboarding_progress()
        if final_progress:
            print(f"\n📊 Final Status:")
            print(f"   Step: {final_progress['data']['current_step']}")
            print(f"   Completed: {final_progress['data']['is_completed']}")
        
        print("\n🎉 All tests completed successfully!")
        return True 

def main():
    """Main function to run the tests"""
    print("Onboarding API Test Suite")
    print("=" * 40)
    print("Make sure your Django server is running on http://127.0.0.1:8000")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Tests cancelled by user")
        return
    
    tester = OnboardingAPITester()
    success = tester.run_tests()
    
    if success:
        print("\n✅ All tests passed! Your onboarding API is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()