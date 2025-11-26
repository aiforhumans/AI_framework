from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.service import (
    ToolCreateRequest,
    ToolUpdateRequest,
)
from app.routers import get_service

router = APIRouter()

@router.get("/api/tools", response_class=JSONResponse)
async def list_tools():
    service = get_service()
    tools = service.list_tools()
    return {"tools": tools}


@router.post("/api/tools", response_class=JSONResponse)
async def create_tool(payload: ToolCreateRequest):
    service = get_service()
    tool = service.create_tool(payload)
    return tool


@router.put("/api/tools/{tool_id}", response_class=JSONResponse)
async def update_tool(tool_id: int, payload: ToolUpdateRequest):
    service = get_service()
    tool = service.update_tool(tool_id, payload)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.delete("/api/tools/{tool_id}", response_class=JSONResponse)
async def delete_tool(tool_id: int):
    service = get_service()
    success = service.delete_tool(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"success": True}


@router.post("/api/tools/{tool_id}/toggle", response_class=JSONResponse)
async def toggle_tool(tool_id: int):
    service = get_service()
    tool = service.toggle_tool(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool
