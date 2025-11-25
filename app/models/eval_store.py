"""Storage layer for evaluation datasets, custom evaluators, and evaluation jobs."""

import json
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# --- Dataset Models ---

class DatasetRow(BaseModel):
    """A single row in an evaluation dataset."""
    query: str
    response: Optional[str] = None  # Pre-filled response or generated during bulk run
    ground_truth: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Dataset(BaseModel):
    """An evaluation dataset containing query/response/ground_truth rows."""
    id: int
    name: str
    description: str = ""
    rows: List[DatasetRow] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class DatasetStore:
    """Persistent storage for evaluation datasets."""

    def __init__(self, path: str = "app/data/datasets.json"):
        self._path = path
        self._datasets: List[Dataset] = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._datasets = [Dataset(**d) for d in data]
            except Exception:
                self._datasets = []
        else:
            self._datasets = []

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in self._datasets], f, indent=2)

    def list_all(self) -> List[Dataset]:
        return self._datasets

    def get(self, dataset_id: int) -> Optional[Dataset]:
        for d in self._datasets:
            if d.id == dataset_id:
                return d
        return None

    def create(self, name: str, description: str = "", rows: List[dict] = None) -> Dataset:
        new_id = max((d.id for d in self._datasets), default=0) + 1
        dataset = Dataset(
            id=new_id,
            name=name,
            description=description,
            rows=[DatasetRow(**r) for r in (rows or [])],
        )
        self._datasets.append(dataset)
        self._save()
        return dataset

    def update(self, dataset_id: int, name: str = None, description: str = None, rows: List[dict] = None) -> Optional[Dataset]:
        dataset = self.get(dataset_id)
        if not dataset:
            return None
        if name is not None:
            dataset.name = name
        if description is not None:
            dataset.description = description
        if rows is not None:
            dataset.rows = [DatasetRow(**r) for r in rows]
        dataset.updated_at = datetime.now().isoformat()
        self._save()
        return dataset

    def delete(self, dataset_id: int) -> bool:
        for i, d in enumerate(self._datasets):
            if d.id == dataset_id:
                self._datasets.pop(i)
                self._save()
                return True
        return False


# --- Custom Evaluator Models ---

class CustomEvaluator(BaseModel):
    """A custom evaluator (LLM-based or code-based)."""
    id: int
    name: str
    description: str = ""
    evaluator_type: str  # "llm" or "code"
    # For LLM-based: the prompt template
    llm_prompt: str = ""
    # For code-based: Python code as a string
    code: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class CustomEvaluatorStore:
    """Persistent storage for custom evaluators."""

    def __init__(self, path: str = "app/data/custom_evaluators.json"):
        self._path = path
        self._evaluators: List[CustomEvaluator] = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._evaluators = [CustomEvaluator(**e) for e in data]
            except Exception:
                self._evaluators = []
        else:
            self._evaluators = []

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in self._evaluators], f, indent=2)

    def list_all(self) -> List[CustomEvaluator]:
        return self._evaluators

    def get(self, evaluator_id: int) -> Optional[CustomEvaluator]:
        for e in self._evaluators:
            if e.id == evaluator_id:
                return e
        return None

    def create(self, name: str, evaluator_type: str, description: str = "", llm_prompt: str = "", code: str = "") -> CustomEvaluator:
        new_id = max((e.id for e in self._evaluators), default=0) + 1
        evaluator = CustomEvaluator(
            id=new_id,
            name=name,
            description=description,
            evaluator_type=evaluator_type,
            llm_prompt=llm_prompt,
            code=code,
        )
        self._evaluators.append(evaluator)
        self._save()
        return evaluator

    def update(self, evaluator_id: int, name: str = None, description: str = None, llm_prompt: str = None, code: str = None) -> Optional[CustomEvaluator]:
        evaluator = self.get(evaluator_id)
        if not evaluator:
            return None
        if name is not None:
            evaluator.name = name
        if description is not None:
            evaluator.description = description
        if llm_prompt is not None:
            evaluator.llm_prompt = llm_prompt
        if code is not None:
            evaluator.code = code
        self._save()
        return evaluator

    def delete(self, evaluator_id: int) -> bool:
        for i, e in enumerate(self._evaluators):
            if e.id == evaluator_id:
                self._evaluators.pop(i)
                self._save()
                return True
        return False


# --- Evaluation Job Models ---

class EvalResult(BaseModel):
    """Result for a single row + evaluator combination."""
    row_index: int
    evaluator_id: str  # "builtin:f1_score" or "custom:3"
    score: float
    reason: str = ""
    error: bool = False


class EvalJob(BaseModel):
    """An evaluation job that runs evaluators against a dataset."""
    id: int
    name: str
    dataset_id: int
    evaluator_ids: List[str] = Field(default_factory=list)  # e.g., ["builtin:f1_score", "custom:1"]
    model_name: Optional[str] = None  # Model used for generating responses (bulk run)
    agent_id: Optional[str] = None  # Agent used for generating responses
    status: str = "pending"  # pending, running, completed, failed
    results: List[EvalResult] = Field(default_factory=list)
    aggregate_scores: Dict[str, float] = Field(default_factory=dict)  # evaluator_id -> avg score
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class EvalJobStore:
    """Persistent storage for evaluation jobs."""

    def __init__(self, path: str = "app/data/eval_jobs.json"):
        self._path = path
        self._jobs: List[EvalJob] = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._jobs = [EvalJob(**j) for j in data]
            except Exception:
                self._jobs = []
        else:
            self._jobs = []

    def _save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([j.model_dump() for j in self._jobs], f, indent=2)

    def list_all(self) -> List[EvalJob]:
        return self._jobs

    def get(self, job_id: int) -> Optional[EvalJob]:
        for j in self._jobs:
            if j.id == job_id:
                return j
        return None

    def create(self, name: str, dataset_id: int, evaluator_ids: List[str], model_name: str = None, agent_id: str = None) -> EvalJob:
        new_id = max((j.id for j in self._jobs), default=0) + 1
        job = EvalJob(
            id=new_id,
            name=name,
            dataset_id=dataset_id,
            evaluator_ids=evaluator_ids,
            model_name=model_name,
            agent_id=agent_id,
        )
        self._jobs.append(job)
        self._save()
        return job

    def update_status(self, job_id: int, status: str, results: List[dict] = None, aggregate_scores: Dict[str, float] = None, error_message: str = None) -> Optional[EvalJob]:
        job = self.get(job_id)
        if not job:
            return None
        job.status = status
        if results is not None:
            job.results = [EvalResult(**r) for r in results]
        if aggregate_scores is not None:
            job.aggregate_scores = aggregate_scores
        if error_message is not None:
            job.error_message = error_message
        if status in ("completed", "failed"):
            job.completed_at = datetime.now().isoformat()
        self._save()
        return job

    def delete(self, job_id: int) -> bool:
        for i, j in enumerate(self._jobs):
            if j.id == job_id:
                self._jobs.pop(i)
                self._save()
                return True
        return False
