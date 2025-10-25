# Testing Scenarios API

## Prerequisites

1. Gophish is running
2. MongoDB is running
3. You have an API key (get from Gophish admin panel)

## API Endpoints Created

- `GET /api/scenarios/` - List all scenarios
- `GET /api/scenarios/{id}` - Get specific scenario
- `POST /api/scenarios/` - Create new scenario
- `PUT /api/scenarios/{id}` - Update scenario
- `DELETE /api/scenarios/{id}` - Delete scenario (system scenarios protected)

## Testing with cURL

### 1. Get Your API Key

1. Login to Gophish admin: https://localhost:3333
2. Go to Account Settings
3. Copy your API Key

### 2. List All Scenarios

```bash
curl -k -H "Authorization: Bearer YOUR_API_KEY" https://localhost:3333/api/scenarios/
```

**Expected Response:**
```json
[
  {
    "id": "6541234567890abcdef12345",
    "name": "password_reset",
    "display_name": "Password Reset",
    "description": "Simulates a password reset phishing attempt...",
    "is_system": true
  },
  {
    "id": "6541234567890abcdef12346",
    "name": "urgent_action",
    "display_name": "Urgent Action Required",
    "description": "High-pressure phishing email...",
    "is_system": true
  },
  ...
]
```

### 3. Get Specific Scenario

```bash
curl -k -H "Authorization: Bearer YOUR_API_KEY" \
  https://localhost:3333/api/scenarios/6541234567890abcdef12345
```

### 4. Create New Custom Scenario

```bash
curl -k -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tax_refund",
    "display_name": "Tax Refund Notification",
    "description": "Fake tax refund notification from IRS/government"
  }' \
  https://localhost:3333/api/scenarios/
```

**Expected Response:**
```json
{
  "id": "6541234567890abcdef99999",
  "name": "tax_refund",
  "display_name": "Tax Refund Notification",
  "description": "Fake tax refund notification from IRS/government",
  "is_system": false,
  "organization_id": null,
  "created_by_user_id": 1,
  "created_at": "2024-10-25T21:23:35Z",
  "updated_at": "2024-10-25T21:23:35Z"
}
```

### 5. Try to Delete System Scenario (Should Fail)

```bash
curl -k -X DELETE \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://localhost:3333/api/scenarios/6541234567890abcdef12345
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Cannot delete system scenarios"
}
```

### 6. Delete Custom Scenario (Should Succeed)

```bash
curl -k -X DELETE \
  -H "Authorization: Bearer YOUR_API_KEY" \
  https://localhost:3333/api/scenarios/6541234567890abcdef99999
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Scenario deleted successfully"
}
```

## Testing with Postman

1. Import collection URL: https://localhost:3333/api/
2. Set Authorization header: `Bearer YOUR_API_KEY`
3. Disable SSL verification (self-signed cert)
4. Test the endpoints above

## Verify MongoDB Data

```bash
# Connect to MongoDB
mongo

# Switch to gophish database
use gophish

# List all scenarios
db.scenarios.find().pretty()

# Count scenarios
db.scenarios.count()

# Find by name
db.scenarios.findOne({name: "password_reset"})

# Find all system scenarios
db.scenarios.find({is_system: true}).count()

# Find all custom scenarios
db.scenarios.find({is_system: false})
```

## Integration Test

Once API is working, you can test the full flow:

1. **List scenarios** (GET /api/scenarios/)
2. **Create custom scenario** (POST /api/scenarios/)
3. **Use in template generation** (next step - Python integration)

## Troubleshooting

### Issue: "Unauthorized"
- Check API key is correct
- Make sure Authorization header format is: `Bearer YOUR_API_KEY`

### Issue: "Scenario not found"
- Check MongoDB is running
- Verify scenarios were seeded: `db.scenarios.count()`
- Check the scenario ID is correct (MongoDB ObjectID format)

### Issue: Can't connect to HTTPS
- Use `-k` flag with curl to skip cert verification
- Self-signed certificates are normal for local development

## Next Steps

After API is working:
1. ✅ Update Python script to fetch scenarios from API
2. ✅ Update frontend dropdown to load from API
3. ✅ Test full workflow: Select scenario → Configure risk → Generate template
