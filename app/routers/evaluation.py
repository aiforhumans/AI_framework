from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json as json_lib

from app.models.service import (
    DatasetCreateRequest,
    DatasetUpdateRequest,
    CustomEvaluatorCreateRequest,
    CustomEvaluatorUpdateRequest,
    EvalJobCreateRequest,
    BulkRunRequest,
)
from app.routers import get_service

router = APIRouter()

# Datasets

@router.get("/api/datasets", response_class=JSONResponse)
async def list_datasets():
    service = get_service()
    datasets = service.list_datasets()
    return {"datasets": [d.model_dump() for d in datasets]}


@router.get("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def get_dataset(dataset_id: int):
    service = get_service()
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.model_dump()


@router.post("/api/datasets", response_class=JSONResponse)
async def create_dataset(payload: DatasetCreateRequest):
    service = get_service()
    dataset = service.create_dataset(payload)
    return dataset.model_dump()


@router.put("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def update_dataset(dataset_id: int, payload: DatasetUpdateRequest):
    service = get_service()
    dataset = service.update_dataset(dataset_id, payload)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.model_dump()


@router.delete("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def delete_dataset(dataset_id: int):
    service = get_service()
    success = service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"success": True}


@router.post("/api/datasets/{dataset_id}/bulk-run", response_class=JSONResponse)
async def bulk_run_dataset(dataset_id: int, payload: BulkRunRequest):
    service = get_service()
    payload.dataset_id = dataset_id
    try:
        dataset = await service.run_bulk_generate(payload)
        return dataset.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/datasets/{dataset_id}/bulk-run-stream")
async def bulk_run_dataset_stream(dataset_id: int, payload: BulkRunRequest):
    service = get_service()
    payload.dataset_id = dataset_id
    
    async def generate_stream():
        async for event in service.run_bulk_generate_stream(payload):
            yield f"data: {json_lib.dumps(event)}\n\n"
        yield "data: {\"done\": true}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# Evaluators

@router.get("/api/evaluators", response_class=JSONResponse)
async def list_evaluators():
    service = get_service()
    builtin = service.get_builtin_evaluators()
    custom = service.list_custom_evaluators()
    custom_list = [
        {
            "id": f"custom:{e.id}",
            "name": e.name,
            "description": e.description,
            "type": e.evaluator_type,
        }
        for e in custom
    ]
    return {"evaluators": builtin + custom_list}


@router.get("/api/evaluators/custom", response_class=JSONResponse)
async def list_custom_evaluators():
    service = get_service()
    evaluators = service.list_custom_evaluators()
    return {"evaluators": [e.model_dump() for e in evaluators]}


@router.get("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def get_custom_evaluator(evaluator_id: int):
    service = get_service()
    evaluator = service.get_custom_evaluator(evaluator_id)
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return evaluator.model_dump()


@router.post("/api/evaluators/custom", response_class=JSONResponse)
async def create_custom_evaluator(payload: CustomEvaluatorCreateRequest):
    service = get_service()
    evaluator = service.create_custom_evaluator(payload)
    return evaluator.model_dump()


@router.put("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def update_custom_evaluator(evaluator_id: int, payload: CustomEvaluatorUpdateRequest):
    service = get_service()
    evaluator = service.update_custom_evaluator(evaluator_id, payload)
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return evaluator.model_dump()


@router.delete("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def delete_custom_evaluator(evaluator_id: int):
    service = get_service()
    success = service.delete_custom_evaluator(evaluator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return {"success": True}


# Evaluation Jobs

@router.get("/api/eval-jobs", response_class=JSONResponse)
async def list_eval_jobs():
    service = get_service()
    jobs = service.list_eval_jobs()
    return {"jobs": [j.model_dump() for j in jobs]}


@router.get("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def get_eval_job(job_id: int):
    service = get_service()
    job = service.get_eval_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Eval job not found")
    return job.model_dump()


@router.post("/api/eval-jobs", response_class=JSONResponse)
async def create_eval_job(payload: EvalJobCreateRequest):
    service = get_service()
    job = service.create_eval_job(payload)
    return job.model_dump()


@router.post("/api/eval-jobs/{job_id}/run", response_class=JSONResponse)
async def run_eval_job(job_id: int):
    service = get_service()
    try:
        job = await service.run_eval_job(job_id)
        return job.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def delete_eval_job(job_id: int):
    service = get_service()
    success = service.delete_eval_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Eval job not found")
    return {"success": True}
