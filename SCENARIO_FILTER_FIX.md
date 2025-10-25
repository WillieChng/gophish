# Scenario Filter Fix - Custom Scenarios Now Appear!

## Issue
Newly added custom scenarios were not appearing in the "Generate AI Template" dropdown, even though they were successfully saved to MongoDB.

## Root Cause
The `GetScenarios()` function in [models/scenario.go](models/scenario.go#L72) was filtering to only return system scenarios:

**BEFORE (Incorrect):**
```go
// Get system scenarios and user's organization scenarios
// For now, we'll just get all system scenarios
filter := bson.M{"is_system": true}  // ❌ Only returns system scenarios
```

This MongoDB filter would only retrieve scenarios where `is_system: true`, completely excluding all user-created custom scenarios (`is_system: false`).

## Solution
Updated the filter to use MongoDB's `$or` operator to return **both** system scenarios **and** scenarios created by the logged-in user:

**AFTER (Correct):**
```go
// Get system scenarios and user's custom scenarios
// Filter: is_system=true OR created_by_user_id=uid
filter := bson.M{
    "$or": []bson.M{
        {"is_system": true},           // Include all system scenarios
        {"created_by_user_id": uid},   // Include user's custom scenarios
    },
}
```

## What This Fixes

### Before Fix
- ✅ System scenarios visible (8 scenarios)
- ❌ Custom scenarios invisible (even though saved successfully)
- User confusion: "Where did my scenario go?"

### After Fix
- ✅ System scenarios visible (8 scenarios)
- ✅ Custom scenarios visible (all scenarios created by the user)
- ✅ Users see their custom scenarios immediately in dropdowns

## Files Modified

### [models/scenario.go](models/scenario.go#L70-77)
```go
func GetScenarios(uid int64) ([]Scenario, error) {
    // ... initialization code ...

    // Get system scenarios and user's custom scenarios
    // Filter: is_system=true OR created_by_user_id=uid
    filter := bson.M{
        "$or": []bson.M{
            {"is_system": true},
            {"created_by_user_id": uid},
        },
    }

    cursor, err := collection.Find(ctx, filter)
    // ... rest of function ...
}
```

## Testing Results

### API Response (After Fix)
```bash
curl -k -H "Authorization: Bearer <token>" https://localhost:3333/api/scenarios/
```

**Returns 11 scenarios:**

✅ **System Scenarios (8):**
1. password_reset
2. urgent_action
3. account_verification
4. security_alert
5. document_share
6. invoice
7. it_support
8. hr_announcement

✅ **Custom Scenarios (3):**
9. lottery_winner
10. tax_refund ← User created this!
11. test_scenario

## User Experience

### Creating a Custom Scenario
1. Click **"Add Scenario"** on Templates page
2. Fill in:
   - Name: `loyalty_program`
   - Display Name: `Loyalty Program Scam`
   - Description: `Fake loyalty rewards notification`
3. Click **"Save Scenario"**
4. ✅ Success message appears
5. ✅ Open "Generate AI Template" modal
6. ✅ **Scenario now appears in dropdown!** 🎉

### What Users See in Dropdown
The "Phishing Scenario" dropdown in "Generate AI Template" now shows:
- Password Reset
- Urgent Action Required
- Account Verification
- Security Alert
- Document Share
- Invoice Payment
- IT Support Request
- HR Announcement
- **Loyalty Program Scam** ← New custom scenario!
- **Tax Refund Notification** ← Previously created
- **Lottery Winner** ← Previously created

## MongoDB Query Explanation

The `$or` operator in MongoDB allows combining multiple conditions:

```javascript
{
  "$or": [
    {"is_system": true},           // Match system scenarios
    {"created_by_user_id": 1}      // OR scenarios created by user 1
  ]
}
```

This returns documents matching **either** condition.

## Security Considerations

✅ **User Isolation**: Each user only sees:
- All system scenarios (shared across all users)
- Their own custom scenarios (not other users' scenarios)

✅ **Organization Support Ready**: The filter can be extended to support organizations:
```go
filter := bson.M{
    "$or": []bson.M{
        {"is_system": true},
        {"created_by_user_id": uid},
        {"organization_id": orgID},  // Future: share within organization
    },
}
```

## Rebuild & Deployment

```bash
# 1. Rebuild Go binary
cd c:\Users\User\Documents\Documents\Degree\Y3S2\FYP2\gophish
go build

# 2. Kill old process
taskkill //F //PID <old_pid>

# 3. Start new Gophish
./gophish.exe &

# 4. Test API
curl -k -H "Authorization: Bearer <token>" https://localhost:3333/api/scenarios/
```

## Summary

**Problem**: MongoDB filter excluded custom scenarios
**Solution**: Changed filter from `is_system: true` to `$or` with both system and user scenarios
**Result**: Custom scenarios now appear in dropdowns immediately after creation
**Files changed**: 1 file (`models/scenario.go`)
**Lines changed**: Filter logic (lines 70-77)
**Status**: ✅ **FIXED AND TESTED**

Users can now create unlimited custom scenarios and use them immediately!
