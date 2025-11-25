"""
Tools Router.

Handles tool configuration CRUD operations.
Tools can be associated with models and agents.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.requests import ToolCreateRequest, ToolUpdateRequest
from app.routers import get_service

router = APIRouter(prefix="/api/tools", tags=["Tools"])


@router.get("", response_class=JSONResponse)
async def list_tools():
    """List all configured tools."""
    return {"tools": get_service().list_tools()}


@router.post("", response_class=JSONResponse)
async def create_tool(payload: ToolCreateRequest):
    """Create a new tool configuration."""
    return get_service().create_tool(payload)


@router.put("/{tool_id}", response_class=JSONResponse)
async def update_tool(tool_id: int, payload: ToolUpdateRequest):
    """Update an existing tool."""
    result = get_service().update_tool(tool_id, payload)
    if result is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return result


@router.delete("/{tool_id}", response_class=JSONResponse)
async def delete_tool(tool_id: int):
    """Delete a tool by ID."""
    if not get_service().delete_tool(tool_id):
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"success": True}


@router.post("/{tool_id}/toggle", response_class=JSONResponse)
async def toggle_tool(tool_id: int):
    """Toggle a tool's enabled/disabled status."""
    result = get_service().toggle_tool(tool_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return result
