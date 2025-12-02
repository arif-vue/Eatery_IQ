# Quick Test Guide - New Features

## Prerequisites
- Server is running
- User is registered and logged in
- Access token available

---

## 🧪 Testing Document Management

### 1. Upload a Document
```bash
curl -X POST http://10.10.12.35:8000/api/auth/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file_name=Test Report" \
  -F "document_type=finance" \
  -F "file_format=pdf" \
  -F "file=@/path/to/your/file.pdf"
```

### 2. List All Documents
```bash
curl -X GET http://10.10.12.35:8000/api/auth/documents/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Search Documents
```bash
curl -X GET "http://10.10.12.35:8000/api/auth/documents/?search=report" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Update Document
```bash
curl -X PUT http://10.10.12.35:8000/api/auth/documents/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"file_name": "Updated Test Report"}'
```

### 5. Delete Document
```bash
curl -X DELETE http://10.10.12.35:8000/api/auth/documents/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing Subscription

### 1. Create Subscription (Starter - Free Trial)
```bash
curl -X POST http://10.10.12.35:8000/api/auth/subscription/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "starter",
    "auto_renew": false
  }'
```

### 2. Create Subscription (Professional)
```bash
curl -X POST http://10.10.12.35:8000/api/auth/subscription/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "professional",
    "auto_renew": true
  }'
```

### 3. Create Subscription (Enterprise)
```bash
curl -X POST http://10.10.12.35:8000/api/auth/subscription/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan": "enterprise",
    "auto_renew": true
  }'
```

### 4. Get Current Subscription
```bash
curl -X GET http://10.10.12.35:8000/api/auth/subscription/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Cancel Subscription
```bash
curl -X DELETE http://10.10.12.35:8000/api/auth/subscription/cancel/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing Calendar

### 1. Create Event
```bash
curl -X POST http://10.10.12.35:8000/api/auth/calendar/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "description": "Weekly sync meeting",
    "event_type": "meeting",
    "start_date": "2025-12-05T10:00:00Z",
    "end_date": "2025-12-05T11:00:00Z",
    "location": "Conference Room A",
    "is_all_day": false,
    "reminder_minutes": 15
  }'
```

### 2. List All Events
```bash
curl -X GET http://10.10.12.35:8000/api/auth/calendar/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Filter Events by Date Range
```bash
curl -X GET "http://10.10.12.35:8000/api/auth/calendar/events/?start_date=2025-12-01T00:00:00Z&end_date=2025-12-31T23:59:59Z" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Filter Events by Type
```bash
curl -X GET "http://10.10.12.35:8000/api/auth/calendar/events/?event_type=meeting" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Update Event
```bash
curl -X PUT http://10.10.12.35:8000/api/auth/calendar/events/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Team Meeting",
    "location": "Conference Room B"
  }'
```

### 6. Delete Event
```bash
curl -X DELETE http://10.10.12.35:8000/api/auth/calendar/events/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📱 Testing with Postman

### Setup:
1. Import the following as a collection
2. Set `{{base_url}}` = `http://10.10.12.35:8000`
3. Set `{{token}}` = Your access token

### Document Management Collection:
- Upload Document: `POST {{base_url}}/api/auth/documents/`
- List Documents: `GET {{base_url}}/api/auth/documents/`
- Get Document: `GET {{base_url}}/api/auth/documents/1/`
- Update Document: `PUT {{base_url}}/api/auth/documents/1/`
- Delete Document: `DELETE {{base_url}}/api/auth/documents/1/`

### Subscription Collection:
- Create Subscription: `POST {{base_url}}/api/auth/subscription/`
- Get Subscription: `GET {{base_url}}/api/auth/subscription/`
- Cancel Subscription: `DELETE {{base_url}}/api/auth/subscription/cancel/`

### Calendar Collection:
- Create Event: `POST {{base_url}}/api/auth/calendar/events/`
- List Events: `GET {{base_url}}/api/auth/calendar/events/`
- Get Event: `GET {{base_url}}/api/auth/calendar/events/1/`
- Update Event: `PUT {{base_url}}/api/auth/calendar/events/1/`
- Delete Event: `DELETE {{base_url}}/api/auth/calendar/events/1/`

---

## 🔍 Verify in Admin Panel

1. Navigate to: `http://10.10.12.35:8000/admin/`
2. Login with admin credentials
3. Check the following sections:
   - **AUTHENTICATIONS**
     - User Documents
     - Subscriptions
     - Calendar Events

---

## ✅ Expected Results

### Document Management:
- ✅ Files uploaded successfully
- ✅ File metadata stored correctly
- ✅ Search returns matching documents
- ✅ Update changes metadata
- ✅ Delete removes file and database entry

### Subscription:
- ✅ Subscription created with correct plan
- ✅ Price auto-calculated based on plan
- ✅ End date auto-calculated
- ✅ Days remaining calculated correctly
- ✅ Cancel updates status

### Calendar:
- ✅ Events created successfully
- ✅ Duration calculated automatically
- ✅ Filters work correctly
- ✅ Update changes event details
- ✅ Delete removes event

---

## 🐛 Troubleshooting

### Issue: "Authentication credentials were not provided"
**Solution:** Add Authorization header with Bearer token

### Issue: "Invalid file format"
**Solution:** Check file extension matches selected file_format

### Issue: "End date must be after start date"
**Solution:** Ensure end_date > start_date for calendar events

### Issue: "File size cannot exceed 50MB"
**Solution:** Use smaller file for documents

---

## 📊 Testing Checklist

### Document Management:
- [ ] Upload document
- [ ] List all documents
- [ ] Search documents
- [ ] Update document metadata
- [ ] Delete document
- [ ] Verify file cleanup after deletion

### Subscription:
- [ ] Create Starter subscription
- [ ] Create Professional subscription
- [ ] Create Enterprise subscription
- [ ] View subscription details
- [ ] Cancel subscription
- [ ] Verify auto-pricing

### Calendar:
- [ ] Create event
- [ ] List all events
- [ ] Filter by date range
- [ ] Filter by event type
- [ ] Update event
- [ ] Delete event
- [ ] Verify duration calculation

---

## 🎯 All Systems Ready!

All three features have been implemented and are ready for testing. The server should be running, and all APIs are accessible at the documented endpoints.
