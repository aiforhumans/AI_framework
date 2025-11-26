from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.service import (
    PromptTemplateCreateRequest,
    PromptTemplateUpdateRequest,
)
from app.routers import get_service

router = APIRouter()

@router.get("/api/prompt-templates", response_class=JSONResponse)
async def list_prompt_templates():
    service = get_service()
    templates = service.list_prompt_templates()
    return {"templates": templates}


@router.post("/api/prompt-templates", response_class=JSONResponse)
async def create_prompt_template(payload: PromptTemplateCreateRequest):
    service = get_service()
    template = service.create_prompt_template(payload)
    return template


@router.put("/api/prompt-templates/{template_id}", response_class=JSONResponse)
async def update_prompt_template(
    template_id: int, payload: PromptTemplateUpdateRequest
):
    service = get_service()
    template = service.update_prompt_template(template_id, payload)
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@router.delete("/api/prompt-templates/{template_id}", response_class=JSONResponse)
async def delete_prompt_template(template_id: int):
    service = get_service()
    success = service.delete_prompt_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"success": True}
