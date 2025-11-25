# LLM Testing Interface

A comprehensive Python-based FastAPI backend with a rich web UI for testing, evaluating, and orchestrating local LLM models and agent workflows.

Current implementation uses **LM Studio** as the local LLM runtime via its OpenAI-compatible HTTP API.

## Requirements

- Python 3.9+
- LM Studio (or any OpenAI-compatible local LLM server)

## Installation (using .venv)

From the project root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

All Python packages are installed into the local `.venv`.

## Running the app

With the virtual environment activated:

```bash
uvicorn app.main:app --reload
```

By default, the server listens on `http://127.0.0.1:8000/`.

### Reload behavior

- With `--reload`, uvicorn automatically restarts when it detects file changes.
- For production or lighter server, omit `--reload`:

```bash
uvicorn app.main:app
```

## Features

### 1. Interactive Playground
- **Multi-turn chat** with conversation history
- **Streaming responses** via Server-Sent Events (SSE)
- **AI-powered prompt improvement** with the ✨ Prompt Generator
- **File attachments** support (images, text files)
- Configurable model, agent, max tokens, and temperature
- System instructions editor with live character count

### 2. Prompt Builder
- Create reusable **prompt templates** with `{{variable}}` placeholders
- **Preset template library** with Role-Play, Chain-of-Thought, Few-Shot, and General categories
- Define system and user prompts separately
- **Live preview** with variable substitution
- Apply templates directly to Playground
- Persisted in `app/data/prompt_templates.json`

### 3. A/B Response Tester
- Compare responses from **2+ models/agents** side-by-side
- Same prompt sent to all variants simultaneously
- View latency metrics for each response
- **Vote feedback** (Better/Worse) for manual evaluation

### 4. Evaluation Suite
- **Dataset Management**
  - Create datasets with query/ground_truth pairs (JSONL format)
  - 8 built-in templates: Factual Q&A, Math, Summarization, Sentiment, Translation, Code Generation, Classification, RAG
  - Bulk run generation with **live streaming progress**
  
- **Evaluators**
  - Built-in: F1 Score, BLEU, Similarity, Exact Match, Contains Match, Length Ratio
  - Custom LLM-based evaluators (use AI to judge responses)
  - Custom code-based evaluators (Python with sandboxed execution)
  
- **Evaluation Jobs**
  - Run datasets against multiple evaluators
  - View aggregate scores and per-row results
  - Job history with status tracking

### 5. Agent Orchestrator
- **Visual workflow builder** for multi-step agent pipelines
- **Node types**: Start, Agent, Tool, Condition, End
- **Drag-and-drop** canvas with edge connections
- **Conditional routing** with expressions (contains, equals, >, <, etc.)
- **Variable interpolation**: `{{input}}`, `{{prev_output}}`
- Execute workflows with JSON input
- View step-by-step execution results and history
- Persisted in `app/data/workflows.json`

### 6. Multi-Turn Chat Lab
- **Branching conversations** with tree visualization
- Create alternative response branches from any message
- **Switch between branches** to explore different paths
- Track conversation state and history per branch
- Compare outcomes across different conversation flows
- Persisted in `app/data/chat_lab.json`

### 7. Guardrail Tester
- **Safety rule definitions** with pattern matching
  - Regex patterns, keyword lists, LLM-based detection
  - Rule categories: PII, profanity, toxic content, custom
- **Test case management** for validation
  - Define expected outcomes (blocked/allowed)
  - Specify expected rule flags
- **Real-time testing** with detailed flag results
- **Test suite execution** with pass/fail reporting
- Persisted in `app/data/guardrails.json`

### 8. Request History & Replay
- **Complete request/response logging** for all LLM calls
- **Filter and search** by endpoint, model, success status, or content
- **Star important entries** for quick reference
- **Add notes** to entries for documentation
- **Replay requests** with optional model/parameter overrides
- **Compare original vs replay** responses
- Statistics dashboard (success rate, latency, tokens)
- Persisted in `app/data/history.json`

