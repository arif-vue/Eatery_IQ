# Onboarding API Documentation

## Overview
The onboarding API allows users to create and update their restaurant onboarding progress through a 9-step process. This API provides two main endpoints for managing onboarding data.

## Authentication
All onboarding endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Base URL
```
/authentications/
```

## Endpoints

### 1. Create/Get Onboarding Progress

**GET /authentications/onboarding/**
- **Purpose**: Retrieve the current user's onboarding progress
- **Authentication**: Required
- **Parameters**: None

**Response (200 OK)**:
```json
{
    "error": false,
    "message": "Onboarding progress retrieved successfully",
    "data": {
        "id": 1,
        "user_email": "user@example.com",
        "current_step": 3,
        "is_completed": false,
        "owner_name": "John Doe",
        "brand_name_dba": "Doe's Diner",
        "email": "john@restaurant.com",
        "business_name": "Doe's Restaurant LLC",
        "address": "123 Main St, City, State 12345",
        "time_zone": "America/New_York",
        "service_model": "Fast Casual",
        "is_franchise": "NO",
        "franchise_brand_name": null,
        "locations_owned_operated": null,
        "region_market": null,
        "menu_url": "https://example.com/menu.pdf",
        "menu_file": null,
        "menu_file_url": null,
        "estimated_instore_sales_last_month": 25000,
        "estimated_online_3p_sales_last_month": 8000,
        "estimated_instore_sales_last_12_months": 300000,
        "estimated_online_3p_sales_last_12_months": 96000,
        "foh_employees": "5 full-time, 3 part-time",
        "boh_employees": "3 full-time, 2 part-time",
        "pay_cadence": "Bi-weekly",
        "document_file": null,
        "document_file_url": null,
        "monthly_marketing_budget": 2000,
        "key_policies": "No refunds after 30 minutes",
        "created_at": "2025-11-01T10:00:00Z",
        "updated_at": "2025-11-01T11:30:00Z"
    }
}
```

**Response (200 OK) - No Progress Found**:
```json
{
    "error": false,
    "message": "No onboarding progress found. You can start your onboarding process.",
    "data": null
}
```

**POST /authentications/onboarding/**
- **Purpose**: Create new onboarding progress for the authenticated user
- **Authentication**: Required
- **Content-Type**: multipart/form-data (for file uploads) or application/json

**Request Body**:
```json
{
    "current_step": 1,
    "owner_name": "John Doe",
    "brand_name_dba": "Doe's Delicious Diner", 
    "email": "john.doe@restaurant.com",
    "business_name": "Doe's Restaurant LLC",
    "address": "123 Main Street, Anytown, USA 12345",
    "time_zone": "America/New_York",
    "service_model": "Fast Casual",
    "is_franchise": "NO"
}
```

**Response (201 Created)**:
```json
{
    "error": false,
    "message": "Onboarding progress created successfully",
    "data": {
        "id": 1,
        "user_email": "user@example.com",
        "current_step": 1,
        "is_completed": false,
        // ... full onboarding data
    }
}
```

**Response (400 Bad Request) - Already Exists**:
```json
{
    "error": true,
    "message": "Onboarding progress already exists. Use PUT method to update.",
    "details": {
        "user": ["User already has onboarding progress"]
    }
}
```

### 2. Update Onboarding Progress

**PUT /authentications/onboarding/update/**
- **Purpose**: Update the current user's onboarding progress
- **Authentication**: Required
- **Content-Type**: multipart/form-data (for file uploads) or application/json

**Request Body** (partial updates allowed):
```json
{
    "current_step": 3,
    "is_franchise": "YES",
    "franchise_brand_name": "Big Chain Restaurant",
    "locations_owned_operated": "3 locations",
    "region_market": "Northeast Region",
    "menu_url": "https://example.com/menu.pdf"
}
```

**Response (200 OK)**:
```json
{
    "error": false,
    "message": "Onboarding progress updated successfully.",
    "data": {
        "id": 1,
        "user_email": "user@example.com",
        "current_step": 3,
        "is_completed": false,
        // ... updated onboarding data
    }
}
```

**Response (200 OK) - Completion**:
```json
{
    "error": false,
    "message": "Onboarding progress updated successfully. Congratulations! Your onboarding is now complete.",
    "data": {
        "id": 1,
        "user_email": "user@example.com", 
        "current_step": 9,
        "is_completed": true,
        // ... complete onboarding data
    }
}
```

**Response (404 Not Found)**:
```json
{
    "error": true,
    "message": "Onboarding progress not found. Please create onboarding progress first.",
    "details": {
        "user": ["No onboarding progress found for this user"]
    }
}
```

## Onboarding Steps

### Step 1: Account Setup
- **owner_name** (string): Name of the restaurant owner
- **brand_name_dba** (string): Brand name or "Doing Business As" name
- **email** (email): Contact email for the business

### Step 2: Business Location
- **business_name** (string): Legal business name
- **address** (text): Full business address
- **time_zone** (choice): Select from:
  - `America/Los_Angeles`
  - `America/Denver`
  - `America/Chicago` 
  - `America/New_York`
- **service_model** (choice): Select from:
  - `QSR`
  - `Fast Casual`
  - `Full Service`
  - `Cafe`
  - `Bar`
  - `Catering`
  - `Ghost Kitchen`

### Step 3: Franchise & Brand
- **is_franchise** (choice): `YES` or `NO`
- **franchise_brand_name** (string, required if franchise=YES): Franchise brand name
- **locations_owned_operated** (text, required if franchise=YES): Number/description of locations
- **region_market** (string, required if franchise=YES): Regional market area

### Step 4: Menu Upload
- **menu_url** (URL): Link to online menu
- **menu_file** (file): Upload menu file (PDF, JPEG, PNG, WebP - max 10MB)

### Step 5: Sales & Baseline
- **estimated_instore_sales_last_month** (integer): In-store sales last month
- **estimated_online_3p_sales_last_month** (integer): Online/3rd-party sales last month  
- **estimated_instore_sales_last_12_months** (integer): In-store sales last 12 months
- **estimated_online_3p_sales_last_12_months** (integer): Online/3rd-party sales last 12 months

### Step 6: Labor & Staff
- **foh_employees** (text): Front of house employee details
- **boh_employees** (text): Back of house employee details
- **pay_cadence** (text): Pay schedule information

### Step 7: Documents
- **document_file** (file): Upload business documents (PDF, DOC, DOCX, JPEG, PNG, WebP - max 15MB)

### Step 8: Marketing & Policies
- **monthly_marketing_budget** (integer): Monthly marketing budget amount
- **key_policies** (text): Important business policies

### Step 9: Completion
- **is_completed** (boolean): Automatically set to `true` when `current_step` reaches 9

## File Upload Fields

### Menu File (`menu_file`)
- **Allowed formats**: PDF, JPEG, PNG, WebP
- **Maximum size**: 10MB
- **Upload path**: `onboarding/menus/%Y/%m/`

### Document File (`document_file`)
- **Allowed formats**: PDF, DOC, DOCX, JPEG, PNG, WebP
- **Maximum size**: 15MB
- **Upload path**: `onboarding/documents/%Y/%m/`

## Error Responses

### Validation Errors (400 Bad Request)
```json
{
    "error": true,
    "message": "Invalid data provided",
    "details": {
        "franchise_brand_name": ["This field is required when franchise is YES"],
        "current_step": ["Current step must be between 1 and 9"],
        "menu_file": ["Menu file size cannot exceed 10MB"]
    }
}
```

### Authentication Errors (401 Unauthorized)
```json
{
    "error": true,
    "message": "Authentication credentials were not provided."
}
```

### Server Errors (500 Internal Server Error)
```json
{
    "error": true,
    "message": "Failed to create onboarding progress",
    "details": {
        "error": ["Database connection error"]
    }
}
```

## Example Usage

### 1. Creating Initial Onboarding Progress
```javascript
// POST /authentications/onboarding/
{
    "current_step": 1,
    "owner_name": "Jane Smith",
    "brand_name_dba": "Smith's Cafe",
    "email": "jane@smithscafe.com"
}
```

### 2. Updating Business Location (Step 2)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 2,
    "business_name": "Smith's Cafe LLC",
    "address": "456 Oak Street, Downtown, CA 90210",
    "time_zone": "America/Los_Angeles",
    "service_model": "Cafe"
}
```

### 3. Franchise Information (Step 3)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 3,
    "is_franchise": "YES",
    "franchise_brand_name": "Coffee Chain Co",
    "locations_owned_operated": "2 locations in California",
    "region_market": "West Coast"
}
```

### 4. Menu Upload with File (Step 4)
```javascript
// PUT /authentications/onboarding/update/
// Content-Type: multipart/form-data
FormData: {
    "current_step": 4,
    "menu_url": "https://smithscafe.com/menu",
    "menu_file": [File object]
}
```

### 5. Sales Data (Step 5)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 5,
    "estimated_instore_sales_last_month": 45000,
    "estimated_online_3p_sales_last_month": 12000,
    "estimated_instore_sales_last_12_months": 540000,
    "estimated_online_3p_sales_last_12_months": 144000
}
```

### 6. Staff Information (Step 6)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 6,
    "foh_employees": "8 full-time baristas, 4 part-time",
    "boh_employees": "2 full-time bakers, 1 part-time prep",
    "pay_cadence": "Weekly"
}
```

### 7. Document Upload (Step 7)
```javascript
// PUT /authentications/onboarding/update/
// Content-Type: multipart/form-data
FormData: {
    "current_step": 7,
    "document_file": [File object]
}
```

### 8. Marketing & Policies (Step 8)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 8,
    "monthly_marketing_budget": 3000,
    "key_policies": "No outside food, 20% gratuity for groups of 6+, Free WiFi for customers"
}
```

### 9. Completion (Step 9)
```javascript
// PUT /authentications/onboarding/update/
{
    "current_step": 9,
    "is_completed": true
}
```

## Notes

1. **Partial Updates**: The PUT endpoint supports partial updates - you only need to send the fields you want to update.

2. **File Management**: Uploaded files are automatically organized by year/month and old files are cleaned up when records are deleted.

3. **Step Validation**: The `current_step` field helps track progress and must be between 1 and 9.

4. **Franchise Logic**: When `is_franchise` is set to "YES", the franchise-related fields become required.

5. **Auto-Completion**: Setting `current_step` to 9 automatically marks `is_completed` as `true`.

6. **User Association**: Onboarding progress is automatically associated with the authenticated user.

7. **File URLs**: File upload fields provide both the file field and a corresponding URL field for easy access.