# Pre-Commit Cleanup Guide

## 🚨 CRITICAL - Files with Sensitive Data

### ❌ NEVER COMMIT THESE FILES:
1. **Phishing-Content-Generation-System/.env**
   - Contains: Claude API key, Gophish API key
   - ✅ Already in .gitignore (safe)

2. **gophish.db**
   - Contains: User credentials, campaign data
   - ✅ Already in .gitignore (safe)

3. **gophish_admin.key / gophish_admin.crt**
   - Contains: SSL private keys
   - ✅ Already in .gitignore (safe)

## 🗑️ Files to DELETE Before Commit

### Temporary/Log Files (Delete these):
```bash
# Log files - not needed in repo
gophish.log
gophish_startup.log
nul

# Backup file
gophish.exe~
```

### Documentation Files (Review needed):
```bash
# Keep or delete based on preference:
AUTHENTICATION_FIX.md          # Implementation notes - KEEP
MONGODB_IMPLEMENTATION_COMPLETE.md  # Implementation notes - KEEP
MONGODB_IMPLEMENTATION_GUIDE.md     # Duplicate? - DELETE if same as above
RISK_PROFILE_COMPLETE.md       # Implementation notes - KEEP
RISK_PROFILE_IMPLEMENTATION.md # Duplicate? - DELETE if same as above
SCENARIO_FILTER_FIX.md         # Implementation notes - KEEP
SCENARIO_MANAGEMENT_FEATURE.md # Implementation notes - KEEP
TEST_SCENARIOS_API.md          # Testing notes - DELETE (temporary)
```

## ✅ SQL Migration Files - KEEP THESE

**YES, commit the SQL files!** They are essential for:

### db/db_sqlite3/migrations/20241024000000_add_risk_profiles.sql
- Adds risk profile columns to templates table
- Required for SQLite users

### db/db_mysql/migrations/20241024000000_add_risk_profiles.sql
- Adds risk profile columns to templates table
- Required for MySQL users

**Why commit migrations?**
- Other developers need to migrate their databases
- Production deployments need these migrations
- They don't contain sensitive data
- They're part of the schema evolution

## 📝 Files Safe to Commit

### New Go Files (SAFE - Core Features):
```
controllers/api/scenario.go    ✅ Scenario API endpoints
models/mongodb.go              ✅ MongoDB connection
models/scenario.go             ✅ Scenario CRUD operations
```

### Modified Go Files (SAFE - Review changes):
```
config/config.go               ✅ Added MongoDB config fields
controllers/api/ai_template.go ✅ AI template generation
controllers/api/server.go      ✅ Added scenario routes
models/group.go               ✅ Risk profile integration
models/models.go              ✅ MongoDB initialization
models/template.go            ✅ Risk profile fields
```

### Modified Frontend Files (SAFE):
```
static/js/src/app/groups.js    ✅ Risk profile UI
static/js/src/app/templates.js ✅ Scenario management UI
static/js/dist/app/*.min.js    ✅ Minified JS (auto-generated)
templates/groups.html          ✅ Risk profile form
templates/templates.html       ✅ Scenario management UI
static/css/*                   ✅ Styling updates
```

### Python Files (SAFE - Check for hardcoded secrets):
```
ai_module/generate_phishing.py ✅ AI generation logic (no secrets)
```

### Config Files (REVIEW):
```
config.json                    ⚠️  CHECK - Should only have localhost/example values
go.mod / go.sum               ✅ Dependency updates
```

## 🔒 Review config.json for Sensitive Data

Check these fields in config.json:
```json
{
  "admin_server": {
    "listen_url": "127.0.0.1:3333"  // ✅ localhost is safe
  },
  "phish_server": {
    "listen_url": "0.0.0.0:80"      // ✅ generic is safe
  },
  "mongo_uri": "mongodb://localhost:27017"  // ✅ localhost is safe
}
```

❌ Do NOT commit if config.json contains:
- Public IP addresses
- Real domain names
- Production database URLs
- Any passwords/tokens

