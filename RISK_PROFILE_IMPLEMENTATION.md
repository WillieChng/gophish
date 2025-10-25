# Risk Profile System - Implementation Status

## Overview

Implementing a comprehensive risk profiling system for user groups and AI template generation. The system allows users to configure difficulty levels (Low, Medium, High) for 6 phishing signs, displayed with color-coded buttons (Green, Yellow, Red).

## 6 Phishing Signs

1. **Urgency** - How urgently the email demands action
2. **Suspicious Links** - How obvious/suspicious the links appear
3. **Generic Greeting** - How personalized vs generic the greeting is
4. **Suspicious Sender** - How suspicious the sender email appears
5. **Attachments** - How suspicious attachments appear
6. **Spelling Errors** - How obvious spelling/grammar errors are

## Risk Levels

- **Low** (Green button) - Easy to detect, obvious phishing signs
- **Medium** (Yellow button) - Moderate difficulty, some subtle signs
- **High** (Red button) - Very sophisticated, hard to detect

## Completed Tasks ✅

### 1. Database Schema
- **Files Created**:
  - `db/db_sqlite3/migrations/20241024000000_add_risk_profiles.sql`
  - `db/db_mysql/migrations/20241024000000_add_risk_profiles.sql`
- **Changes**: Added 6 risk profile columns to `groups` table with default 'medium' values

### 2. Go Model Updates
- **File Modified**: `models/group.go`
- **Changes**: Added 6 risk profile fields to Group struct:
  ```go
  RiskUrgency            string `json:"risk_urgency"`
  RiskSuspiciousLinks    string `json:"risk_suspicious_links"`
  RiskGenericGreeting    string `json:"risk_generic_greeting"`
  RiskSuspiciousSender   string `json:"risk_suspicious_sender"`
  RiskAttachments        string `json:"risk_attachments"`
  RiskSpellingErrors     string `json:"risk_spelling_errors"`
  ```

### 3. Groups UI
- **File Modified**: `templates/groups.html`
- **Changes**:
  - Added Risk Profile Configuration panel with 6 phishing signs
  - Each sign has 3 color-coded buttons (Green/Yellow/Red for Low/Medium/High)
  - Added tooltips explaining the system
  - Used Font Awesome icons for each phishing sign

### 4. Groups JavaScript
- **File Modified**: `static/js/src/app/groups.js`
- **Changes**:
  - Updated `save()` function to capture risk profile values
  - Added `resetRiskButtons()` function to set defaults
  - Added `setRiskButton()` function to load existing values
  - Added click handler for risk buttons
  - Risk values are saved/loaded when editing groups

### 5. AI Template Modal UI
- **File Modified**: `templates/templates.html`
- **Changes**:
  - Added Risk Level Configuration section to AI generation modal
  - 6 phishing signs with Low/Medium/High buttons
  - Smaller buttons (btn-group-sm) to fit in modal
  - Color-coded: Green (Low), Yellow (Medium), Red (High)
  - All default to Medium

## Remaining Tasks 🚧

### 6. Update AI Template JavaScript ⏳
- **File to Modify**: `static/js/src/app/templates.js`
- **Required Changes**:
  ```javascript
  // In generateAITemplate():
  // 1. Read risk values from buttons
  var riskProfile = {
      urgency: $('.ai-risk-btn[data-risk="urgency"].active').data('value'),
      suspicious_links: $('.ai-risk-btn[data-risk="suspicious_links"].active').data('value'),
      // ... etc for all 6 signs
  }

  // 2. Pass to API
  api.templates.generate_ai({
      scenario: scenario,
      target_company: targetCompany,
      include_landing_page: includeLandingPage,
      phishing_signs: riskProfile
  })

  // 3. Add button click handler
  $(document).on('click', '.ai-risk-btn', function() {
      var riskType = $(this).data('risk')
      $('.ai-risk-btn[data-risk="' + riskType + '"]').removeClass('active')
      $(this).addClass('active')
  })
  ```

