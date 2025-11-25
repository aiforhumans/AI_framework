"""
Evaluation Router.

Handles dataset management, evaluators, and evaluation jobs.
Supports bulk generation with streaming progress updates.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json

from app.schemas.requests import (
    DatasetCreateRequest, DatasetUpdateRequest,
    CustomEvaluatorCreateRequest, CustomEvaluatorUpdateRequest,
    EvalJobCreateRequest, BulkRunRequest,
)
from app.routers import get_service

router = APIRouter(tags=["Evaluation"])


# =============================================================================
# DATASETS
# =============================================================================

@router.get("/api/datasets", response_class=JSONResponse)
async def list_datasets():
    """List all evaluation datasets."""
    datasets = get_service().list_datasets()
    return {"datasets": [d.model_dump() for d in datasets]}


@router.get("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def get_dataset(dataset_id: int):
    """Get a specific dataset by ID."""
    dataset = get_service().get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.model_dump()


@router.post("/api/datasets", response_class=JSONResponse)
async def create_dataset(payload: DatasetCreateRequest):
    """Create a new evaluation dataset with query/response/ground_truth rows."""
    return get_service().create_dataset(payload).model_dump()


@router.put("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def update_dataset(dataset_id: int, payload: DatasetUpdateRequest):
    """Update an existing dataset."""
    result = get_service().update_dataset(dataset_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return result.model_dump()


@router.delete("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def delete_dataset(dataset_id: int):
    """Delete a dataset."""
    if not get_service().delete_dataset(dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"success": True}


@router.post("/api/datasets/{dataset_id}/bulk-run", response_class=JSONResponse)
async def bulk_run_dataset(dataset_id: int, payload: BulkRunRequest):
    """Run bulk generation for all queries in a dataset."""
    payload.dataset_id = dataset_id
    try:
        dataset = await get_service().run_bulk_generate(payload)
        return dataset.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/datasets/{dataset_id}/bulk-run-stream")
async def bulk_run_dataset_stream(dataset_id: int, payload: BulkRunRequest):
    """Bulk generation with SSE streaming progress updates."""
    payload.dataset_id = dataset_id
    
    async def generate_stream():
        async for event in get_service().run_bulk_generate_stream(payload):
            yield f"data: {json.dumps(event)}\n\n"
        yield "data: {\"done\": true}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# =============================================================================
# EVALUATORS
# =============================================================================

@router.get("/api/evaluators", response_class=JSONResponse)
async def list_evaluators():
    """List all evaluators (built-in and custom)."""
    svc = get_service()
    builtin = svc.get_builtin_evaluators()
    custom = svc.list_custom_evaluators()
    custom_list = [
        {"id": f"custom:{e.id}", "name": e.name, "description": e.description, "type": e.evaluator_type}
        for e in custom
    ]
    return {"evaluators": builtin + custom_list}


@router.get("/api/evaluators/custom", response_class=JSONResponse)
async def list_custom_evaluators():
    """List custom evaluators only."""
    evaluators = get_service().list_custom_evaluators()
    return {"evaluators": [e.model_dump() for e in evaluators]}


@router.get("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def get_custom_evaluator(evaluator_id: int):
    """Get a specific custom evaluator."""
    evaluator = get_service().get_custom_evaluator(evaluator_id)
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return evaluator.model_dump()


@router.post("/api/evaluators/custom", response_class=JSONResponse)
async def create_custom_evaluator(payload: CustomEvaluatorCreateRequest):
    """Create a custom evaluator (LLM-based or code-based)."""
    return get_service().create_custom_evaluator(payload).model_dump()


@router.put("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def update_custom_evaluator(evaluator_id: int, payload: CustomEvaluatorUpdateRequest):
    """Update a custom evaluator."""
    result = get_service().update_custom_evaluator(evaluator_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return result.model_dump()


@router.delete("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def delete_custom_evaluator(evaluator_id: int):
    """Delete a custom evaluator."""
    if not get_service().delete_custom_evaluator(evaluator_id):
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return {"success": True}


# =============================================================================
# EVALUATION JOBS
# =============================================================================

@router.get("/api/eval-jobs", response_class=JSONResponse)
async def list_eval_jobs():
    """List all evaluation jobs."""
    jobs = get_service().list_eval_jobs()
    return {"jobs": [j.model_dump() for j in jobs]}


@router.get("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def get_eval_job(job_id: int):
    """Get a specific evaluation job with results."""
    job = get_service().get_eval_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Eval job not found")
    return job.model_dump()


@router.post("/api/eval-jobs", response_class=JSONResponse)
async def create_eval_job(payload: EvalJobCreateRequest):
    """Create a new evaluation job."""
    return get_service().create_eval_job(payload).model_dump()


@router.post("/api/eval-jobs/{job_id}/run", response_class=JSONResponse)
async def run_eval_job(job_id: int):
    """Run an evaluation job (applies evaluators to dataset)."""
    try:
        job = await get_service().run_eval_job(job_id)
        return job.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def delete_eval_job(job_id: int):
    """Delete an evaluation job."""
    if not get_service().delete_eval_job(job_id):
        raise HTTPException(status_code=404, detail="Eval job not found")
    return {"success": True}
