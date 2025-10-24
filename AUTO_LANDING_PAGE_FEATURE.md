# Automatic Landing Page Generation Feature

## Overview

The AI template generation feature has been extended to automatically create matching landing pages alongside email templates. This feature streamlines the campaign setup process by generating both components in a single action.

## What Was Added

### 1. Python Module Enhancement
**File**: `ai_module/generate_phishing.py`

Added `generate_landing_page()` function that creates scenario-specific landing pages:
- **8 Unique Landing Page Templates** - Each scenario has a professionally designed landing page
- **Scenario Matching** - Landing pages match the email template theme
- **Credential Capture Forms** - All pages include forms for capturing credentials
- **Responsive Design** - Modern, mobile-friendly HTML/CSS
- **Customization** - Company name is dynamically inserted

### 2. Backend API Update
**File**: `controllers/api/ai_template.go`

Enhanced the API endpoint to support landing page generation:
- Added `IncludeLandingPage` boolean field to `AITemplateRequest`
- Added `LandingPage` field to `AITemplateResponse`
- Updated `generateTemplateWithAI()` to pass `--include-landing-page` flag to Python module
- Response now includes landing page HTML when requested

### 3. Frontend UI Enhancement
**File**: `templates/templates.html`

Added user control for landing page generation:
- New checkbox: "Also create a matching landing page"
- Checked by default for convenience
- Tooltip explaining the feature
- Visual icon (desktop icon) for clarity

### 4. JavaScript Integration
**File**: `static/js/src/app/templates.js`

Updated the AI generation workflow:
- Reads checkbox state for `include_landing_page`
- Sends flag to API endpoint
- Automatically saves landing page when generated
- Shows updated loading message ("Generating AI Template & Landing Page...")
- Displays success message indicating both were created
- Landing page is saved with automatic naming: `"[Template Name] - Landing Page"`

## Landing Page Scenarios

Each scenario generates a unique, themed landing page:

### 1. Password Reset
- Clean, professional design with gradient background
- Email, new password, and confirm password fields
- Security notice about link expiration
- Purple/blue color scheme

### 2. Urgent Action
- Red alert header for urgency
- Warning box with urgent message
- Email and password fields
- Emphasis on immediate action required

### 3. Account Verification
- Blue corporate theme
- Information box explaining unusual activity
- Username/email and password fields
- Professional trust signals

### 4. Security Alert
- Dark theme with red security alerts
- Shield icon for credibility
- Warning box about unrecognized login
- "Secure My Account" call-to-action

### 5. Document Share
- Green theme suggesting file access
- Document icon
- Notification about shared document
- "Access Document" button

### 6. Invoice/Payment
- Professional billing portal design
- Invoice details (number, amount, due date)
- Payment required badge
- Green "Sign In & Pay Now" button

### 7. IT Support
- Blue IT department theme
- Support icon
- System maintenance notice
- Corporate email and network password fields

### 8. HR Announcement
- Purple HR department theme
- Announcement badge
- Benefits update notification
- Employee portal design

## Configuration

Each landing page is automatically configured with:
- `capture_credentials: true`
- `capture_passwords: true`
- `redirect_url: "https://example.com"` (can be customized after creation)

## User Workflow

### With Landing Page (Default)
1. Click "Generate AI Template"
2. Select scenario
3. Enter target company
4. Ensure "Also create a matching landing page" is checked
5. Click "Generate Template"
6. Wait 5-10 seconds
7. **Both** email template and landing page are created
8. Email template editor opens for review
9. Landing page is saved and available in the Landing Pages section

### Without Landing Page
1. Same as above, but uncheck the landing page option
2. Only the email template is generated
3. Faster generation (no landing page HTML to create)

## API Usage

### Request Format
```json
{
  "scenario": "password_reset",
  "target_company": "Acme Corp",
  "include_landing_page": true
}
```

### Response Format
```json
{
  "subject": "Urgent: Reset Your Password - Acme Corp",
  "text": "Dear Employee...",
  "html": "<html>...</html>",
  "landing_page": "<html>...</html>"
}
```

## File Changes Summary

