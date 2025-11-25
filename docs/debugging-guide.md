# Step-by-Step Debugging Guide

## Pre-Debugging Checklist

### 1. Check Server Status
```powershell
# Check if server is running
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Check port 8000
netstat -ano | findstr :8000
```

### 2. Verify LM Studio
```powershell
# Check if LM Studio is running on port 1234
Invoke-WebRequest -Uri "http://127.0.0.1:1234/v1/models" -Method GET
```

### 3. Check Data Directory
```powershell
# Verify all JSON files exist
ls F:\AI_framework\app\data\*.json
```

Expected files:
- `chat_lab.json`
- `datasets.json`
- `eval_jobs.json`
- `guardrail_tests.json`
- `guardrails.json`
- `metrics.json`
- `prompt_templates.json`
- `tools.json`

---

## Tab-by-Tab Debugging

## 1. Playground Tab

### Issue: Chat messages not appearing

**Step 1:** Open browser console (F12)
```javascript
// Check if chatHistory is being updated
console.log("chatHistory:", chatHistory);
```

**Step 2:** Check if sendMessage is being called
```javascript
// Add breakpoint in main.js line ~350
console.log("sendMessage called", { userMessage, attachments });
```

**Step 3:** Verify API response
```javascript
// Check network tab for /api/chat request
// Look for response status and data
```

**Step 4:** Check renderChatMessages
```javascript
// Verify container exists
console.log("Container:", document.getElementById("chat-messages"));
```

**Fix Options:**
- Clear browser cache
- Check if `isGenerating` is stuck true
- Verify model selection dropdown has value
- Check FastAPI logs for errors

### Issue: Streaming not working

**Step 1:** Check stream mode toggle
```javascript
console.log("Stream mode:", document.getElementById("stream-mode").checked);
```

**Step 2:** Verify SSE connection
```javascript
// In browser console during streaming:
// Network tab → filter by "chat" → check for SSE events
```

**Step 3:** Check backend streaming
```bash
# In terminal, watch for streaming output
# Should see "data: {..." lines
```

**Fix Options:**
- Toggle stream mode off and on
- Check CORS headers in FastAPI
- Verify LM Studio supports streaming

### Issue: Prompt generator not working

**Step 1:** Check modal visibility
```javascript
console.log(document.getElementById("prompt-generator-modal").style.display);
```

**Step 2:** Verify API endpoint
```powershell
# Test endpoint directly
Invoke-WebRequest -Uri "http://localhost:8000/api/prompt-generator" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"input":"test prompt"}'
```

**Step 3:** Check model availability
```javascript
// Ensure a model is selected in Playground
console.log(document.getElementById("model-select").value);
```

---

## 2. Prompt Builder Tab

### Issue: Templates not loading

**Step 1:** Check JSON file
```powershell
# View prompt_templates.json
cat F:\AI_framework\app\data\prompt_templates.json
```

