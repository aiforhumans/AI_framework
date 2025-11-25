"""
Workflows Router.

Handles agent orchestration workflows with visual node-based editing.
Supports: agent nodes, condition nodes, transform nodes, output nodes.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json

from app.schemas.requests import WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowRunRequest
from app.routers import get_service

router = APIRouter(tags=["Workflows"])


# =============================================================================
# WORKFLOW DEFINITIONS
# =============================================================================

@router.get("/api/workflows", response_class=JSONResponse)
async def list_workflows():
    """List all workflow definitions."""
    workflows = get_service().list_workflows()
    return {"workflows": [w.model_dump() for w in workflows]}


@router.get("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def get_workflow(workflow_id: int):
    """Get a specific workflow with nodes and edges."""
    workflow = get_service().get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@router.post("/api/workflows", response_class=JSONResponse)
async def create_workflow(payload: WorkflowCreateRequest):
    """Create a new workflow definition."""
    return get_service().create_workflow(payload).model_dump()


@router.put("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def update_workflow(workflow_id: int, payload: WorkflowUpdateRequest):
    """Update workflow nodes, edges, or metadata."""
    result = get_service().update_workflow(workflow_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result.model_dump()


@router.delete("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def delete_workflow(workflow_id: int):
    """Delete a workflow."""
    if not get_service().delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True}


# =============================================================================
# WORKFLOW EXECUTION
# =============================================================================

@router.post("/api/workflows/{workflow_id}/run")
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest):
    """
    Execute a workflow with streaming step-by-step results.
    
    Returns SSE stream with progress updates for each node.
    """
    async def generate_stream():
        async for event in get_service().run_workflow(workflow_id, payload.input_text):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# =============================================================================
# WORKFLOW RUNS (HISTORY)
# =============================================================================

@router.get("/api/workflow-runs", response_class=JSONResponse)
async def list_workflow_runs(workflow_id: int = None):
    """List workflow execution history."""
    runs = get_service().list_workflow_runs(workflow_id)
    return {"runs": [r.model_dump() for r in runs]}


@router.get("/api/workflow-runs/{run_id}", response_class=JSONResponse)
async def get_workflow_run(run_id: int):
    """Get a specific workflow run with step details."""
    run = get_service().get_workflow_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run.model_dump()
