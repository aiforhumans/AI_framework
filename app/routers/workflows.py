from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.models.service import (
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowRunRequest,
)
from app.routers import get_service

router = APIRouter()

@router.get("/api/workflows", response_class=JSONResponse)
async def list_workflows():
    service = get_service()
    workflows = service.list_workflows()
    return {"workflows": [w.model_dump() for w in workflows]}


@router.get("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def get_workflow(workflow_id: int):
    service = get_service()
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@router.post("/api/workflows", response_class=JSONResponse)
async def create_workflow(payload: WorkflowCreateRequest):
    service = get_service()
    workflow = service.create_workflow(payload)
    return workflow.model_dump()


@router.put("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def update_workflow(workflow_id: int, payload: WorkflowUpdateRequest):
    service = get_service()
    workflow = service.update_workflow(workflow_id, payload)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@router.delete("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def delete_workflow(workflow_id: int):
    service = get_service()
    success = service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True}


@router.post("/api/workflows/{workflow_id}/run", response_class=JSONResponse)
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest):
    service = get_service()
    payload.workflow_id = workflow_id
    try:
        run = await service.run_workflow(payload)
        return run.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/workflow-runs", response_class=JSONResponse)
async def list_workflow_runs(workflow_id: int = None):
    service = get_service()
    runs = service.list_workflow_runs(workflow_id)
    return {"runs": [r.model_dump() for r in runs]}


@router.get("/api/workflow-runs/{run_id}", response_class=JSONResponse)
async def get_workflow_run(run_id: int):
    service = get_service()
    runs = service.list_workflow_runs()
    for run in runs:
        if run.id == run_id:
            return run.model_dump()
    raise HTTPException(status_code=404, detail="Workflow run not found")
