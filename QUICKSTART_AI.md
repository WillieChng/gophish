# Quick Start - AI Template Generation

## 5-Minute Setup

### Step 1: Configure Claude API Key

```bash
cd Phishing-Content-Generation-System
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

Get your API key from: https://console.anthropic.com/

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test Python Module

```bash
cd ..
python ai_module/generate_phishing.py --scenario password_reset --target "TestCorp" --format json
```

**Expected:** JSON output with subject, text, and html fields

### Step 4: Start Gophish

```bash
./gophish.exe
```

Navigate to: http://localhost:3333

## Using AI Generation

### Quick Usage

1. **Email Templates** → **New Template**
2. Click green **"Generate AI Template"** button
3. Select **Scenario** (e.g., "Password Reset")
4. Enter **Target Company** (e.g., "Acme Corp")
5. Click **"Generate Template"**
6. Wait 5-10 seconds
7. Review generated content
8. Click **"Save Template"**

### 8 Available Scenarios

1. **Password Reset** - Urgent password change requests
2. **Urgent Action** - Time-sensitive demands
3. **Account Verification** - Account confirmation requests
4. **Security Alert** - Fake security notifications
5. **Document Share** - File sharing notifications
6. **Invoice** - Payment requests
7. **IT Support** - Tech support communications
8. **HR Announcement** - HR policy updates

## Troubleshooting

### "Failed to generate template"

**Quick Fixes:**
```bash
# 1. Check Python works
python --version

# 2. Test module manually
python ai_module/generate_phishing.py --scenario password_reset --target "Test"

# 3. Verify API key
cd Phishing-Content-Generation-System
cat .env

# 4. Check dependencies
pip list | grep anthropic
```

### Button doesn't appear

```bash
# Rebuild JavaScript
npx gulp scripts

# Restart Gophish
taskkill //F //IM gophish.exe
./gophish.exe

# Hard refresh browser (Ctrl+Shift+R)
```

## Example Generated Template

**Input:**
- Scenario: Password Reset
- Company: Acme Corporation

**Output:**
```
Subject: Urgent: Password Reset Required - Acme Corporation

Text:
Dear Acme Corporation Employee,

Your password will expire in 24 hours. To maintain access to your
account, please reset your password immediately using the link below:

[Reset Password]

If you do not reset your password, your account will be suspended.

IT Security Team
Acme Corporation

HTML:
<html>
<body>
<p>Dear Acme Corporation Employee,</p>
<p>Your password will expire in 24 hours...</p>
...
</body>
</html>
```

## What's Next?

- **Use in campaigns**: Select your AI template when creating campaigns
- **Edit templates**: Customize generated content as needed
- **Try scenarios**: Generate different types of phishing emails
- **Read full guide**: See [AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)

## API Test (Optional)

Test the API endpoint directly:

```bash
curl -X POST http://localhost:3333/api/templates/generate_ai \
  -H "Authorization: Bearer YOUR_GOPHISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "password_reset",
    "target_company": "Acme Corp"
  }'
```

## Success Checklist

- ✅ Claude API key configured in `.env`
- ✅ Python dependencies installed
- ✅ Test generation works from command line
- ✅ Gophish running and accessible
- ✅ "Generate AI Template" button visible in UI
- ✅ Template generation completes successfully

**All set!** You can now generate AI-powered phishing templates in Gophish.

## Need Help?

See the full guide: [AI_INTEGRATION_GUIDE.md](AI_INTEGRATION_GUIDE.md)

Common issues:
- Missing dependencies: `pip install -r Phishing-Content-Generation-System/requirements.txt`
- Python path issues: Ensure `Phishing-Content-Generation-System` is in `gophish/` directory
- API key errors: Verify `.env` file has correct `ANTHROPIC_API_KEY`
