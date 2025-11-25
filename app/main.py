from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json as json_lib

from app.models.service import (
    LocalLLMService,
    GenerateRequest,
    ChatRequest,
    PromptGeneratorRequest,
    ToolCreateRequest,
    ToolUpdateRequest,
    PromptTemplateCreateRequest,
    PromptTemplateUpdateRequest,
    ABTestRequest,
    DatasetCreateRequest,
    DatasetUpdateRequest,
    CustomEvaluatorCreateRequest,
    CustomEvaluatorUpdateRequest,
    EvalJobCreateRequest,
    BulkRunRequest,
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowRunRequest,
)


app = FastAPI(title="LLM Testing Interface")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/static")

llm_service = LocalLLMService()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    models = await llm_service.list_models()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_models": models,
            "agents": llm_service.list_agents(),
        },
    )


@app.get("/api/models", response_class=JSONResponse)
async def get_models():
    models = await llm_service.refresh_models()
    return {"models": models}


@app.post("/api/generate", response_class=JSONResponse)
async def generate(payload: GenerateRequest):
    response = await llm_service.generate(payload)
    return response


# Chat endpoint (multi-turn with streaming)


@app.post("/api/chat")
async def chat(payload: ChatRequest):
    if payload.stream:
        async def generate_stream():
            async for event in llm_service.chat_stream(payload):
                yield f"data: {json_lib.dumps(event)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    else:
        response = await llm_service.chat(payload)
        return response


# Prompt Generator endpoint


@app.post("/api/prompt-generator", response_class=JSONResponse)
async def prompt_generator(payload: PromptGeneratorRequest):
    result = await llm_service.generate_prompt(payload)
    return result


# Tool management endpoints


@app.get("/api/tools", response_class=JSONResponse)
async def list_tools():
    tools = llm_service.list_tools()
    return {"tools": tools}


@app.post("/api/tools", response_class=JSONResponse)
async def create_tool(payload: ToolCreateRequest):
    tool = llm_service.create_tool(payload)
    return tool


@app.put("/api/tools/{tool_id}", response_class=JSONResponse)
async def update_tool(tool_id: int, payload: ToolUpdateRequest):
    tool = llm_service.update_tool(tool_id, payload)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@app.delete("/api/tools/{tool_id}", response_class=JSONResponse)
async def delete_tool(tool_id: int):
    success = llm_service.delete_tool(tool_id)
    if not success:
        raise HTTPException(status_code=404, detail="Tool not found")
    return {"success": True}