### 9. Latency Dashboard
- **Real-time performance metrics** tracking
- **Charts and visualizations** for response times
- **Model comparison** metrics
- **Endpoint breakdowns** by usage
- **Hourly trends** analysis
- Configurable time range (1h, 6h, 24h, 7d)
- Persisted in `app/data/metrics.json`

### 10. Tools Tab
- Define tools with name, description, endpoint, and input schema
- Associate tools with specific models or agents
- Toggle enabled/disabled state
- Persisted in `app/data/tools.json`

## Project Structure

```
app/
├── main.py                 # FastAPI app setup & router registration
├── config.py               # Centralized configuration settings
│
├── routers/                # API endpoint routers (organized by feature)
│   ├── __init__.py         # Router exports
│   ├── playground.py       # /api/models, /api/generate, /api/chat
│   ├── tools.py            # /api/tools/*
│   ├── templates.py        # /api/prompt-templates/*
│   ├── ab_test.py          # /api/ab-test
│   ├── evaluation.py       # /api/datasets/*, /api/evaluators/*, /api/eval-jobs/*
│   ├── workflows.py        # /api/workflows/*, /api/workflow-runs/*
│   ├── guardrails.py       # /api/guardrails/*
│   ├── chat_lab.py         # /api/chat-lab/*
│   ├── history.py          # /api/history/*
│   └── metrics.py          # /api/metrics/*
│
├── schemas/                # Pydantic request/response models
│   ├── __init__.py
│   ├── requests.py         # All API request models
│   └── responses.py        # All API response models
│
├── services/               # Business logic services
│   └── __init__.py         # Service exports
│
├── models/                 # Data models and persistence stores
│   ├── service.py          # LocalLLMService - core LLM interaction
│   ├── base_store.py       # Generic CRUD base class
│   ├── tools_store.py      # Tool configuration persistence
│   ├── prompt_templates_store.py  # Template storage with presets
│   ├── eval_store.py       # Dataset, Evaluator, EvalJob models
│   ├── evaluators.py       # Built-in evaluator functions
│   ├── workflow_store.py   # Workflow nodes, edges, runs
│   ├── guardrail_store.py  # Guardrail rules and test cases
│   ├── chat_lab_store.py   # Branching conversation trees
│   ├── history_store.py    # Request/response logging
│   └── metrics_store.py    # Performance metrics tracking
│
├── static/                 # Frontend assets
│   ├── index.html          # Main UI with 10 tabs
│   ├── main.js             # Frontend logic
│   └── style.css           # Dark theme styling
│
└── data/                   # JSON persistence (auto-created)
    ├── tools.json
    ├── prompt_templates.json
    ├── datasets.json
    ├── custom_evaluators.json
    ├── eval_jobs.json
    ├── workflows.json
    ├── workflow_runs.json
    ├── guardrails.json
    ├── guardrail_tests.json
    ├── chat_lab.json
    ├── history.json
    └── metrics.json
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | List available LLM models |
| `/api/generate` | POST | Single-turn generation |
| `/api/chat` | POST | Multi-turn chat (supports streaming) |
| `/api/prompt-generator` | POST | AI-powered prompt improvement |
| `/api/ab-test` | POST | A/B test multiple variants |
| `/api/tools` | GET/POST | List/create tools |
| `/api/tools/{id}` | PUT/DELETE | Update/delete tool |
| `/api/prompt-templates` | GET/POST | List/create templates |
| `/api/datasets` | GET/POST | List/create datasets |
| `/api/datasets/{id}/bulk-run-stream` | POST | Bulk run with SSE streaming |
| `/api/evaluators` | GET | List all evaluators |
| `/api/evaluators/custom` | GET/POST | Custom evaluator CRUD |
| `/api/eval-jobs` | GET/POST | Evaluation job management |
| `/api/eval-jobs/{id}/run` | POST | Execute evaluation job |
| `/api/workflows` | GET/POST | List/create workflows |
| `/api/workflows/{id}` | GET/PUT/DELETE | Workflow CRUD |
| `/api/workflows/{id}/run` | POST | Execute workflow |
| `/api/workflow-runs` | GET | List workflow executions |
| `/api/guardrails/rules` | GET/POST | Guardrail rule management |
| `/api/guardrails/tests` | GET/POST | Guardrail test cases |
| `/api/guardrails/check` | POST | Check text against rules |
| `/api/guardrails/run-tests` | POST | Run test suite |
| `/api/chat-lab/trees` | GET/POST | Conversation tree management |
| `/api/chat-lab/trees/{id}/messages` | POST | Send chat message |
| `/api/chat-lab/trees/{id}/branch` | POST | Create conversation branch |
| `/api/history` | GET | List request history |
| `/api/history/{id}` | GET/PUT/DELETE | History entry management |
| `/api/history/replay` | POST | Replay a historical request |
| `/api/history/stats` | GET | Get history statistics |
| `/api/metrics` | GET | Get performance metrics |
| `/api/metrics/summary` | GET | Get metrics summary |

## Local LLM Integration (LM Studio)

This project uses LM Studio's OpenAI-compatible HTTP API:

- Generation via `/v1/chat/completions`
- Model listing via `/v1/models`
- Default endpoint: `http://127.0.0.1:1234/v1`

