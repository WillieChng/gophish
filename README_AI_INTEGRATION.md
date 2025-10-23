# Gophish AI Integration

This repository contains Gophish with AI-powered phishing template generation capabilities.

## What's New

✨ **AI Template Generation** - Generate realistic phishing emails using Claude AI directly from the Gophish UI.

### Features

- **8 Phishing Scenarios**: Password reset, urgent action, account verification, security alerts, document sharing, invoices, IT support, and HR announcements
- **Custom Targeting**: Personalize emails for specific companies
- **One-Click Generation**: Simple button in the Email Templates interface
- **Realistic Content**: AI-generated subjects, text, and HTML email bodies

## Quick Start

### 1. Setup (5 minutes)

```bash
# Configure Claude API key
cd Phishing-Content-Generation-System
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Install Python dependencies
pip install -r requirements.txt

# Test the integration
cd ..
python ai_module/generate_phishing.py --scenario password_reset --target "TestCorp" --format json

# Start Gophish
./gophish.exe
```

### 2. Use AI Generation

1. Navigate to **Email Templates** in Gophish
2. Click **New Template**
3. Click the green **"Generate AI Template"** button
4. Select a **scenario** (e.g., "Password Reset")
5. Enter **target company** name
6. Click **"Generate Template"**
7. Wait 5-10 seconds for AI to generate content
8. Review and save the template

### 3. Use in Campaigns

- Select your AI-generated template when creating campaigns
- Configure landing pages and sending profiles as normal
- Launch your campaign

## Documentation

- **[QUICKSTART_AI.md](QUICKSTART_AI.md)** - 5-minute setup guide
- **[AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)** - Complete technical documentation
- **[AI_INTEGRATION_COMPLETE.md](AI_INTEGRATION_COMPLETE.md)** - Implementation summary

## Architecture

```
User Interface (templates/templates.html)
    ↓
JavaScript (static/js/src/app/templates.js)
    ↓
Go API (controllers/api/ai_template.go)
    ↓
Python Wrapper (ai_module/generate_phishing.py)
    ↓
Phishing-Content-Generation-System
    ↓
Claude API
```

## Files Added/Modified

### New Files
- `controllers/api/ai_template.go` - API endpoint for AI generation
- `ai_module/generate_phishing.py` - Python wrapper for AI system
- Documentation files (guides and summaries)

### Modified Files
- `controllers/api/server.go` - Added AI endpoint route
- `templates/templates.html` - Added AI generation button and modal
- `static/js/src/app/templates.js` - Added AI generation JavaScript

## Requirements

- **Gophish** - Latest version
- **Python 3.x** - For AI module
- **Phishing-Content-Generation-System** - In `gophish/` directory
- **Claude API Key** - From https://console.anthropic.com/
- **Internet Connection** - For Claude API access

## Available Scenarios

1. **Password Reset** - Urgent password change requests
2. **Urgent Action Required** - Time-sensitive demands
3. **Account Verification** - Account confirmation requests
4. **Security Alert** - Fake security notifications
5. **Document Shared** - File sharing notifications (OneDrive, Google Drive)
6. **Invoice/Payment** - Payment requests and invoices
7. **IT Support** - Technical support communications
8. **HR Announcement** - HR policy updates and announcements

## Example Output

**Input:**
- Scenario: Password Reset
- Company: Acme Corporation

**Generated Template:**
```
Subject: Urgent: Password Reset Required - Acme Corporation

Your password will expire in 24 hours. To maintain access to your
account, please reset your password immediately using the link below:

[Reset Password Link]

If you do not reset your password, your account will be suspended.

IT Security Team
Acme Corporation
```

## Troubleshooting

### "Failed to generate template"

```bash
# Check Python
python --version

# Test module
python ai_module/generate_phishing.py --scenario password_reset --target "Test"

# Verify API key
cat Phishing-Content-Generation-System/.env
```

### Button doesn't appear

```bash
# Rebuild JavaScript
npx gulp scripts

# Restart Gophish
taskkill //F //IM gophish.exe
./gophish.exe

# Clear browser cache (Ctrl+Shift+R)
```

## API Reference

### POST /api/templates/generate_ai

**Request:**
```json
{
  "scenario": "password_reset",
  "target_company": "Acme Corporation"
}
```

**Response:**
```json
{
  "subject": "Urgent: Password Reset Required",
  "text": "Dear Employee, ...",
  "html": "<html>...</html>"
}
```

## Security Notes

- Claude API key stored in `.env` file (not in code)
- Input validation prevents injection attacks
- 30-second timeout prevents hanging requests
- Requires Gophish authentication to access
- Keep `.env` in `.gitignore`

## Performance

- **Generation Time**: 5-10 seconds per template
- **Cost**: ~$0.01-0.05 per generation (Claude API)
- **Rate Limit**: Based on Claude API limits
- **Offline**: Not supported (requires API access)

## Testing

### Manual Test
1. Open Gophish at http://localhost:3333
2. Go to Email Templates → New Template
3. Click "Generate AI Template"
4. Select scenario and enter company
5. Verify content populates correctly

### API Test
```bash
curl -X POST http://localhost:3333/api/templates/generate_ai \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"scenario":"password_reset","target_company":"Acme"}'
```

## Build & Deploy

```bash
# Build JavaScript
npx gulp scripts

# Build Go application
go build

# Run
./gophish.exe
```

## Support

### Documentation
- [Quick Start](QUICKSTART_AI.md)
- [Full Integration Guide](AI_INTEGRATION_GUIDE.md)
- [Implementation Details](AI_INTEGRATION_COMPLETE.md)

### Common Issues
- **Module not found**: Install Python dependencies
- **API timeout**: Check internet connection, Claude API status
- **Empty response**: Verify API key in `.env`
- **Button missing**: Rebuild JavaScript, clear cache

## Contributing

To add new scenarios:

1. Update scenario dropdown in `templates/templates.html`
2. Add scenario mapping in `ai_module/generate_phishing.py`
3. Implement scenario in Phishing-Content-Generation-System (optional)

## License

Same as Gophish - MIT License

## Credits

- **Gophish** - Original phishing framework
- **Anthropic Claude** - AI content generation
- **Phishing-Content-Generation-System** - AI template generator

---

**Status**: ✅ Ready for use

Get started: [QUICKSTART_AI.md](QUICKSTART_AI.md)