@app.post("/api/tools/{tool_id}/toggle", response_class=JSONResponse)
async def toggle_tool(tool_id: int):
    tool = llm_service.toggle_tool(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


# Prompt template endpoints


@app.get("/api/prompt-templates", response_class=JSONResponse)
async def list_prompt_templates():
    templates = llm_service.list_prompt_templates()
    return {"templates": templates}


@app.post("/api/prompt-templates", response_class=JSONResponse)
async def create_prompt_template(payload: PromptTemplateCreateRequest):
    template = llm_service.create_prompt_template(payload)
    return template


@app.put("/api/prompt-templates/{template_id}", response_class=JSONResponse)
async def update_prompt_template(
    template_id: int, payload: PromptTemplateUpdateRequest
):
    template = llm_service.update_prompt_template(template_id, payload)
    if template is None:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@app.delete("/api/prompt-templates/{template_id}", response_class=JSONResponse)
async def delete_prompt_template(template_id: int):
    success = llm_service.delete_prompt_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return {"success": True}


# A/B Response Tester endpoint


@app.post("/api/ab-test", response_class=JSONResponse)
async def ab_test(payload: ABTestRequest):
    results = await llm_service.generate_ab(payload)
    return {"results": results}


# --- Evaluation Endpoints ---

# Datasets

@app.get("/api/datasets", response_class=JSONResponse)
async def list_datasets():
    datasets = llm_service.list_datasets()
    return {"datasets": [d.model_dump() for d in datasets]}


@app.get("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def get_dataset(dataset_id: int):
    dataset = llm_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.model_dump()


@app.post("/api/datasets", response_class=JSONResponse)
async def create_dataset(payload: DatasetCreateRequest):
    dataset = llm_service.create_dataset(payload)
    return dataset.model_dump()


@app.put("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def update_dataset(dataset_id: int, payload: DatasetUpdateRequest):
    dataset = llm_service.update_dataset(dataset_id, payload)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset.model_dump()


@app.delete("/api/datasets/{dataset_id}", response_class=JSONResponse)
async def delete_dataset(dataset_id: int):
    success = llm_service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"success": True}


@app.post("/api/datasets/{dataset_id}/bulk-run", response_class=JSONResponse)
async def bulk_run_dataset(dataset_id: int, payload: BulkRunRequest):
    payload.dataset_id = dataset_id
    try:
        dataset = await llm_service.run_bulk_generate(payload)
        return dataset.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/datasets/{dataset_id}/bulk-run-stream")
async def bulk_run_dataset_stream(dataset_id: int, payload: BulkRunRequest):
    payload.dataset_id = dataset_id
    
    async def generate_stream():
        async for event in llm_service.run_bulk_generate_stream(payload):
            yield f"data: {json_lib.dumps(event)}\n\n"
        yield "data: {\"done\": true}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


# Evaluators

@app.get("/api/evaluators", response_class=JSONResponse)
async def list_evaluators():
    builtin = llm_service.get_builtin_evaluators()
    custom = llm_service.list_custom_evaluators()
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


@app.get("/api/evaluators/custom", response_class=JSONResponse)
async def list_custom_evaluators():
    evaluators = llm_service.list_custom_evaluators()
    return {"evaluators": [e.model_dump() for e in evaluators]}


@app.get("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def get_custom_evaluator(evaluator_id: int):
    evaluator = llm_service.get_custom_evaluator(evaluator_id)
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return evaluator.model_dump()


@app.post("/api/evaluators/custom", response_class=JSONResponse)
async def create_custom_evaluator(payload: CustomEvaluatorCreateRequest):
    evaluator = llm_service.create_custom_evaluator(payload)
    return evaluator.model_dump()


@app.put("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def update_custom_evaluator(evaluator_id: int, payload: CustomEvaluatorUpdateRequest):
    evaluator = llm_service.update_custom_evaluator(evaluator_id, payload)
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return evaluator.model_dump()


@app.delete("/api/evaluators/custom/{evaluator_id}", response_class=JSONResponse)
async def delete_custom_evaluator(evaluator_id: int):
    success = llm_service.delete_custom_evaluator(evaluator_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evaluator not found")
    return {"success": True}


# Evaluation Jobs

@app.get("/api/eval-jobs", response_class=JSONResponse)
async def list_eval_jobs():
    jobs = llm_service.list_eval_jobs()
    return {"jobs": [j.model_dump() for j in jobs]}


@app.get("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def get_eval_job(job_id: int):
    job = llm_service.get_eval_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Eval job not found")
    return job.model_dump()


@app.post("/api/eval-jobs", response_class=JSONResponse)
async def create_eval_job(payload: EvalJobCreateRequest):
    job = llm_service.create_eval_job(payload)
    return job.model_dump()


@app.post("/api/eval-jobs/{job_id}/run", response_class=JSONResponse)
async def run_eval_job(job_id: int):
    try:
        job = await llm_service.run_eval_job(job_id)
        return job.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/api/eval-jobs/{job_id}", response_class=JSONResponse)
async def delete_eval_job(job_id: int):
    success = llm_service.delete_eval_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Eval job not found")
    return {"success": True}


# --- Workflow (Agent Orchestrator) Endpoints ---

@app.get("/api/workflows", response_class=JSONResponse)
async def list_workflows():
    workflows = llm_service.list_workflows()
    return {"workflows": [w.model_dump() for w in workflows]}


@app.get("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def get_workflow(workflow_id: int):
    workflow = llm_service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@app.post("/api/workflows", response_class=JSONResponse)
async def create_workflow(payload: WorkflowCreateRequest):
    workflow = llm_service.create_workflow(payload)
    return workflow.model_dump()


@app.put("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def update_workflow(workflow_id: int, payload: WorkflowUpdateRequest):
    workflow = llm_service.update_workflow(workflow_id, payload)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.model_dump()


@app.delete("/api/workflows/{workflow_id}", response_class=JSONResponse)
async def delete_workflow(workflow_id: int):
    success = llm_service.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True}


@app.post("/api/workflows/{workflow_id}/run", response_class=JSONResponse)
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest):
    payload.workflow_id = workflow_id
    try:
        run = await llm_service.run_workflow(payload)
        return run.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/api/workflow-runs", response_class=JSONResponse)
async def list_workflow_runs(workflow_id: int = None):
    runs = llm_service.list_workflow_runs(workflow_id)
    return {"runs": [r.model_dump() for r in runs]}


@app.get("/api/workflow-runs/{run_id}", response_class=JSONResponse)
async def get_workflow_run(run_id: int):
    runs = llm_service.list_workflow_runs()
    for run in runs:
        if run.id == run_id:
            return run.model_dump()
    raise HTTPException(status_code=404, detail="Workflow run not found")