To use a different backend (Ollama, vLLM, etc.), modify `LocalLLMService` in `app/models/service.py`.

---

## Advanced Tool Instructions & Examples

### Creating Tools

Tools extend agent capabilities by connecting to external endpoints. Each tool has:

| Field | Description |
|-------|-------------|
| **Name** | Unique identifier (e.g., `web_search`, `calculator`) |
| **Description** | What the tool does (shown to agents for tool selection) |
| **Endpoint** | API URL to call when tool is invoked |
| **Input Schema** | JSON Schema defining expected parameters |
| **Models/Agents** | Which models or agents can use this tool |

### Example Tool Definitions

#### 1. Web Search Tool
```json
{
  "name": "web_search",
  "description": "Search the web for current information. Use for questions about recent events, facts, or topics requiring up-to-date data.",
  "endpoint": "https://api.example.com/search",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query"
      },
      "num_results": {
        "type": "integer",
        "description": "Number of results to return",
        "default": 5
      }
    },
    "required": ["query"]
  },
  "enabled": true
}
```

#### 2. Calculator Tool
```json
{
  "name": "calculator",
  "description": "Perform mathematical calculations. Use for arithmetic, algebra, or any numeric computation.",
  "endpoint": "/api/tools/calculator",
  "input_schema": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "Mathematical expression to evaluate (e.g., '2 + 2 * 3')"
      }
    },
    "required": ["expression"]
  },
  "enabled": true
}
```

#### 3. Database Query Tool
```json
{
  "name": "query_database",
  "description": "Query the product database. Use to look up inventory, prices, or product details.",
  "endpoint": "/api/tools/db-query",
  "input_schema": {
    "type": "object",
    "properties": {
      "table": {
        "type": "string",
        "enum": ["products", "orders", "customers"],
        "description": "Database table to query"
      },
      "filters": {
        "type": "object",
        "description": "Key-value pairs for filtering results"
      },
      "limit": {
        "type": "integer",
        "default": 10
      }
    },
    "required": ["table"]
  },
  "enabled": true,
  "agents": ["sales-agent", "support-agent"]
}
```

#### 4. Code Execution Tool
```json
{
  "name": "run_python",
  "description": "Execute Python code in a sandboxed environment. Use for data processing, calculations, or generating outputs.",
  "endpoint": "/api/tools/python-sandbox",
  "input_schema": {
    "type": "object",
    "properties": {
      "code": {
        "type": "string",
        "description": "Python code to execute"
      },
      "timeout": {
        "type": "integer",
        "description": "Maximum execution time in seconds",
        "default": 30
      }
    },
    "required": ["code"]
  },
  "enabled": true,
  "models": ["gpt-4", "claude-3"]
}
```

