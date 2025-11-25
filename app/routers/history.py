"""
History Router.

Handles request/response logging and replay:
- History browsing with filters
- Entry annotation (notes, tags, starring)
- Request replay with parameter override
- Statistics and cleanup
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.requests import HistoryUpdateRequest, HistoryFilterRequest, ReplayRequest
from app.routers import get_service

router = APIRouter(prefix="/api/history", tags=["History"])


# =============================================================================
# HISTORY LISTING & FILTERING
# =============================================================================

@router.get("", response_class=JSONResponse)
async def list_history(
    limit: int = 100,
    offset: int = 0,
    endpoint: str = None,
    model: str = None,
    success: bool = None,
    starred: bool = None,
    search: str = None
):
    """List history entries with optional filters."""
    filter_req = None
    if any([endpoint, model, success is not None, starred is not None, search]):
        filter_req = HistoryFilterRequest(
            endpoint=endpoint, model=model, success=success, 
            starred=starred, search=search
        )
    entries = get_service().list_history(filter_req, limit, offset)
    return {"entries": [e.model_dump() for e in entries]}


@router.get("/stats", response_class=JSONResponse)
async def get_history_stats():
    """Get history statistics (counts, success rates, etc.)."""
    return get_service().get_history_stats()


@router.get("/endpoints", response_class=JSONResponse)
async def get_history_endpoints():
    """Get list of unique endpoints in history."""
    return {"endpoints": get_service().get_history_endpoints()}


@router.get("/models", response_class=JSONResponse)
async def get_history_models():
    """Get list of unique models used in history."""
    return {"models": get_service().get_history_models()}


# =============================================================================
# INDIVIDUAL ENTRIES
# =============================================================================

@router.get("/{entry_id}", response_class=JSONResponse)
async def get_history_entry(entry_id: int):
    """Get a specific history entry with full details."""
    entry = get_service().get_history_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    return entry.model_dump()


@router.put("/{entry_id}", response_class=JSONResponse)
async def update_history_entry(entry_id: int, payload: HistoryUpdateRequest):
    """Update history entry (notes, tags, starred)."""
    result = get_service().update_history_entry(entry_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="History entry not found")
    return result.model_dump()


@router.delete("/{entry_id}", response_class=JSONResponse)
async def delete_history_entry(entry_id: int):
    """Delete a history entry."""
    return {"success": get_service().delete_history_entry(entry_id)}


# =============================================================================
# BULK OPERATIONS
# =============================================================================

@router.post("/clear", response_class=JSONResponse)
async def clear_history(keep_starred: bool = True):
    """Clear history entries (optionally keep starred)."""
    deleted = get_service().clear_history(keep_starred)
    return {"deleted": deleted, "kept_starred": keep_starred}


@router.post("/replay", response_class=JSONResponse)
async def replay_request(payload: ReplayRequest):
    """Replay a historical request with optional overrides."""
    return await get_service().replay_request(payload)
