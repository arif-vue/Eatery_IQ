# Eatery IQ API Documentation

## New Features Added

### 1. Document Management API
### 2. Subscription API
### 3. Calendar Events API

---

## 📄 DOCUMENT MANAGEMENT APIs

### Upload Document
**POST** `/api/auth/documents/`

Upload a new document with metadata.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Body (Form Data):**
```json
{
  "file_name": "Sales Report Q1",
  "document_type": "finance",
  "file_format": "excel",
  "file": <file_upload>
}
```

**Document Types:**
- `all` - All
- `operations` - Operations
- `compliance` - Compliance
- `finance` - Finance
- `legal` - Legal
- `hr_staff` - HR/Staff

**File Formats:**
- `excel` - Excel files (.xls, .xlsx, .csv)
- `pdf` - PDF files (.pdf)
- `docs` - Document files (.doc, .docx, .txt)

**Response (201 Created):**
```json
{
  "error": false,
  "message": "Document uploaded successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "file_name": "Sales Report Q1",
    "document_type": "finance",
    "file_format": "excel",
    "file_url": "http://example.com/media/user_documents/2025/11/file.xlsx",
    "file_size": 1048576,
    "file_size_mb": 1.0,
    "upload_date": "2025-11-29T10:00:00Z",
    "updated_at": "2025-11-29T10:00:00Z"
  }
}
```

---

### List All Documents
**GET** `/api/auth/documents/`

Get all documents uploaded by the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `search` (optional) - Search by file name

**Example:**
```
GET /api/auth/documents/?search=report
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Documents retrieved successfully",
  "count": 2,
  "data": [
    {
      "id": 1,
      "user_email": "user@example.com",
      "file_name": "Sales Report Q1",
      "document_type": "finance",
      "file_format": "excel",
      "file_url": "http://example.com/media/user_documents/2025/11/file.xlsx",
      "file_size": 1048576,
      "file_size_mb": 1.0,
      "upload_date": "2025-11-29T10:00:00Z",
      "updated_at": "2025-11-29T10:00:00Z"
    }
  ]
}
```

---

### Get Single Document
**GET** `/api/auth/documents/<document_id>/`

Retrieve a specific document by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Document retrieved successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "file_name": "Sales Report Q1",
    "document_type": "finance",
    "file_format": "excel",
    "file_url": "http://example.com/media/user_documents/2025/11/file.xlsx",
    "file_size": 1048576,
    "file_size_mb": 1.0,
    "upload_date": "2025-11-29T10:00:00Z",
    "updated_at": "2025-11-29T10:00:00Z"
  }
}
```

---

### Update Document Metadata
**PUT** `/api/auth/documents/<document_id>/`

Update document metadata (file name, type, format). Cannot update the file itself.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "file_name": "Updated Sales Report Q1",
  "document_type": "operations"
}
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Document updated successfully",
  "data": { /* updated document data */ }
}
```

---

### Delete Document
**DELETE** `/api/auth/documents/<document_id>/`

Delete a document.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Document 'Sales Report Q1' deleted successfully"
}
```

---

## 💳 SUBSCRIPTION APIs

### Get Current Subscription
**GET** `/api/auth/subscription/`

Retrieve the authenticated user's current subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Subscription retrieved successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "plan": "professional",
    "price": "29.00",
    "status": "active",
    "start_date": "2025-11-29T10:00:00Z",
    "end_date": "2025-12-29T10:00:00Z",
    "is_trial": false,
    "auto_renew": true,
    "is_currently_active": true,
    "days_remaining": 30
  }
}
```

---

### Create/Update Subscription
**POST** `/api/auth/subscription/`

Create a new subscription or update an existing one.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "plan": "professional",
  "auto_renew": true
}
```

**Subscription Plans:**
1. **Starter** - Free for 10 days (Trial)
   - `plan`: "starter"
   - `price`: 0.00
   - `duration`: 10 days

2. **Professional** - $29 for 1 month
   - `plan`: "professional"
   - `price`: 29.00
   - `duration`: 30 days

3. **Enterprise** - $69 for 6 months
   - `plan`: "enterprise"
   - `price`: 69.00
   - `duration`: 180 days

**Response (201 Created or 200 OK):**
```json
{
  "error": false,
  "message": "Subscription created successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "plan": "professional",
    "price": "29.00",
    "status": "active",
    "start_date": "2025-11-29T10:00:00Z",
    "end_date": "2025-12-29T10:00:00Z",
    "is_trial": false,
    "auto_renew": true,
    "is_currently_active": true,
    "days_remaining": 30
  }
}
```

---

### Cancel Subscription
**DELETE** `/api/auth/subscription/cancel/`

Cancel the authenticated user's subscription.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Subscription cancelled successfully"
}
```

