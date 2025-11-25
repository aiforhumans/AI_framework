from typing import List, Dict, Optional
from pydantic import BaseModel
import asyncio
import httpx

from app.models.tools_store import ToolStore, ToolConfig
from app.models.prompt_templates_store import PromptTemplateStore, PromptTemplate
from app.models.eval_store import DatasetStore, Dataset, CustomEvaluatorStore, CustomEvaluator, EvalJobStore, EvalJob
from app.models.evaluators import BUILTIN_EVALUATORS, run_builtin_evaluator


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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    agent_id: Optional[str] = None
    model_name: Optional[str] = None
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    images: Optional[List[str]] = None  # Base64 encoded images


class PromptGeneratorRequest(BaseModel):
    input: str


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


class PromptTemplateCreateRequest(BaseModel):
    name: str
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = ""
    variables: List[str] = []


class PromptTemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[List[str]] = None


class ABTestRequest(BaseModel):
    prompt: str
    system_prompt: str = ""
    variants: List[dict]  # each: {"model_name": str} or {"agent_id": str}
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7


# --- Evaluation Request Models ---

class DatasetCreateRequest(BaseModel):
    name: str
    description: str = ""
    rows: List[dict] = []  # each: {"query": str, "response": str, "ground_truth": str}


class DatasetUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rows: Optional[List[dict]] = None


class CustomEvaluatorCreateRequest(BaseModel):
    name: str
    description: str = ""
    evaluator_type: str  # "llm" or "code"
    llm_prompt: str = ""
    code: str = ""


class CustomEvaluatorUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    llm_prompt: Optional[str] = None
    code: Optional[str] = None


class EvalJobCreateRequest(BaseModel):
    name: str
    dataset_id: int
    evaluator_ids: List[str]  # e.g., ["builtin:f1_score", "custom:1"]
    model_name: Optional[str] = None
    agent_id: Optional[str] = None


class BulkRunRequest(BaseModel):
    dataset_id: int
    model_name: Optional[str] = None
    agent_id: Optional[str] = None
    max_tokens: Optional[int] = 256
    temperature: Optional[float] = 0.7


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
        # Prompt template store for Dynamic Prompt Builder
        self._prompt_template_store = PromptTemplateStore()
        # Evaluation stores
        self._dataset_store = DatasetStore()
        self._custom_evaluator_store = CustomEvaluatorStore()
        self._eval_job_store = EvalJobStore()

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

    # Prompt template helpers

    def list_prompt_templates(self) -> List[PromptTemplate]:
        return self._prompt_template_store.list_templates()

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

        start = asyncio.get_event_loop().time()

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

        return {
            "response": content,
            "model_name": model_name,
            "latency_ms": round((end - start) * 1000.0, 1),
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

        async with httpx.AsyncClient(timeout=120.0) as client:
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

        async with httpx.AsyncClient(timeout=120.0) as client:
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

            start = asyncio.get_event_loop().time()
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
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
                error = None
            except Exception as e:
                content = ""
                error = str(e)
            end = asyncio.get_event_loop().time()

            return {
                "variant": variant,
                "model_name": effective_model,
                "agent_id": agent_id,
                "agent_name": agent.name if agent else None,
                "response": content,
                "error": error,
                "latency_ms": (end - start) * 1000.0,
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

            try:
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
                response = data["choices"][0]["message"]["content"]
                error = None
            except Exception as e:
                response = f"[Error: {str(e)}]"
                error = str(e)

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
            async with httpx.AsyncClient(timeout=60.0) as client:
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
