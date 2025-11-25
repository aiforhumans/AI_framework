# LLM Testing Interface

Python-based FastAPI backend with a minimal web UI for testing local LLM models.

Current implementation uses a **stubbed local LLM service** so you can develop the UI and flow before plugging in a real local model runtime (e.g., Ollama, llama.cpp, LM Studio, or in-process `transformers`).

## Requirements

- Python 3.9+

## Installation (using .venv)

From the project root (`f:\\AI_framework`):

```bash
python -m venv .venv
.\.venv\\Scripts\\activate
pip install -r requirements.txt
```

All Python packages are installed into the local `.venv`.

## Running the app

With the virtual environment activated from `f:\\AI_framework`:

```bash
uvicorn app.main:app --reload
```

### What the command does

- `uvicorn` – runs the ASGI server from your active `.venv`.
- `app.main:app` – tells uvicorn to load the `app` instance in `app/main.py`.
- `--reload` – watches your files and automatically restarts the server on code changes (handy during development).

By default, the server listens on `http://127.0.0.1:8000/`.

### Stopping the server

- In the terminal where uvicorn is running:
	- Press `Ctrl + C` once to request a clean shutdown.
	- If it does not stop (rare), press `Ctrl + C` again.

### Reload behavior

- With `--reload`, uvicorn automatically restarts when it detects file changes under `F:\\AI_framework`.
- Typical workflow:
	1. Keep uvicorn running in one terminal.
	2. Edit Python or static files in VS Code.
	3. Wait for uvicorn to log a reload, then refresh the browser.

If you ever want to run without auto-reload (for a slightly lighter server), omit `--reload`:

```bash
uvicorn app.main:app
```

Then open `http://127.0.0.1:8000/` in your browser.

## Replacing the stub with a real local LLM

- Implement real generation logic in `app/models/service.py` inside `LocalLLMService.generate`.
- Option 1: call an external local server (e.g., Ollama HTTP API).
- Option 2: load a model in-process (e.g., `llama-cpp-python` or HuggingFace `transformers`).

The UI and API contract (`/api/generate`) remain the same; only the internals of `LocalLLMService` need to change.

