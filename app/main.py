from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.service import LocalLLMService, GenerateRequest


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
