# Gophish AI Integration Guide

## Overview

This integration adds AI-powered phishing template generation to Gophish using your Phishing-Content-Generation-System. Users can now generate realistic phishing emails directly from the Gophish UI by selecting a scenario and target company.

## Features

✅ **AI Template Generation** - Generate phishing emails using Claude AI
✅ **8 Phishing Scenarios** - Pre-configured scenarios covering common phishing types
✅ **Custom Target Company** - Personalize emails for specific organizations
✅ **Seamless UI Integration** - Button integrated into Email Templates page
✅ **Automatic Population** - Generated content fills Subject, Text, and HTML fields

## Architecture

### Components

1. **Frontend (templates/templates.html)**
   - "Generate AI Template" button in Email Templates modal
   - Modal dialog for scenario and company selection
   - 8 pre-configured phishing scenarios

2. **JavaScript (static/js/src/app/templates.js)**
   - `generateAITemplate()` function handles API calls
   - Populates template fields with AI-generated content
   - Error handling and loading states

3. **Backend API (controllers/api/ai_template.go)**
   - `/api/templates/generate_ai` endpoint
   - Validates inputs and calls Python module
   - Returns JSON with subject, text, and HTML

4. **Python Wrapper (ai_module/generate_phishing.py)**
   - Bridges Gophish and Phishing-Content-Generation-System
   - Converts scenarios to generator calls
   - Formats output for Gophish compatibility

5. **AI Generator (Phishing-Content-Generation-System)**
   - Claude API integration
   - Generates realistic phishing content
   - Configurable via .env file

## File Structure

```
gophish/
├── controllers/api/
│   ├── ai_template.go          # NEW: AI generation endpoint
│   └── server.go                # MODIFIED: Added route
├── templates/
│   └── templates.html           # MODIFIED: Added AI button and modal
├── static/js/src/app/
│   └── templates.js             # MODIFIED: Added generateAITemplate()
├── ai_module/
│   └── generate_phishing.py     # NEW: Python wrapper script
└── Phishing-Content-Generation-System/  # External AI system
    ├── src/
    │   └── generators/
    │       └── phishing_generator.py
    └── .env                     # Claude API key configuration
```

## Setup Instructions

### Prerequisites

1. **Phishing-Content-Generation-System**
   - Must be in the `gophish/` directory
   - `.env` file configured with Claude API key
   - Python dependencies installed

2. **Python 3.x**
   - Accessible via `python` command
   - Required packages: see Phishing-Content-Generation-System requirements

### Installation Steps

1. **Verify Directory Structure**
   ```bash
   cd gophish
   ls Phishing-Content-Generation-System/
   # Should show: src/, .env, requirements.txt, etc.
   ```

2. **Configure Claude API Key**
   ```bash
   cd Phishing-Content-Generation-System
   # Edit .env file
   echo "ANTHROPIC_API_KEY=your-claude-api-key-here" > .env
   ```

3. **Install Python Dependencies**
   ```bash
   cd Phishing-Content-Generation-System
   pip install -r requirements.txt
   ```

4. **Test Python Module**
   ```bash
   cd gophish
   python ai_module/generate_phishing.py --scenario password_reset --target "TestCorp" --format json
   ```

   Expected output:
   ```json
   {
     "subject": "Reset Your Password",
     "text": "...",
     "html": "..."
   }
   ```

5. **Build Gophish**
   ```bash
   # Rebuild JavaScript
   npx gulp scripts

   # Build Go application
   go build

   # Start Gophish
   ./gophish.exe
   ```

## Usage Guide

### Generating an AI Template

1. **Navigate to Email Templates**
   - Log in to Gophish
   - Go to "Email Templates" section
   - Click "New Template"

2. **Open AI Generator**
   - Click the green "Generate AI Template" button
   - This opens the AI generation modal

3. **Configure Generation**
   - **Phishing Scenario**: Select from dropdown
     - Password Reset
     - Urgent Action Required
     - Account Verification
     - Security Alert
     - Document Shared
     - Invoice/Payment
     - IT Support
     - HR Announcement

   - **Target Company Name**: Enter the company (e.g., "Acme Corp")
     - Optional: Defaults to "Your Organization"

