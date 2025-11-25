# LLM Testing Interface - Documentation Index

## Overview
Comprehensive testing interface for LLM models and agents with 10 specialized tabs.

## Tabs Documentation

### 1. [Playground](./playground.md)
Interactive chat interface for real-time LLM testing with streaming support.

### 2. [Prompt Builder](./prompt-builder.md)
Template system with variable substitution and 20+ preset templates.

### 3. [A/B Tester](./ab-tester.md)
Side-by-side model/agent comparison tool for performance testing.

### 4. [Evaluation](./evaluation.md)
Comprehensive evaluation suite with datasets, evaluators, and bulk testing.

### 5. [Orchestrator](./orchestrator.md)
Visual workflow builder for multi-step agent orchestration.

### 6. [Chat Lab](./chat-lab.md)
Branching conversation system with tree visualization.

### 7. [Guardrails](./guardrails.md)
Safety testing with rule-based content moderation.

### 8. [History](./history.md)
Request/response logging with replay and annotation.

### 9. [Dashboard](./dashboard.md)
Metrics dashboard with latency tracking and usage statistics.

### 10. [Tools](./tools.md)
Tool configuration management for function calling.

## Quick Links

- **Backend**: FastAPI with modular routers in `app/routers/`
- **Frontend**: Static files in `app/static/`
- **Configuration**: `app/config.py`
- **Data Storage**: JSON files in `app/data/`
- **Debugging**: [Step-by-Step Debugging Guide](./debugging-guide.md)

## Getting Started

1. Start the server: `uvicorn app.main:app --reload --port 8000`
2. Open browser: `http://localhost:8000`
3. LM Studio should be running at `http://127.0.0.1:1234/v1`

## Architecture

```
app/
├── routers/       # API endpoints by feature
├── models/        # Data stores & business logic
├── schemas/       # Pydantic models
└── static/        # Frontend (HTML/JS/CSS)
```
