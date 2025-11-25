from typing import List, Dict, Optional
from pydantic import BaseModel
import asyncio
import httpx

from app.models.tools_store import ToolStore, ToolConfig


class AgentConfig(BaseModel):
    """High-level agent configuration similar to an Agent Builder card."""

    id: str
    name: str
    model_name: str
    instructions: str
    max_tokens: int = 256
    temperature: float = 0.7


class GenerateRequest(BaseModel):
    agent_id: Optional[str] = None
    model_name: Optional[str] = None
    prompt: str
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class GenerateResponse(BaseModel):
    agent_id: Optional[str]
    agent_name: Optional[str]
    model_name: str
    prompt: str
    system_instructions: str
    response: str
    latency_ms: float


class ToolCreateRequest(BaseModel):
    name: str
    description: str = ""
    input_schema: dict = {}
    endpoint: str = ""
    enabled: bool = True
    models: List[str] = []
    agents: List[str] = []


class ToolUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[dict] = None
    endpoint: Optional[str] = None
    enabled: Optional[bool] = None
    models: Optional[List[str]] = None
    agents: Optional[List[str]] = None


LMSTUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
LMSTUDIO_CHAT_COMPLETIONS = f"{LMSTUDIO_BASE_URL}/chat/completions"
LMSTUDIO_MODELS = f"{LMSTUDIO_BASE_URL}/models/"


class LocalLLMService:
    """Abstraction for local LLM backends and agent configs.

    Currently uses stubbed models and simple, in-memory agent configurations so
    the UI and flow can be developed before integrating a real local model
    backend.
    """

    def __init__(self) -> None:
        # These will be populated from LM Studio on demand.
        self._models: List[str] = []
        # Predefined example agents
        self._agents: Dict[str, AgentConfig] = {
            "teacher-grades-3-5": AgentConfig(
                id="teacher-grades-3-5",
                name="Teacher (Grades 3-5)",
                model_name="stub-model-1",
                instructions=(
                    "Rewrite the given text so that young learners in grades 3-5 "
                    "can easily read and understand it. Focus on making the "
                    "information clear and age-appropriate."
                ),
                max_tokens=256,
                temperature=0.6,
            ),
            "default-general": AgentConfig(
                id="default-general",
                name="General Assistant",
                model_name="stub-model-2",
                instructions="You are a helpful, concise assistant.",
                max_tokens=256,
                temperature=0.7,
            ),
        }
        # Tool store for managing tool configurations
        self._tool_store = ToolStore()

    async def refresh_models(self) -> List[str]:
        """Fetch available models from LM Studio's /models/ endpoint."""

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(LMSTUDIO_MODELS)
            resp.raise_for_status()
            data = resp.json()

        models = [m.get("id") for m in data.get("data", []) if m.get("id")]
        self._models = models
        return models

    async def list_models(self) -> List[str]:
        if not self._models:
            try:
                await self.refresh_models()
            except Exception:
                # If LM Studio is not reachable, keep whatever we have (possibly empty)
                pass
        return self._models

    def list_agents(self) -> List[AgentConfig]:
        return list(self._agents.values())

    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        return self._agents.get(agent_id)

    # Tool management helpers

    def list_tools(self) -> List[ToolConfig]:
        return self._tool_store.list_tools()

    def create_tool(self, tool_request: ToolCreateRequest) -> ToolConfig:
        tool = ToolConfig(
            id=0,
            name=tool_request.name,
            description=tool_request.description,
            input_schema=tool_request.input_schema,
            endpoint=tool_request.endpoint,
            enabled=tool_request.enabled,
            models=tool_request.models,
            agents=tool_request.agents,
        )
        return self._tool_store.create_tool(tool)

    def update_tool(self, tool_id: int, update_request: ToolUpdateRequest) -> Optional[ToolConfig]:
        update_data = {
            k: v
            for k, v in update_request.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_data:
            return self._tool_store.get_tool(tool_id)
        return self._tool_store.update_tool(tool_id, update_data)

    def delete_tool(self, tool_id: int) -> bool:
        return self._tool_store.delete_tool(tool_id)

    def toggle_tool(self, tool_id: int) -> Optional[ToolConfig]:
        return self._tool_store.toggle_tool(tool_id)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        # Resolve agent and effective configuration
        agent: Optional[AgentConfig] = None
        if request.agent_id is not None:
            agent = self.get_agent(request.agent_id)

        model_name = request.model_name or (agent.model_name if agent else self._models[0])
        max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
        temperature = request.temperature or (agent.temperature if agent else 0.7)
        system_instructions = agent.instructions if agent else ""

        start = asyncio.get_event_loop().time()

        messages = []
        if system_instructions:
            messages.append({"role": "system", "content": system_instructions})
        messages.append({"role": "user", "content": request.prompt})

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                LMSTUDIO_CHAT_COMPLETIONS,
                json={
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        end = asyncio.get_event_loop().time()

        return GenerateResponse(
            agent_id=agent.id if agent else None,
            agent_name=agent.name if agent else None,
            model_name=model_name,
            prompt=request.prompt,
            system_instructions=system_instructions,
            response=content,
            latency_ms=(end - start) * 1000.0,
        )
