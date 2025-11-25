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

### 6. Tools Tab
- Define tools with name, description, endpoint, and input schema
- Associate tools with specific models or agents
- Toggle enabled/disabled state
- Persisted in `app/data/tools.json`

## Project Structure

```
app/
├── main.py                 # FastAPI routes and endpoints
├── models/
│   ├── service.py          # LocalLLMService - core business logic
│   ├── tools_store.py      # Tool persistence
│   ├── eval_store.py       # Dataset, Evaluator, EvalJob models
│   ├── evaluators.py       # Built-in evaluator functions
│   └── workflow_store.py   # Workflow models and persistence
├── static/
│   ├── index.html          # Main UI with 6 tabs
│   ├── main.js             # All frontend logic
│   └── style.css           # Dark theme styling
└── data/                   # JSON persistence (auto-created)
    ├── tools.json
    ├── prompt_templates.json
    ├── datasets.json
    ├── evaluators.json
    ├── eval_jobs.json
    └── workflows.json
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

## Local LLM Integration (LM Studio)

This project uses LM Studio's OpenAI-compatible HTTP API:

- Generation via `/v1/chat/completions`
- Model listing via `/v1/models`
- Default endpoint: `http://127.0.0.1:1234/v1`

To use a different backend (Ollama, vLLM, etc.), modify `LocalLLMService` in `app/models/service.py`.

## Upcoming Features

- **Latency Dashboard**: Response time tracking and performance metrics
- **Guardrail Tester**: Safety filters and PII detection testing
- **Template Modes**: Role-play, Chain-of-Thought, few-shot templates
- **Multi-Turn Chat Lab**: Conversation simulation with branching paths
- **History & Replay**: Request/response logging with replay capability

