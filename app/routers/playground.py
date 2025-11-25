"""
Playground Router.

Handles core LLM interaction endpoints:
- Model listing and refresh
- Single-turn text generation
- Multi-turn chat (streaming & non-streaming)
- AI-powered prompt improvement
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
import json

from app.schemas.requests import GenerateRequest, ChatRequest, PromptGeneratorRequest
from app.routers import get_service

router = APIRouter(tags=["Playground"])


@router.get("/api/models", response_class=JSONResponse)
async def get_models():
    """Refresh and list available LLM models from LM Studio."""
    models = await get_service().refresh_models()
    return {"models": models}


@router.post("/api/generate", response_class=JSONResponse)
async def generate(payload: GenerateRequest):
    """Single-turn text generation with optional agent configuration."""
    return await get_service().generate(payload)


@router.post("/api/chat")
async def chat(payload: ChatRequest):
    """
    Multi-turn chat completion.
    
    Supports streaming (SSE) when stream=True.
    """
    svc = get_service()
    if payload.stream:
        async def generate_stream():
            async for event in svc.chat_stream(payload):
                yield f"data: {json.dumps(event)}\n\n"
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    return await svc.chat(payload)


@router.post("/api/prompt-generator", response_class=JSONResponse)
async def prompt_generator(payload: PromptGeneratorRequest):
    """AI-powered prompt improvement using meta-prompting."""
    return await get_service().generate_prompt(payload)