**Step 2:** Verify API response
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/prompt-templates" -Method GET
```

**Step 3:** Check frontend rendering
```javascript
// In console
refreshPromptTemplatesUI();
```

**Fix Options:**
- Regenerate empty JSON: `echo "[]" > app/data/prompt_templates.json`
- Check file permissions
- Restart server

### Issue: Variable substitution not working

**Step 1:** Check template syntax
```javascript
// Variables must use {{variable}} format
console.log(document.getElementById("prompt-template-user").value);
```

**Step 2:** Verify JSON input
```javascript
// Check if JSON is valid
let vars = JSON.parse(document.getElementById("prompt-template-vars-json").value);
console.log(vars);
```

**Step 3:** Test preview update
```javascript
updatePromptTemplatePreview();
```

**Fix Options:**
- Use correct `{{variable}}` syntax (double braces)
- Ensure variable names match exactly
- Check for JSON syntax errors

### Issue: Preset templates not showing

**Step 1:** Check category filter
```javascript
console.log(document.getElementById("template-category-filter").value);
```

**Step 2:** Verify preset data in code
```javascript
// Check if DATASET_TEMPLATES is defined in main.js
// Search for "DATASET_TEMPLATES" in file
```

**Step 3:** Check grid rendering
```javascript
renderPresetTemplatesGrid(templates);
```

---

## 3. A/B Tester Tab

### Issue: Variants not being added

**Step 1:** Check variant array
```javascript
console.log("abVariants:", abVariants);
```

**Step 2:** Verify select value
```javascript
console.log(document.getElementById("ab-add-variant-select").value);
```

**Step 3:** Check event listener
```javascript
// Ensure onABAddVariant is called
document.getElementById("ab-add-variant-select").onchange();
```

**Fix Options:**
- Refresh models/agents list
- Check if models are loaded
- Verify agent definitions

### Issue: Parallel execution failing

**Step 1:** Check payload structure
```javascript
// In runABTest function
console.log("Payload:", payload);
```

**Step 2:** Verify backend execution
```bash
# Check FastAPI logs for errors
# Look for /api/ab-test POST request
```

**Step 3:** Test single variant
```javascript
// Try with just one variant to isolate issue
```

**Fix Options:**
- Check if all models are available
- Verify system prompt is valid
- Test each model individually first

---

## 4. Evaluation Tab

### Issue: Dataset not saving

**Step 1:** Check JSONL format
```javascript
// Each line must be valid JSON
let rows = document.getElementById("dataset-rows").value;
console.log("Testing JSONL:", rows.split("\n").map(l => JSON.parse(l)));
```

**Step 2:** Verify API call
```powershell
# Test create endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/datasets" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Test","description":"Test","rows":[{"query":"test","ground_truth":"test"}]}'
```

**Step 3:** Check datasets.json
```powershell
cat F:\AI_framework\app\data\datasets.json
```

**Fix Options:**
- Validate JSONL syntax (one JSON object per line)
- Check for special characters
- Ensure each row has required fields

### Issue: Bulk generation stuck

**Step 1:** Check SSE connection
```javascript
// Network tab → Look for bulk-run-stream
// Should show "EventStream" type
```

**Step 2:** Monitor backend
```bash
# Watch terminal for progress
# Should see processing messages
```

**Step 3:** Check dataset ID
```javascript
console.log(document.getElementById("dataset-id").value);
```

**Fix Options:**
- Save dataset before running bulk
- Check model/agent selection
- Verify dataset has rows
- Check LM Studio connection

### Issue: Evaluators not running

**Step 1:** Check evaluator selection
```javascript
let selected = Array.from(document.getElementById("eval-job-evaluators").selectedOptions);
console.log("Selected evaluators:", selected.map(o => o.value));
```

**Step 2:** Verify dataset has responses
```javascript
// Dataset rows must have 'response' field populated
```

**Step 3:** Test evaluator individually
```powershell
# Test specific evaluator
Invoke-WebRequest -Uri "http://localhost:8000/api/evaluators" -Method GET
```

**Fix Options:**
- Run bulk generation first
- Select at least one evaluator
- Check custom evaluator code for errors

---

## 5. Orchestrator Tab

### Issue: Nodes not appearing

**Step 1:** Check workflowNodes array
```javascript
console.log("workflowNodes:", workflowNodes);
```

**Step 2:** Verify canvas element
```javascript
console.log(document.getElementById("workflow-canvas"));
```

**Step 3:** Check rendering
```javascript
renderWorkflowCanvas();
```

**Fix Options:**
- Click node add buttons to add nodes
- Check if canvas CSS is loaded
- Verify no JavaScript errors

### Issue: Edges not connecting

**Step 1:** Check selectedNodeId
```javascript
console.log("Selected node:", selectedNodeId);
```

**Step 2:** Verify target selection
```javascript
console.log(document.getElementById("node-connect-target").value);
```

**Step 3:** Check workflowEdges array
```javascript
console.log("workflowEdges:", workflowEdges);
```

**Fix Options:**
- Select source node first
- Choose target from dropdown
- Check for duplicate edges

### Issue: Workflow execution failing

**Step 1:** Check workflow structure
```javascript
// Must have at least one node
console.log("Nodes:", workflowNodes.length);
```

**Step 2:** Verify workflow ID
```javascript
console.log(document.getElementById("workflow-id").value);
```

**Step 3:** Check input JSON
```javascript
let input = JSON.parse(document.getElementById("workflow-run-input").value);
console.log("Input:", input);
```

**Fix Options:**
- Save workflow before running
- Check node configurations
- Verify input JSON is valid
- Check agent/tool configurations

---

## 6. Chat Lab Tab

### Issue: Tree not loading

**Step 1:** Check currentChatTreeId
```javascript
console.log("Current tree ID:", currentChatTreeId);
```

**Step 2:** Verify tree exists
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/chat-lab/trees" -Method GET
```

