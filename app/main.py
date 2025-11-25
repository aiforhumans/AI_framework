from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.service import (
    LocalLLMService,
    GenerateRequest,
    ToolCreateRequest,
    ToolUpdateRequest,
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
