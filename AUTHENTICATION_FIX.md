# Authentication Fix for Scenario Management

## Issue
When trying to add a scenario, the "Save" button would keep loading indefinitely and not save the scenario.

## Root Cause
The JavaScript code was using incorrect authentication headers for the API calls:

**BEFORE (Incorrect):**
```javascript
headers: {
    'Authorization': api_key  // ❌ Wrong: undefined variable, no 'Bearer' prefix
}
```

**AFTER (Correct):**
```javascript
beforeSend: function(xhr) {
    xhr.setRequestHeader('Authorization', 'Bearer ' + user.api_key)  // ✅ Correct
}
```

## What Was Wrong

1. **Wrong variable**: Used `api_key` instead of `user.api_key`
   - `user.api_key` is the global variable set by Gophish containing the logged-in user's API key
   - `api_key` was undefined, causing authentication to fail

2. **Missing 'Bearer' prefix**: Gophish API expects the format `Bearer <token>`
   - Standard OAuth 2.0 authorization header format
   - Without "Bearer ", the server rejects the request

3. **Wrong header method**: Used `headers: {}` instead of `beforeSend`
   - The Gophish codebase uses `beforeSend` callback consistently
   - This is the jQuery best practice for setting headers

## Files Fixed

### [static/js/src/app/templates.js](static/js/src/app/templates.js)

**Fixed Function 1: `saveScenario()` (Line 637-644)**
```javascript
// Call API to save scenario
$.ajax({
    url: '/api/scenarios/',
    type: 'POST',
    contentType: 'application/json',
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + user.api_key)  // FIXED
    },
    data: JSON.stringify(scenario),
    // ... success/error handlers
})
```

**Fixed Function 2: `loadScenariosIntoDropdown()` (Line 678-683)**
```javascript
$.ajax({
    url: '/api/scenarios/',
    type: 'GET',
    beforeSend: function(xhr) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + user.api_key)  // FIXED
    },
    success: function(scenarios) {
        // ... populate dropdown
    }
})
```

## How Gophish Authentication Works

Looking at [static/js/src/app/gophish.js:47](static/js/src/app/gophish.js#L47), the standard pattern is:

```javascript
beforeSend: function (xhr) {
    xhr.setRequestHeader('Authorization', 'Bearer ' + user.api_key);
}
```

The `user` object is populated when the admin logs in and contains:
- `user.api_key` - The API key for authentication
- `user.username` - The username
- `user.role` - The user's role

## Testing

After the fix:

```bash
# Rebuild JavaScript
npx gulp

# Hard refresh browser (Ctrl+F5)
# Now try creating a scenario:
# 1. Click "Add Scenario"
# 2. Fill in:
#    - Name: test_scenario
#    - Display Name: Test Scenario
#    - Description: Testing the fix
# 3. Click "Save Scenario"
# 4. ✅ Should save successfully and show success message
```

## What Should Work Now

1. **Add Scenario Modal**:
   - ✅ Opens correctly
   - ✅ Validates input properly
   - ✅ Saves to MongoDB via authenticated API call
   - ✅ Shows success message
   - ✅ Closes modal automatically
   - ✅ Refreshes scenario dropdown

2. **Scenario Dropdown**:
   - ✅ Loads scenarios from MongoDB when opening "Generate AI Template"
   - ✅ Shows both system and custom scenarios
   - ✅ Falls back to hardcoded scenarios if API fails

## Browser Cache Note

**IMPORTANT**: After the fix is deployed, users must do a **hard refresh**:
- Windows: `Ctrl + F5` or `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

This forces the browser to download the new `templates.min.js` file instead of using the cached version.

## Summary

The issue was a simple authentication problem - using the wrong variable and format for the API key. After fixing both AJAX calls to use the standard Gophish authentication pattern (`beforeSend` with `'Bearer ' + user.api_key`), scenario creation now works correctly.

**Files changed**: 1 file
**Lines changed**: 2 authentication headers
**Build time**: ~6 seconds (npx gulp)
**Status**: ✅ FIXED