4. **Generate**
   - Click "Generate Template" button
   - Wait 5-10 seconds for AI generation
   - Content automatically populates template fields

5. **Review and Save**
   - Review Subject, Text, and HTML content
   - Edit as needed
   - Add template name
   - Click "Save Template"

### Using Generated Templates in Campaigns

1. Create new campaign
2. Select the AI-generated template
3. Configure landing page and sending profile
4. Launch campaign as normal

## API Reference

### POST /api/templates/generate_ai

Generates a phishing email template using AI.

**Request Body:**
```json
{
  "scenario": "password_reset",
  "target_company": "Acme Corporation"
}
```

**Response (Success):**
```json
{
  "subject": "Important: Password Reset Required",
  "text": "Dear Employee,\n\nYour password will expire...",
  "html": "<p>Dear Employee,</p><p>Your password will expire...</p>"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "AI module execution failed: ..."
}
```

**Status Codes:**
- `200 OK` - Template generated successfully
- `400 Bad Request` - Invalid input (missing scenario)
- `500 Internal Server Error` - AI generation failed

## Available Scenarios

### 1. Password Reset
Simulates urgent password reset emails from IT department.

**Example:**
- Subject: "Action Required: Reset Your Password"
- Content: Urgent tone, fake reset link

### 2. Urgent Action Required
Creates time-sensitive requests requiring immediate action.

**Example:**
- Subject: "URGENT: Account Security Alert"
- Content: Pressure tactics, countdown timers

### 3. Account Verification
Mimics account verification requests from services.

**Example:**
- Subject: "Verify Your Account"
- Content: Account suspension threat

### 4. Security Alert
Fake security notifications about suspicious activity.

**Example:**
- Subject: "Security Alert: Unauthorized Access Detected"
- Content: Alarm triggers, review link

### 5. Document Shared
Simulates file sharing notifications (OneDrive, Google Drive, etc.)

**Example:**
- Subject: "John Doe shared 'Q4 Report' with you"
- Content: View document link

### 6. Invoice/Payment
Fake invoices or payment requests.

**Example:**
- Subject: "Invoice #12345 - Payment Due"
- Content: Urgent payment, fake portal link

### 7. IT Support
Emails appearing to be from IT support team.

**Example:**
- Subject: "IT Support: System Update Required"
- Content: Technical instructions, update link

### 8. HR Announcement
HR-related announcements or policy updates.

**Example:**
- Subject: "New HR Policy - Action Required"
- Content: Policy review, acknowledgment link

## Customization

### Adding New Scenarios

1. **Update UI Dropdown** (`templates/templates.html`):
   ```html
   <option value="new_scenario">New Scenario Name</option>
   ```

2. **Update Python Module** (`ai_module/generate_phishing.py`):
   ```python
   scenario_mapping = {
       # ... existing ...
       'new_scenario': 'new_scenario_method'
   }
   ```

3. **Implement in Generator** (`Phishing-Content-Generation-System`):
   - Add method to PhishingGenerator class
   - Or use generic scenario handling

### Adjusting AI Parameters

Modify `ai_module/generate_phishing.py` to pass additional parameters:

```python
result = generator.generate_email(
    scenario=scenario_type,
    target_info={
        'company': target_company,
        'organization': target_company,
        # Add custom parameters here
        'sophistication_level': 'high',
        'include_urgency': True
    }
)
```

## Troubleshooting

### "Failed to generate template" Error

**Possible Causes:**
1. Python not installed or not in PATH
2. Phishing-Content-Generation-System not present
3. Claude API key not configured
4. API rate limit exceeded

**Solutions:**
```bash
# Test Python
python --version

# Test module import
cd gophish
python -c "import sys; sys.path.insert(0, 'Phishing-Content-Generation-System/src'); from generators.phishing_generator import PhishingGenerator; print('OK')"

# Check API key
cd Phishing-Content-Generation-System
cat .env | grep ANTHROPIC_API_KEY

# Test generation manually
cd ..
python ai_module/generate_phishing.py --scenario password_reset --target "Test"
```

### Button Not Appearing

**Cause:** JavaScript not rebuilt or browser cache

