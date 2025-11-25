"""
Chat Lab Router.

Handles multi-turn branching conversations:
- Conversation tree management
- Message sending with LLM responses
- Branch creation and switching
- Conversation visualization
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.requests import (
    ChatTreeCreateRequest, ChatTreeUpdateRequest,
    ChatMessageRequest, ChatBranchRequest,
)
from app.routers import get_service

router = APIRouter(prefix="/api/chat-lab", tags=["Chat Lab"])


# =============================================================================
# CONVERSATION TREES
# =============================================================================

@router.get("/trees", response_class=JSONResponse)
async def list_chat_trees():
    """List all conversation trees."""
    trees = get_service().list_chat_trees()
    return {"trees": [t.model_dump() for t in trees]}


@router.get("/trees/{tree_id}", response_class=JSONResponse)
async def get_chat_tree(tree_id: int):
    """Get a specific conversation tree."""
    tree = get_service().get_chat_tree(tree_id)
    if not tree:
        raise HTTPException(status_code=404, detail="Conversation tree not found")
    return tree.model_dump()


@router.post("/trees", response_class=JSONResponse)
async def create_chat_tree(payload: ChatTreeCreateRequest):
    """Create a new conversation tree with model and system prompt."""
    return get_service().create_chat_tree(payload).model_dump()


@router.put("/trees/{tree_id}", response_class=JSONResponse)
async def update_chat_tree(tree_id: int, payload: ChatTreeUpdateRequest):
    """Update conversation tree metadata."""
    result = get_service().update_chat_tree(tree_id, payload)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation tree not found")
    return result.model_dump()


@router.delete("/trees/{tree_id}", response_class=JSONResponse)
async def delete_chat_tree(tree_id: int):
    """Delete a conversation tree."""
    return {"success": get_service().delete_chat_tree(tree_id)}


# =============================================================================
# TREE STRUCTURE & HISTORY
# =============================================================================

@router.get("/trees/{tree_id}/structure", response_class=JSONResponse)
async def get_chat_tree_structure(tree_id: int):
    """Get tree structure for visualization (nodes and edges)."""
    return get_service().get_chat_tree_structure(tree_id)


@router.get("/trees/{tree_id}/history", response_class=JSONResponse)
async def get_chat_history(tree_id: int, node_id: str = None):
    """Get conversation history up to a specific node."""
    history = get_service().get_chat_history(tree_id, node_id)
    return {"messages": [m.model_dump() for m in history]}


# =============================================================================
# MESSAGING & BRANCHING
# =============================================================================

@router.post("/trees/{tree_id}/messages", response_class=JSONResponse)
async def send_chat_message(tree_id: int, payload: ChatMessageRequest):
    """Send a user message and get LLM response."""
    return await get_service().send_chat_message(tree_id, payload)


@router.post("/trees/{tree_id}/branch", response_class=JSONResponse)
async def create_chat_branch(tree_id: int, payload: ChatBranchRequest):
    """Create a new conversation branch from a specific node."""
    return get_service().create_chat_branch(tree_id, payload)


@router.post("/trees/{tree_id}/switch", response_class=JSONResponse)
async def switch_chat_branch(tree_id: int, to_node_id: str):
    """Switch active conversation path to a specific node."""
    return get_service().switch_chat_branch(tree_id, to_node_id)


@router.delete("/trees/{tree_id}/nodes/{node_id}", response_class=JSONResponse)
async def delete_chat_node(tree_id: int, node_id: str):
    """Delete a node and all its descendants."""
    return get_service().delete_chat_node(tree_id, node_id)
