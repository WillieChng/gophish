#!/usr/bin/env python3
"""
Gophish AI Template Generator

This script wraps the Phishing-Content-Generation-System to generate
phishing email templates for Gophish campaigns.
"""

import sys
import os
import json
import argparse
from dotenv import load_dotenv

# Get the absolute path to this script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the Phishing-Content-Generation-System to the path
project_root = os.path.abspath(os.path.join(script_dir, '..', 'Phishing-Content-Generation-System'))
sys.path.insert(0, os.path.join(project_root, 'src'))

# Load environment variables from the .env file in Phishing-Content-Generation-System
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    # Load the .env file and override system environment variables
    load_dotenv(dotenv_path=env_path, override=True)

    # Verify the API key was loaded
    if not os.getenv("CLAUDE_API_KEY"):
        print(json.dumps({
            "error": "CLAUDE_API_KEY not found in .env file",
            "subject": "Error: API Key Not Set",
            "text": "Please set CLAUDE_API_KEY in the .env file located at: " + env_path,
            "html": "<p>Please set CLAUDE_API_KEY in the .env file located at: " + env_path + "</p>"
        }))
        sys.exit(1)
else:
    print(json.dumps({
        "error": f".env file not found at: {env_path}",
        "subject": "Error: Configuration File Missing",
        "text": "Please create a .env file with CLAUDE_API_KEY",
        "html": "<p>Please create a .env file with CLAUDE_API_KEY</p>"
    }))
    sys.exit(1)

try:
    from generators.phishing_generator import PhishingGenerator
except ImportError as e:
    print(json.dumps({
        "error": f"Failed to import PhishingGenerator: {e}",
        "subject": "Error: AI Module Not Configured",
        "text": "Please ensure the Phishing-Content-Generation-System is properly installed.",
        "html": "<p>Please ensure the Phishing-Content-Generation-System is properly installed.</p>"
    }))
    sys.exit(1)


