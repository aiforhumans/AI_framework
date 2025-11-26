from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json as json_lib

from app.models.service import (
    GenerateRequest,
    ChatRequest,
    PromptGeneratorRequest,
)
from app.routers import get_service

router = APIRouter()

@router.get("/api/models", response_class=JSONResponse)
async def get_models():
    service = get_service()
    models = await service.refresh_models()
    return {"models": models}


@router.post("/api/generate", response_class=JSONResponse)
async def generate(payload: GenerateRequest):
    service = get_service()
    response = await service.generate(payload)
    return response


@router.post("/api/chat")
async def chat(payload: ChatRequest):
    service = get_service()
    if payload.stream:
        async def generate_stream():
            async for event in service.chat_stream(payload):
                yield f"data: {json_lib.dumps(event)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
    else:
        response = await service.chat(payload)
        return response


@router.post("/api/prompt-generator", response_class=JSONResponse)
async def prompt_generator(payload: PromptGeneratorRequest):
    service = get_service()
    result = await service.generate_prompt(payload)
    return result
