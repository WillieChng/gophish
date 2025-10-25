# Scenario Management Feature - Implementation Complete

## Overview

Added a complete scenario management feature to Gophish that allows users to create custom phishing scenarios through the UI. Scenarios are stored persistently in MongoDB and are immediately available for use in AI template generation.

## Features Implemented

### 1. Add Scenario Button
- **Location**: Templates page, next to "Generate AI Template" button
- **Appearance**: Blue button with sitemap icon
- **Label**: "Add Scenario"

### 2. Add Scenario Modal Dialog
A user-friendly modal form with the following fields:

- **Scenario Name** (required)
  - Internal identifier (e.g., `tax_refund`, `ceo_directive`)
  - Must be lowercase letters and underscores only
  - Validated with regex: `/^[a-z_]+$/`

- **Display Name** (required)
  - User-friendly name shown in dropdown (e.g., "Tax Refund")
  - No format restrictions

- **Description** (optional)
  - Brief description of what the scenario simulates
  - Helps users understand the context

### 3. Real-time Validation
- Client-side validation for required fields
- Format validation for scenario name
- Clear error messages shown in modal
- Loading state with spinner during save

### 4. MongoDB Integration
- Custom scenarios stored persistently in MongoDB `scenarios` collection
- System scenarios protected from modification/deletion
- User ID tracking for custom scenarios
- Timestamps (created_at, updated_at) automatically managed

### 5. Dynamic Scenario Dropdown
- AI Template Generation modal now loads scenarios from MongoDB API
- Automatically updates when new scenarios are added
- Shows both system and custom scenarios
- Graceful fallback to hardcoded scenarios if API fails

## Files Modified

### Frontend Files

#### [templates/templates.html](templates/templates.html)
- **Line 13**: Added "Add Scenario" button
- **Lines 296-333**: New modal dialog for adding scenarios

#### [static/js/src/app/templates.js](static/js/src/app/templates.js)
- **Lines 586-593**: `openAddScenarioModal()` - Clears form and opens modal
- **Lines 595-674**: `saveScenario()` - Validates and saves new scenario via API
- **Lines 676-701**: `loadScenariosIntoDropdown()` - Fetches scenarios from API and populates dropdown
- **Lines 705-708**: Event listener to load scenarios when opening AI modal

#### [static/js/dist/app/templates.min.js](static/js/dist/app/templates.min.js)
- Rebuilt with `npx gulp` to include new JavaScript functions

## API Endpoints Used

### GET /api/scenarios/
- Returns all scenarios (system + custom) for the authenticated user
- Used to populate dropdown in AI Template Generation modal

### POST /api/scenarios/
- Creates new custom scenario
- Requires: name, display_name, description (optional)
- Automatically sets: is_system=false, created_by_user_id, timestamps

## Testing Results

### ✅ API Testing
```bash
# List all scenarios (8 system scenarios)
curl -k -H "Authorization: <api_key>" https://localhost:3333/api/scenarios/
# Returns 8 system scenarios

# Create custom scenario
curl -k -X POST -H "Authorization: <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"name":"lottery_winner","display_name":"Lottery Winner","description":"Fake lottery or prize notification"}' \
  https://localhost:3333/api/scenarios/
# Success! Returns created scenario with ID
```

### ✅ MongoDB Persistence
- Custom scenarios stored in `gophish.scenarios` collection
- Fields: `_id`, `name`, `display_name`, `description`, `is_system`, `organization_id`, `created_by_user_id`, `created_at`, `updated_at`
- System scenarios protected with `is_system: true` flag

### ✅ UI Integration
- "Add Scenario" button visible on Templates page
- Modal opens correctly with validation
- Form submits to API successfully
- Success flash message displayed
- Scenario dropdown refreshes automatically

## User Workflow

1. **Navigate to Templates page** in Gophish admin
2. **Click "Add Scenario" button** (blue button with sitemap icon)
3. **Fill out the form**:
   - Scenario Name: `ceo_directive` (lowercase with underscores)
   - Display Name: `CEO Directive` (user-friendly name)
   - Description: `Urgent message from CEO requesting immediate action`
4. **Click "Save Scenario"**
5. **Success!** The scenario is now:
   - Saved in MongoDB
   - Available in the AI Template Generation dropdown
   - Persistent across sessions
   - Available to all users in the organization

## Architecture Benefits

### Separation of Concerns
- **Scenarios**: Define the theme/context (name, display_name, description)
- **Risk Configuration**: Applied at generation time (phishing sign difficulty levels)
- **No coupling**: Same scenario can be used with different risk configurations

### Flexibility
- Users can create unlimited custom scenarios
- No need to modify code or configuration files
- Immediate availability after creation
- Easy to manage and delete (custom scenarios only)

### Data Flow
```
User Input (UI Form)
    ↓
JavaScript Validation
    ↓
POST /api/scenarios/
    ↓
Go API Handler (controllers/api/scenario.go)
    ↓
MongoDB (models/scenario.go)
    ↓
Python AI System (fetch_scenarios_from_api)
    ↓
Claude AI Template Generation
```

## System Scenarios (Built-in)

1. **Password Reset** - Password reset phishing attempt
2. **Urgent Action Required** - High-pressure demanding action
3. **Account Verification** - Account verification request
4. **Security Alert** - Fake security alert
5. **Document Share** - Shared document/file
6. **Invoice Payment** - Fake invoice/payment
7. **IT Support Request** - IT support ticket
8. **HR Announcement** - HR announcement/policy

## Custom Scenario Examples

Users can now create scenarios like:
- **Tax Refund** - Government tax refund notification
- **CEO Directive** - Urgent message from CEO
- **Prize Notification** - Lottery/contest winner
- **Package Delivery** - Missed package notification
- **Subscription Renewal** - Service renewal required
- **Two-Factor Authentication** - 2FA setup request

## Future Enhancements (Optional)

1. **Scenario Management Page**: Dedicated page to view/edit/delete custom scenarios
2. **Scenario Import/Export**: Share scenarios between organizations
3. **Scenario Templates**: Pre-built scenario packs for different industries
4. **Scenario Analytics**: Track which scenarios are most effective
5. **Scenario Versioning**: Track changes to scenarios over time
6. **Scenario Categories**: Organize scenarios by type (financial, IT, HR, etc.)

## Security Considerations

- ✅ API authentication required (API key validation)
- ✅ User ID tracking for audit trails
- ✅ System scenarios protected from modification
- ✅ Input validation on client and server side
- ✅ MongoDB injection protection (using driver's type-safe methods)
- ✅ HTTPS for all API communications

## Conclusion

The scenario management feature is **fully functional and production-ready**. Users can now:
- Create custom phishing scenarios through the UI
- Have scenarios stored persistently in MongoDB
- Use them immediately in AI template generation
- No code changes required for new scenarios

This feature significantly enhances the flexibility and usability of the Gophish phishing simulation system.
