"""
Metrics Router.

Handles latency and usage dashboard:
- Summary statistics
- Model-level breakdown
- Endpoint-level breakdown
- Hourly trends
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.routers import get_service

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])


@router.get("/summary", response_class=JSONResponse)
async def get_metrics_summary(hours: int = 24):
    """Get aggregated metrics summary for the last N hours."""
    return get_service().get_metrics_summary(hours).model_dump()


@router.get("/list", response_class=JSONResponse)
async def get_metrics_list(limit: int = 100, offset: int = 0):
    """Get recent individual metrics with pagination."""
    svc = get_service()
    metrics = svc.get_metrics_list(limit, offset)
    return {"metrics": [m.model_dump() for m in metrics], "count": svc.get_metrics_count()}


@router.get("/by-model", response_class=JSONResponse)
async def get_metrics_by_model(hours: int = 24):
    """Get metrics grouped by model."""
    breakdown = get_service().get_metrics_by_model(hours)
    return {"models": [m.model_dump() for m in breakdown]}


@router.get("/by-endpoint", response_class=JSONResponse)
async def get_metrics_by_endpoint(hours: int = 24):
    """Get metrics grouped by endpoint."""
    breakdown = get_service().get_metrics_by_endpoint(hours)
    return {"endpoints": [e.model_dump() for e in breakdown]}


@router.get("/hourly", response_class=JSONResponse)
async def get_metrics_hourly(hours: int = 24):
    """Get hourly metrics breakdown for trend charts."""
    breakdown = get_service().get_metrics_hourly(hours)
    return {"hourly": [h.model_dump() for h in breakdown]}


@router.delete("", response_class=JSONResponse)
async def clear_metrics():
    """Clear all metrics data."""
    get_service().clear_metrics()
    return {"success": True}
