"""
Response Models.

All Pydantic models for API response serialization.
"""

from typing import List, Optional
from pydantic import BaseModel


# =============================================================================
# CORE / PLAYGROUND RESPONSES
# =============================================================================

class GenerateResponse(BaseModel):
    """Response for text generation."""
    agent_id: Optional[str]
    agent_name: Optional[str]
    model_name: str
    prompt: str
    system_instructions: str
    response: str
    latency_ms: float


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

class AgentConfig(BaseModel):
    """High-level agent configuration similar to an Agent Builder card."""
    id: str
    name: str
    model_name: str
    instructions: str
    max_tokens: int = 256
    temperature: float = 0.7
