# LLM Testing Interface - Debugging Plan

## Overview
Comprehensive step-by-step debugging strategy for the LLM Testing Interface with 10 specialized tabs.

## Phase 1: Environment Validation

### Server Health Check
1. Verify FastAPI server is running on port 8000
2. Check LM Studio connection at http://127.0.0.1:1234/v1
3. Validate all JSON data files exist in `app/data/`
4. Test API endpoints with simple requests
5. Verify Python virtual environment is activated

### Data Integrity Check
1. Validate JSON syntax in all data files
2. Check file permissions (read/write)
3. Verify data structure matches schemas
4. Test data persistence on write operations
5. Backup existing data before debugging

## Phase 2: Frontend Debugging

### Browser Environment
1. Open DevTools (F12) - Console, Network, and Sources tabs
2. Check for JavaScript errors on page load
3. Verify all static assets loaded (CSS, JS)
4. Test localStorage/sessionStorage
5. Clear cache and test fresh load

### UI Component Testing
1. Verify all tabs are clickable and switch correctly
2. Check form inputs accept and validate data
3. Test button click events fire correctly
4. Verify modal dialogs open/close
5. Check responsive layout at different sizes

## Phase 3: Tab-Specific Debugging

### Playground Tab Priority Issues
**Critical Path:**
1. Model selection → dropdown populated
2. Message input → textarea accepts input
3. Send button → message sent to backend
4. Response → message displayed in chat
5. Streaming → SSE events received

**Debug Steps:**
- Console log `chatHistory` array
- Monitor `/api/chat` in Network tab
- Verify `isGenerating` flag toggles correctly
- Check `renderChatMessages()` executes
- Test both streaming and non-streaming modes

### Prompt Builder Tab Priority Issues
**Critical Path:**
1. Template list → loads from `/api/prompt-templates`
2. Create template → form submission works
3. Variable substitution → `{{var}}` replaced correctly
4. Preview → shows final prompt
5. Apply → transfers to Playground

**Debug Steps:**
- Check `prompt_templates.json` structure
- Verify `renderPromptTemplatesTable()` renders
- Test `updatePromptTemplatePreview()` function
- Monitor template CRUD operations
- Validate preset templates load

### A/B Tester Tab Priority Issues
**Critical Path:**
1. Variant selection → models/agents listed
2. Add variant → appears in variants list
3. Run test → parallel execution completes
4. Results → all variants show responses
5. Comparison → latency visible

**Debug Steps:**
- Log `abVariants` array
- Check `/api/ab-test` POST payload
- Verify parallel Promise.all execution
- Monitor response timing
- Test error handling per variant

### Evaluation Tab Priority Issues
**Critical Path:**
1. Dataset creation → JSONL parsed correctly
2. Template loading → presets available
3. Bulk generation → SSE streaming works
4. Evaluator setup → built-in + custom loaded
5. Job execution → results calculated

**Debug Steps:**
- Validate JSONL format (one JSON per line)
- Check `datasets.json` structure
- Monitor `/api/datasets/{id}/bulk-run-stream`
- Test SSE event parsing
- Verify evaluator execution

### Orchestrator Tab Priority Issues
**Critical Path:**
1. Canvas rendering → SVG and nodes visible
2. Node creation → types render correctly
3. Edge connections → source to target
4. Node configuration → forms populate
5. Workflow execution → steps complete

**Debug Steps:**
- Log `workflowNodes` and `workflowEdges`
- Check SVG rendering in canvas
- Test drag-and-drop functionality
- Verify node editor shows/hides
- Monitor workflow execution streaming

### Chat Lab Tab Priority Issues
**Critical Path:**
1. Tree creation → conversation started
2. Message sending → LLM responds
3. Tree visualization → hierarchy displayed
4. Branching → new paths created
5. Navigation → switch between branches

**Debug Steps:**
- Check `currentChatTreeId`
- Log tree structure from API
- Verify message rendering
- Test branch creation flow
- Monitor active path tracking

### Guardrails Tab Priority Issues
**Critical Path:**
1. Rule creation → types configured
2. Rule toggling → enabled/disabled works
3. Test cases → expectations defined
4. Real-time check → flags detected
5. Test suite → pass/fail calculated

