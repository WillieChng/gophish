# MongoDB Implementation Guide

## Overview

This guide provides step-by-step instructions to implement MongoDB for managing phishing scenarios in Gophish.

## Architecture

**Scenarios** are now stored in MongoDB as simple templates:
- **No phishing sign configurations** in scenarios
- Users select a scenario when generating templates
- Risk configuration comes from groups/templates or custom selection at generation time

### Scenario Schema
```javascript
{
  "_id": ObjectId("..."),
  "name": "password_reset",              // Unique identifier
  "display_name": "Password Reset",      // UI display name
  "description": "Simulates password reset phishing attempt",
  "is_system": true,                     // Built-in vs user-created
  "organization_id": null,               // null = available to all
  "created_by_user_id": null,
  "created_at": ISODate("2024-10-25"),
  "updated_at": ISODate("2024-10-25")
}
```

---

## Step 1: Install MongoDB

### Windows:
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Run the installer (MSI)
3. Choose "Complete" installation
4. Install MongoDB as a Windows Service (check the box)
5. Install MongoDB Compass (optional GUI)

### Verify Installation:
```bash
# Check if MongoDB is running
mongo --version

# Or check the service
net start MongoDB
```

---

## Step 2: Install Go MongoDB Driver

```bash
cd c:\Users\User\Documents\Documents\Degree\Y3S2\FYP2\gophish

# Install MongoDB driver
go get go.mongodb.org/mongo-driver/mongo
go get go.mongodb.org/mongo-driver/bson
go get go.mongodb.org/mongo-driver/bson/primitive

# Update go.mod and go.sum
go mod tidy
```

---

## Step 3: Configuration Files Already Updated

The following files have been updated with MongoDB configuration:

### 1. `.env` (Phishing-Content-Generation-System)
```env
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017
MONGO_DB=gophish
```

### 2. `config.json` (Gophish root)
```json
{
  ...
  "mongo_uri": "mongodb://localhost:27017",
  "mongo_db": "gophish"
}
```

---

## Step 4: Files Created

The following new files have been created:

1. **models/mongodb.go** - MongoDB connection management
2. **models/scenario.go** - Scenario CRUD operations
3. **config/config.go** - Updated with MongoDB fields
4. **models/models.go** - Updated Setup() to initialize MongoDB and seed scenarios

---

## Step 5: Build and Run

```bash
cd c:\Users\User\Documents\Documents\Degree\Y3S2\FYP2\gophish

# Build Gophish
go build

# Run Gophish
.\gophish.exe
```

**Expected Output:**
```
[INFO] Successfully connected to MongoDB database: gophish
[INFO] Seeding system scenarios...
[INFO] Successfully seeded 8 system scenarios
[INFO] Please login with the username admin and the password XXXXXXXX
```

---

## Step 6: Verify MongoDB Data

### Using MongoDB Compass (GUI):
1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Select database: `gophish`
4. View collection: `scenarios`
5. Should see 8 system scenarios

### Using Mongo Shell:
```bash
mongo
> use gophish
> db.scenarios.find().pretty()
> db.scenarios.count()  # Should return 8
```

---

## Step 7: Next Steps - Create API Endpoints

Now create API endpoints for scenarios (I'll provide this code next):

### File to create: `controllers/api/scenario.go`

This will handle:
- `GET /api/scenarios` - List all scenarios
- `GET /api/scenarios/:id` - Get specific scenario
- `POST /api/scenarios` - Create new scenario
- `PUT /api/scenarios/:id` - Update scenario
- `DELETE /api/scenarios/:id` - Delete scenario

---

## System Scenarios Seeded

The following 8 scenarios are automatically seeded on first run:

1. **password_reset** - Password Reset
2. **urgent_action** - Urgent Action Required
3. **account_verification** - Account Verification
4. **security_alert** - Security Alert
5. **document_share** - Document Share
6. **invoice** - Invoice Payment
7. **it_support** - IT Support Request
8. **hr_announcement** - HR Announcement

---

## Workflow After Implementation

### For Users Creating Templates:

**OLD WAY (Hardcoded):**
```
1. Select scenario: "password_reset"
2. Scenario has predefined signs: ['urgency', 'suspicious_links']
3. Generate template (no customization)
```

**NEW WAY (MongoDB + User Config):**
```
1. Select scenario: "password_reset" (from MongoDB)
2. Select Group/Template (has risk profile)
   - OR manually configure all 6 phishing signs with difficulty levels
3. Generate template with full customization
```

### Example API Call:
```javascript
POST /api/ai/generate
{
  "scenario": "password_reset",        // Fetched from MongoDB
  "target_company": "Acme Corp",
  "phishing_signs": {                  // From group or custom
    "spelling_errors": "high",
    "urgency": "medium",
    "suspicious_sender": "low",
    "generic_greeting": "high",
    "suspicious_links": "medium",
    "attachments": "low"
  },
  "include_landing_page": true
}
```

---

## Troubleshooting

### Issue: "MongoDB not initialized"
**Solution:** Check if MongoDB service is running:
```bash
net start MongoDB
```

### Issue: "Failed to connect to MongoDB"
**Solution:** Verify connection string in `config.json`:
```json
"mongo_uri": "mongodb://localhost:27017"
```

### Issue: Go build errors about mongo driver
**Solution:** Run:
```bash
go mod download
go mod tidy
```

### Issue: Scenarios not appearing
**Solution:** Check MongoDB:
```bash
mongo
> use gophish
> db.scenarios.count()
> db.scenarios.find().pretty()
```

If count is 0, manually trigger seed:
```go
// In Go code or create a seed script
models.SeedSystemScenarios()
```

---

## Migration from Hardcoded Scenarios

The Python script `ai_module/generate_phishing.py` still has hardcoded scenarios at lines 853-887.

**Next step:** Update Python to fetch scenarios from MongoDB via API instead of using hardcoded dict.

---

## Connection String Format

### Local Development:
```
mongodb://localhost:27017
```

### With Authentication:
```
mongodb://username:password@localhost:27017
```

### MongoDB Atlas (Cloud):
```
mongodb+srv://username:password@cluster.mongodb.net/gophish?retryWrites=true&w=majority
```

**Update both:**
1. `config.json` - for Go backend
2. `.env` in Phishing-Content-Generation-System - for Python scripts

---

## Security Notes

1. **Never commit `.env` with real credentials**
2. **Use authentication in production**:
   ```json
   "mongo_uri": "mongodb://admin:password@localhost:27017/gophish?authSource=admin"
   ```
3. **Enable MongoDB authentication**:
   ```bash
   # In MongoDB shell
   use admin
   db.createUser({
     user: "gophish_admin",
     pwd: "strong_password",
     roles: [{role: "readWrite", db: "gophish"}]
   })
   ```

---

## What's Next?

1. ✅ MongoDB connection setup
2. ✅ Scenario model created
3. ✅ System scenarios seeded
4. ⏳ Create API endpoints (scenario.go)
5. ⏳ Update Python to use MongoDB
6. ⏳ Update frontend to fetch from API
7. ⏳ Add UI for creating custom scenarios

Continue with the implementation guide after verifying MongoDB is working!
