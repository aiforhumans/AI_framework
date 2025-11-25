"""
LLM Testing Interface - Main Application.

A comprehensive interface for testing and evaluating Local LLMs.

Features:
- Playground: Interactive multi-turn chat with streaming
- Prompt Builder: Template system with {{variable}} placeholders
- A/B Tester: Side-by-side model/agent comparison
- Evaluation: Datasets, bulk runs, built-in + custom evaluators
- Orchestrator: Visual workflow builder with nodes and edges
- Guardrails: Safety testing and content moderation
- Chat Lab: Multi-turn branching conversations
- History: Request/response logging with replay
- Metrics: Latency and usage dashboard

Usage:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.models.service import LocalLLMService

# Import routers
from app.routers import (
    playground_router,
    tools_router,
    templates_router,
    ab_test_router,
    evaluation_router,
    workflows_router,
    guardrails_router,
    chat_lab_router,
    history_router,
    metrics_router,
)


# =============================================================================
# APPLICATION SETUP
# =============================================================================

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")

# Global service instance (shared across routers)
llm_service = LocalLLMService()


# =============================================================================
# REGISTER ROUTERS
# =============================================================================

app.include_router(playground_router)
app.include_router(tools_router)
app.include_router(templates_router)
app.include_router(ab_test_router)
app.include_router(evaluation_router)
app.include_router(workflows_router)
app.include_router(guardrails_router)
app.include_router(chat_lab_router)
app.include_router(history_router)
app.include_router(metrics_router)


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Serve the main application page.
    
    Passes available models and agents to the template.
    """
    models = await llm_service.list_models()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_models": models,
            "agents": llm_service.list_agents(),
        },
    )


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": API_VERSION}