**Debug Steps:**
- Verify `guardrails.json` structure
- Test `/api/guardrails/check` endpoint
- Check rule configuration JSON validity
- Monitor test execution results
- Validate match detection

### History Tab Priority Issues
**Critical Path:**
1. Entry logging → requests saved
2. List display → entries rendered
3. Filtering → queries work
4. Detail view → full entry shown
5. Replay → request re-executed

**Debug Steps:**
- Check if logging middleware active
- Verify `metrics.json` writes
- Test filter combinations
- Monitor replay endpoint
- Check pagination logic

### Dashboard Tab Priority Issues
**Critical Path:**
1. Stats loading → summary displayed
2. Time range → filters data correctly
3. Charts rendering → bars visible
4. Breakdowns → tables populated
5. Recent requests → latest shown

**Debug Steps:**
- Test `/api/metrics/summary` endpoint
- Verify hourly data aggregation
- Check chart container rendering
- Monitor auto-refresh if enabled
- Validate time range calculations

### Tools Tab Priority Issues
**Critical Path:**
1. Tools list → loaded from storage
2. Form input → schema validated
3. Save → persists to `tools.json`
4. Toggle → enabled status changes
5. Association → models/agents linked

**Debug Steps:**
- Check `tools.json` structure
- Validate input schema JSON
- Test CRUD operations
- Verify toggle endpoint
- Monitor tool associations

## Phase 4: Backend API Testing

### API Endpoint Validation
For each endpoint:
1. Test with valid payload → expect 200
2. Test with invalid payload → expect 400
3. Test with missing data → expect 404
4. Test with malformed JSON → expect 422
5. Test error handling → expect descriptive errors

### Key Endpoints to Test
```powershell
# Playground
GET /api/models
POST /api/chat
POST /api/prompt-generator

# Prompt Builder
GET /api/prompt-templates
POST /api/prompt-templates
PUT /api/prompt-templates/{id}

# A/B Tester
POST /api/ab-test

# Evaluation
GET /api/datasets
POST /api/datasets/{id}/bulk-run-stream
GET /api/evaluators
POST /api/eval-jobs/{id}/run

# Orchestrator
GET /api/workflows
POST /api/workflows/{id}/run

# Chat Lab
GET /api/chat-lab/trees
POST /api/chat-lab/trees/{id}/messages

# Guardrails
POST /api/guardrails/check
POST /api/guardrails/run-tests

# History
GET /api/history
POST /api/history/replay

# Dashboard
GET /api/metrics/summary
GET /api/metrics/hourly

# Tools
GET /api/tools
POST /api/tools
```

## Phase 5: Common Issues Resolution

### Issue: Network Errors
**Symptoms:** "Failed to fetch", CORS errors, 404s
**Checks:**
1. Server running on correct port
2. CORS headers configured
3. Routes registered in main.py
4. API paths match frontend calls
5. Firewall not blocking requests

**Solutions:**
- Restart server
- Check router registration
- Verify URL construction
- Test with curl/Postman first

### Issue: Data Not Persisting
**Symptoms:** Changes lost on refresh, empty lists
**Checks:**
1. JSON files writable
2. Store methods called correctly
3. File paths correct
4. Disk space available
5. Encoding issues (UTF-8)

**Solutions:**
- Check file permissions
- Verify store base class methods
- Test write operations directly
- Check for concurrent write conflicts

### Issue: UI Not Updating
**Symptoms:** Stale data, no re-render
**Checks:**
1. Render functions called after data change
2. Event listeners attached
3. DOM elements exist
4. State variables updated
5. No JavaScript errors blocking execution

**Solutions:**
- Add explicit render calls
- Re-attach event listeners
- Check element IDs match
- Use debugger to step through

### Issue: Streaming Not Working
**Symptoms:** No progress updates, frozen UI
**Checks:**
1. SSE endpoint returns correct headers
2. EventSource connected successfully
3. Data format matches "data: {json}\n\n"
4. Buffer handling correct
5. LM Studio supports streaming

**Solutions:**
- Toggle streaming mode
- Check Content-Type: text/event-stream
- Verify line breaks in SSE format
- Test non-streaming first

### Issue: Performance Degradation
**Symptoms:** Slow responses, browser lag
**Checks:**
1. Large datasets slowing operations
2. Memory leaks in frontend
3. LM Studio model size
4. Too many metrics stored
5. Inefficient queries