## 🧹 Cleanup Commands

```bash
cd "c:\Users\User\Documents\Documents\Degree\Y3S2\FYP2\gophish"

# Delete temporary files
rm -f gophish.log gophish_startup.log nul "gophish.exe~"

# Delete duplicate documentation (optional)
rm -f MONGODB_IMPLEMENTATION_GUIDE.md RISK_PROFILE_IMPLEMENTATION.md TEST_SCENARIOS_API.md

# Verify .env is not tracked
cd Phishing-Content-Generation-System
git status | grep ".env" && echo "⚠️ WARNING: .env might be tracked!" || echo "✅ .env is safe"
cd ..

# Check what will be committed
git status
git diff config.json  # Review config changes
```

## 📋 Recommended Commit Structure

### Option 1: Single Large Commit
```bash
git add controllers/api/scenario.go
git add models/mongodb.go models/scenario.go
git add db/db_sqlite3/migrations/ db/db_mysql/migrations/
git add config.json config/config.go
git add controllers/api/server.go controllers/api/ai_template.go
git add models/group.go models/models.go models/template.go
git add static/js/src/app/templates.js static/js/dist/app/templates.min.js
git add templates/templates.html
git add ai_module/generate_phishing.py
git add go.mod go.sum
git add *.md  # Documentation files

git commit -m "Add MongoDB scenario management and risk profiles

Features:
- MongoDB integration for custom scenario storage
- Scenario management UI (add/view custom scenarios)
- Risk profile configuration for templates and groups
- AI template generation with risk levels
- API endpoints for scenario CRUD operations

Technical changes:
- New models: mongodb.go, scenario.go
- New API: scenario.go endpoints
- Database migrations: risk profile columns
- Frontend: scenario modal, risk profile UI
- Python: scenario API integration"
```

### Option 2: Separate Commits (Better for review)
```bash
# Commit 1: Database migrations
git add db/db_sqlite3/migrations/ db/db_mysql/migrations/
git commit -m "Add database migrations for risk profiles"

# Commit 2: MongoDB integration
git add models/mongodb.go config/config.go config.json
git commit -m "Add MongoDB integration for scenarios"

# Commit 3: Scenario models and API
git add models/scenario.go controllers/api/scenario.go controllers/api/server.go
git commit -m "Add scenario management API and models"

# Commit 4: Risk profile models
git add models/template.go models/group.go models/models.go
git commit -m "Add risk profile fields to templates and groups"

# Commit 5: Frontend UI
git add static/ templates/
git commit -m "Add scenario management and risk profile UI"

# Commit 6: Python integration
git add ai_module/generate_phishing.py
git commit -m "Integrate scenario API with Python generator"

# Commit 7: Documentation
git add *.md
git commit -m "Add implementation documentation"
```

## ⚠️ Final Safety Checks

Before pushing:
```bash
# 1. Check for accidentally staged .env files
git ls-files | grep -E "\.env$|api.*key|secret|password"

# 2. Review all staged changes
git diff --staged

# 3. Check file sizes (large files = possible binary/data)
git diff --staged --stat

# 4. Search staged files for sensitive patterns
git diff --staged | grep -iE "sk-ant-|api.*key.*=|password.*=|mongodb://.*:.*@"
```

If any of the above commands show sensitive data:
```bash
git reset HEAD <file>  # Unstage the file
# Edit the file to remove sensitive data
git add <file>         # Re-stage the clean version
```

## 🎯 Summary

**DELETE**: Log files, backups, temp files (gophish.log, nul, gophish.exe~)
**KEEP**: SQL migrations (essential for database schema)
**SAFE**: All .go files, .js files, .html files, .py files
**REVIEW**: config.json (ensure no production secrets)
**PROTECTED**: .env files (already in .gitignore)

✅ SQL migration files are **NECESSARY** - they update the database schema
✅ Documentation .md files are **OPTIONAL** - keep for future reference
✅ All code changes are safe to commit
