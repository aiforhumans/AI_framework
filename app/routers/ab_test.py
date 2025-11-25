"""
A/B Test Router.

Handles side-by-side model/agent comparison testing.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas.requests import ABTestRequest
from app.routers import get_service

router = APIRouter(tags=["A/B Testing"])


@router.post("/api/ab-test", response_class=JSONResponse)
async def ab_test(payload: ABTestRequest):
    """
    Run the same prompt against multiple models/agents in parallel.
    
    Returns comparison results with latency for each variant.
    """
    results = await get_service().generate_ab(payload)
    return {"results": results}