def convert_text_to_html(text, company_name=""):
    """
    Convert plain text email to professional HTML format with modern styling

    Args:
        text: Plain text email content
        company_name: Name of the target company for header

    Returns:
        HTML formatted email with professional styling
    """
    if not text:
        return ""

    import re

    # Split into lines
    lines = text.split('\n')

    # Extract company name from first line if it contains company info
    if not company_name:
        for line in lines[:3]:
            if 'employee' in line.lower() or 'company' in line.lower():
                # Try to extract company name
                match = re.search(r'at\s+([A-Z][A-Za-z\s&]+?)(?:\s|$|,)', line)
                if match:
                    company_name = match.group(1).strip()
                    break

    if not company_name:
        company_name = "Security Alert"

    # Start with professional HTML structure
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h2 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .content p {{
            margin: 15px 0;
            line-height: 1.8;
        }}
        .button {{
            display: inline-block;
            background: #0066cc;
            color: white !important;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
            font-weight: 600;
            text-align: center;
        }}
        .button:hover {{
            background: #0052a3;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 20px 0;
        }}
        .urgent {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            padding: 12px;
            margin: 20px 0;
            color: #721c24;
            font-weight: 600;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{company_name}</h2>
        </div>
        <div class="content">
'''

    # Track if we found the main CTA link
    main_link = None
    content_parts = []
    in_list = False
    is_footer = False

    for line in lines:
        line_stripped = line.strip()

        if not line_stripped:
            if in_list:
                content_parts.append('</ul>')
                in_list = False
            continue

        # Check if this is footer content
        if line_stripped.startswith('---') or 'training purposes' in line_stripped.lower() or 'simulated' in line_stripped.lower():
            is_footer = True
            if in_list:
                content_parts.append('</ul>')
                in_list = False
            continue

        # Skip if already in footer section
        if is_footer:
            continue

        # Extract main call-to-action link
        url_match = re.search(r'https?://[^\s]+', line_stripped)
        if url_match and not main_link and ('click' in line_stripped.lower() or 'verify' in line_stripped.lower() or 'secure' in line_stripped.lower()):
            main_link = url_match.group(0)
            # Don't add this line as regular content, we'll add button later
            continue

        # Convert URLs to clickable links in text
        if 'http://' in line_stripped or 'https://' in line_stripped:
            url_pattern = r'(https?://[^\s]+)'
            line_stripped = re.sub(url_pattern, r'<a href="\1">\1</a>', line_stripped)

        # Check if line is a list item
        if line_stripped.startswith('- ') or line_stripped.startswith('• '):
            if not in_list:
                content_parts.append('<ul>')
                in_list = True
            content_parts.append(f'<li>{line_stripped[2:]}</li>')
        elif in_list and line_stripped and not line_stripped[0].isalpha():
            # Continue list
            content_parts.append(f'<li>{line_stripped}</li>')
        else:
            # Close list if open
            if in_list:
                content_parts.append('</ul>')
                in_list = False

            # Check for urgent/warning content
            if 'URGENT' in line_stripped.upper() or 'IMMEDIATE' in line_stripped.upper() or 'SUSPENDED' in line_stripped.upper():
                content_parts.append(f'<div class="urgent">{line_stripped}</div>')
            elif 'ACTION REQUIRED' in line_stripped.upper() or 'WARNING' in line_stripped.upper():
                content_parts.append(f'<div class="warning"><strong>{line_stripped}</strong></div>')
            else:
                content_parts.append(f'<p>{line_stripped}</p>')

    # Close any open list
    if in_list:
        content_parts.append('</ul>')

    # Add content
    html += '\n'.join(content_parts)

    # Add call-to-action button if we found a link
    if main_link:
        html += f'''
            <p style="text-align: center;">
                <a href="{{{{.URL}}}}" class="button">Verify Your Account Now</a>
            </p>
'''

    # Close content and add footer
    html += '''
        </div>
        <div class="footer">
            <p>This is an automated security message.</p>
            <p>If you have questions, please contact your IT department.</p>
            <p>&copy; 2024 All rights reserved.</p>
        </div>
    </div>
    {{.Tracker}}
</body>
</html>'''

    return html


def generate_landing_page(scenario, target_company):
    """
    Generate a landing page HTML that matches the phishing scenario

    Args:
        scenario: The phishing scenario type
        target_company: The target company name

    Returns:
        HTML string for the landing page
    """
    scenario_pages = {
        'password_reset': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Password Reset</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .container {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 450px;
            width: 100%;
            padding: 40px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo h1 {{
            color: #333;
            font-size: 28px;
            font-weight: 600;
        }}
        h2 {{
            color: #333;
            font-size: 22px;
            margin-bottom: 10px;
            text-align: center;
        }}
        .subtitle {{
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        label {{
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }}
        input[type="email"],
        input[type="password"],
        input[type="text"] {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e8ed;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}
        input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        .btn {{
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .btn:hover {{
            transform: translateY(-2px);
        }}
        .security-notice {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 12px;
            margin-top: 20px;
            font-size: 13px;
            color: #666;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>{target_company}</h1>
        </div>
        <h2>Reset Your Password</h2>
        <p class="subtitle">Please enter your email and new password below</p>
        <form method="POST">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required placeholder="you@example.com">
            </div>
            <div class="form-group">
                <label for="password">New Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter new password">
            </div>
            <div class="form-group">
                <label for="confirm_password">Confirm Password</label>
                <input type="password" id="confirm_password" name="confirm_password" required placeholder="Confirm new password">
            </div>
            <button type="submit" class="btn">Reset Password</button>
        </form>
        <div class="security-notice">
            <strong>Security Notice:</strong> For your protection, this link will expire in 24 hours.
        </div>
        <div class="footer">
            &copy; 2024 {target_company}. All rights reserved.
        </div>
    </div>
</body>
</html>''',

        'urgent_action': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Account Verification Required</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 500px;
            margin: 40px auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: #dc3545;
            color: white;
            padding: 30px;
            border-radius: 8px 8px 0 0;
            text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 10px; }}
        .urgent {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px; color: #856404; }}
        .content {{ padding: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; font-weight: 500; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; }}
        input:focus {{ outline: none; border-color: #dc3545; }}
        .btn {{ width: 100%; background: #dc3545; color: white; border: none; padding: 14px; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }}
        .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ {target_company}</h1>
            <p>Immediate Action Required</p>
        </div>
        <div class="content">
            <div class="urgent">
                <strong>URGENT:</strong> Your account requires immediate verification to prevent suspension.
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" required placeholder="Enter your email">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn">Verify Account Now</button>
            </form>
        </div>
        <div class="footer">&copy; 2024 {target_company}</div>
    </div>
</body>
</html>''',

        'account_verification': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Verify Your Account</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #e9ecef; padding: 20px; }}
        .container {{ max-width: 480px; margin: 40px auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ font-size: 26px; margin-bottom: 10px; }}
        .content {{ padding: 35px 30px; }}
        .info {{ background: #e7f3ff; border-left: 4px solid #0066cc; padding: 15px; margin-bottom: 25px; font-size: 14px; }}
        .form-group {{ margin-bottom: 18px; }}
        label {{ display: block; margin-bottom: 6px; font-weight: 500; color: #333; font-size: 14px; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ced4da; border-radius: 5px; font-size: 14px; }}
        .btn {{ width: 100%; background: #0066cc; color: white; border: none; padding: 14px; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; }}
        .footer {{ padding: 20px; text-align: center; background: #f8f9fa; font-size: 12px; color: #6c757d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{target_company}</h1>
            <p>Account Verification</p>
        </div>
        <div class="content">
            <div class="info">
                We've detected unusual activity on your account. Please verify your identity to continue.
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Username or Email</label>
                    <input type="text" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn">Verify My Account</button>
            </form>
        </div>
        <div class="footer">&copy; 2024 {target_company}. All rights reserved.</div>
    </div>
</body>
</html>''',

        'security_alert': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Security Alert</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #1a1a1a; padding: 20px; }}
        .container {{ max-width: 520px; margin: 30px auto; background: white; border-radius: 8px; overflow: hidden; }}
        .alert-header {{ background: #ff4444; color: white; padding: 25px; text-align: center; }}
        .alert-header h1 {{ font-size: 24px; margin-bottom: 8px; }}
        .shield {{ font-size: 48px; margin-bottom: 10px; }}
        .content {{ padding: 30px; }}
        .warning-box {{ background: #fff3cd; border: 2px solid #ffc107; padding: 15px; border-radius: 5px; margin-bottom: 25px; color: #856404; }}
        .form-group {{ margin-bottom: 18px; }}
        label {{ display: block; margin-bottom: 7px; font-weight: 600; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; }}
        .btn {{ width: 100%; background: #ff4444; color: white; border: none; padding: 15px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }}
        .footer {{ padding: 20px; background: #f5f5f5; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="alert-header">
            <div class="shield">🛡️</div>
            <h1>{target_company} Security</h1>
            <p>Unusual Activity Detected</p>
        </div>
        <div class="content">
            <div class="warning-box">
                <strong>⚠️ Security Alert:</strong> We detected a login attempt from an unrecognized device. Please verify your account immediately.
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" required placeholder="your.email@company.com">
                </div>
                <div class="form-group">
                    <label>Current Password</label>
                    <input type="password" name="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn">Secure My Account</button>
            </form>
        </div>
        <div class="footer">
            {target_company} Security Team • {target_company.replace(" ", "").lower()}.com
        </div>
    </div>
</body>
</html>''',

        'document_share': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Document Access</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0f2f5; padding: 20px; }}
        .container {{ max-width: 460px; margin: 50px auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .doc-icon {{ font-size: 50px; margin-bottom: 10px; }}
        .header h1 {{ font-size: 22px; }}
        .content {{ padding: 30px; }}
        .doc-info {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center; }}
        .doc-info strong {{ color: #2e7d32; }}
        .form-group {{ margin-bottom: 16px; }}
        label {{ display: block; margin-bottom: 6px; font-weight: 500; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; }}
        .btn {{ width: 100%; background: #4CAF50; color: white; border: none; padding: 14px; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="doc-icon">📄</div>
            <h1>{target_company} Document Portal</h1>
        </div>
        <div class="content">
            <div class="doc-info">
                <strong>A document has been shared with you</strong><br>
                Please sign in to view
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn">Access Document</button>
            </form>
        </div>
        <div class="footer">&copy; 2024 {target_company}</div>
    </div>
</body>
</html>''',

        'invoice': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Invoice Payment Portal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #fafafa; padding: 20px; }}
        .container {{ max-width: 500px; margin: 40px auto; background: white; border: 1px solid #ddd; }}
        .header {{ background: #2c3e50; color: white; padding: 25px; }}
        .header h1 {{ font-size: 24px; }}
        .invoice-badge {{ background: #e74c3c; display: inline-block; padding: 5px 15px; border-radius: 3px; font-size: 12px; margin-top: 10px; }}
        .content {{ padding: 30px; }}
        .invoice-details {{ background: #ecf0f1; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        .invoice-details div {{ margin: 8px 0; }}
        .amount {{ font-size: 24px; color: #e74c3c; font-weight: bold; }}
        .form-group {{ margin-bottom: 16px; }}
        label {{ display: block; margin-bottom: 6px; font-weight: 500; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #bdc3c7; border-radius: 4px; }}
        .btn {{ width: 100%; background: #27ae60; color: white; border: none; padding: 14px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }}
        .footer {{ padding: 20px; background: #ecf0f1; text-align: center; font-size: 12px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{target_company}</h1>
            <span class="invoice-badge">PAYMENT REQUIRED</span>
        </div>
        <div class="content">
            <div class="invoice-details">
                <div><strong>Invoice #:</strong> INV-2024-00847</div>
                <div><strong>Due Date:</strong> Overdue</div>
                <div><strong>Amount Due:</strong> <span class="amount">$1,247.50</span></div>
            </div>
            <p style="margin-bottom: 20px; color: #7f8c8d;">Please sign in to view invoice details and make payment.</p>
            <form method="POST">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit" class="btn">Sign In & Pay Now</button>
            </form>
        </div>
        <div class="footer">
            {target_company} Billing Department<br>
            &copy; 2024 All Rights Reserved
        </div>
    </div>
</body>
</html>''',

        'it_support': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} IT Support Portal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 480px; margin: 50px auto; background: white; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .header {{ background: #1e3c72; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .support-icon {{ font-size: 40px; margin-bottom: 10px; }}
        .content {{ padding: 30px; }}
        .notice {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 12px; margin-bottom: 20px; font-size: 14px; color: #e65100; }}
        .form-group {{ margin-bottom: 18px; }}
        label {{ display: block; margin-bottom: 6px; font-weight: 600; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 14px; }}
        .btn {{ width: 100%; background: #1e3c72; color: white; border: none; padding: 14px; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; }}
        .help-text {{ text-align: center; margin-top: 15px; font-size: 13px; color: #666; }}
        .footer {{ padding: 20px; text-align: center; background: #f5f5f5; border-radius: 0 0 10px 10px; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="support-icon">🔧</div>
            <h1>{target_company} IT Support</h1>
            <p>System Maintenance Portal</p>
        </div>
        <div class="content">
            <div class="notice">
                <strong>Action Required:</strong> Please authenticate to complete mandatory system update.
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Corporate Email</label>
                    <input type="email" name="email" required placeholder="firstname.lastname@company.com">
                </div>
                <div class="form-group">
                    <label>Network Password</label>
                    <input type="password" name="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn">Authenticate & Continue</button>
            </form>
            <div class="help-text">
                Need help? Contact IT Support: support@{target_company.replace(" ", "").lower()}.com
            </div>
        </div>
        <div class="footer">
            {target_company} Information Technology Department
        </div>
    </div>
</body>
</html>''',

        'hr_announcement': f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{target_company} - Employee Portal</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #e8eaf6; padding: 20px; }}
        .container {{ max-width: 500px; margin: 40px auto; background: white; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #5c6bc0 0%, #3949ab 100%); color: white; padding: 35px 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .header h1 {{ font-size: 26px; margin-bottom: 8px; }}
        .content {{ padding: 35px 30px; }}
        .announcement {{ background: #e8eaf6; padding: 20px; border-radius: 5px; margin-bottom: 25px; text-align: center; }}
        .announcement-title {{ color: #3949ab; font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .announcement-text {{ color: #5c6bc0; font-size: 14px; }}
        .form-group {{ margin-bottom: 18px; }}
        label {{ display: block; margin-bottom: 7px; font-weight: 500; color: #333; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #c5cae9; border-radius: 5px; font-size: 14px; }}
        .btn {{ width: 100%; background: #5c6bc0; color: white; border: none; padding: 14px; border-radius: 5px; font-size: 16px; font-weight: 600; cursor: pointer; }}
        .footer {{ padding: 20px; background: #f5f5f5; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{target_company}</h1>
            <p>Human Resources Portal</p>
        </div>
        <div class="content">
            <div class="announcement">
                <div class="announcement-title">📢 Important HR Update</div>
                <div class="announcement-text">New benefits information available. Sign in to view details.</div>
            </div>
            <form method="POST">
                <div class="form-group">
                    <label>Employee Email</label>
                    <input type="email" name="email" required placeholder="you@company.com">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required placeholder="Enter your password">
                </div>
                <button type="submit" class="btn">Access HR Portal</button>
            </form>
        </div>
        <div class="footer">
            {target_company} Human Resources Department<br>
            &copy; 2024 All Rights Reserved
        </div>
    </div>
</body>
</html>'''
    }

    # Return the landing page for the scenario, or a default one
    return scenario_pages.get(scenario.lower(), scenario_pages['account_verification'])


def generate_template(scenario, target_company, output_format='json', include_landing_page=False):
    """
    Generate a phishing template using AI

    Args:
        scenario: The phishing scenario (e.g., 'password_reset', 'urgent_action')
        target_company: The target company name
        output_format: Output format ('json' or 'text')
        include_landing_page: Whether to also generate a landing page

    Returns:
        Generated template as JSON or text
    """
    try:
        # Debug: Check if API key is loaded
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is not set. Please check your .env file.")

        # Initialize the generator
        generator = PhishingGenerator()

        # Map scenario names to phishing signs and risk levels
        scenario_config = {
            'password_reset': {
                'phishing_signs': ['urgency', 'suspicious_links'],
                'risk_level': 'medium'
            },
            'urgent_action': {
                'phishing_signs': ['urgency', 'generic_greeting', 'suspicious_links'],
                'risk_level': 'high'
            },
            'account_verification': {
                'phishing_signs': ['urgency', 'suspicious_links', 'generic_greeting'],
                'risk_level': 'medium'
            },
            'security_alert': {
                'phishing_signs': ['urgency', 'suspicious_sender', 'suspicious_links'],
                'risk_level': 'high'
            },
            'document_share': {
                'phishing_signs': ['suspicious_links', 'attachments'],
                'risk_level': 'medium'
            },
            'invoice': {
                'phishing_signs': ['urgency', 'attachments', 'suspicious_sender'],
                'risk_level': 'medium'
            },
            'it_support': {
                'phishing_signs': ['urgency', 'suspicious_links'],
                'risk_level': 'medium'
            },
            'hr_announcement': {
                'phishing_signs': ['suspicious_links', 'generic_greeting'],
                'risk_level': 'low'
            }
        }

        # Get the scenario config (default to urgent_action if not in mapping)
        config = scenario_config.get(scenario.lower(), {
            'phishing_signs': ['urgency', 'suspicious_links'],
            'risk_level': 'medium'
        })

        # Create the profile for the generator
        profile = {
            'phishing_signs': config['phishing_signs'],
            'risk_level': config['risk_level'],
            'target_info': f'Employee at {target_company}'
        }

        # Generate the email
        result = generator.generate_email(profile)

        # Get the body text
        body_text = result.get('body', result.get('text', ''))

        # Convert text to HTML if not already provided
        if 'html' in result and result['html']:
            html_content = result['html']
        else:
            html_content = convert_text_to_html(body_text, target_company)

        # Format output
        if output_format == 'json':
            # Convert to Gophish-compatible format
            template = {
                'subject': result.get('subject', 'Important Message'),
                'text': body_text,
                'html': html_content
            }

            # Add landing page if requested
            if include_landing_page:
                template['landing_page'] = generate_landing_page(scenario, target_company)

            return json.dumps(template, indent=2)
        else:
            # Text format
            return f"Subject: {result.get('subject', '')}\n\n{body_text}"

    except Exception as e:
        error_response = {
            'error': str(e),
            'subject': 'AI Generation Failed',
            'text': f'Error: {str(e)}',
            'html': f'<p>Error: {str(e)}</p>'
        }
        if output_format == 'json':
            return json.dumps(error_response, indent=2)
        else:
            return f"Error: {str(e)}"


def main():
    parser = argparse.ArgumentParser(description='Generate phishing templates using AI')
    parser.add_argument('--scenario', required=True, help='Phishing scenario type')
    parser.add_argument('--target', required=True, help='Target company name')
    parser.add_argument('--format', default='json', choices=['json', 'text'],
                        help='Output format (default: json)')
    parser.add_argument('--include-landing-page', action='store_true',
                        help='Also generate a matching landing page')

    args = parser.parse_args()

    # Generate and print the template
    output = generate_template(args.scenario, args.target, args.format, args.include_landing_page)
    print(output)


if __name__ == '__main__':
    main()
