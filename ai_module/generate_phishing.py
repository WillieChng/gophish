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


def generate_template(scenario, target_company, output_format='json'):
    """
    Generate a phishing template using AI

    Args:
        scenario: The phishing scenario (e.g., 'password_reset', 'urgent_action')
        target_company: The target company name
        output_format: Output format ('json' or 'text')

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

    args = parser.parse_args()

    # Generate and print the template
    output = generate_template(args.scenario, args.target, args.format)
    print(output)


if __name__ == '__main__':
    main()