**Solutions:**
- Implement pagination
- Clear old data
- Use smaller models
- Add data limits
- Optimize queries

## Phase 6: Testing Protocol

### Unit Testing (Per Function)
1. Identify function inputs/outputs
2. Test with valid data
3. Test with edge cases
4. Test with invalid data
5. Verify error handling

### Integration Testing (Per Tab)
1. Test full user workflow
2. Verify data flows between components
3. Check API → Store → UI chain
4. Test error scenarios
5. Verify state management

### End-to-End Testing (Across Tabs)
1. Create workflow spanning multiple tabs
2. Test data sharing between tabs
3. Verify consistency across features
4. Check navigation works
5. Test complete use case

## Phase 7: Logging and Monitoring

### Frontend Logging
```javascript
// Add to main.js
const DEBUG = true;

function log(component, action, data) {
  if (DEBUG) {
    console.log(`[${component}] ${action}:`, data);
  }
}

// Usage
log('Playground', 'sendMessage', { userMessage, attachments });
```

### Backend Logging
```python
# Add to service methods
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Processing request: {payload}")
logger.info(f"Operation completed: {result}")
logger.error(f"Error occurred: {error}")
```

### Network Monitoring
1. Keep DevTools Network tab open
2. Filter by XHR/Fetch
3. Check request/response bodies
4. Monitor timing
5. Look for failed requests

## Phase 8: Validation Checklist

### Before Deployment
- [ ] All JSON files have valid structure
- [ ] All API endpoints return expected responses
- [ ] All forms validate input correctly
- [ ] All tabs load without errors
- [ ] Error messages are user-friendly
- [ ] Loading states show appropriately
- [ ] Data persists across sessions
- [ ] Browser console has no errors
- [ ] Network requests complete successfully
- [ ] Performance is acceptable

### After Each Fix
- [ ] Test the specific feature fixed
- [ ] Test related features for regressions
- [ ] Check browser console for new errors
- [ ] Verify data integrity maintained
- [ ] Test in different browsers if possible
- [ ] Document the fix for reference

## Phase 9: Emergency Procedures

### Complete Reset
```powershell
# Backup data
cp -r app/data app/data_backup_$(Get-Date -Format "yyyyMMdd_HHmmss")

# Reset all JSON files
@('chat_lab','datasets','eval_jobs','guardrail_tests','guardrails','metrics','prompt_templates','tools') | ForEach-Object {
    echo "[]" > "app/data/$_.json"
}

# Restart server
# Stop with Ctrl+C
uvicorn app.main:app --reload --port 8000
```

### Data Recovery
```powershell
# Restore from backup
cp -r app/data_backup/* app/data/

# Verify files
ls app/data/*.json | ForEach-Object {
    Write-Host "Checking $_"
    Get-Content $_ | ConvertFrom-Json
}
```

## Phase 10: Documentation

### Record Issues Found
1. Issue description
2. Steps to reproduce
3. Expected vs actual behavior
4. Error messages
5. Solution applied
6. Prevention strategy

### Update Debug Guide
- Add new issues discovered
- Update troubleshooting steps
- Add specific error patterns
- Document workarounds
- Note version-specific issues

## Success Criteria

### Per Tab
✅ All features work as documented
✅ No console errors during normal use
✅ Data persists correctly
✅ Error handling is graceful
✅ Performance is acceptable
✅ UI updates reflect data changes

### Overall System
✅ Server starts without errors
✅ All API endpoints respond
✅ LM Studio integration works
✅ All tabs accessible and functional
✅ Data files maintain integrity
✅ Cross-tab workflows complete
✅ Documentation is accurate

## Next Steps After Debugging

1. **Optimize Performance**
   - Profile slow operations
   - Add caching where appropriate
   - Implement lazy loading
   - Optimize database queries

2. **Enhance Error Handling**
   - Add more specific error messages
   - Implement retry logic
   - Add user-friendly error displays
   - Log errors for analysis

3. **Improve Testing**
   - Add automated tests
   - Create test fixtures
   - Implement CI/CD
   - Add integration tests

4. **User Experience**
   - Add loading indicators
   - Improve visual feedback
   - Add keyboard shortcuts
   - Enhance accessibility

5. **Documentation**
   - Add inline code comments
   - Update API documentation
   - Create user guide
   - Record video tutorials
