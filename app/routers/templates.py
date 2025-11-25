"""
Prompt Templates Router.

Handles prompt template CRUD operations.
Supports categories: cot, fewshot, roleplay, structured, custom.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.requests import PromptTemplateCreateRequest, PromptTemplateUpdateRequest
from app.routers import get_service

router = APIRouter(prefix="/api/prompt-templates", tags=["Prompt Templates"])


@router.get("", response_class=JSONResponse)
async def list_prompt_templates(category: str = None, include_presets: bool = True):
    """List all prompt templates with optional category filter."""
    templates = get_service().list_prompt_templates(category=category, include_presets=include_presets)
    return {"templates": [t.model_dump() for t in templates]}


@router.get("/categories", response_class=JSONResponse)
async def list_template_categories():
    """List available template categories."""
    return {"categories": [
        {"id": "cot", "name": "Chain of Thought", "icon": "🔗"},
        {"id": "fewshot", "name": "Few-Shot Learning", "icon": "📝"},
        {"id": "roleplay", "name": "Role-Play", "icon": "🎭"},
        {"id": "structured", "name": "Structured Output", "icon": "📋"},
        {"id": "custom", "name": "Custom", "icon": "✏️"},
    ]}


@router.post("", response_class=JSONResponse)
async def create_prompt_template(payload: PromptTemplateCreateRequest):
    """Create a new prompt template with {{variable}} placeholders."""
    return get_service().create_prompt_template(payload).model_dump()


@router.put("/{template_id}", response_class=JSONResponse)
async def update_prompt_template(template_id: int, payload: PromptTemplateUpdateRequest):
    """Update an existing prompt template."""
    result = get_service().update_prompt_template(template_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return result


@router.delete("/{template_id}", response_class=JSONResponse)
async def delete_prompt_template(template_id: int):
    """Delete a prompt template (presets cannot be deleted)."""
    if not get_service().delete_prompt_template(template_id):
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"success": True}
