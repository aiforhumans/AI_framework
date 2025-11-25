# LLM Testing Interface – Copilot Instructions

## Architecture Overview

- **Backend**: FastAPI with modular routers in `app/routers/`
- **Core Service**: `LocalLLMService` in `app/models/service.py`
- **Frontend**: Static files in `app/static/` (`index.html`, `main.js`, `style.css`)
- **Persistence**: JSON files in `app/data/` (auto-created)
- **LLM Runtime**: LM Studio at `http://127.0.0.1:1234/v1` (OpenAI-compatible API)
- **Configuration**: Centralized in `app/config.py`
- **Documentation**: Comprehensive guides in `docs/` folder
- **Debugging**: Step-by-step guide available at `docs/debugging-guide.md`

## Project Structure

```
app/
├── main.py              # FastAPI app setup & router registration
├── config.py            # Centralized settings (URLs, defaults, paths)
├── routers/             # API routers by feature domain
│   ├── playground.py    # /api/models, /api/generate, /api/chat
│   ├── tools.py         # /api/tools/*
│   ├── templates.py     # /api/prompt-templates/*
│   ├── ab_test.py       # /api/ab-test
│   ├── evaluation.py    # /api/datasets/*, /api/evaluators/*, /api/eval-jobs/*
│   ├── workflows.py     # /api/workflows/*, /api/workflow-runs/*
│   ├── guardrails.py    # /api/guardrails/*
│   ├── chat_lab.py      # /api/chat-lab/*
│   ├── history.py       # /api/history/*
│   └── metrics.py       # /api/metrics/*
├── schemas/             # Pydantic models
│   ├── requests.py      # All request models
│   └── responses.py     # All response models
├── models/              # Data stores & business logic
│   ├── service.py       # LocalLLMService (main orchestration)
│   ├── base_store.py    # Generic CRUD base class
│   └── *_store.py       # Feature-specific stores
└── static/              # Frontend assets
```

## Current Tabs & Features

All tabs fully documented in `docs/` folder:

1. **Playground** - Interactive multi-turn chat with streaming, prompt generator, attachments
   - API: `/api/models`, `/api/chat`, `/api/prompt-generator`
   - Features: Streaming, file attachments, AI prompt improvement
   
2. **Prompt Builder** - Template system with `{{variable}}` placeholders
   - API: `/api/prompt-templates/*`
   - Features: 19 templates (14 presets + custom), variable substitution
   
3. **A/B Tester** - Side-by-side model/agent comparison
   - API: `/api/ab-test`
   - Features: Parallel execution, latency tracking
   
4. **Evaluation** - Datasets, bulk runs with SSE streaming, built-in + custom evaluators
   - API: `/api/datasets/*`, `/api/evaluators/*`, `/api/eval-jobs/*`
   - Features: 8 dataset templates, custom evaluators, streaming bulk runs
   
5. **Orchestrator** - Visual workflow builder with nodes and conditional routing
   - API: `/api/workflows/*`, `/api/workflow-runs/*`
   - Features: Drag-drop nodes, conditional routing, step-by-step execution
   
6. **Chat Lab** - Multi-turn branching conversations with tree visualization
   - API: `/api/chat-lab/trees/*`
   - Features: Conversation branching, tree visualization, path switching
   
7. **Guardrails** - Safety testing with PII, keyword, regex, content filters
   - API: `/api/guardrails/rules/*`, `/api/guardrails/tests/*`
   - Features: 5 rule types, test suite, real-time checking
   
8. **History** - Request/response logging with replay capability
   - API: `/api/history/*`
   - Features: Filtering, replay, annotations, statistics
   
9. **Dashboard** - Latency dashboard with charts and breakdowns
   - API: `/api/metrics/*`
   - Features: Summary stats, hourly trends, model/endpoint breakdowns
   
10. **Tools** - Tool definition with schema, endpoint, model/agent associations
    - API: `/api/tools/*`
    - Features: JSON schema validation, model/agent linking

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | App initialization, router registration |
| `app/config.py` | LM Studio URL, timeouts, paths |
| `app/routers/*.py` | API endpoints by domain |
| `app/schemas/requests.py` | All Pydantic request models |
| `app/models/service.py` | Core LLM service orchestration |
| `app/models/base_store.py` | Generic CRUD base class |
| `app/static/main.js` | All frontend JavaScript |
| `app/static/style.css` | Dark theme CSS |