---

## 📅 CALENDAR APIs

### List Calendar Events
**GET** `/api/auth/calendar/events/`

Get all calendar events for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters (optional):**
- `start_date` - Filter events from this date (ISO 8601 format)
- `end_date` - Filter events until this date (ISO 8601 format)
- `event_type` - Filter by event type

**Example:**
```
GET /api/auth/calendar/events/?start_date=2025-11-01T00:00:00Z&event_type=meeting
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Calendar events retrieved successfully",
  "count": 2,
  "data": [
    {
      "id": 1,
      "user_email": "user@example.com",
      "title": "Team Meeting",
      "description": "Weekly sync meeting",
      "event_type": "meeting",
      "start_date": "2025-12-01T10:00:00Z",
      "end_date": "2025-12-01T11:00:00Z",
      "location": "Conference Room A",
      "is_all_day": false,
      "reminder_minutes": 15,
      "duration_minutes": 60,
      "created_at": "2025-11-29T10:00:00Z",
      "updated_at": "2025-11-29T10:00:00Z"
    }
  ]
}
```

---

### Create Calendar Event
**POST** `/api/auth/calendar/events/`

Create a new calendar event.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Team Meeting",
  "description": "Weekly sync meeting",
  "event_type": "meeting",
  "start_date": "2025-12-01T10:00:00Z",
  "end_date": "2025-12-01T11:00:00Z",
  "location": "Conference Room A",
  "is_all_day": false,
  "reminder_minutes": 15
}
```

**Event Types:**
- `meeting` - Meeting
- `reminder` - Reminder
- `task` - Task
- `appointment` - Appointment
- `other` - Other

**Response (201 Created):**
```json
{
  "error": false,
  "message": "Calendar event created successfully",
  "data": {
    "id": 1,
    "user_email": "user@example.com",
    "title": "Team Meeting",
    "description": "Weekly sync meeting",
    "event_type": "meeting",
    "start_date": "2025-12-01T10:00:00Z",
    "end_date": "2025-12-01T11:00:00Z",
    "location": "Conference Room A",
    "is_all_day": false,
    "reminder_minutes": 15,
    "duration_minutes": 60,
    "created_at": "2025-11-29T10:00:00Z",
    "updated_at": "2025-11-29T10:00:00Z"
  }
}
```

---

### Get Single Calendar Event
**GET** `/api/auth/calendar/events/<event_id>/`

Retrieve a specific calendar event by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Calendar event retrieved successfully",
  "data": { /* event data */ }
}
```

---

### Update Calendar Event
**PUT** `/api/auth/calendar/events/<event_id>/`

Update an existing calendar event.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "title": "Updated Team Meeting",
  "location": "Conference Room B"
}
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Calendar event updated successfully",
  "data": { /* updated event data */ }
}
```

---

### Delete Calendar Event
**DELETE** `/api/auth/calendar/events/<event_id>/`

Delete a calendar event.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "error": false,
  "message": "Calendar event 'Team Meeting' deleted successfully"
}
```

---

## 🔐 Authentication

All endpoints require authentication using JWT tokens. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

To get an access token, use the login endpoint:

**POST** `/api/auth/login/`

---

## 📝 Notes

1. **File Size Limits:**
   - Documents: 50MB maximum
   - Profile pictures: 5MB maximum

2. **Date Format:**
   - All dates should be in ISO 8601 format
   - Example: `2025-12-01T10:00:00Z`

3. **Subscription Auto-pricing:**
   - Prices and durations are automatically set based on the plan
   - Starter: $0 for 10 days
   - Professional: $29 for 30 days
   - Enterprise: $69 for 180 days

4. **Document Search:**
   - Search is case-insensitive
   - Searches in file_name field only

5. **Calendar Filtering:**
   - All query parameters are optional
   - Combine multiple filters for precise results
