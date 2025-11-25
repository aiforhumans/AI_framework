# Guardrails Tab

## Overview
Safety testing and content moderation system with rule-based checking.

## Features

### Rule Management
- Create/edit/delete rules
- Enable/disable toggle
- Rule types:
  - **PII** - Personal information detection
  - **Keyword** - Blocked word lists
  - **Regex** - Pattern matching
  - **Content** - Content policy checks
  - **LLM** - AI-powered safety checks

### Rule Configuration
- JSON-based config
- Rule name and description
- Type selection
- Custom parameters per type

### Test Case Management
- Create test cases
- Expected outcomes (blocked/passed)
- Expected flags
- Test tags
- Test descriptions

### Real-time Checking
- Check text against active rules
- Flag severity indicators
- Execution time tracking
- Match highlighting
- Passed rules summary
- Status badges (Blocked/Flagged/Passed)

### Test Suite Execution
- Run all tests
- Pass/fail rate calculation
- Block match validation
- Flag match validation
- Detailed test results

### Results Display
- Visual status indicators
- Rule type badges
- Match details
- Execution metrics

## API Endpoints
- `GET /api/guardrails/rules` - List rules
- `POST /api/guardrails/rules` - Create rule
- `GET /api/guardrails/rules/{id}` - Get rule
- `PUT /api/guardrails/rules/{id}` - Update rule
- `DELETE /api/guardrails/rules/{id}` - Delete rule
- `POST /api/guardrails/rules/{id}/toggle` - Toggle rule
- `GET /api/guardrails/tests` - List tests
- `POST /api/guardrails/tests` - Create test
- `PUT /api/guardrails/tests/{id}` - Update test
- `DELETE /api/guardrails/tests/{id}` - Delete test
- `POST /api/guardrails/check` - Check text
- `POST /api/guardrails/run-tests` - Run test suite