## When Extending the Project

### Adding a New API Feature
1. Create router in `app/routers/new_feature.py`
2. Add request models to `app/schemas/requests.py`
3. Create store in `app/models/new_feature_store.py` (extend `BaseStore` if CRUD)
4. Add methods to `LocalLLMService` in `app/models/service.py`
5. Register router in `app/main.py`

### Adding a New UI Tab
1. Add nav link in `index.html`
2. Create `<section id="new-tab">` panel
3. Add `initNewUI()` function in `main.js`
4. Call from `DOMContentLoaded`

## Patterns to Follow

- **Routers**: Use `APIRouter` with prefix and tags
- **Persistence**: JSON in `app/data/*.json` via store classes
- **Models**: Pydantic for all request/response validation
- **Async**: Use `async def` for LLM-calling endpoints
- **CRUD**: Follow `list_*`, `get_*`, `create_*`, `update_*`, `delete_*` pattern
- **Streaming**: SSE via `StreamingResponse` + `EventSource`
- **Styling**: Dark theme (`#0f172a`, `#1e293b`, `#374151`)

## Commands

```powershell
# Activate virtual environment
& F:\AI_framework\.venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload --port 8000

# Run full debugging check
# See docs/debugging-guide.md for complete test suite

# Test specific endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/models" -Method GET

# Validate all JSON files
foreach ($file in @('chat_lab','datasets','eval_jobs','guardrail_tests','guardrails','metrics','prompt_templates','tools')) {
    Get-Content "app/data/$file.json" | ConvertFrom-Json | Out-Null
    Write-Host "$file.json - Valid"
}

# Default URL
http://127.0.0.1:8000/
```

## Environment Status Check

**Quick health check:**
```powershell
# Server running?
Get-Process -Name python -ErrorAction SilentlyContinue

# Ports listening?
netstat -ano | findstr ":8000 :1234"

# JSON files valid?
ls app/data/*.json | ForEach-Object { 
    try { Get-Content $_ | ConvertFrom-Json | Out-Null; "✓ $_" } 
    catch { "✗ $_ - Invalid JSON" }
}
```

## Documentation

Comprehensive documentation available in `docs/`:
- `README.md` - Overview and quick links
- `playground.md` - Playground tab features
- `prompt-builder.md` - Template system
- `ab-tester.md` - Model comparison
- `evaluation.md` - Testing suite
- `orchestrator.md` - Workflow builder
- `chat-lab.md` - Branching conversations
- `guardrails.md` - Safety testing
- `history.md` - Request logging
- `dashboard.md` - Metrics
- `tools.md` - Tool configuration
- `debugging-guide.md` - Step-by-step troubleshooting

## Debugging Process

**Before making changes:**
1. Verify server is running on port 8000
2. Check LM Studio connection on port 1234
3. Validate all JSON files in `app/data/`
4. Test relevant API endpoints
5. Check browser console for errors

**Common Issues:**
- **Port conflicts**: Check `netstat -ano | findstr :8000`
- **JSON errors**: Validate files with `ConvertFrom-Json`
- **API failures**: Test with `Invoke-WebRequest`
- **UI not updating**: Check browser console and Network tab
- **Data not persisting**: Verify file permissions and disk space

**Debugging Commands:**
```powershell
# Check server status
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Test API endpoint
Invoke-WebRequest -Uri "http://localhost:8000/api/models" -Method GET

# Validate JSON file
Get-Content "app/data/datasets.json" | ConvertFrom-Json

# Check port usage
netstat -ano | findstr :8000
```

Refer to `docs/debugging-guide.md` for detailed troubleshooting steps per tab.

## Guidelines

- Do not scaffold a new project; build on current structure
- Do not install extra VS Code extensions unless explicitly requested
- Keep responses concise and focused on actionable changes
- When adding features, update both backend (endpoints) and frontend (UI + JS)
- Use existing patterns from similar features as reference
- **Always check documentation first** before making assumptions
- **Test changes** using debugging commands provided
- **Validate data integrity** after modifications
- Update relevant documentation when adding new features
