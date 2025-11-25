from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import asyncio
import httpx

from app.config import (
    LMSTUDIO_BASE_URL,
    LMSTUDIO_CHAT_COMPLETIONS,
    LMSTUDIO_MODELS,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TIMEOUT,
    STREAMING_TIMEOUT,
)
from app.schemas.requests import (
    GenerateRequest, ChatMessage, ChatRequest, PromptGeneratorRequest,
    ToolCreateRequest, ToolUpdateRequest,
    PromptTemplateCreateRequest, PromptTemplateUpdateRequest,
    ABTestRequest,
    DatasetCreateRequest, DatasetUpdateRequest,
    CustomEvaluatorCreateRequest, CustomEvaluatorUpdateRequest,
    EvalJobCreateRequest, BulkRunRequest,
    WorkflowCreateRequest, WorkflowUpdateRequest,
    GuardrailRuleCreateRequest, GuardrailRuleUpdateRequest,
    GuardrailTestCreateRequest, GuardrailTestUpdateRequest, GuardrailCheckRequest,
    ChatTreeCreateRequest, ChatTreeUpdateRequest, ChatMessageRequest, ChatBranchRequest,
    HistoryUpdateRequest, HistoryFilterRequest, ReplayRequest,
)
from app.models.tools_store import ToolStore, ToolConfig
from app.models.prompt_templates_store import PromptTemplateStore, PromptTemplate
from app.models.eval_store import DatasetStore, Dataset, CustomEvaluatorStore, CustomEvaluator, EvalJobStore, EvalJob
from app.models.evaluators import BUILTIN_EVALUATORS, run_builtin_evaluator
from app.models.workflow_store import (
    WorkflowStore, Workflow, WorkflowNode, WorkflowEdge,
    WorkflowRunStore, WorkflowRun, WorkflowStepResult
)
from app.models.metrics_store import (
    MetricsStore, MetricEntry, MetricsSummary, 
    ModelMetrics, EndpointMetrics, HourlyMetrics
)
from app.models.guardrail_store import (
    GuardrailStore, GuardrailRule, GuardrailTestStore, GuardrailTest,
    GuardrailEngine, GuardrailTestResult
)
from app.models.chat_lab_store import (
    ChatLabStore, ConversationTree, ConversationNode, 
    ChatMessage as ChatLabMessage
)
from app.models.history_store import HistoryStore, HistoryEntry, HistoryFilter


class AgentConfig(BaseModel):
    """High-level agent configuration similar to an Agent Builder card."""

    id: str
    name: str
    model_name: str
    instructions: str
    max_tokens: int = DEFAULT_MAX_TOKENS
    temperature: float = DEFAULT_TEMPERATURE


