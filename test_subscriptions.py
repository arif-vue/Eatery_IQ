"""
Test Script for All Subscription APIs
Run this script to test all subscription endpoints and identify bugs
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://10.10.12.35:8000"
API_URL = f"{BASE_URL}/api/auth"

# Test User Credentials (create a test user first if needed)
TEST_USER = {
    "email": "testuser@example.com",
    "password": "Test@1234"
}

# Global token storage
ACCESS_TOKEN = None

def print_test(title):
    """Print test section header"""
    print("\n" + "="*80)
    print(f"TEST: {title}")
    print("="*80)

def print_result(status, message, data=None):
    """Print test result"""
    status_symbol = "✅" if status == "PASS" else "❌"
    print(f"{status_symbol} {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")

def register_user():
    """Test 1: Register a new user"""
    print_test("Register New User")
    
    url = f"{API_URL}/register/"
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "confirm_password": TEST_USER["password"],
        "full_name": "Test User",
        "business_name": "Test Business",
        "role": "operations"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            print_result("PASS", "User registered successfully", response.json())
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print_result("PASS", "User already exists, continuing with login")
            return True
        else:
            print_result("FAIL", f"Registration failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def verify_otp():
    """Test 2: Verify OTP (using database query for test email)"""
    print_test("Verify OTP")
    
    # For test emails (@example.com), OTP is printed to console
    # We'll use a fixed OTP for testing or query the database
    import sqlite3
    
    try:
        # Query the database to get the OTP
        conn = sqlite3.connect('/home/arif/Desktop/Eatery_IQ/db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("SELECT otp FROM authentications_otp WHERE email=?", (TEST_USER["email"],))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            print_result("FAIL", "No OTP found in database")
            return False
        
        otp_value = result[0]
        print(f"📧 Retrieved OTP from database: {otp_value}")
        
        url = f"{API_URL}/verify-otp/"
        payload = {
            "email": TEST_USER["email"],
            "otp": otp_value
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print_result("PASS", "OTP verified successfully", response.json())
            return True
        else:
            print_result("FAIL", f"OTP verification failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def login_user():
    """Test 3: Login and get access token"""
    global ACCESS_TOKEN
    print_test("User Login")
    
    url = f"{API_URL}/login/"
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            ACCESS_TOKEN = data.get("access")
            if ACCESS_TOKEN:
                print_result("PASS", "Login successful", {"access_token": ACCESS_TOKEN[:20] + "..."})
                return True
            else:
                print_result("FAIL", "No access token in response", data)
                return False
        else:
            print_result("FAIL", f"Login failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def get_headers():
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def test_stripe_setup():
    """Test 4: Setup Stripe Products"""
    print_test("Stripe Product Setup")
    
    url = f"{API_URL}/subscription/stripe/setup/"
    
    try:
        response = requests.post(url, headers=get_headers())
        if response.status_code == 200:
            print_result("PASS", "Stripe products created successfully", response.json())
            return True
        else:
            print_result("FAIL", f"Setup failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def test_starter_plan():
    """Test 5: Subscribe to Free Starter Plan"""
    print_test("Subscribe to Starter Plan (Free - 10 days)")
    
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "starter"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 201:
            data = response.json()
            print_result("PASS", "Starter plan activated instantly", data)
            return data.get("subscription_id")
        else:
            print_result("FAIL", f"Starter plan failed: {response.status_code}", response.json())
            return None
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return None

def test_professional_checkout():
    """Test 5: Create Checkout Session for Professional Plan"""
    print_test("Create Checkout for Professional Plan ($29/month)")
    
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "professional"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print_result("PASS", "Checkout session created", data)
            print(f"\n📋 Checkout URL: {data.get('checkout_url')}")
            return True
        else:
            print_result("FAIL", f"Checkout failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def test_enterprise_checkout():
    """Test 6: Create Checkout Session for Enterprise Plan"""
    print_test("Create Checkout for Enterprise Plan ($69/6 months)")
    
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "enterprise"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print_result("PASS", "Checkout session created", data)
            print(f"\n📋 Checkout URL: {data.get('checkout_url')}")
            return True
        else:
            print_result("FAIL", f"Checkout failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def test_list_subscriptions():
    """Test 7: List All User Subscriptions"""
    print_test("List All Subscriptions")
    
    url = f"{API_URL}/subscription/"
    
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print_result("PASS", f"Found {len(data)} subscription(s)", data)
            return data
        else:
            print_result("FAIL", f"List failed: {response.status_code}", response.json())
            return []
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return []

def test_get_subscription(subscription_id):
    """Test 8: Get Specific Subscription Details"""
    print_test(f"Get Subscription Details (ID: {subscription_id})")
    
    url = f"{API_URL}/subscription/{subscription_id}/"
    
    try:
        response = requests.get(url, headers=get_headers())
        if response.status_code == 200:
            data = response.json()
            print_result("PASS", "Subscription retrieved successfully", data)
            return True
        else:
            print_result("FAIL", f"Get failed: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def test_invalid_plan():
    """Test 9: Test Invalid Plan Name"""
    print_test("Test Invalid Plan (Should Fail)")
    
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "invalid_plan"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 400:
            print_result("PASS", "Invalid plan correctly rejected", response.json())
            return True
        else:
            print_result("FAIL", "Should have returned 400 error", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def test_duplicate_subscription():
    """Test 10: Test Duplicate Subscription Prevention"""
    print_test("Test Duplicate Active Subscription (Should Fail)")
    
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "starter"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        if response.status_code == 400 and "already have an active" in response.text:
            print_result("PASS", "Duplicate subscription correctly prevented", response.json())
            return True
        elif response.status_code == 201:
            print_result("FAIL", "Should have prevented duplicate subscription")
            return False
        else:
            print_result("FAIL", f"Unexpected response: {response.status_code}", response.json())
            return False
    except Exception as e:
        print_result("FAIL", f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🚀"*40)
    print("SUBSCRIPTION API COMPREHENSIVE TEST SUITE")
    print("🚀"*40)
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0
    }
    
    # Test 1: Register
    results["total"] += 1
    if register_user():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Registration failed, stopping tests")
        return
    
    # Test 2: Verify OTP
    results["total"] += 1
    if verify_otp():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  OTP verification failed, stopping tests")
        return
    
    # Test 3: Login
    results["total"] += 1
    if login_user():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Login failed, stopping tests")
        return
    
    # Test 3: Stripe Setup
    results["total"] += 1
    if test_stripe_setup():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Stripe setup failed, continuing with other tests")
    
    # Test 4: Starter Plan
    results["total"] += 1
    subscription_id = test_starter_plan()
    if subscription_id:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 5: Professional Checkout
    results["total"] += 1
    if test_professional_checkout():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 6: Enterprise Checkout
    results["total"] += 1
    if test_enterprise_checkout():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 7: List Subscriptions
    results["total"] += 1
    subscriptions = test_list_subscriptions()
    if subscriptions:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 8: Get Specific Subscription
    if subscription_id:
        results["total"] += 1
        if test_get_subscription(subscription_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Test 9: Invalid Plan
    results["total"] += 1
    if test_invalid_plan():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 10: Duplicate Subscription
    results["total"] += 1
    if test_duplicate_subscription():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Summary
    print("\n" + "📊"*40)
    print("TEST SUMMARY")
    print("📊"*40)
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
