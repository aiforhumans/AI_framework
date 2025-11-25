"""
Workflow Store for Agent Orchestrator.

Manages workflow definitions with nodes (agents/steps) and edges (connections).
Supports sequential, parallel, and conditional execution flows.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
WORKFLOWS_FILE = os.path.join(DATA_DIR, "workflows.json")
WORKFLOW_RUNS_FILE = os.path.join(DATA_DIR, "workflow_runs.json")


class WorkflowNode(BaseModel):
    """A node in the workflow graph - represents an agent or action."""
    id: str
    type: str  # "agent", "condition", "transform", "output"
    label: str
    config: Dict[str, Any] = {}
    # For agent nodes: {"agent_id": str, "model_name": str, "system_prompt": str, "max_tokens": int}
    # For condition nodes: {"variable": str, "operator": str, "value": Any}
    # For transform nodes: {"template": str} - uses {{input}} and {{prev_output}}
    # For output nodes: {"format": str}
    position: Dict[str, float] = {"x": 0, "y": 0}


class WorkflowEdge(BaseModel):
    """An edge connecting two nodes in the workflow."""
    id: str
    source: str  # source node id
    target: str  # target node id
    label: str = ""  # optional label (e.g., "true", "false" for conditions)
    condition: Optional[str] = None  # for conditional edges: "true", "false", or None


class Workflow(BaseModel):
    """A complete workflow definition."""
    id: int
    name: str
    description: str = ""
    nodes: List[WorkflowNode] = []
    edges: List[WorkflowEdge] = []
    entry_node: Optional[str] = None  # id of the starting node
    created_at: str = ""
    updated_at: str = ""


class WorkflowStepResult(BaseModel):
    """Result of executing a single workflow step."""
    node_id: str
    node_label: str
    node_type: str
    input_text: str
    output_text: str
    latency_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class WorkflowRun(BaseModel):
    """A recorded execution of a workflow."""
    id: int
    workflow_id: int
    workflow_name: str
    input_text: str
    final_output: str
    status: str  # "running", "completed", "failed"
    steps: List[WorkflowStepResult] = []
    total_latency_ms: float = 0.0
    error_message: Optional[str] = None
    created_at: str = ""


class WorkflowStore:
    """Persistent storage for workflows."""

    def __init__(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        self._workflows: Dict[int, Workflow] = {}
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if os.path.exists(WORKFLOWS_FILE):
            try:
                with open(WORKFLOWS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    wf = Workflow(**item)
                    self._workflows[wf.id] = wf
                    if wf.id >= self._next_id:
                        self._next_id = wf.id + 1
            except Exception:
                pass

    def _save(self) -> None:
        with open(WORKFLOWS_FILE, "w", encoding="utf-8") as f:
            json.dump([wf.model_dump() for wf in self._workflows.values()], f, indent=2)

    def list_all(self) -> List[Workflow]:
        return list(self._workflows.values())

    def get(self, workflow_id: int) -> Optional[Workflow]:
        return self._workflows.get(workflow_id)

    def create(self, name: str, description: str = "", nodes: List[dict] = None, 
               edges: List[dict] = None, entry_node: str = None) -> Workflow:
        now = datetime.utcnow().isoformat()
        wf = Workflow(
            id=self._next_id,
            name=name,
            description=description,
            nodes=[WorkflowNode(**n) for n in (nodes or [])],
            edges=[WorkflowEdge(**e) for e in (edges or [])],
            entry_node=entry_node,
            created_at=now,
            updated_at=now,
        )
        self._workflows[wf.id] = wf
        self._next_id += 1
        self._save()
        return wf

    def update(self, workflow_id: int, name: str = None, description: str = None,
               nodes: List[dict] = None, edges: List[dict] = None, 
               entry_node: str = None) -> Optional[Workflow]:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return None
        if name is not None:
            wf.name = name
        if description is not None:
            wf.description = description
        if nodes is not None:
            wf.nodes = [WorkflowNode(**n) for n in nodes]
        if edges is not None:
            wf.edges = [WorkflowEdge(**e) for e in edges]
        if entry_node is not None:
            wf.entry_node = entry_node
        wf.updated_at = datetime.utcnow().isoformat()
        self._save()
        return wf

    def delete(self, workflow_id: int) -> bool:
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            self._save()
            return True
        return False


class WorkflowRunStore:
    """Persistent storage for workflow run history."""

    def __init__(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        self._runs: Dict[int, WorkflowRun] = {}
        self._next_id = 1
        self._load()

    def _load(self) -> None:
        if os.path.exists(WORKFLOW_RUNS_FILE):
            try:
                with open(WORKFLOW_RUNS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    run = WorkflowRun(**item)
                    self._runs[run.id] = run
                    if run.id >= self._next_id:
                        self._next_id = run.id + 1
            except Exception:
                pass

    def _save(self) -> None:
        with open(WORKFLOW_RUNS_FILE, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in self._runs.values()], f, indent=2)

    def list_all(self) -> List[WorkflowRun]:
        return list(self._runs.values())

    def list_by_workflow(self, workflow_id: int) -> List[WorkflowRun]:
        return [r for r in self._runs.values() if r.workflow_id == workflow_id]

    def get(self, run_id: int) -> Optional[WorkflowRun]:
        return self._runs.get(run_id)

    def create(self, workflow_id: int, workflow_name: str, input_text: str) -> WorkflowRun:
        now = datetime.utcnow().isoformat()
        run = WorkflowRun(
            id=self._next_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            input_text=input_text,
            final_output="",
            status="running",
            steps=[],
            created_at=now,
        )
        self._runs[run.id] = run
        self._next_id += 1
        self._save()
        return run

    def add_step(self, run_id: int, step: WorkflowStepResult) -> None:
        run = self._runs.get(run_id)
        if run:
            run.steps.append(step)
            run.total_latency_ms += step.latency_ms
            self._save()

    def complete(self, run_id: int, final_output: str, status: str = "completed", 
                 error_message: str = None) -> Optional[WorkflowRun]:
        run = self._runs.get(run_id)
        if run:
            run.final_output = final_output
            run.status = status
            run.error_message = error_message
            self._save()
        return run

    def delete(self, run_id: int) -> bool:
        if run_id in self._runs:
            del self._runs[run_id]
            self._save()
            return True
        return False
