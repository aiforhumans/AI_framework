LLM Testing Interface – Copilot Instructions

- Use FastAPI backend in `app/main.py` with `LocalLLMService`.
- Static frontend lives in `app/static` (`index.html`, `main.js`, `style.css`).
- Start the app with `uvicorn app.main:app --reload` from the repo root.

When asked to extend the project:
- Prefer adding new features as additional tabs (e.g. Tools, Prompt Builder) in `index.html`.
- Keep styles consistent with the existing dark theme in `style.css`.
- Wire new UI features through small, focused REST endpoints in `app/main.py`.
- Keep persistence simple (JSON file or SQLite) under `app/models`.

For this repo specifically:
- Do not scaffold a new project; build on the current structure.
- Do not install extra VS Code extensions or frameworks unless explicitly requested.
- Keep responses concise and focused on actionable changes.
