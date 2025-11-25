# LLM Testing Interface – Copilot Instructions

## Architecture Overview

- **Backend**: FastAPI in `app/main.py` with `LocalLLMService` in `app/models/service.py`
- **Frontend**: Static files in `app/static/` (`index.html`, `main.js`, `style.css`)
- **Persistence**: JSON files in `app/data/` (auto-created)
- **LLM Runtime**: LM Studio at `http://127.0.0.1:1234/v1` (OpenAI-compatible API)

## Current Tabs & Features

1. **Playground** - Interactive multi-turn chat with streaming, prompt generator, attachments
2. **Prompt Builder** - Template system with `{{variable}}` placeholders
3. **A/B Tester** - Side-by-side model/agent comparison
4. **Evaluation** - Datasets, bulk runs with SSE streaming, built-in + custom evaluators, eval jobs
5. **Orchestrator** - Visual workflow builder with nodes (Start/Agent/Tool/Condition/End), edges, conditional routing
6. **Tools** - Tool definition with schema, endpoint, model/agent associations

## Key Files

- `app/main.py` - All REST endpoints
- `app/models/service.py` - Core business logic, request models, LLM calls
- `app/models/workflow_store.py` - Workflow, Node, Edge, Run models
- `app/models/eval_store.py` - Dataset, CustomEvaluator, EvalJob models
- `app/models/evaluators.py` - Built-in evaluator functions (F1, BLEU, etc.)
- `app/models/tools_store.py` - Tool persistence
- `app/static/main.js` - All frontend JavaScript logic
- `app/static/style.css` - Dark theme CSS

## When Extending the Project

- Add new tabs in `index.html` nav and create corresponding `<section id="...-tab">` panels
- Initialize tab UI in `main.js` with `initXxxUI()` function called from `DOMContentLoaded`
- Create Pydantic models in `service.py` for request/response validation
- Add store classes in `app/models/` for new data types (follow pattern of `ToolStore`, `EvalStore`)
- Use SSE (`StreamingResponse` + `EventSource`) for long-running operations with progress
- Keep styles consistent with existing dark theme (`#0f172a`, `#1e293b`, `#374151`)

## Patterns to Follow

- JSON persistence in `app/data/*.json` (create directory if needed)
- Pydantic models for all request bodies
- `async def` for endpoints that call LLM
- CRUD pattern: `list_*`, `get_*`, `create_*`, `update_*`, `delete_*`
- Frontend: fetch API, no external JS frameworks

## Commands

```bash
# Start server
uvicorn app.main:app --reload

# Default URL
http://127.0.0.1:8000/
```

## Guidelines

- Do not scaffold a new project; build on current structure
- Do not install extra VS Code extensions unless explicitly requested
- Keep responses concise and focused on actionable changes
- When adding features, update both backend (endpoints) and frontend (UI + JS)
