# Onboarding API - cURL Commands for Testing

## Prerequisites
1. Start Django server: `python manage.py runserver`
2. Register a user and get authentication token
3. Replace `<YOUR_TOKEN>` with your actual JWT token

## 1. Register a User (if needed)
```bash
curl -X POST http://127.0.0.1:8000/authentications/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123",
    "confirm_password": "testpassword123",
    "role": "operator",
    "full_name": "Test User",
    "business_name": "Test Restaurant"
  }'
```

## 2. Login to Get Token
```bash
curl -X POST http://127.0.0.1:8000/authentications/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "testpassword123"
  }'
```

## 3. Create Onboarding Progress
```bash
curl -X POST http://127.0.0.1:8000/authentications/onboarding/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "current_step": 1,
    "owner_name": "John Doe",
    "brand_name_dba": "Doe'\''s Delicious Diner",
    "email": "john.doe@restaurant.com",
    "business_name": "Doe'\''s Restaurant LLC",
    "address": "123 Main Street, Anytown, USA 12345",
    "time_zone": "America/New_York",
    "service_model": "Fast Casual",
    "is_franchise": "NO",
    "estimated_instore_sales_last_month": 25000,
    "estimated_online_3p_sales_last_month": 8000,
    "estimated_instore_sales_last_12_months": 300000,
    "estimated_online_3p_sales_last_12_months": 96000,
    "foh_employees": "5 full-time, 3 part-time",
    "boh_employees": "3 full-time, 2 part-time",
    "pay_cadence": "Bi-weekly",
    "monthly_marketing_budget": 2000,
    "key_policies": "No refunds after 30 minutes, 15% gratuity for groups of 8+"
  }'
```

## 4. Get Onboarding Progress
```bash
curl -X GET http://127.0.0.1:8000/authentications/onboarding/ \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## 5. Update Onboarding Progress (Move to Step 3 with Franchise Info)
```bash
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "current_step": 3,
    "is_franchise": "YES",
    "franchise_brand_name": "Big Chain Restaurant",
    "locations_owned_operated": "3 locations",
    "region_market": "Northeast Region",
    "menu_url": "https://example.com/menu.pdf"
  }'
```

## 6. Upload Menu File (Step 4)
```bash
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -F "current_step=4" \
  -F "menu_url=https://restaurant.com/menu" \
  -F "menu_file=@/path/to/your/menu.pdf"
```

## 7. Upload Document File (Step 7)
```bash
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -F "current_step=7" \
  -F "document_file=@/path/to/your/document.pdf"
```

## 8. Complete Onboarding (Step 9)
```bash
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "current_step": 9,
    "is_completed": true
  }'
```

## 9. Final Check - Get Completed Progress
```bash
curl -X GET http://127.0.0.1:8000/authentications/onboarding/ \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```

## Error Testing Examples

### Try to Create Duplicate Onboarding Progress
```bash
curl -X POST http://127.0.0.1:8000/authentications/onboarding/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "current_step": 1,
    "owner_name": "Another User"
  }'
```

### Try to Update Without Existing Progress
```bash
# First, create a new user and login to get a different token
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <NEW_USER_TOKEN>" \
  -d '{
    "current_step": 2
  }'
```

### Invalid Franchise Data
```bash
curl -X PUT http://127.0.0.1:8000/authentications/onboarding/update/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_TOKEN>" \
  -d '{
    "is_franchise": "YES"
    // Missing required franchise fields
  }'
```

## Notes
- Replace `<YOUR_TOKEN>` with the actual JWT token from login response
- For file uploads, replace `/path/to/your/file.pdf` with actual file paths
- All endpoints require valid authentication
- The server should be running on http://127.0.0.1:8000/