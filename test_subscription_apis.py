"""
Comprehensive Subscription API Testing with Real Token
"""

import requests
import json

# Configuration
BASE_URL = "http://10.10.12.35:8000"
API_URL = f"{BASE_URL}/api/auth"

# Your Access Token
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY0ODQzNDk3LCJpYXQiOjE3NjQ3NTcwOTcsImp0aSI6IjhmNzlmOTM1NGQ2MTQyMTA5MDBmMTFlODE2OTkwNTA0IiwidXNlcl9pZCI6IjEifQ.Kambv0MPLjYp05-HDXl3nqnRwvywIKV1i05QXvNyKwU"

def get_headers():
    """Get authorization headers"""
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

def print_section(title):
    """Print section header"""
    print("\n" + "="*100)
    print(f"🔥 {title}")
    print("="*100)

def print_response(response):
    """Print response details"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-"*100)

# ==================== TEST 1: STRIPE SETUP ====================
def test_stripe_setup():
    print_section("TEST 1: Setup Stripe Products & Prices")
    url = f"{API_URL}/subscription/stripe/setup/"
    
    try:
        response = requests.post(url, headers=get_headers())
        print_response(response)
        
        if response.status_code == 200:
            print("✅ PASS: Stripe products created successfully")
            data = response.json()
            print(f"\n📋 Price IDs Created:")
            for plan, details in data.get('price_ids', {}).items():
                print(f"  - {plan.upper()}: {details}")
            return True
        else:
            print("❌ FAIL: Stripe setup failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 2: STARTER PLAN (FREE) ====================
def test_starter_plan():
    print_section("TEST 2: Subscribe to Starter Plan (Free - 10 Days)")
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "starter"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        print_response(response)
        
        if response.status_code == 201:
            print("✅ PASS: Starter plan activated instantly (no payment required)")
            data = response.json()
            subscription_id = data.get('subscription_id')
            print(f"\n📌 Subscription ID: {subscription_id}")
            return subscription_id
        elif response.status_code == 400:
            print("⚠️  INFO: User might already have an active subscription")
            return None
        else:
            print("❌ FAIL: Starter plan activation failed")
            return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

# ==================== TEST 3: PROFESSIONAL PLAN ====================
def test_professional_checkout():
    print_section("TEST 3: Create Checkout Session for Professional Plan ($29/month)")
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "professional"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        print_response(response)
        
        if response.status_code == 200:
            print("✅ PASS: Professional checkout session created")
            data = response.json()
            checkout_url = data.get('checkout_url')
            print(f"\n🔗 Checkout URL: {checkout_url}")
            print(f"💳 Open this URL in browser to complete payment")
            return True
        elif response.status_code == 400:
            print("⚠️  INFO: User might already have an active subscription")
            return False
        else:
            print("❌ FAIL: Professional checkout failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 4: ENTERPRISE PLAN ====================
def test_enterprise_checkout():
    print_section("TEST 4: Create Checkout Session for Enterprise Plan ($69/6 months)")
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "enterprise"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        print_response(response)
        
        if response.status_code == 200:
            print("✅ PASS: Enterprise checkout session created")
            data = response.json()
            checkout_url = data.get('checkout_url')
            print(f"\n🔗 Checkout URL: {checkout_url}")
            print(f"💳 Open this URL in browser to complete payment")
            return True
        elif response.status_code == 400:
            print("⚠️  INFO: User might already have an active subscription")
            return False
        else:
            print("❌ FAIL: Enterprise checkout failed")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 5: LIST SUBSCRIPTIONS ====================
def test_list_subscriptions():
    print_section("TEST 5: List All User Subscriptions")
    url = f"{API_URL}/subscription/"
    
    try:
        response = requests.get(url, headers=get_headers())
        print_response(response)
        
        if response.status_code == 200:
            response_data = response.json()
            data = response_data.get('data', [])
            count = response_data.get('count', len(data))
            print(f"✅ PASS: Found {count} subscription(s)")
            
            for idx, sub in enumerate(data, 1):
                print(f"\n📦 Subscription {idx}:")
                print(f"  - ID: {sub.get('id')}")
                print(f"  - Plan: {sub.get('plan')}")
                print(f"  - Status: {sub.get('status')}")
                print(f"  - Price: ${sub.get('price')}")
                print(f"  - Start: {sub.get('start_date')}")
                print(f"  - End: {sub.get('end_date')}")
                print(f"  - Auto Renew: {sub.get('auto_renew')}")
            return data
        else:
            print("❌ FAIL: Failed to list subscriptions")
            return []
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return []

# ==================== TEST 6: GET SPECIFIC SUBSCRIPTION ====================
def test_get_subscription(subscription_id):
    print_section(f"TEST 6: Get Subscription Details (ID: {subscription_id})")
    url = f"{API_URL}/subscription/{subscription_id}/"
    
    try:
        response = requests.get(url, headers=get_headers())
        print_response(response)
        
        if response.status_code == 200:
            print("✅ PASS: Subscription details retrieved")
            return True
        else:
            print("❌ FAIL: Failed to get subscription details")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 7: INVALID PLAN ====================
def test_invalid_plan():
    print_section("TEST 7: Test Invalid Plan (Should Return 400 Error)")
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {"plan": "invalid_plan_name"}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        print_response(response)
        
        if response.status_code == 400:
            print("✅ PASS: Invalid plan correctly rejected")
            return True
        else:
            print("❌ FAIL: Should have returned 400 error")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 8: MISSING PLAN PARAMETER ====================
def test_missing_plan():
    print_section("TEST 8: Test Missing Plan Parameter (Should Return 400)")
    url = f"{API_URL}/subscription/stripe/checkout/"
    payload = {}
    
    try:
        response = requests.post(url, json=payload, headers=get_headers())
        print_response(response)
        
        if response.status_code == 400:
            print("✅ PASS: Missing plan parameter correctly handled")
            return True
        else:
            print("❌ FAIL: Should have returned 400 error")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 9: PAYMENT SUCCESS REDIRECT ====================
def test_payment_success_redirect():
    print_section("TEST 9: Test Payment Success Redirect")
    url = f"{API_URL}/subscription/payment/success/"
    
    try:
        response = requests.get(url, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Redirect Location: {response.headers.get('Location', 'N/A')}")
        print("-"*100)
        
        if response.status_code in [301, 302, 303, 307, 308]:
            print("✅ PASS: Payment success redirect works")
            return True
        else:
            print("⚠️  INFO: Redirect status code might be different than expected")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== TEST 10: PAYMENT CANCEL REDIRECT ====================
def test_payment_cancel_redirect():
    print_section("TEST 10: Test Payment Cancel Redirect")
    url = f"{API_URL}/subscription/payment/cancel/"
    
    try:
        response = requests.get(url, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        print(f"Redirect Location: {response.headers.get('Location', 'N/A')}")
        print("-"*100)
        
        if response.status_code in [301, 302, 303, 307, 308]:
            print("✅ PASS: Payment cancel redirect works")
            return True
        else:
            print("⚠️  INFO: Redirect status code might be different than expected")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

# ==================== MAIN TEST RUNNER ====================
def run_all_tests():
    print("\n" + "🚀"*50)
    print(" "*30 + "SUBSCRIPTION API COMPREHENSIVE TEST SUITE")
    print("🚀"*50)
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "warnings": 0
    }
    
    tests = [
        ("Stripe Setup", test_stripe_setup),
        ("Starter Plan", test_starter_plan),
        ("Professional Checkout", test_professional_checkout),
        ("Enterprise Checkout", test_enterprise_checkout),
        ("List Subscriptions", test_list_subscriptions),
        ("Invalid Plan", test_invalid_plan),
        ("Missing Plan Parameter", test_missing_plan),
        ("Payment Success Redirect", test_payment_success_redirect),
        ("Payment Cancel Redirect", test_payment_cancel_redirect),
    ]
    
    subscription_id = None
    subscriptions = []
    
    for test_name, test_func in tests:
        results["total"] += 1
        try:
            if test_name == "Starter Plan":
                result = test_func()
                if isinstance(result, str) or isinstance(result, int):
                    subscription_id = result
                    results["passed"] += 1
                elif result is None:
                    results["warnings"] += 1
                elif result:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            elif test_name == "List Subscriptions":
                result = test_func()
                if result:
                    subscriptions = result
                    results["passed"] += 1
                    if len(subscriptions) > 0 and not subscription_id:
                        subscription_id = subscriptions[0].get('id')
                else:
                    results["failed"] += 1
            else:
                if test_func():
                    results["passed"] += 1
                else:
                    results["failed"] += 1
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results["failed"] += 1
    
    # Additional test if we have a subscription ID
    if subscription_id:
        results["total"] += 1
        if test_get_subscription(subscription_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    
    # Print Summary
    print("\n" + "📊"*50)
    print(" "*35 + "TEST SUMMARY REPORT")
    print("📊"*50)
    print(f"\n{'Total Tests:':<30} {results['total']}")
    print(f"{'✅ Passed:':<30} {results['passed']}")
    print(f"{'❌ Failed:':<30} {results['failed']}")
    print(f"{'⚠️  Warnings:':<30} {results['warnings']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"{'Success Rate:':<30} {success_rate:.1f}%")
    
    print("\n" + "="*100)
    print("🎯 TESTING COMPLETED!")
    print("="*100 + "\n")
    
    # Print Important Notes
    print("📝 IMPORTANT NOTES:")
    print("1. Starter plan should activate instantly (no payment required)")
    print("2. Professional & Enterprise plans create Stripe checkout URLs")
    print("3. To test full payment flow, open the checkout URLs in a browser")
    print("4. Use Stripe test cards: 4242 4242 4242 4242 (success) or 4000 0000 0000 0002 (decline)")
    print("5. Webhook endpoint: http://10.10.12.35:8000/api/auth/subscription/webhook/")
    print("\n")

if __name__ == "__main__":
    run_all_tests()
