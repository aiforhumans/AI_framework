from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import (
    get_service,
    playground,
    tools,
    templates,
    ab_test,
    evaluation,
    workflows,
)

app = FastAPI(title="LLM Testing Interface")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
jinja_templates = Jinja2Templates(directory="app/static")

# Register routers
app.include_router(playground.router)
app.include_router(tools.router)
app.include_router(templates.router)
app.include_router(ab_test.router)
app.include_router(evaluation.router)
app.include_router(workflows.router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    service = get_service()
    models = await service.list_models()
    return jinja_templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "available_models": models,
            "agents": service.list_agents(),
        },
    )