### 7. Update Go API ⏳
- **File to Modify**: `controllers/api/ai_template.go`
- **Required Changes**:
  ```go
  // Update AITemplateRequest struct
  type AITemplateRequest struct {
      Scenario           string            `json:"scenario"`
      TargetCompany      string            `json:"target_company"`
      IncludeLandingPage bool              `json:"include_landing_page"`
      PhishingSigns      map[string]string `json:"phishing_signs"` // NEW
  }

  // Update generateTemplateWithAI() to pass phishing_signs as JSON
  args := []string{
      "ai_module/generate_phishing.py",
      "--scenario", scenario,
      "--target", targetCompany,
      "--format", "json",
  }

  if len(phishingSigns) > 0 {
      signsJSON, _ := json.Marshal(phishingSigns)
      args = append(args, "--phishing-signs", string(signsJSON))
  }
  ```

### 8. Update Python Module ⏳
- **File to Modify**: `ai_module/generate_phishing.py`
- **Required Changes**:
  ```python
  # Add argument parser support
  parser.add_argument('--phishing-signs', type=str,
                      help='JSON string of phishing signs with difficulty levels')

  # In generate_template():
  if args.phishing_signs:
      signs_dict = json.loads(args.phishing_signs)
      profile = {
          'phishing_signs': signs_dict,  # Now a dict instead of list
          'risk_level': determine_overall_risk(signs_dict),
          'target_info': f'Employee at {target_company}'
      }
  else:
      # Use default scenario-based config
      profile = {
          'phishing_signs': config['phishing_signs'],
          'risk_level': config['risk_level'],
          'target_info': f'Employee at {target_company}'
      }
  ```

### 9. Build and Test ⏳
- **Commands**:
  ```bash
  # Build JavaScript
  npx gulp scripts

  # Build Go
  go build

  # Run database migration (if needed)
  # The migrations will run automatically on next startup

  # Test Group Creation with Risk Profile
  # - Create a group with custom risk levels
  # - Verify risk values are saved
  # - Edit group and verify values load correctly

  # Test AI Template Generation with Risk Levels
  # - Generate template with different risk combinations
  # - Verify Python receives correct parameters
  # - Verify generated content matches risk levels
  ```

## Testing Checklist

### Groups Risk Profile
- [ ] Create new group with default risk levels (all medium)
- [ ] Create group with custom risk levels
- [ ] Edit existing group and change risk levels
- [ ] Verify risk buttons show correct active state when editing
- [ ] Verify risk values are saved to database
- [ ] Check button colors (green/yellow/red) display correctly

### AI Template Generation
- [ ] Open AI generation modal
- [ ] Verify risk buttons default to medium (yellow)
- [ ] Click different risk levels, verify active state changes
- [ ] Generate template with all low risk
- [ ] Generate template with all high risk
- [ ] Generate template with mixed risk levels
- [ ] Verify generated content matches selected risk levels

### Integration
- [ ] Select a group with specific risk profile
- [ ] When creating campaign, AI should use group's risk profile (future feature)
- [ ] Risk levels should affect email sophistication appropriately

## File Structure

```
gophish/
├── db/
│   ├── db_sqlite3/migrations/
│   │   └── 20241024000000_add_risk_profiles.sql ✅
│   └── db_mysql/migrations/
│       └── 20241024000000_add_risk_profiles.sql ✅
├── models/
│   └── group.go ✅
├── controllers/api/
│   └── ai_template.go ⏳ (needs update)
├── ai_module/
│   └── generate_phishing.py ⏳ (needs update)
├── templates/
│   ├── groups.html ✅
│   └── templates.html ✅
└── static/js/src/app/
    ├── groups.js ✅
    └── templates.js ⏳ (needs update)
```

## UI Screenshots (Conceptual)

