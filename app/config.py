"""
Application Configuration Module.

Centralizes all configuration settings for the LLM Testing Interface.
Uses environment variables with sensible defaults for development.
"""

import os
from pathlib import Path
from typing import Optional

# =============================================================================
# BASE PATHS
# =============================================================================

# Project root directory
BASE_DIR = Path(__file__).parent.parent

# Application directory
APP_DIR = Path(__file__).parent

# Data directory for JSON persistence
DATA_DIR = APP_DIR / "data"

# Static files directory
STATIC_DIR = APP_DIR / "static"


# =============================================================================
# LM STUDIO CONFIGURATION
# =============================================================================

# LM Studio API base URL (OpenAI-compatible)
LMSTUDIO_HOST = os.getenv("LMSTUDIO_HOST", "127.0.0.1")
LMSTUDIO_PORT = int(os.getenv("LMSTUDIO_PORT", "1234"))
LMSTUDIO_BASE_URL = os.getenv(
    "LMSTUDIO_BASE_URL", 
    f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1"
)

# LM Studio endpoints
LMSTUDIO_CHAT_COMPLETIONS = f"{LMSTUDIO_BASE_URL}/chat/completions"
LMSTUDIO_MODELS = f"{LMSTUDIO_BASE_URL}/models/"


# =============================================================================
# DEFAULT MODEL PARAMETERS
# =============================================================================

DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "256"))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "60.0"))
STREAMING_TIMEOUT = float(os.getenv("STREAMING_TIMEOUT", "120.0"))


# =============================================================================
# API SETTINGS
# =============================================================================

# FastAPI configuration
API_TITLE = "LLM Testing Interface"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
A comprehensive interface for testing and evaluating Local LLMs.

## Features
- **Playground**: Interactive multi-turn chat with streaming
- **Prompt Builder**: Template system with variables
- **A/B Tester**: Side-by-side model comparison
- **Evaluation**: Datasets, bulk runs, built-in + custom evaluators
- **Orchestrator**: Visual workflow builder
- **Guardrails**: Safety testing and content moderation
- **Chat Lab**: Multi-turn branching conversations
- **History**: Request/response logging with replay
- **Metrics**: Latency and usage dashboard
"""


# =============================================================================
# DATA FILE PATHS
# =============================================================================

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# JSON file paths for persistence
TOOLS_FILE = DATA_DIR / "tools.json"
PROMPT_TEMPLATES_FILE = DATA_DIR / "prompt_templates.json"
DATASETS_FILE = DATA_DIR / "datasets.json"
CUSTOM_EVALUATORS_FILE = DATA_DIR / "custom_evaluators.json"
EVAL_JOBS_FILE = DATA_DIR / "eval_jobs.json"
WORKFLOWS_FILE = DATA_DIR / "workflows.json"
WORKFLOW_RUNS_FILE = DATA_DIR / "workflow_runs.json"
METRICS_FILE = DATA_DIR / "metrics.json"
GUARDRAILS_FILE = DATA_DIR / "guardrails.json"
GUARDRAIL_TESTS_FILE = DATA_DIR / "guardrail_tests.json"
CHAT_LAB_FILE = DATA_DIR / "chat_lab.json"
HISTORY_FILE = DATA_DIR / "history.json"


# =============================================================================
# EVALUATION SETTINGS
# =============================================================================

# Maximum rows to process in a single bulk run
MAX_BULK_RUN_ROWS = int(os.getenv("MAX_BULK_RUN_ROWS", "1000"))

# Code evaluator sandbox settings
CODE_EVALUATOR_ALLOWED_BUILTINS = {
    "len", "str", "int", "float", "bool", "list", "dict",
    "min", "max", "sum", "abs", "round"
}


# =============================================================================
# HISTORY SETTINGS
# =============================================================================

# Maximum history entries to keep
MAX_HISTORY_ENTRIES = int(os.getenv("MAX_HISTORY_ENTRIES", "10000"))


# =============================================================================
# METRICS SETTINGS
# =============================================================================

# Default hours for metrics aggregation
DEFAULT_METRICS_HOURS = int(os.getenv("DEFAULT_METRICS_HOURS", "24"))


# =============================================================================
# LOGGING
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def get_config_summary() -> dict:
    """Return a summary of current configuration for debugging."""
    return {
        "lmstudio_base_url": LMSTUDIO_BASE_URL,
        "data_dir": str(DATA_DIR),
        "default_max_tokens": DEFAULT_MAX_TOKENS,
        "default_temperature": DEFAULT_TEMPERATURE,
        "default_timeout": DEFAULT_TIMEOUT,
        "log_level": LOG_LEVEL,
    }
