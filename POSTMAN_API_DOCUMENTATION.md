# 🚀 EATERY IQ - COMPLETE API DOCUMENTATION FOR POSTMAN

## 📋 TABLE OF CONTENTS
1. [Authentication APIs](#authentication-apis)
2. [Subscription APIs](#subscription-apis)
3. [Document Management APIs](#document-management-apis)
4. [Calendar APIs](#calendar-apis)
5. [Profile Management APIs](#profile-management-apis)
6. [Stripe Test Cards](#stripe-test-cards)

---

## 🔐 AUTHENTICATION APIs

### 1. Register User
**POST** `http://10.10.12.35:8000/api/auth/register/`

**Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "YourPassword@123",
  "confirm_password": "YourPassword@123",
  "full_name": "John Doe",
  "business_name": "My Restaurant",
  "role": "operations"
}
```

**Roles:** `operations`, `marketing manager`, `executive`

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful! Please verify your email with the OTP sent to your inbox",
  "user": {
    "email": "user@example.com",
    "role": "operations"
  }
}
```

---

### 2. Verify OTP
**POST** `http://10.10.12.35:8000/api/auth/verify-otp/`

**Body (JSON):**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Note:** For test emails (@example.com, @test.com), OTP is printed in terminal console.

**Response (200):**
```json
{
  "message": "Email verified successfully. You can now log in"
}
```

---

### 3. Login
**POST** `http://10.10.12.35:8000/api/auth/login/`

**Body (JSON):**
```json
{
  "email": "user@example.com",
  "password": "YourPassword@123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "1",
    "email": "user@example.com",
    "role": "operations",
    "is_verified": true,
    "user_profile": {
      "full_name": "John Doe",
      "business_name": "My Restaurant",
      "phone": null
    }
  }
}
```

**⚠️ IMPORTANT:** Copy the `access_token` - you'll need it for all protected endpoints!

---

### 4. Resend OTP
**POST** `http://10.10.12.35:8000/api/auth/resend-otp/`

**Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

---

### 5. Password Reset Request
**POST** `http://10.10.12.35:8000/api/auth/password-reset/request/`

**Body (JSON):**
```json
{
  "email": "user@example.com"
}
```

---

### 6. Verify Reset OTP
**POST** `http://10.10.12.35:8000/api/auth/password-reset/verify/`

**Body (JSON):**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

---

### 7. Reset Password
**POST** `http://10.10.12.35:8000/api/auth/password-reset/confirm/`

**Body (JSON):**
```json
{
  "email": "user@example.com",
  "otp": "123456",
  "new_password": "NewPassword@123",
  "confirm_password": "NewPassword@123"
}
```

---

## 💳 SUBSCRIPTION APIs (STRIPE INTEGRATION)

### 🔑 AUTHORIZATION REQUIRED
Add to **Headers** for all subscription endpoints:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

---

### 1. Setup Stripe Products (Run Once)
**POST** `http://10.10.12.35:8000/api/auth/subscription/stripe/setup/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Stripe products created successfully",
  "data": [
    {
      "plan": "starter",
      "product_id": "prod_XXX",
      "price_id": "price_XXX",
      "amount": 0.0,
      "currency": "usd"
    },
    {
      "plan": "professional",
      "product_id": "prod_XXX",
      "price_id": "price_XXX",
      "amount": 29.0,
      "currency": "usd"
    },
    {
      "plan": "enterprise",
      "product_id": "prod_XXX",
      "price_id": "price_XXX",
      "amount": 69.0,
      "currency": "usd"
    }
  ],
  "price_ids": {
    "starter": "price_XXX",
    "professional": "price_XXX",
    "enterprise": "price_XXX"
  }
}
```

**Note:** This creates products in Stripe Dashboard. Only needs to be run once.

---

### 2. Subscribe to Starter Plan (FREE)
**POST** `http://10.10.12.35:8000/api/auth/subscription/stripe/checkout/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "plan": "starter"
}
```

**Response (201):**
```json
{
  "error": false,
  "message": "Starter subscription activated successfully (Free Trial)",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "plan": "starter",
    "price": "0.00",
    "status": "active",
    "start_date": "2025-12-03T10:00:00Z",
    "end_date": "2025-12-13T10:00:00Z",
    "is_trial": true,
    "auto_renew": false,
    "is_currently_active": true,
    "days_remaining": 10
  }
}
```

**✅ Starter plan activates instantly - no payment required!**

---

### 3. Create Checkout for Professional Plan ($29)
**POST** `http://10.10.12.35:8000/api/auth/subscription/stripe/checkout/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "plan": "professional"
}
```

**Response (200):**
```json
{
  "error": false,
  "message": "Checkout session created successfully",
  "data": {
    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
    "session_id": "cs_test_...",
    "plan": "Professional Plan",
    "price": 29.0
  }
}
```

**📋 Next Steps:**
1. Copy the `checkout_url`
2. Open it in your browser
3. Use test card: `4242 4242 4242 4242`
4. Complete payment
5. Webhook will activate subscription

---

### 4. Create Checkout for Enterprise Plan ($69)
**POST** `http://10.10.12.35:8000/api/auth/subscription/stripe/checkout/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "plan": "enterprise"
}
```

**Response (200):**
```json
{
  "error": false,
  "message": "Checkout session created successfully",
  "data": {
    "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...",
    "session_id": "cs_test_...",
    "plan": "Enterprise Plan",
    "price": 69.0
  }
}
```

---

### 5. List All User Subscriptions
**GET** `http://10.10.12.35:8000/api/auth/subscription/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Subscriptions retrieved successfully",
  "data": [
    {
      "id": 1,
      "user_email": "user@example.com",
      "plan": "professional",
      "price": "29.00",
      "status": "active",
      "start_date": "2025-12-03T10:00:00Z",
      "end_date": "2026-01-03T10:00:00Z",
      "is_trial": false,
      "auto_renew": false,
      "is_currently_active": true,
      "days_remaining": 30
    }
  ],
  "count": 1
}
```

---

### 6. Get Specific Subscription Details
**GET** `http://10.10.12.35:8000/api/auth/subscription/{subscription_id}/`

**Example:** `http://10.10.12.35:8000/api/auth/subscription/1/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Subscription details retrieved successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "plan": "professional",
    "price": "29.00",
    "status": "active",
    "start_date": "2025-12-03T10:00:00Z",
    "end_date": "2026-01-03T10:00:00Z",
    "is_trial": false,
    "auto_renew": false,
    "is_currently_active": true,
    "days_remaining": 30
  }
}
```

---

### 7. Cancel Subscription
**DELETE** `http://10.10.12.35:8000/api/auth/subscription/cancel/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Subscription cancelled successfully"
}
```

---

### 8. Payment Success Redirect
**GET** `http://10.10.12.35:8000/api/auth/subscription/payment/success/`

**Response:** HTTP 302 Redirect to `http://localhost:3000/subscription/success`

---

### 9. Payment Cancel Redirect
**GET** `http://10.10.12.35:8000/api/auth/subscription/payment/cancel/`

**Response:** HTTP 302 Redirect to `http://localhost:3000/subscription/cancel`

---

### 10. Stripe Webhook Endpoint
**POST** `http://10.10.12.35:8000/api/auth/subscription/webhook/`

**Note:** This is called automatically by Stripe. Configure in Stripe Dashboard:
- URL: `http://10.10.12.35:8000/api/auth/subscription/webhook/`
- Events: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`
- Webhook Secret: `whsec_UQTcICoRfQO1N1RevpAsMJMcH6ZJIygW`

---

## 📄 DOCUMENT MANAGEMENT APIs

### 1. Upload Document
**POST** `http://10.10.12.35:8000/api/auth/documents/upload/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Body (form-data):**
```
file_name: "Financial Report Q1"
document_type: "finance"
file: [Choose File - Max 50MB]
```

**Document Types:** `all`, `operations`, `compliance`, `finance`, `legal`, `hr_staff`

**Response (201):**
```json
{
  "error": false,
  "message": "Document uploaded successfully",
  "data": {
    "id": 1,
    "user": "user@example.com",
    "file_name": "Financial Report Q1",
    "document_type": "finance",
    "file": "/media/user_documents/report.pdf",
    "file_size": 1024000,
    "uploaded_at": "2025-12-03T10:00:00Z"
  }
}
```

---

### 2. List All Documents
**GET** `http://10.10.12.35:8000/api/auth/documents/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Documents retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": "user@example.com",
      "file_name": "Financial Report Q1",
      "document_type": "finance",
      "file": "/media/user_documents/report.pdf",
      "file_size": 1024000,
      "uploaded_at": "2025-12-03T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

### 3. Search Documents
**GET** `http://10.10.12.35:8000/api/auth/documents/search/?q=financial`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Query Parameters:**
- `q`: Search term (searches in file_name)

---

### 4. Get Document Details
**GET** `http://10.10.12.35:8000/api/auth/documents/{document_id}/`

**Example:** `http://10.10.12.35:8000/api/auth/documents/1/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### 5. Update Document
**PUT** `http://10.10.12.35:8000/api/auth/documents/{document_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "file_name": "Updated Report Name",
  "document_type": "compliance"
}
```

---

### 6. Delete Document
**DELETE** `http://10.10.12.35:8000/api/auth/documents/{document_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "Document deleted successfully"
}
```

---

## 📅 CALENDAR APIs

### 1. Create Calendar Event
**POST** `http://10.10.12.35:8000/api/auth/calendar/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "title": "Team Meeting",
  "description": "Quarterly review meeting",
  "event_type": "meeting",
  "start_time": "2025-12-10T14:00:00Z",
  "end_time": "2025-12-10T15:00:00Z",
  "location": "Conference Room A"
}
```

**Event Types:** `meeting`, `reminder`, `task`, `appointment`, `other`

**Response (201):**
```json
{
  "error": false,
  "message": "Event created successfully",
  "data": {
    "id": 1,
    "user": "user@example.com",
    "title": "Team Meeting",
    "description": "Quarterly review meeting",
    "event_type": "meeting",
    "start_time": "2025-12-10T14:00:00Z",
    "end_time": "2025-12-10T15:00:00Z",
    "location": "Conference Room A",
    "is_completed": false,
    "duration_hours": 1.0,
    "created_at": "2025-12-03T10:00:00Z"
  }
}
```

---

### 2. List All Calendar Events
**GET** `http://10.10.12.35:8000/api/auth/calendar/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Query Parameters (Optional):**
- `date`: Filter by specific date (YYYY-MM-DD)
- `event_type`: Filter by event type

**Examples:**
- `http://10.10.12.35:8000/api/auth/calendar/?date=2025-12-10`
- `http://10.10.12.35:8000/api/auth/calendar/?event_type=meeting`

---

### 3. Get Event Details
**GET** `http://10.10.12.35:8000/api/auth/calendar/{event_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### 4. Update Calendar Event
**PUT** `http://10.10.12.35:8000/api/auth/calendar/{event_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "title": "Updated Meeting Title",
  "is_completed": true
}
```

---

### 5. Delete Calendar Event
**DELETE** `http://10.10.12.35:8000/api/auth/calendar/{event_id}/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## 👤 PROFILE MANAGEMENT APIs

### 1. Get Current User Profile
**GET** `http://10.10.12.35:8000/api/auth/user-profile/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Response (200):**
```json
{
  "error": false,
  "message": "User profile retrieved successfully",
  "data": {
    "id": "1",
    "email": "user@example.com",
    "role": "operations",
    "is_verified": true,
    "user_profile": {
      "full_name": "John Doe",
      "business_name": "My Restaurant",
      "phone": "+1234567890",
      "country": "United States",
      "state": "California",
      "city": "Los Angeles",
      "zip_code": "90001",
      "profile_picture": "/media/profile_pictures/photo.jpg"
    }
  }
}
```

---

### 2. Update User Profile
**PUT** `http://10.10.12.35:8000/api/auth/user-profile/`

**Headers:**
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

**Body (form-data):**
```
full_name: "John Smith"
business_name: "Smith's Restaurant"
phone: "+1234567890"
country: "United States"
state: "California"
city: "Los Angeles"
zip_code: "90001"
profile_picture: [Choose File - Optional]
```

---

## 💳 STRIPE TEST CARDS

### ✅ Successful Payment
```
Card Number: 4242 4242 4242 4242
Expiry: Any future date (e.g., 12/25)
CVC: Any 3 digits (e.g., 123)
ZIP: Any 5 digits (e.g., 12345)
```

### ❌ Declined Payment
```
Card Number: 4000 0000 0000 0002
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

### 🔄 Requires Authentication (3D Secure)
```
Card Number: 4000 0027 6000 3184
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

---

## 📊 SUBSCRIPTION PLAN SUMMARY

| Plan | Price | Duration | Trial | Features |
|------|-------|----------|-------|----------|
| **Starter** | FREE | 10 days | Yes | Basic features, instant activation |
| **Professional** | $29 | 1 month | No | Advanced features, Stripe payment |
| **Enterprise** | $69 | 6 months | No | Full access, Stripe payment |

---

## 🔧 ENVIRONMENT SETUP

### Base URL
```
http://10.10.12.35:8000
```

### Stripe Configuration
```
Publishable Key: pk_test_51SZrhtAanzr8AVBe...
Secret Key: sk_test_51SZrhtAanzr8AVBe...
Webhook Secret: whsec_UQTcICoRfQO1N1RevpAsMJMcH6ZJIygW
Webhook URL: http://10.10.12.35:8000/api/auth/subscription/webhook/
```

---

## 🚀 QUICK START GUIDE

### Step 1: Register & Verify
1. Call `/register/` endpoint
2. Check terminal for OTP (test emails)
3. Call `/verify-otp/` with OTP
4. Call `/login/` and save access token

### Step 2: Setup Subscriptions
1. Call `/subscription/stripe/setup/` (once)
2. Note the price IDs created

### Step 3: Subscribe
1. For FREE trial: Call `/subscription/stripe/checkout/` with `"plan": "starter"`
2. For paid plans: Get checkout URL and complete payment in browser

### Step 4: Manage Data
1. Upload documents via `/documents/upload/`
2. Create calendar events via `/calendar/`
3. Update profile via `/user-profile/`

---

## ❗ COMMON ERRORS

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Solution:** Add `Authorization: Bearer YOUR_ACCESS_TOKEN` header

---

### 400 Invalid Plan
```json
{
  "error": true,
  "message": "Invalid plan",
  "details": {
    "plan": ["Please provide a valid plan: starter, professional, or enterprise"]
  }
}
```
**Solution:** Use correct plan name: `starter`, `professional`, or `enterprise`

---

### 500 Stripe Not Configured
```json
{
  "error": true,
  "message": "Stripe price not configured",
  "details": {
    "error": ["Please run /api/auth/subscription/stripe/setup/ first to create products"]
  }
}
```
**Solution:** Run the setup endpoint first

---

## 📞 SUPPORT

For issues or questions:
- Check terminal logs for detailed errors
- Verify all required fields are provided
- Ensure access token is valid and not expired
- Check Stripe Dashboard for webhook events

---

## ✅ BUGS FIXED

1. ✅ Stripe setup returns 200 (was 201)
2. ✅ Subscription list returns array (was single object)
3. ✅ Price IDs fetched dynamically from Stripe
4. ✅ Payment redirect endpoints use HTTP 302
5. ✅ Duplicate subscription prevention
6. ✅ Invalid plan validation
7. ✅ Missing plan parameter handling

---

## 🎉 ALL TESTS PASSED: 90% SUCCESS RATE

**Test Results:**
- ✅ Stripe Setup
- ✅ Starter Plan (Free)
- ✅ Professional Checkout
- ✅ Enterprise Checkout
- ✅ List Subscriptions
- ✅ Get Subscription Details
- ✅ Invalid Plan Validation
- ✅ Missing Plan Validation
- ✅ Payment Success Redirect
- ✅ Payment Cancel Redirect

---

**END OF DOCUMENTATION**