#### 5. Email Sender Tool
```json
{
  "name": "send_email",
  "description": "Send an email to a recipient. Use when user explicitly requests to send an email.",
  "endpoint": "/api/tools/email",
  "input_schema": {
    "type": "object",
    "properties": {
      "to": {
        "type": "string",
        "format": "email",
        "description": "Recipient email address"
      },
      "subject": {
        "type": "string",
        "description": "Email subject line"
      },
      "body": {
        "type": "string",
        "description": "Email body content (plain text or HTML)"
      },
      "cc": {
        "type": "array",
        "items": { "type": "string", "format": "email" },
        "description": "CC recipients"
      }
    },
    "required": ["to", "subject", "body"]
  },
  "enabled": true
}
```

### Using Tools in Workflows (Orchestrator)

In the Agent Orchestrator, tools are integrated as **Tool Nodes**:

1. **Add a Tool Node** to your workflow canvas
2. **Configure the node**:
   - Set `Tool ID` to match your tool name (e.g., `web_search`)
   - Set `Input Template` using variables:
     ```
     {"query": "{{prev_output}}"}
     ```
3. **Connect edges** from Agent nodes to Tool nodes

#### Workflow Example: Research Assistant

```
[Start] → [Agent: Parse Query] → [Tool: web_search] → [Agent: Summarize] → [End]
```

**Node Configurations:**

- **Agent: Parse Query**
  - Prompt: `Extract the main search topic from: {{input}}`
  
- **Tool: web_search**
  - Input Template: `{"query": "{{prev_output}}", "num_results": 3}`
  
- **Agent: Summarize**
  - Prompt: `Summarize these search results:\n{{prev_output}}`

### Conditional Tool Selection

Use **Condition Nodes** to dynamically choose tools:

```
[Start] → [Agent: Classify] → [Condition: contains:math] 
                                    ├─ Yes → [Tool: calculator]
                                    └─ No  → [Tool: web_search]
```

**Condition expressions:**
- `contains:math` - Check if output contains "math"
- `equals:search` - Exact match
- `startswith:calculate` - Prefix match
- `>:100` - Numeric comparison (for scores/counts)

### Best Practices

1. **Write clear descriptions** - Agents use descriptions to decide when to call tools
2. **Define strict schemas** - Validate inputs with required fields and types
3. **Use enums for fixed options** - Prevents invalid inputs
4. **Set reasonable defaults** - Reduce required parameters
5. **Scope to specific agents** - Not all tools should be available to all agents
6. **Test with A/B Tester** - Compare tool-enabled vs tool-disabled responses
7. **Monitor in Evaluation** - Create datasets to test tool usage accuracy

### Implementing Tool Endpoints

Tool endpoints receive POST requests with the input data:

```python
# Example: Add to app/main.py

@app.post("/api/tools/calculator")
async def calculator_tool(request: Request):
    data = await request.json()
    expression = data.get("expression", "")
    
    try:
        # WARNING: Use a safe evaluator in production!
        result = eval(expression)
        return {"result": result, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

@app.post("/api/tools/weather")
async def weather_tool(request: Request):
    data = await request.json()
    location = data.get("location", "")
    
    # Call external weather API
    # weather_data = await fetch_weather(location)
    
    return {
        "location": location,
        "temperature": "72°F",
        "conditions": "Sunny",
        "success": True
    }
```

---

## Upcoming Features

- **Agent Memory**: Persistent context and knowledge storage for agents
- **API Key Management**: Secure storage and rotation of API keys
- **Export/Import**: Export workflows, datasets, and configurations
- **Webhook Integration**: Trigger workflows from external events
- **Custom Metrics**: Define and track custom performance metrics