**Step 3:** Check tree structure API
```javascript
// Test structure endpoint
fetch(`/api/chat-lab/trees/${treeId}/structure`).then(r => r.json()).then(console.log);
```

**Fix Options:**
- Create a new tree first
- Check chat_lab.json file
- Verify tree ID is valid

### Issue: Messages not sending

**Step 1:** Check tree selection
```javascript
if (!currentChatTreeId) {
  console.error("No tree selected!");
}
```

**Step 2:** Verify input value
```javascript
console.log(document.getElementById("chat-lab-input").value);
```

**Step 3:** Check send button state
```javascript
console.log(document.getElementById("chat-lab-send-btn").disabled);
```

**Fix Options:**
- Select or create a tree first
- Check model configuration
- Verify system prompt is set

### Issue: Branching not working

**Step 1:** Check branchFromNodeId
```javascript
console.log("Branch from:", branchFromNodeId);
```

**Step 2:** Verify branch indicator
```javascript
console.log(document.getElementById("chat-branch-indicator").style.display);
```

**Step 3:** Test branch API
```powershell
# Test branch creation
Invoke-WebRequest -Uri "http://localhost:8000/api/chat-lab/trees/1/branch" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"from_node_id":"node_123"}'
```

**Fix Options:**
- Click 🌿 button on a message
- Verify node ID exists
- Check tree structure integrity

---

## 7. Guardrails Tab

### Issue: Rules not applying

**Step 1:** Check rule enabled status
```javascript
// Verify checkbox is checked
document.querySelectorAll("#guardrails-rules-table input[type=checkbox]").forEach(cb => {
  console.log("Rule enabled:", cb.checked);
});
```

**Step 2:** Test check endpoint
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/guardrails/check" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"test content with PII: john@example.com"}'
```

**Step 3:** Verify rule config
```javascript
// Check guardrails.json
```

**Fix Options:**
- Enable rules with toggle
- Check rule configuration JSON
- Verify rule type is correct

### Issue: Test suite failing

**Step 1:** Check test expectations
```javascript
// Expected_blocked must match actual result
```

**Step 2:** Verify rules are enabled
```javascript
// Tests run against enabled rules only
```

**Step 3:** Check test input
```javascript
// Ensure test input triggers expected rules
```

**Fix Options:**
- Update test expectations
- Enable required rules
- Check test input text

---

## 8. History Tab

### Issue: Entries not showing

**Step 1:** Check if logging is working
```powershell
# Make a request in Playground first
# Then check history
```

**Step 2:** Verify history API
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/history?limit=10" -Method GET
```

**Step 3:** Check metrics.json
```powershell
cat F:\AI_framework\app\data\metrics.json
```

**Fix Options:**
- Make some requests to generate history
- Check if history store is initialized
- Verify JSON file is valid

### Issue: Replay failing

**Step 1:** Check entry ID
```javascript
console.log("Replaying entry:", selectedHistoryEntryId);
```

**Step 2:** Verify entry exists
```javascript
fetch(`/api/history/${entryId}`).then(r => r.json()).then(console.log);
```

**Step 3:** Check model availability
```javascript
// Model from history must still exist
```

**Fix Options:**
- Ensure model is still available
- Check if endpoint still exists
- Verify entry has required data

---

## 9. Dashboard Tab

### Issue: Metrics not updating

**Step 1:** Check time range
```javascript
console.log(document.getElementById("dashboard-hours").value);
```

**Step 2:** Verify metrics exist
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/metrics/summary?hours=24" -Method GET
```

**Step 3:** Test refresh
```javascript
refreshDashboard();
```

**Fix Options:**
- Generate some requests first
- Change time range
- Check metrics.json file

### Issue: Charts not rendering

**Step 1:** Check hourly data
```javascript
fetch("/api/metrics/hourly?hours=24").then(r => r.json()).then(console.log);
```

**Step 2:** Verify chart container
```javascript
console.log(document.getElementById("hourly-chart-container"));
```

**Step 3:** Check CSS
```javascript
// Ensure chart styles are loaded
```

**Fix Options:**
- Refresh page
- Clear browser cache
- Check CSS is loaded

---

## 10. Tools Tab

### Issue: Tools not saving

**Step 1:** Check form values
```javascript
console.log({
  name: document.getElementById("tool-name").value,
  endpoint: document.getElementById("tool-endpoint").value
});
```

**Step 2:** Validate input schema
```javascript
let schema = JSON.parse(document.getElementById("tool-input-schema").value);
console.log("Schema valid:", schema);
```

**Step 3:** Test API
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/tools" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"name":"Test","description":"Test","endpoint":"http://test.com","input_schema":{},"enabled":true}'
```