### Modified Files (4)
1. **ai_module/generate_phishing.py** - Added `generate_landing_page()` function and `--include-landing-page` argument (+560 lines)
2. **controllers/api/ai_template.go** - Added landing page support to API (+20 lines)
3. **static/js/src/app/templates.js** - Integrated landing page creation logic (+30 lines)
4. **templates/templates.html** - Added checkbox for landing page option (+8 lines)

### Total Impact
- **New Code**: ~620 lines
- **Files Modified**: 4
- **New Feature**: Fully automated landing page generation

## Technical Details

### Landing Page HTML Structure
Each landing page includes:
- Responsive meta tags
- Embedded CSS (no external dependencies)
- Form with POST method (captures credentials via Gophish)
- Company branding in header
- Professional footer
- Scenario-appropriate styling and messaging

### Form Field Names
All landing pages use consistent field names for Gophish compatibility:
- `email` - For email/username input
- `password` - For password input
- Additional fields as needed per scenario (e.g., `confirm_password`)

### Styling Features
- Modern CSS with gradients and shadows
- Mobile-responsive design
- Hover effects on buttons
- Focus states for inputs
- Color-coded by scenario theme

## Benefits

### For Users
- **Time Savings** - Create both template and landing page in one action
- **Consistency** - Landing page automatically matches email theme
- **Professional Quality** - Well-designed, realistic landing pages
- **Flexibility** - Option to generate email only if desired

### For Campaigns
- **Complete Setup** - Both components ready to use
- **Theme Coherence** - Email and landing page tell the same story
- **Higher Realism** - Matching design increases believability
- **Quick Deployment** - Faster campaign creation

## Testing

### Manual Tests Completed
✓ Password Reset scenario with landing page
✓ Urgent Action scenario with landing page
✓ All 8 scenarios generate unique landing pages
✓ Checkbox controls feature correctly
✓ Landing pages save with correct naming
✓ Email-only generation still works
✓ API returns landing_page field when requested
✓ Python module handles both modes

### Test Results
```bash
# With landing page flag
Subject: URGENT: Security Breach Detected - Immediate Action
Text length: 988
HTML length: 4130
Landing page included: YES
Landing page length: 4161

# Without landing page flag
Subject: URGENT: Security Breach Detected - Immediate Action
Text length: 792
HTML length: 3736
Landing page included: NO
```

## Future Enhancements

Potential improvements for this feature:

1. **Custom Redirect URLs** - Allow users to specify redirect URL during generation
2. **Landing Page Preview** - Show landing page preview before saving
3. **Template Pairing** - Automatically link template to landing page in UI
4. **Credential Field Customization** - Choose which fields to capture
5. **Multi-Step Landing Pages** - Support for multi-page credential harvesting
6. **A/B Testing** - Generate multiple landing page variants
7. **Logo Upload** - Add company logo to landing pages
8. **Color Theme Selection** - Let users pick color schemes
9. **Mobile Preview** - Show how landing page looks on mobile devices
10. **Landing Page Analytics** - Track which designs perform best

## Troubleshooting

### Landing Page Not Created
- Check that checkbox is checked
- Verify API response includes `landing_page` field
- Check browser console for JavaScript errors
- Ensure user has permission to create landing pages

### Landing Page Styling Issues
- Landing pages use embedded CSS (no external dependencies)
- Check that HTML is not being sanitized/stripped
- Verify form fields have correct `name` attributes

### Credential Capture Not Working
- Ensure `capture_credentials` is set to `true`
- Verify form has `method="POST"`
- Check that input fields have `name` attributes

## Compatibility

- **Gophish Version**: Compatible with current version
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **Mobile**: Fully responsive design
- **Dependencies**: No additional dependencies required

## Security Notes

- Landing pages are stored in the database like any other page
- Credential capture follows Gophish's existing security model
- No external resources loaded (all CSS is embedded)
- Forms use relative URLs for submission
- No client-side validation (to maintain phishing authenticity)

## Summary

This feature significantly enhances the AI template generation capability by providing complete, ready-to-use campaign materials. Users can now generate professional email templates and matching landing pages with a single click, reducing setup time and improving campaign consistency.

**Status**: ✅ **IMPLEMENTED AND TESTED**

---

**Feature Complete!** 🚀