**Solution:**
```bash
# Rebuild JavaScript
npx gulp scripts

# Restart Gophish
taskkill //F //IM gophish.exe
./gophish.exe

# Clear browser cache (Ctrl+Shift+R)
```

### Generation Takes Too Long

**Cause:** Claude API timeout (default: 30 seconds)

**Solution:** Adjust timeout in `controllers/api/ai_template.go`:
```go
ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)  // Increase to 60s
```

### Module Import Errors

**Error:** `No module named 'generators.phishing_generator'`

**Solution:**
```bash
cd Phishing-Content-Generation-System
pip install -r requirements.txt
python -c "from src.generators.phishing_generator import PhishingGenerator"
```

## Security Considerations

### API Key Protection

The Claude API key is stored in `.env` file. Ensure:
- `.env` is in `.gitignore`
- File permissions restrict access
- Key is not exposed in logs

### Rate Limiting

Consider implementing rate limiting for the AI endpoint:
```go
// In server.go
router.HandleFunc("/templates/generate_ai",
    mid.Use(as.GenerateAITemplate, mid.RequirePermission(models.PermissionModifyObjects)))
```

### Input Validation

The endpoint validates:
- Scenario is not empty
- Company name is sanitized (if needed)

Add additional validation in `ai_template.go` as needed.

## Performance

### Generation Time
- **Average:** 5-10 seconds per template
- **Factors:**
  - Claude API response time
  - Network latency
  - Template complexity

### Caching
Currently, no caching is implemented. Each request generates fresh content.

**Optional Enhancement:** Cache templates by scenario + company combination.

## Testing

### Manual Testing

1. **UI Test:**
   - Create new template
   - Click "Generate AI Template"
   - Select scenario and company
   - Verify content populates

2. **API Test:**
   ```bash
   curl -X POST http://localhost:3333/api/templates/generate_ai \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"scenario":"password_reset","target_company":"TestCorp"}'
   ```

3. **Python Module Test:**
   ```bash
   python ai_module/generate_phishing.py \
     --scenario password_reset \
     --target "Acme Corp" \
     --format json
   ```

### Automated Testing

Create test script (`test_ai_integration.sh`):
```bash
#!/bin/bash

echo "Testing AI Integration..."

# Test 1: Python module
echo "Test 1: Python module"
python ai_module/generate_phishing.py --scenario password_reset --target "Test" --format json
if [ $? -eq 0 ]; then
    echo "✓ Python module works"
else
    echo "✗ Python module failed"
    exit 1
fi

# Test 2: Build succeeds
echo "Test 2: Build"
go build
if [ $? -eq 0 ]; then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

echo "All tests passed!"
```

## Logs and Debugging

### Enable Verbose Logging

Check Gophish logs for AI-related messages:
```bash
tail -f gophish.log | grep -i "ai\|template\|python"
```

### Python Module Debugging

Run Python module with verbose output:
```python
# In generate_phishing.py, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Go Debugging

Add debug logs in `ai_template.go`:
```go
log.Infof("Generating AI template: scenario=%s, company=%s", req.Scenario, req.TargetCompany)
log.Debugf("Python output: %s", stdout.String())
```

## Future Enhancements

### Potential Features

1. **Template Variations**
   - Generate multiple variations per scenario
   - A/B testing support

2. **Difficulty Levels**
   - Easy to detect (training)
   - Hard to detect (testing)

3. **Custom Scenarios**
   - User-defined scenario descriptions
   - Free-form AI prompting

4. **Template History**
   - Store generated templates
   - Regenerate with modifications

5. **Batch Generation**
   - Generate multiple templates at once
   - Different scenarios for campaign rotation

## Support

### Common Questions

**Q: Can I use a different AI provider?**
A: Yes, modify `ai_module/generate_phishing.py` to call different APIs.

**Q: Does this work offline?**
A: No, requires Claude API access (internet connection).

**Q: How much does it cost?**
A: Depends on Claude API pricing. ~$0.01-0.05 per template generation.

**Q: Can I save favorite templates?**
A: Yes, generated templates are saved like normal Gophish templates.

## Summary

✅ **AI integration complete and functional**
✅ **8 scenario types available**
✅ **Simple UI integration**
✅ **Full documentation provided**

The AI integration is now ready for use. Generate realistic phishing templates directly from the Gophish interface!
