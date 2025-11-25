"""
Request Models.

All Pydantic models for API request validation.
Organized by feature domain for easy navigation.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


# =============================================================================
# CORE / PLAYGROUND REQUESTS
# =============================================================================

class GenerateRequest(BaseModel):
    """Request for single-turn text generation."""
    agent_id: Optional[str] = None
    model_name: Optional[str] = None
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""
    role: str  # "system", "user", "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for multi-turn chat completion."""
    agent_id: Optional[str] = None
    model_name: Optional[str] = None
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    images: Optional[List[str]] = None  # Base64 encoded images


class PromptGeneratorRequest(BaseModel):
    """Request for AI-powered prompt improvement."""
    input: str


# =============================================================================
# A/B TESTING REQUESTS
# =============================================================================

class ABTestRequest(BaseModel):
    """Request for A/B testing across multiple models/agents."""
    prompt: str
    system_prompt: str = ""
    variants: List[dict]  # each: {"model_name": str} or {"agent_id": str}
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7


# =============================================================================
# TOOL MANAGEMENT REQUESTS
# =============================================================================

class ToolCreateRequest(BaseModel):
    """Request to create a new tool configuration."""
    name: str
    description: str = ""
    input_schema: dict = {}
    endpoint: str = ""
    enabled: bool = True
    models: List[str] = []
    agents: List[str] = []


class ToolUpdateRequest(BaseModel):
    """Request to update an existing tool."""
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    endpoint: Optional[str] = None
    enabled: Optional[bool] = None
    models: Optional[List[str]] = None
    agents: Optional[List[str]] = None


# =============================================================================
# PROMPT TEMPLATE REQUESTS
# =============================================================================

class PromptTemplateCreateRequest(BaseModel):
    """Request to create a new prompt template."""
    name: str
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    variables: List[str] = []


class PromptTemplateUpdateRequest(BaseModel):
    """Request to update an existing prompt template."""
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[List[str]] = None


# =============================================================================
# EVALUATION REQUESTS
# =============================================================================

class DatasetCreateRequest(BaseModel):
    """Request to create a new evaluation dataset."""
    name: str
    description: str = ""
    rows: List[dict] = []  # each: {"query": str, "response": str, "ground_truth": str}


class DatasetUpdateRequest(BaseModel):
    """Request to update an existing dataset."""
    name: Optional[str] = None
    description: Optional[str] = None
    rows: Optional[List[dict]] = None


class CustomEvaluatorCreateRequest(BaseModel):
    """Request to create a custom evaluator."""
    name: str
    description: str = ""
    evaluator_type: str  # "llm" or "code"
    llm_prompt: str = ""
    code: str = ""


class CustomEvaluatorUpdateRequest(BaseModel):
    """Request to update a custom evaluator."""
    name: Optional[str] = None
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    code: Optional[str] = None


class EvalJobCreateRequest(BaseModel):
    """Request to create an evaluation job."""
    name: str
    dataset_id: int
    evaluator_ids: List[str]  # e.g., ["builtin:f1_score", "custom:1"]
    model_name: Optional[str] = None
    agent_id: Optional[str] = None


class BulkRunRequest(BaseModel):
    """Request for bulk generation across a dataset."""
    dataset_id: int
    model_name: Optional[str] = None
    agent_id: Optional[str] = None
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7


# =============================================================================
# WORKFLOW / ORCHESTRATOR REQUESTS
# =============================================================================

class WorkflowCreateRequest(BaseModel):
    """Request to create a new workflow."""
    name: str
    description: str = ""
    nodes: List[dict] = []
    edges: List[dict] = []
    entry_node: Optional[str] = None


class WorkflowUpdateRequest(BaseModel):
    """Request to update an existing workflow."""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[dict]] = None
    edges: Optional[List[dict]] = None
    entry_node: Optional[str] = None


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""
    input_text: str


# =============================================================================
# GUARDRAIL REQUESTS
# =============================================================================

class GuardrailRuleCreateRequest(BaseModel):
    """Request to create a guardrail rule."""
    name: str
    type: str  # "pii", "keyword", "regex", "content", "llm"
    config: Dict[str, Any] = {}
    description: str = ""
    enabled: bool = True


class GuardrailRuleUpdateRequest(BaseModel):
    """Request to update a guardrail rule."""
    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


class GuardrailTestCreateRequest(BaseModel):
    """Request to create a guardrail test case."""
    name: str
    input_text: str
    expected_blocked: bool = False
    expected_flags: List[str] = []
    description: str = ""
    tags: List[str] = []


class GuardrailTestUpdateRequest(BaseModel):
    """Request to update a guardrail test case."""
    name: Optional[str] = None
    input_text: Optional[str] = None
    expected_blocked: Optional[bool] = None
    expected_flags: Optional[List[str]] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class GuardrailCheckRequest(BaseModel):
    """Request to check text against guardrails."""
    text: str
    rule_ids: Optional[List[int]] = None  # If None, use all enabled rules


# =============================================================================
# CHAT LAB REQUESTS
# =============================================================================

class ChatTreeCreateRequest(BaseModel):
    """Request to create a conversation tree."""
    name: str
    description: str = ""
    model_name: str = ""
    system_prompt: str = ""


class ChatTreeUpdateRequest(BaseModel):
    """Request to update a conversation tree."""
    name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None


class ChatMessageRequest(BaseModel):
    """Request to send a message in Chat Lab."""
    content: str
    parent_node_id: Optional[str] = None


class ChatBranchRequest(BaseModel):
    """Request to create a branch in a conversation."""
    from_node_id: str
    branch_name: Optional[str] = None


# =============================================================================
# HISTORY REQUESTS
# =============================================================================

class HistoryUpdateRequest(BaseModel):
    """Request to update a history entry."""
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    starred: Optional[bool] = None


class HistoryFilterRequest(BaseModel):
    """Filter criteria for history queries."""
    endpoint: Optional[str] = None
    model: Optional[str] = None
    success: Optional[bool] = None
    starred: Optional[bool] = None
    tags: Optional[List[str]] = None
    from_timestamp: Optional[float] = None
    to_timestamp: Optional[float] = None
    search: Optional[str] = None


class ReplayRequest(BaseModel):
    """Request to replay a historical request."""
    entry_id: int
    override_model: Optional[str] = None
    override_parameters: Optional[Dict[str, Any]] = None
