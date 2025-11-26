from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.service import ABTestRequest
from app.routers import get_service

router = APIRouter()

@router.post("/api/ab-test", response_class=JSONResponse)
async def ab_test(payload: ABTestRequest):
    service = get_service()
    results = await service.generate_ab(payload)
    return {"results": results}