class GenerateResponse(BaseModel):
    """Response from text generation."""
    agent_id: Optional[str]
    agent_name: Optional[str]
    model_name: str
    prompt: str
    system_instructions: str
    response: str
    latency_ms: float


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
        # Prompt template store for Dynamic Prompt Builder
        self._prompt_template_store = PromptTemplateStore()
        # Evaluation stores
        self._dataset_store = DatasetStore()
        self._custom_evaluator_store = CustomEvaluatorStore()
        self._eval_job_store = EvalJobStore()
        # Workflow stores for Agent Orchestrator
        self._workflow_store = WorkflowStore()
        self._workflow_run_store = WorkflowRunStore()
        # Metrics store for Latency Dashboard
        self._metrics_store = MetricsStore()
        # Guardrail stores for safety testing
        self._guardrail_store = GuardrailStore()
        self._guardrail_test_store = GuardrailTestStore()
        # Chat Lab store for multi-turn branching conversations
        self._chat_lab_store = ChatLabStore()
        # History store for request/response logging
        self._history_store = HistoryStore()

    async def refresh_models(self) -> List[str]:
        """Fetch available models from LM Studio's /models/ endpoint."""

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
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

    # Prompt template helpers

    def list_prompt_templates(self, category: str = None, include_presets: bool = True) -> List[PromptTemplate]:
        if category:
            return self._prompt_template_store.list_by_category(category)
        return self._prompt_template_store.list_templates(include_presets=include_presets)

    def get_prompt_template(self, template_id: int) -> Optional[PromptTemplate]:
        return self._prompt_template_store.get_template(template_id)

    def create_prompt_template(self, request: PromptTemplateCreateRequest) -> PromptTemplate:
        template = PromptTemplate(
            id=0,
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            variables=request.variables,
        )
        return self._prompt_template_store.create_template(template)

    def update_prompt_template(
        self, template_id: int, request: PromptTemplateUpdateRequest
    ) -> Optional[PromptTemplate]:
        update_data = {
            k: v
            for k, v in request.model_dump(exclude_unset=True).items()
            if v is not None
        }
        if not update_data:
            return self._prompt_template_store.get_template(template_id)
        return self._prompt_template_store.update_template(template_id, update_data)

    def delete_prompt_template(self, template_id: int) -> bool:
        return self._prompt_template_store.delete_template(template_id)

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

        prompt_length = len(request.prompt) + len(system_instructions)
        error_msg = None
        content = ""
        prompt_tokens = 0
        completion_tokens = 0

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
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
            
            # Extract token usage if available
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
        except Exception as e:
            error_msg = str(e)
            
        end = asyncio.get_event_loop().time()
        latency_ms = (end - start) * 1000.0

        # Record metrics
        self._metrics_store.record(
            endpoint="/api/generate",
            model_name=model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            prompt_length=prompt_length,
            response_length=len(content),
            max_tokens_requested=max_tokens,
            temperature=temperature,
            agent_id=agent.id if agent else None,
            agent_name=agent.name if agent else None,
            success=error_msg is None,
            error=error_msg,
        )

        # Record history
        self._history_store.record(
            endpoint="generate",
            model=model_name,
            agent_id=agent.id if agent else None,
            prompt=request.prompt,
            system_prompt=system_instructions,
            parameters={"max_tokens": max_tokens, "temperature": temperature},
            response=content,
            error=error_msg,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            success=error_msg is None,
        )

        if error_msg:
            raise Exception(error_msg)

        return GenerateResponse(
            agent_id=agent.id if agent else None,
            agent_name=agent.name if agent else None,
            model_name=model_name,
            prompt=request.prompt,
            system_instructions=system_instructions,
            response=content,
            latency_ms=latency_ms,
        )

    async def chat(self, request: ChatRequest) -> dict:
        """Multi-turn chat endpoint."""
        agent: Optional[AgentConfig] = None
        if request.agent_id:
            agent = self.get_agent(request.agent_id)

        model_name = request.model_name or (agent.model_name if agent else (self._models[0] if self._models else "unknown"))
        max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
        temperature = request.temperature if request.temperature is not None else (agent.temperature if agent else 0.7)

        # Convert messages to API format
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        prompt_length = sum(len(m.content) for m in request.messages)

        start = asyncio.get_event_loop().time()
        error_msg = None
        content = ""
        prompt_tokens = 0
        completion_tokens = 0

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
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
            # Extract token usage if available
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
        except Exception as e:
            error_msg = str(e)

        end = asyncio.get_event_loop().time()
        latency_ms = round((end - start) * 1000.0, 1)

        # Record metrics
        self._metrics_store.record(
            endpoint="chat",
            model_name=model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            prompt_length=prompt_length,
            response_length=len(content),
            max_tokens_requested=max_tokens,
            temperature=temperature,
            agent_id=request.agent_id,
            agent_name=agent.name if agent else None,
            success=error_msg is None,
            error=error_msg,
        )

        # Record history
        self._history_store.record(
            endpoint="chat",
            model=model_name,
            agent_id=request.agent_id,
            messages=messages,
            parameters={"max_tokens": max_tokens, "temperature": temperature},
            response=content,
            error=error_msg,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            success=error_msg is None,
        )

        if error_msg:
            return {
                "response": f"Error: {error_msg}",
                "model_name": model_name,
                "latency_ms": latency_ms,
            }

        return {
            "response": content,
            "model_name": model_name,
            "latency_ms": latency_ms,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }

    async def chat_stream(self, request: ChatRequest):
        """Multi-turn chat with streaming response."""
        agent: Optional[AgentConfig] = None
        if request.agent_id:
            agent = self.get_agent(request.agent_id)

        model_name = request.model_name or (agent.model_name if agent else (self._models[0] if self._models else "unknown"))
        max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
        temperature = request.temperature if request.temperature is not None else (agent.temperature if agent else 0.7)

        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        start = asyncio.get_event_loop().time()

        async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
            async with client.stream(
                "POST",
                LMSTUDIO_CHAT_COMPLETIONS,
                json={
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": True,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta:
                                yield {"content": delta["content"]}
                        except Exception:
                            pass

        end = asyncio.get_event_loop().time()
        yield {
            "done": True,
            "model_name": model_name,
            "latency_ms": round((end - start) * 1000.0, 1),
        }

    async def generate_prompt(self, request: PromptGeneratorRequest) -> dict:
        """Generate an improved prompt using the meta-prompt."""
        meta_prompt = '''Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, TORTURE HIM BY REVERSING the order! Never begin examples with conclusions!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a note of this. For example: "(Note: These examples are significantly shortened for readability. Real-world inputs and outputs would be more detailed.)"]

# Notes [optional]

[optional: edge cases, details, and an area to call or am am am I allowed to anything the user should pay attention to]'''

        model_name = self._models[0] if self._models else "unknown"

        async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
            resp = await client.post(
                LMSTUDIO_CHAT_COMPLETIONS,
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": meta_prompt},
                        {"role": "user", "content": request.input},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
            )
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        return {"prompt": content}

    async def generate_ab(self, request: ABTestRequest) -> List[dict]:
        """Run the same prompt against multiple models/agents in parallel."""

        async def run_variant(variant: dict) -> dict:
            agent: Optional[AgentConfig] = None
            agent_id = variant.get("agent_id")
            model_name = variant.get("model_name")
            if agent_id:
                agent = self.get_agent(agent_id)

            effective_model = model_name or (agent.model_name if agent else self._models[0] if self._models else "unknown")
            effective_system = request.system_prompt or (agent.instructions if agent else "")
            max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
            temperature = request.temperature or (agent.temperature if agent else 0.7)

            messages = []
            if effective_system:
                messages.append({"role": "system", "content": effective_system})
            messages.append({"role": "user", "content": request.prompt})

            prompt_length = len(request.prompt) + len(effective_system)
            start = asyncio.get_event_loop().time()
            content = ""
            error = None
            prompt_tokens = 0
            completion_tokens = 0

            try:
                async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                    resp = await client.post(
                        LMSTUDIO_CHAT_COMPLETIONS,
                        json={
                            "model": effective_model,
                            "messages": messages,
                            "max_tokens": max_tokens,
                            "temperature": temperature,
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                content = data["choices"][0]["message"]["content"]
                
                # Extract token usage
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
            except Exception as e:
                error = str(e)

            end = asyncio.get_event_loop().time()
            latency_ms = (end - start) * 1000.0

            # Record metrics
            self._metrics_store.record(
                endpoint="/api/ab-test",
                model_name=effective_model,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                prompt_length=prompt_length,
                response_length=len(content),
                max_tokens_requested=max_tokens,
                temperature=temperature,
                agent_id=agent_id,
                agent_name=agent.name if agent else None,
                success=error is None,
                error=error,
            )

            return {
                "variant": variant,
                "model_name": effective_model,
                "agent_id": agent_id,
                "agent_name": agent.name if agent else None,
                "response": content,
                "error": error,
                "latency_ms": latency_ms,
            }

        results = await asyncio.gather(*[run_variant(v) for v in request.variants])
        return list(results)

    # --- Dataset Management ---

    def list_datasets(self) -> List[Dataset]:
        return self._dataset_store.list_all()

    def get_dataset(self, dataset_id: int) -> Optional[Dataset]:
        return self._dataset_store.get(dataset_id)

    def create_dataset(self, request: DatasetCreateRequest) -> Dataset:
        return self._dataset_store.create(
            name=request.name,
            description=request.description,
            rows=request.rows,
        )

    def update_dataset(self, dataset_id: int, request: DatasetUpdateRequest) -> Optional[Dataset]:
        return self._dataset_store.update(
            dataset_id,
            name=request.name,
            description=request.description,
            rows=request.rows,
        )

    def delete_dataset(self, dataset_id: int) -> bool:
        return self._dataset_store.delete(dataset_id)

    # --- Custom Evaluator Management ---

    def list_custom_evaluators(self) -> List[CustomEvaluator]:
        return self._custom_evaluator_store.list_all()

    def get_custom_evaluator(self, evaluator_id: int) -> Optional[CustomEvaluator]:
        return self._custom_evaluator_store.get(evaluator_id)

    def create_custom_evaluator(self, request: CustomEvaluatorCreateRequest) -> CustomEvaluator:
        return self._custom_evaluator_store.create(
            name=request.name,
            evaluator_type=request.evaluator_type,
            description=request.description,
            llm_prompt=request.llm_prompt,
            code=request.code,
        )

    def update_custom_evaluator(self, evaluator_id: int, request: CustomEvaluatorUpdateRequest) -> Optional[CustomEvaluator]:
        return self._custom_evaluator_store.update(
            evaluator_id,
            name=request.name,
            description=request.description,
            llm_prompt=request.llm_prompt,
            code=request.code,
        )

    def delete_custom_evaluator(self, evaluator_id: int) -> bool:
        return self._custom_evaluator_store.delete(evaluator_id)

    # --- Evaluation Job Management ---

    def list_eval_jobs(self) -> List[EvalJob]:
        return self._eval_job_store.list_all()

    def get_eval_job(self, job_id: int) -> Optional[EvalJob]:
        return self._eval_job_store.get(job_id)

    def create_eval_job(self, request: EvalJobCreateRequest) -> EvalJob:
        return self._eval_job_store.create(
            name=request.name,
            dataset_id=request.dataset_id,
            evaluator_ids=request.evaluator_ids,
            model_name=request.model_name,
            agent_id=request.agent_id,
        )

    def delete_eval_job(self, job_id: int) -> bool:
        return self._eval_job_store.delete(job_id)

    async def run_bulk_generate(self, request: BulkRunRequest) -> Dataset:
        """Generate responses for all queries in a dataset using a model/agent."""
        dataset = self._dataset_store.get(request.dataset_id)
        if not dataset:
            raise ValueError(f"Dataset {request.dataset_id} not found")

        agent: Optional[AgentConfig] = None
        if request.agent_id:
            agent = self.get_agent(request.agent_id)

        model_name = request.model_name or (agent.model_name if agent else (self._models[0] if self._models else "unknown"))
        system_prompt = agent.instructions if agent else ""
        max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
        temperature = request.temperature or (agent.temperature if agent else 0.7)

        updated_rows = []
        for row in dataset.rows:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": row.query})

            try:
                async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
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
                response = data["choices"][0]["message"]["content"]
            except Exception as e:
                response = f"[Error: {str(e)}]"

            updated_rows.append({
                "query": row.query,
                "response": response,
                "ground_truth": row.ground_truth,
                "metadata": row.metadata,
            })

        # Update dataset with generated responses
        return self._dataset_store.update(request.dataset_id, rows=updated_rows)

    async def run_bulk_generate_stream(self, request: BulkRunRequest):
        """Generate responses with streaming updates for live display."""
        dataset = self._dataset_store.get(request.dataset_id)
        if not dataset:
            yield {"error": f"Dataset {request.dataset_id} not found"}
            return

        agent: Optional[AgentConfig] = None
        if request.agent_id:
            agent = self.get_agent(request.agent_id)

        model_name = request.model_name or (agent.model_name if agent else (self._models[0] if self._models else "unknown"))
        system_prompt = agent.instructions if agent else ""
        max_tokens = request.max_tokens or (agent.max_tokens if agent else 256)
        temperature = request.temperature or (agent.temperature if agent else 0.7)

        total = len(dataset.rows)
        updated_rows = []

        for idx, row in enumerate(dataset.rows):
            # Send progress update
            yield {
                "type": "progress",
                "index": idx,
                "total": total,
                "query": row.query[:100] + "..." if len(row.query) > 100 else row.query
            }

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": row.query})

            prompt_length = len(row.query) + len(system_prompt)
            start = asyncio.get_event_loop().time()
            response = ""
            error = None
            prompt_tokens = 0
            completion_tokens = 0

            try:
                async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
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
                response = data["choices"][0]["message"]["content"]
                
                # Extract token usage
                usage = data.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
            except Exception as e:
                response = f"[Error: {str(e)}]"
                error = str(e)

            end = asyncio.get_event_loop().time()
            latency_ms = (end - start) * 1000.0

            # Record metrics
            self._metrics_store.record(
                endpoint="/api/bulk-generate",
                model_name=model_name,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                prompt_length=prompt_length,
                response_length=len(response),
                max_tokens_requested=max_tokens,
                temperature=temperature,
                agent_id=request.agent_id,
                agent_name=agent.name if agent else None,
                success=error is None,
                error=error,
            )

            updated_rows.append({
                "query": row.query,
                "response": response,
                "ground_truth": row.ground_truth,
                "metadata": row.metadata,
            })

            # Send response update
            yield {
                "type": "response",
                "index": idx,
                "total": total,
                "query": row.query,
                "response": response,
                "ground_truth": row.ground_truth,
                "error": error
            }

        # Update dataset with generated responses
        self._dataset_store.update(request.dataset_id, rows=updated_rows)

    async def run_eval_job(self, job_id: int) -> EvalJob:
        """Run evaluation job: apply evaluators to each row in the dataset."""
        job = self._eval_job_store.get(job_id)
        if not job:
            raise ValueError(f"Eval job {job_id} not found")

        dataset = self._dataset_store.get(job.dataset_id)
        if not dataset:
            self._eval_job_store.update_status(job_id, "failed", error_message="Dataset not found")
            raise ValueError(f"Dataset {job.dataset_id} not found")

        self._eval_job_store.update_status(job_id, "running")

        results = []
        scores_by_evaluator: Dict[str, List[float]] = {}

        for row_index, row in enumerate(dataset.rows):
            response = row.response or ""
            ground_truth = row.ground_truth or ""

            for evaluator_id in job.evaluator_ids:
                if evaluator_id.startswith("builtin:"):
                    builtin_id = evaluator_id.split(":", 1)[1]
                    result = run_builtin_evaluator(builtin_id, response, ground_truth)
                elif evaluator_id.startswith("custom:"):
                    custom_id = int(evaluator_id.split(":", 1)[1])
                    result = await self._run_custom_evaluator(custom_id, row.query, response, ground_truth)
                else:
                    result = {"score": 0.0, "reason": f"Unknown evaluator format: {evaluator_id}", "error": True}

                results.append({
                    "row_index": row_index,
                    "evaluator_id": evaluator_id,
                    "score": result.get("score", 0.0),
                    "reason": result.get("reason", ""),
                    "error": result.get("error", False),
                })

                if evaluator_id not in scores_by_evaluator:
                    scores_by_evaluator[evaluator_id] = []
                if not result.get("error"):
                    scores_by_evaluator[evaluator_id].append(result.get("score", 0.0))

        # Compute aggregate scores
        aggregate_scores = {}
        for eid, scores in scores_by_evaluator.items():
            if scores:
                aggregate_scores[eid] = sum(scores) / len(scores)
            else:
                aggregate_scores[eid] = 0.0

        self._eval_job_store.update_status(job_id, "completed", results=results, aggregate_scores=aggregate_scores)
        return self._eval_job_store.get(job_id)

    async def _run_custom_evaluator(self, evaluator_id: int, query: str, response: str, ground_truth: str) -> dict:
        """Run a custom evaluator (LLM-based or code-based)."""
        evaluator = self._custom_evaluator_store.get(evaluator_id)
        if not evaluator:
            return {"score": 0.0, "reason": f"Custom evaluator {evaluator_id} not found", "error": True}

        if evaluator.evaluator_type == "code":
            return self._run_code_evaluator(evaluator.code, query, response, ground_truth)
        elif evaluator.evaluator_type == "llm":
            return await self._run_llm_evaluator(evaluator.llm_prompt, query, response, ground_truth)
        else:
            return {"score": 0.0, "reason": f"Unknown evaluator type: {evaluator.evaluator_type}", "error": True}

    def _run_code_evaluator(self, code: str, query: str, response: str, ground_truth: str) -> dict:
        """Execute Python code evaluator in a sandboxed manner."""
        try:
            local_vars = {}
            exec(code, {"__builtins__": {"len": len, "str": str, "int": int, "float": float, "bool": bool, "list": list, "dict": dict, "min": min, "max": max, "sum": sum, "abs": abs, "round": round}}, local_vars)

            # Find the evaluator function (first callable in local_vars)
            eval_fn = None
            for name, val in local_vars.items():
                if callable(val):
                    eval_fn = val
                    break

            if not eval_fn:
                return {"score": 0.0, "reason": "No evaluator function found in code", "error": True}

            result = eval_fn(query=query, response=response, ground_truth=ground_truth)
            if isinstance(result, dict) and "score" in result:
                return result
            else:
                return {"score": float(result) if isinstance(result, (int, float)) else 0.0, "reason": ""}
        except Exception as e:
            return {"score": 0.0, "reason": f"Code execution error: {str(e)}", "error": True}

    async def _run_llm_evaluator(self, llm_prompt: str, query: str, response: str, ground_truth: str) -> dict:
        """Run LLM-based evaluator using the model."""
        # Substitute variables in the prompt
        prompt = llm_prompt.replace("{{query}}", query).replace("{{response}}", response).replace("{{ground_truth}}", ground_truth)

        try:
            model_name = self._models[0] if self._models else "unknown"
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(
                    LMSTUDIO_CHAT_COMPLETIONS,
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are an evaluation assistant. Return ONLY a JSON object with 'score' (0-1) and 'reason' fields."},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 256,
                        "temperature": 0.0,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            content = data["choices"][0]["message"]["content"]
            # Try to parse JSON from response
            import json
            import re
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                result = json.loads(json_match.group())
                return {"score": float(result.get("score", 0)), "reason": result.get("reason", "")}
            else:
                return {"score": 0.0, "reason": f"Could not parse LLM response: {content}", "error": True}
        except Exception as e:
            return {"score": 0.0, "reason": f"LLM evaluator error: {str(e)}", "error": True}

    def get_builtin_evaluators(self) -> List[dict]:
        """Return list of built-in evaluators with metadata."""
        return [
            {
                "id": f"builtin:{key}",
                "name": val["name"],
                "description": val["description"],
                "type": "builtin",
                "requires_ground_truth": val["requires_ground_truth"],
            }
            for key, val in BUILTIN_EVALUATORS.items()
        ]

    # --- Workflow Management ---

    def list_workflows(self) -> List[Workflow]:
        return self._workflow_store.list_all()

    def get_workflow(self, workflow_id: int) -> Optional[Workflow]:
        return self._workflow_store.get(workflow_id)

    def create_workflow(self, request: WorkflowCreateRequest) -> Workflow:
        return self._workflow_store.create(
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            edges=request.edges,
            entry_node=request.entry_node,
        )

    def update_workflow(self, workflow_id: int, request: WorkflowUpdateRequest) -> Optional[Workflow]:
        return self._workflow_store.update(
            workflow_id,
            name=request.name,
            description=request.description,
            nodes=request.nodes,
            edges=request.edges,
            entry_node=request.entry_node,
        )

    def delete_workflow(self, workflow_id: int) -> bool:
        return self._workflow_store.delete(workflow_id)

    # --- Workflow Run Management ---

    def list_workflow_runs(self, workflow_id: int = None) -> List[WorkflowRun]:
        if workflow_id:
            return self._workflow_run_store.list_by_workflow(workflow_id)
        return self._workflow_run_store.list_all()

    def get_workflow_run(self, run_id: int) -> Optional[WorkflowRun]:
        return self._workflow_run_store.get(run_id)

    def delete_workflow_run(self, run_id: int) -> bool:
        return self._workflow_run_store.delete(run_id)

    async def run_workflow(self, workflow_id: int, input_text: str):
        """Execute a workflow and stream step results."""
        workflow = self._workflow_store.get(workflow_id)
        if not workflow:
            yield {"error": f"Workflow {workflow_id} not found"}
            return

        if not workflow.nodes:
            yield {"error": "Workflow has no nodes"}
            return

        # Create a run record
        run = self._workflow_run_store.create(workflow_id, workflow.name, input_text)
        yield {"type": "run_started", "run_id": run.id}

        # Build adjacency list for traversal
        adjacency: Dict[str, List[tuple]] = {}  # node_id -> [(target_id, edge_label)]
        for edge in workflow.edges:
            if edge.source not in adjacency:
                adjacency[edge.source] = []
            adjacency[edge.source].append((edge.target, edge.label, edge.condition))

        # Find entry node
        entry_node_id = workflow.entry_node
        if not entry_node_id and workflow.nodes:
            entry_node_id = workflow.nodes[0].id

        # Build node lookup
        nodes_by_id = {n.id: n for n in workflow.nodes}

        # Execute workflow
        current_output = input_text
        visited = set()
        queue = [entry_node_id]
        final_output = ""
        error_occurred = False

        while queue and not error_occurred:
            node_id = queue.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)

            node = nodes_by_id.get(node_id)
            if not node:
                continue

            yield {"type": "step_started", "node_id": node.id, "node_label": node.label}

            step_result = await self._execute_node(node, current_output, input_text)
            
            # Record step
            self._workflow_run_store.add_step(run.id, step_result)

            yield {
                "type": "step_completed",
                "node_id": node.id,
                "node_label": node.label,
                "node_type": node.type,
                "output": step_result.output_text,
                "latency_ms": step_result.latency_ms,
                "error": step_result.error,
            }

            if step_result.error:
                error_occurred = True
                self._workflow_run_store.complete(run.id, "", "failed", step_result.error)
                yield {"type": "run_failed", "error": step_result.error}
                return

            current_output = step_result.output_text
            final_output = current_output

            # Determine next nodes based on edges
            if node_id in adjacency:
                for target_id, edge_label, condition in adjacency[node_id]:
                    if condition:
                        # Conditional edge - check if condition matches
                        # For condition nodes, output is "true" or "false"
                        if node.type == "condition":
                            if condition.lower() == current_output.lower().strip():
                                queue.append(target_id)
                        else:
                            queue.append(target_id)
                    else:
                        queue.append(target_id)

        # Complete the run
        self._workflow_run_store.complete(run.id, final_output, "completed")
        yield {"type": "run_completed", "final_output": final_output, "run_id": run.id}

    async def _execute_node(self, node: WorkflowNode, current_input: str, original_input: str) -> WorkflowStepResult:
        """Execute a single workflow node."""
        start = asyncio.get_event_loop().time()
        output = ""
        error = None

        try:
            if node.type == "agent":
                output = await self._execute_agent_node(node.config, current_input)
            elif node.type == "condition":
                output = self._execute_condition_node(node.config, current_input)
            elif node.type == "transform":
                output = self._execute_transform_node(node.config, current_input, original_input)
            elif node.type == "output":
                output = current_input  # Pass through
            else:
                output = current_input
        except Exception as e:
            error = str(e)
            output = ""

        end = asyncio.get_event_loop().time()

        return WorkflowStepResult(
            node_id=node.id,
            node_label=node.label,
            node_type=node.type,
            input_text=current_input[:500],  # Truncate for storage
            output_text=output,
            latency_ms=round((end - start) * 1000, 1),
            error=error,
        )

    async def _execute_agent_node(self, config: dict, input_text: str) -> str:
        """Execute an agent node - call LLM with configuration."""
        agent_id = config.get("agent_id")
        model_name = config.get("model_name")
        system_prompt = config.get("system_prompt", "")
        max_tokens = config.get("max_tokens", 256)
        temperature = config.get("temperature", 0.7)

        # Resolve agent if specified
        agent = None
        if agent_id:
            agent = self.get_agent(agent_id)
            if agent:
                system_prompt = system_prompt or agent.instructions
                model_name = model_name or agent.model_name
                max_tokens = max_tokens or agent.max_tokens
                temperature = temperature if temperature is not None else agent.temperature

        # Default model
        if not model_name:
            model_name = self._models[0] if self._models else "unknown"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": input_text})

        prompt_length = len(input_text) + len(system_prompt)
        start = asyncio.get_event_loop().time()
        content = ""
        error_msg = None
        prompt_tokens = 0
        completion_tokens = 0

        try:
            async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
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
            
            # Extract token usage
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
        except Exception as e:
            error_msg = str(e)

        end = asyncio.get_event_loop().time()
        latency_ms = (end - start) * 1000.0

        # Record metrics
        self._metrics_store.record(
            endpoint="/api/workflow",
            model_name=model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            prompt_length=prompt_length,
            response_length=len(content),
            max_tokens_requested=max_tokens,
            temperature=temperature,
            agent_id=agent_id,
            agent_name=agent.name if agent else None,
            success=error_msg is None,
            error=error_msg,
        )

        if error_msg:
            raise Exception(error_msg)

        return content

    def _execute_condition_node(self, config: dict, input_text: str) -> str:
        """Evaluate a condition and return 'true' or 'false'."""
        variable = config.get("variable", "input")
        operator = config.get("operator", "contains")
        value = config.get("value", "")

        # Get the value to check
        check_value = input_text if variable == "input" else str(config.get(variable, input_text))

        # Evaluate condition
        result = False
        if operator == "contains":
            result = value.lower() in check_value.lower()
        elif operator == "equals":
            result = check_value.strip().lower() == str(value).lower()
        elif operator == "starts_with":
            result = check_value.lower().startswith(value.lower())
        elif operator == "ends_with":
            result = check_value.lower().endswith(value.lower())
        elif operator == "length_gt":
            result = len(check_value) > int(value)
        elif operator == "length_lt":
            result = len(check_value) < int(value)
        elif operator == "not_empty":
            result = len(check_value.strip()) > 0

        return "true" if result else "false"

    def _execute_transform_node(self, config: dict, current_input: str, original_input: str) -> str:
        """Transform input using a template."""
        template = config.get("template", "{{input}}")
        
        # Replace placeholders
        output = template.replace("{{input}}", current_input)
        output = output.replace("{{original_input}}", original_input)
        output = output.replace("{{prev_output}}", current_input)
        
        return output

    # --- Metrics API ---

    def get_metrics_summary(self, hours: int = 24) -> MetricsSummary:
        """Get aggregated metrics summary."""
        return self._metrics_store.get_summary(hours)

    def get_metrics_list(self, limit: int = 100, offset: int = 0) -> List[MetricEntry]:
        """Get recent metrics list."""
        return self._metrics_store.list_all(limit, offset)

    def get_metrics_by_model(self, hours: int = 24) -> List[ModelMetrics]:
        """Get metrics grouped by model."""
        return self._metrics_store.get_model_breakdown(hours)

    def get_metrics_by_endpoint(self, hours: int = 24) -> List[EndpointMetrics]:
        """Get metrics grouped by endpoint."""
        return self._metrics_store.get_endpoint_breakdown(hours)

    def get_metrics_hourly(self, hours: int = 24) -> List[HourlyMetrics]:
        """Get hourly metrics breakdown."""
        return self._metrics_store.get_hourly_breakdown(hours)

    def clear_metrics(self):
        """Clear all metrics data."""
        self._metrics_store.clear()

    def get_metrics_count(self) -> int:
        """Get total metrics count."""
        return self._metrics_store.count()

    # --- Guardrail API ---

    def list_guardrail_rules(self) -> List[GuardrailRule]:
        """List all guardrail rules."""
        return self._guardrail_store.list_all()

    def get_guardrail_rule(self, rule_id: int) -> Optional[GuardrailRule]:
        """Get a specific guardrail rule."""
        return self._guardrail_store.get(rule_id)

    def create_guardrail_rule(self, request: GuardrailRuleCreateRequest) -> GuardrailRule:
        """Create a new guardrail rule."""
        return self._guardrail_store.create(
            name=request.name,
            type=request.type,
            config=request.config,
            description=request.description,
            enabled=request.enabled,
        )

    def update_guardrail_rule(self, rule_id: int, request: GuardrailRuleUpdateRequest) -> Optional[GuardrailRule]:
        """Update a guardrail rule."""
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.type is not None:
            updates["type"] = request.type
        if request.config is not None:
            updates["config"] = request.config
        if request.description is not None:
            updates["description"] = request.description
        if request.enabled is not None:
            updates["enabled"] = request.enabled
        return self._guardrail_store.update(rule_id, **updates)

    def delete_guardrail_rule(self, rule_id: int) -> bool:
        """Delete a guardrail rule."""
        return self._guardrail_store.delete(rule_id)

    def toggle_guardrail_rule(self, rule_id: int) -> Optional[GuardrailRule]:
        """Toggle a guardrail rule's enabled status."""
        return self._guardrail_store.toggle(rule_id)

    def list_guardrail_tests(self) -> List[GuardrailTest]:
        """List all guardrail test cases."""
        return self._guardrail_test_store.list_all()

    def get_guardrail_test(self, test_id: int) -> Optional[GuardrailTest]:
        """Get a specific guardrail test case."""
        return self._guardrail_test_store.get(test_id)

    def create_guardrail_test(self, request: GuardrailTestCreateRequest) -> GuardrailTest:
        """Create a new guardrail test case."""
        return self._guardrail_test_store.create(
            name=request.name,
            input_text=request.input_text,
            expected_blocked=request.expected_blocked,
            expected_flags=request.expected_flags,
            description=request.description,
            tags=request.tags,
        )

    def update_guardrail_test(self, test_id: int, request: GuardrailTestUpdateRequest) -> Optional[GuardrailTest]:
        """Update a guardrail test case."""
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.input_text is not None:
            updates["input_text"] = request.input_text
        if request.expected_blocked is not None:
            updates["expected_blocked"] = request.expected_blocked
        if request.expected_flags is not None:
            updates["expected_flags"] = request.expected_flags
        if request.description is not None:
            updates["description"] = request.description
        if request.tags is not None:
            updates["tags"] = request.tags
        return self._guardrail_test_store.update(test_id, **updates)

    def delete_guardrail_test(self, test_id: int) -> bool:
        """Delete a guardrail test case."""
        return self._guardrail_test_store.delete(test_id)

    def check_guardrails(self, request: GuardrailCheckRequest) -> GuardrailTestResult:
        """Run guardrail checks on input text."""
        if request.rule_ids:
            rules = [self._guardrail_store.get(rid) for rid in request.rule_ids]
            rules = [r for r in rules if r is not None]
        else:
            rules = self._guardrail_store.list_enabled()
        
        return GuardrailEngine.check_text(request.text, rules)

    def run_guardrail_test_suite(self, rule_ids: Optional[List[int]] = None, 
                                  test_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Run guardrail test suite and return results."""
        # Get rules to test
        if rule_ids:
            rules = [self._guardrail_store.get(rid) for rid in rule_ids]
            rules = [r for r in rules if r is not None]
        else:
            rules = self._guardrail_store.list_enabled()
        
        # Get test cases
        if test_ids:
            tests = [self._guardrail_test_store.get(tid) for tid in test_ids]
            tests = [t for t in tests if t is not None]
        else:
            tests = self._guardrail_test_store.list_all()
        
        results = []
        passed = 0
        failed = 0
        
        for test in tests:
            result = GuardrailEngine.check_text(test.input_text, rules)
            
            # Check if result matches expectations
            block_match = result.blocked == test.expected_blocked
            
            # Check if expected flags were triggered
            triggered_names = [f["rule_name"] for f in result.flags]
            flags_match = all(ef in triggered_names for ef in test.expected_flags)
            
            test_passed = block_match and flags_match
            
            if test_passed:
                passed += 1
            else:
                failed += 1
            
            results.append({
                "test_id": test.id,
                "test_name": test.name,
                "input_text": test.input_text[:100] + "..." if len(test.input_text) > 100 else test.input_text,
                "expected_blocked": test.expected_blocked,
                "actual_blocked": result.blocked,
                "expected_flags": test.expected_flags,
                "actual_flags": triggered_names,
                "passed": test_passed,
                "block_match": block_match,
                "flags_match": flags_match,
                "execution_time_ms": result.execution_time_ms,
                "details": result.flags,
            })
        
        return {
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(tests) * 100) if tests else 0,
            "rules_tested": [r.name for r in rules],
            "results": results,
        }

    # -------------------------------------------------------------------------
    # Chat Lab Methods (Multi-Turn Branching Conversations)
    # -------------------------------------------------------------------------
    
    def list_chat_trees(self) -> List[ConversationTree]:
        """List all conversation trees."""
        return self._chat_lab_store.list_trees()
    
    def get_chat_tree(self, tree_id: int) -> Optional[ConversationTree]:
        """Get a specific conversation tree."""
        return self._chat_lab_store.get_tree(tree_id)
    
    def create_chat_tree(self, request: ChatTreeCreateRequest) -> ConversationTree:
        """Create a new conversation tree."""
        return self._chat_lab_store.create_tree(
            name=request.name,
            description=request.description,
            model_name=request.model_name,
            system_prompt=request.system_prompt
        )
    
    def update_chat_tree(self, tree_id: int, request: ChatTreeUpdateRequest) -> Optional[ConversationTree]:
        """Update conversation tree metadata."""
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.model_name is not None:
            updates["model_name"] = request.model_name
        if request.system_prompt is not None:
            updates["system_prompt"] = request.system_prompt
        return self._chat_lab_store.update_tree(tree_id, **updates)
    
    def delete_chat_tree(self, tree_id: int) -> bool:
        """Delete a conversation tree."""
        return self._chat_lab_store.delete_tree(tree_id)
    
    def get_chat_tree_structure(self, tree_id: int) -> Dict:
        """Get tree structure for visualization."""
        return self._chat_lab_store.get_tree_structure(tree_id)
    
    def get_chat_history(self, tree_id: int, node_id: str = None) -> List[ChatLabMessage]:
        """Get conversation history up to a specific node."""
        return self._chat_lab_store.get_conversation_history(tree_id, node_id)
    
    async def send_chat_message(self, tree_id: int, request: ChatMessageRequest) -> Dict:
        """Send a user message and get assistant response."""
        import time
        
        tree = self._chat_lab_store.get_tree(tree_id)
        if not tree:
            return {"error": "Conversation tree not found"}
        
        # Add user message
        user_node = self._chat_lab_store.add_message(
            tree_id=tree_id,
            role="user",
            content=request.content,
            parent_node_id=request.parent_node_id
        )
        
        if not user_node:
            return {"error": "Failed to add user message"}
        
        # Build conversation history for LLM
        history = self._chat_lab_store.get_conversation_history(tree_id)
        messages = []
        
        # Add system prompt if set
        if tree.system_prompt:
            messages.append({"role": "system", "content": tree.system_prompt})
        
        # Add conversation history
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Call LLM
        model_name = tree.model_name or (self._models[0] if self._models else None)
        if not model_name:
            return {"error": "No model available"}
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": 1024,
                    "temperature": 0.7,
                    "stream": False
                }
                
                resp = await client.post(LMSTUDIO_CHAT_COMPLETIONS, json=payload)
                resp.raise_for_status()
                data = resp.json()
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            assistant_content = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # Add assistant message
            assistant_node = self._chat_lab_store.add_message(
                tree_id=tree_id,
                role="assistant",
                content=assistant_content,
                metadata={
                    "latency_ms": latency_ms,
                    "model": model_name,
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
            )
            
            # Record metrics
            self._metrics_store.record(
                endpoint="chat_lab",
                model=model_name,
                latency_ms=latency_ms,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                success=True
            )
            
            return {
                "user_node": user_node.model_dump(),
                "assistant_node": assistant_node.model_dump() if assistant_node else None,
                "response": assistant_content,
                "latency_ms": latency_ms,
                "model": model_name,
            }
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._metrics_store.record(
                endpoint="chat_lab",
                model=model_name,
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                success=False
            )
            return {"error": str(e), "user_node": user_node.model_dump()}
    
    def create_chat_branch(self, tree_id: int, request: ChatBranchRequest) -> Dict:
        """Create a new branch from a specific node."""
        result = self._chat_lab_store.create_branch(
            tree_id=tree_id,
            from_node_id=request.from_node_id,
            branch_name=request.branch_name
        )
        if result:
            return {"success": True, "branch_point": result}
        return {"success": False, "error": "Failed to create branch"}
    
    def switch_chat_branch(self, tree_id: int, to_node_id: str) -> Dict:
        """Switch active path to include a specific node."""
        success = self._chat_lab_store.switch_branch(tree_id, to_node_id)
        return {"success": success}
    
    def delete_chat_node(self, tree_id: int, node_id: str) -> Dict:
        """Delete a node and all its descendants."""
        success = self._chat_lab_store.delete_node(tree_id, node_id)
        return {"success": success}
    
    # -------------------------------------------------------------------------
    # History & Replay Methods
    # -------------------------------------------------------------------------
    
    def list_history(self, filter_req: HistoryFilterRequest = None, 
                     limit: int = 100, offset: int = 0) -> List[HistoryEntry]:
        """List history entries with optional filtering."""
        filter_obj = None
        if filter_req:
            filter_obj = HistoryFilter(
                endpoint=filter_req.endpoint,
                model=filter_req.model,
                success=filter_req.success,
                starred=filter_req.starred,
                tags=filter_req.tags,
                from_timestamp=filter_req.from_timestamp,
                to_timestamp=filter_req.to_timestamp,
                search=filter_req.search
            )
        return self._history_store.list(filter_obj, limit, offset)
    
    def get_history_entry(self, entry_id: int) -> Optional[HistoryEntry]:
        """Get a specific history entry."""
        return self._history_store.get(entry_id)
    
    def update_history_entry(self, entry_id: int, 
                              request: HistoryUpdateRequest) -> Optional[HistoryEntry]:
        """Update a history entry (notes, tags, starred)."""
        updates = {}
        if request.notes is not None:
            updates["notes"] = request.notes
        if request.tags is not None:
            updates["tags"] = request.tags
        if request.starred is not None:
            updates["starred"] = request.starred
        return self._history_store.update(entry_id, **updates)
    
    def delete_history_entry(self, entry_id: int) -> bool:
        """Delete a history entry."""
        return self._history_store.delete(entry_id)
    
    def clear_history(self, keep_starred: bool = True) -> int:
        """Clear history entries."""
        return self._history_store.clear(keep_starred)
    
    def get_history_stats(self) -> Dict[str, Any]:
        """Get history statistics."""
        return self._history_store.get_stats()
    
    def get_history_endpoints(self) -> List[str]:
        """Get list of unique endpoints."""
        return self._history_store.get_endpoints()
    
    def get_history_models(self) -> List[str]:
        """Get list of unique models used."""
        return self._history_store.get_models()
    
    async def replay_request(self, request: ReplayRequest) -> Dict[str, Any]:
        """Replay a historical request."""
        import time
        
        entry = self._history_store.get(request.entry_id)
        if not entry:
            return {"error": "History entry not found"}
        
        # Use override model or original
        model = request.override_model or entry.model
        if not model:
            return {"error": "No model specified"}
        
        # Build parameters
        params = entry.parameters.copy()
        if request.override_parameters:
            params.update(request.override_parameters)
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=STREAMING_TIMEOUT) as client:
                # Build the request based on endpoint type
                if entry.messages:
                    # Chat-style request
                    messages = entry.messages.copy()
                    if entry.system_prompt:
                        messages.insert(0, {"role": "system", "content": entry.system_prompt})
                    
                    payload = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": params.get("max_tokens", 1024),
                        "temperature": params.get("temperature", 0.7),
                        "stream": False
                    }
                else:
                    # Generate-style request
                    messages = []
                    if entry.system_prompt:
                        messages.append({"role": "system", "content": entry.system_prompt})
                    if entry.prompt:
                        messages.append({"role": "user", "content": entry.prompt})
                    
                    payload = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": params.get("max_tokens", 1024),
                        "temperature": params.get("temperature", 0.7),
                        "stream": False
                    }
                
                resp = await client.post(LMSTUDIO_CHAT_COMPLETIONS, json=payload)
                resp.raise_for_status()
                data = resp.json()
            
            latency_ms = (time.time() - start_time) * 1000
            response_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            
            # Record this replay as a new history entry
            self._history_store.record(
                endpoint="replay",
                model=model,
                prompt=entry.prompt,
                system_prompt=entry.system_prompt,
                messages=entry.messages,
                parameters=params,
                response=response_text,
                latency_ms=latency_ms,
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens"),
                success=True,
                tags=["replay", f"original:{entry.id}"]
            )
            
            # Record metrics
            self._metrics_store.record(
                endpoint="replay",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                success=True
            )
            
            return {
                "original_entry_id": entry.id,
                "response": response_text,
                "original_response": entry.response,
                "model": model,
                "latency_ms": latency_ms,
                "usage": usage,
            }
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._metrics_store.record(
                endpoint="replay",
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=0,
                completion_tokens=0,
                success=False
            )
            return {"error": str(e)}
    
    def record_history(self, **kwargs) -> HistoryEntry:
        """Record a history entry (used by endpoints)."""
        return self._history_store.record(**kwargs)