**Fix Options:**
- Validate JSON schema syntax
- Check all required fields
- Verify tools.json is writable

---

## Common Issues Across All Tabs

### Issue: "Failed to fetch" errors

**Diagnosis:**
```powershell
# Check if server is running
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Test API directly
Invoke-WebRequest -Uri "http://localhost:8000/api/models" -Method GET
```

**Fix:**
1. Restart server: `uvicorn app.main:app --reload --port 8000`
2. Check firewall settings
3. Verify CORS configuration

### Issue: JSON parse errors

**Diagnosis:**
```javascript
// Check response in Network tab
// Look for malformed JSON
```

**Fix:**
1. Validate JSON files in `app/data/`
2. Check for trailing commas
3. Verify encoding (UTF-8)

### Issue: UI not responding

**Diagnosis:**
```javascript
// Check console for errors
// Look for "Uncaught" errors
```

**Fix:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check JavaScript is enabled
4. Try different browser

### Issue: Data not persisting

**Diagnosis:**
```powershell
# Check file permissions
Get-Acl F:\AI_framework\app\data
```

**Fix:**
1. Verify write permissions
2. Check disk space
3. Run as administrator if needed

---

## Debug Mode Setup

### Enable verbose logging

**In app/main.py:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**In browser console:**
```javascript
// Enable verbose logging
localStorage.setItem('debug', 'true');
```

### Monitor network traffic

1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "Fetch/XHR"
4. Monitor all API calls

### Check FastAPI logs

```powershell
# Run server with verbose output
uvicorn app.main:app --reload --port 8000 --log-level debug
```

---

## Performance Issues

### Slow API responses

**Step 1:** Check LM Studio performance
```powershell
# Test direct LM Studio API
Measure-Command {
  Invoke-WebRequest -Uri "http://127.0.0.1:1234/v1/chat/completions" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"model":"local-model","messages":[{"role":"user","content":"Hi"}]}'
}
```

**Step 2:** Monitor memory usage
```powershell
Get-Process python | Select-Object ProcessName, WorkingSet
```

**Fix Options:**
- Reduce model size in LM Studio
- Lower max_tokens
- Enable GPU acceleration
- Close other applications

### Browser freezing

**Step 1:** Check memory
```javascript
// In console
performance.memory
```

**Step 2:** Reduce data load
```javascript
// Limit history entries
// Clear old metrics
```

**Fix Options:**
- Clear browser cache
- Reduce pagination size
- Archive old data

---

## Emergency Recovery

### Reset all data
```powershell
# Backup first
cp -r F:\AI_framework\app\data F:\AI_framework\app\data_backup

# Reset all JSON files to empty arrays
echo "[]" > F:\AI_framework\app\data\chat_lab.json
echo "[]" > F:\AI_framework\app\data\datasets.json
echo "[]" > F:\AI_framework\app\data\eval_jobs.json
echo "[]" > F:\AI_framework\app\data\guardrail_tests.json
echo "[]" > F:\AI_framework\app\data\guardrails.json
echo "[]" > F:\AI_framework\app\data\metrics.json
echo "[]" > F:\AI_framework\app\data\prompt_templates.json
echo "[]" > F:\AI_framework\app\data\tools.json
```

### Restart everything
```powershell
# Stop server (Ctrl+C in terminal)
# Restart LM Studio
# Clear browser cache
# Restart browser
# Start server
uvicorn app.main:app --reload --port 8000
```

---

## Getting Help

1. **Check logs:** FastAPI terminal output
2. **Browser console:** F12 → Console tab
3. **Network tab:** F12 → Network tab
4. **Check docs:** Each tab has detailed documentation
5. **Test API:** Use PowerShell or Postman to test endpoints directly
