"""
Routers Package.

Contains all FastAPI router modules organized by feature domain.
Each router handles a specific set of related API endpoints.
"""


def get_service():
    """Get the LLM service instance. Shared dependency for all routers."""
    from app.main import llm_service
    return llm_service


from app.routers.playground import router as playground_router
from app.routers.tools import router as tools_router
from app.routers.templates import router as templates_router
from app.routers.evaluation import router as evaluation_router
from app.routers.workflows import router as workflows_router
from app.routers.guardrails import router as guardrails_router
from app.routers.chat_lab import router as chat_lab_router
from app.routers.history import router as history_router
from app.routers.metrics import router as metrics_router
from app.routers.ab_test import router as ab_test_router

__all__ = [
    "playground_router",
    "tools_router", 
    "templates_router",
    "evaluation_router",
    "workflows_router",
    "guardrails_router",
    "chat_lab_router",
    "history_router",
    "metrics_router",
    "ab_test_router",
]