### Groups Modal - Risk Profile Section
```
┌─────────────────────────────────────────────┐
│ Risk Profile Configuration                   │
├─────────────────────────────────────────────┤
│ Urgency                 Suspicious Links     │
│ [Low][Medium][High]    [Low][Medium][High]  │
│  🟢   🟡     🔴         🟢   🟡     🔴      │
│                                              │
│ Generic Greeting        Suspicious Sender    │
│ [Low][Medium][High]    [Low][Medium][High]  │
│  🟢   🟡     🔴         🟢   🟡     🔴      │
│                                              │
│ Attachments             Spelling Errors      │
│ [Low][Medium][High]    [Low][Medium][High]  │
│  🟢   🟡     🔴         🟢   🟡     🔴      │
└─────────────────────────────────────────────┘
```

### AI Template Modal - Risk Configuration
```
┌─────────────────────────────────────────────┐
│ Generate AI Template                         │
├─────────────────────────────────────────────┤
│ Scenario: [Password Reset ▼]                │
│ Company:  [Acme Corp         ]               │
│ ☑ Create matching landing page              │
│ ───────────────────────────────────────────  │
│ Risk Level Configuration                     │
│                                              │
│ Urgency              Suspicious Links        │
│ [L][M][H]           [L][M][H]               │
│                                              │
│ Generic Greeting     Suspicious Sender       │
│ [L][M][H]           [L][M][H]               │
│                                              │
│ Attachments          Spelling Errors         │
│ [L][M][H]           [L][M][H]               │
│                                              │
│           [Cancel]  [Generate Template]      │
└─────────────────────────────────────────────┘
```

## API Changes

### Request Format (NEW)
```json
POST /api/templates/generate_ai
{
  "scenario": "password_reset",
  "target_company": "Acme Corp",
  "include_landing_page": true,
  "phishing_signs": {
    "urgency": "high",
    "suspicious_links": "medium",
    "generic_greeting": "low",
    "suspicious_sender": "high",
    "attachments": "medium",
    "spelling_errors": "low"
  }
}
```

### Response Format (unchanged)
```json
{
  "subject": "...",
  "text": "...",
  "html": "...",
  "landing_page": "..." // if requested
}
```

## Next Steps

1. **Complete JavaScript Updates** (30 min)
   - Update templates.js to handle risk buttons
   - Pass risk profile to API

2. **Complete Go API Updates** (20 min)
   - Add PhishingSigns field to request struct
   - Pass to Python module

3. **Complete Python Module Updates** (40 min)
   - Accept --phishing-signs argument
   - Parse JSON and use in profile
   - Handle both dict and list formats for backward compatibility

4. **Build and Test** (30 min)
   - Compile JavaScript and Go
   - Test group creation/editing
   - Test AI generation with various risk levels

5. **Documentation** (20 min)
   - Update user guide
   - Add examples
   - Create tutorial

## Total Estimated Time Remaining: ~2.5 hours

## Benefits

### For Users
- **Granular Control**: Set specific difficulty for each phishing sign
- **Group-Based**: Save risk profiles per group for consistency
- **Visual Feedback**: Color-coded buttons (green/yellow/red) for easy understanding
- **Flexible Training**: Can create easy, medium, or hard templates on demand

### For Training Programs
- **Progressive Difficulty**: Start with low risk, increase over time
- **Targeted Training**: Focus on specific phishing indicators
- **Group Segmentation**: Different risk levels for different departments
- **Realistic Scenarios**: High-risk templates for executive training

## Implementation Notes

- Risk buttons use Bootstrap's `btn-group-justified` for consistent width
- Active state managed via `.active` class
- Default to "medium" for all signs
- Risk values stored as strings: "low", "medium", "high"
- Color scheme: Green (#5cb85c), Yellow (#f0ad4e), Red (#d9534f)

---

**Status**: ~60% Complete
**Next Priority**: Complete JavaScript, Go, and Python updates
**Target Completion**: Next session
