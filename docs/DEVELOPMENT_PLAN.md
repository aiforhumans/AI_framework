# LLM Testing Interface - Full Development Plan

## Executive Summary

This document provides a comprehensive development plan based on analysis of all documentation files in the `docs/` folder. The plan identifies gaps between documented features and current implementation, prioritizes development phases, and provides actionable task breakdowns.

---

## 📊 Documentation Analysis Summary

### Documented Components (12 Files Analyzed)

| File | Component | Status | Priority |
|------|-----------|--------|----------|
| `README.md` | Documentation Index | ✅ Complete | - |
| `playground.md` | Interactive Chat | ⚠️ Partial | High |
| `prompt-builder.md` | Template System | ⚠️ Partial | High |
| `ab-tester.md` | Model Comparison | ⚠️ Partial | Medium |
| `evaluation.md` | Testing Suite | ⚠️ Partial | High |
| `orchestrator.md` | Workflow Builder | ⚠️ Partial | Medium |
| `chat-lab.md` | Branching Conversations | ❌ Missing | High |
| `guardrails.md` | Safety Testing | ❌ Missing | High |
| `history.md` | Request Logging | ❌ Missing | Medium |
| `dashboard.md` | Metrics Dashboard | ❌ Missing | Medium |
| `tools.md` | Tool Configuration | ⚠️ Partial | Medium |
| `debugging-guide.md` | Troubleshooting | ✅ Complete | - |

### Current Implementation Status

**Implemented Routers:**
- `playground.py` - Basic chat functionality
- `templates.py` - Prompt templates
- `ab_test.py` - A/B testing
- `evaluation.py` - Evaluation framework
- `workflows.py` - Workflow orchestration
- `tools.py` - Tool management

**Missing Routers (Per Documentation):**
- `chat_lab.py` - Branching conversations
- `guardrails.py` - Safety rules and testing
- `history.py` - Request/response logging
- `metrics.py` - Dashboard metrics

**Missing Stores:**
- `base_store.py` - Generic CRUD base class
- `chat_lab_store.py` - Conversation tree storage
- `guardrails_store.py` - Rules and tests storage
- `history_store.py` - History entries storage
- `metrics_store.py` - Metrics data storage

---

## 🗓️ Development Phases

### Phase 1: Core Infrastructure (Week 1-2)

#### 1.1 BaseStore Pattern Implementation
**Priority:** Critical | **Effort:** 4 hours

Create the foundational generic CRUD base class that all stores should extend.

**Tasks:**
- [ ] Create `app/models/base_store.py`
- [ ] Implement generic type parameter `BaseStore[T]`
- [ ] Add auto-incrementing ID management
- [ ] Add auto-save on create/update/delete
- [ ] Add `_next_id` tracking in JSON
- [ ] Add `created_at` auto-population
- [ ] Update existing stores to extend BaseStore

**Implementation Pattern:**
```python
from typing import TypeVar, Generic, List, Optional
from pydantic import BaseModel
from pathlib import Path
import json

T = TypeVar('T', bound=BaseModel)

class BaseStore(Generic[T]):
    model_class: type[T]
    file_path: Path
    json_key: str = "items"
    
    def __init__(self):
        self._data: List[T] = []
        self._next_id: int = 1
        self._load()
    
    def _load(self): ...
    def _save(self): ...
    def list_all(self) -> List[T]: ...
    def get(self, id: int) -> Optional[T]: ...
    def create(self, item: T) -> T: ...
    def update(self, id: int, item: T) -> Optional[T]: ...
    def delete(self, id: int) -> bool: ...
```

#### 1.2 Configuration Centralization
**Priority:** High | **Effort:** 2 hours

Ensure all paths and settings are in `app/config.py`.

**Tasks:**
- [ ] Add file paths for all data stores
- [ ] Add LM Studio URL configuration
- [ ] Add timeout settings
- [ ] Add default values for UI settings
- [ ] Add environment variable support

---

### Phase 2: Chat Lab Implementation (Week 2-3)

#### 2.1 Backend: Chat Lab Router & Store
**Priority:** High | **Effort:** 8 hours

Implement branching conversation trees with full CRUD.

**Tasks:**
- [ ] Create `app/routers/chat_lab.py`
- [ ] Create `app/models/chat_lab_store.py`
- [ ] Add Pydantic models to `schemas/requests.py`:
  - `CreateTreeRequest`
  - `UpdateTreeRequest`
  - `SendMessageRequest`
  - `CreateBranchRequest`
  - `SwitchPathRequest`
- [ ] Implement endpoints:
  - `GET /api/chat-lab/trees` - List trees
  - `POST /api/chat-lab/trees` - Create tree
  - `GET /api/chat-lab/trees/{id}` - Get tree
  - `PUT /api/chat-lab/trees/{id}` - Update tree
  - `DELETE /api/chat-lab/trees/{id}` - Delete tree
  - `GET /api/chat-lab/trees/{id}/structure` - Get tree structure
  - `GET /api/chat-lab/trees/{id}/history` - Get history to active node
  - `POST /api/chat-lab/trees/{id}/messages` - Send message
  - `POST /api/chat-lab/trees/{id}/branch` - Create branch
  - `POST /api/chat-lab/trees/{id}/switch` - Switch active path
  - `DELETE /api/chat-lab/trees/{id}/nodes/{node_id}` - Delete node

**Data Model:**
```python
class ConversationTree(BaseModel):
    id: int = 0
    name: str
    model: str
    system_prompt: str = ""
    created_at: str = ""
    nodes: Dict[str, TreeNode] = {}
    root_id: str = ""
    active_node_id: str = ""

class TreeNode(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    parent_id: Optional[str]
    children: List[str] = []
    branch_name: Optional[str]
    metadata: Dict[str, Any] = {}
```

#### 2.2 Frontend: Chat Lab Tab
**Priority:** High | **Effort:** 6 hours

**Tasks:**
- [ ] Add Chat Lab nav link and tab panel in `index.html`
- [ ] Add `initChatLabUI()` function in `main.js`
- [ ] Implement tree list panel
- [ ] Implement message display with branching UI
- [ ] Implement tree visualization (SVG or CSS-based)
- [ ] Add branch creation from any message (🌿 button)
- [ ] Add path switching on node click
- [ ] Add branch indicator for active branches

---

### Phase 3: Guardrails System (Week 3-4)

#### 3.1 Backend: Guardrails Router & Store
**Priority:** High | **Effort:** 8 hours

Implement safety rules and content moderation.

**Tasks:**
- [ ] Create `app/routers/guardrails.py`
- [ ] Create `app/models/guardrails_store.py`
- [ ] Add Pydantic models:
  - `GuardrailRule`
  - `GuardrailTest`
  - `CheckRequest`
  - `CheckResult`
- [ ] Implement rule types:
  - **PII** - Personal information detection (email, phone, SSN patterns)
  - **Keyword** - Blocked word list matching
  - **Regex** - Custom pattern matching
  - **Content** - Content policy checks
  - **LLM** - AI-powered safety analysis
- [ ] Implement endpoints:
  - `GET /api/guardrails/rules` - List rules
  - `POST /api/guardrails/rules` - Create rule
  - `GET /api/guardrails/rules/{id}` - Get rule
  - `PUT /api/guardrails/rules/{id}` - Update rule
  - `DELETE /api/guardrails/rules/{id}` - Delete rule
  - `POST /api/guardrails/rules/{id}/toggle` - Toggle enabled
  - `GET /api/guardrails/tests` - List tests
  - `POST /api/guardrails/tests` - Create test
  - `PUT /api/guardrails/tests/{id}` - Update test
  - `DELETE /api/guardrails/tests/{id}` - Delete test
  - `POST /api/guardrails/check` - Check text against rules
  - `POST /api/guardrails/run-tests` - Run test suite

**Rule Configuration Examples:**
```python
# PII Rule
{
    "type": "pii",
    "config": {
        "detect_email": True,
        "detect_phone": True,
        "detect_ssn": True
    }
}

# Keyword Rule
{
    "type": "keyword",
    "config": {
        "keywords": ["forbidden", "banned", "blocked"],
        "case_sensitive": False
    }
}

# Regex Rule
{
    "type": "regex",
    "config": {
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
        "description": "SSN pattern"
    }
}
```

#### 3.2 Frontend: Guardrails Tab
**Priority:** High | **Effort:** 5 hours

**Tasks:**
- [ ] Add Guardrails nav link and tab panel
- [ ] Add `initGuardrailsUI()` function
- [ ] Implement rule management table with toggle
- [ ] Implement rule creation/edit form
- [ ] Implement test case management
- [ ] Implement real-time text checking panel
- [ ] Add test suite runner with results display
- [ ] Add status badges (Blocked/Flagged/Passed)

---

### Phase 4: History & Metrics (Week 4-5)

#### 4.1 Backend: History Router & Store
**Priority:** Medium | **Effort:** 6 hours

Implement request/response logging with replay.

**Tasks:**
- [ ] Create `app/routers/history.py`
- [ ] Create `app/models/history_store.py`
- [ ] Add Pydantic models:
  - `HistoryEntry`
  - `HistoryFilter`
  - `ReplayRequest`
- [ ] Implement endpoints:
  - `GET /api/history` - List entries with filtering
  - `GET /api/history/stats` - Get statistics
  - `GET /api/history/endpoints` - List unique endpoints
  - `GET /api/history/models` - List unique models
  - `GET /api/history/{id}` - Get entry details
  - `PUT /api/history/{id}` - Update annotations
  - `DELETE /api/history/{id}` - Delete entry
  - `POST /api/history/clear` - Clear history
  - `POST /api/history/replay` - Replay request
- [ ] Add automatic logging in service.py for all LLM calls

**HistoryEntry Model:**
```python
class HistoryEntry(BaseModel):
    id: int = 0
    timestamp: str
    endpoint: str
    model: str
    request: Dict[str, Any]
    response: Dict[str, Any]
    latency_ms: float
    tokens_prompt: int
    tokens_completion: int
    tokens_total: int
    success: bool
    error: Optional[str]
    starred: bool = False
    notes: str = ""
    tags: List[str] = []
```

#### 4.2 Backend: Metrics Router & Store
**Priority:** Medium | **Effort:** 6 hours

Implement latency tracking and usage statistics.

**Tasks:**
- [ ] Create `app/routers/metrics.py`
- [ ] Create `app/models/metrics_store.py`
- [ ] Add Pydantic models for metrics
- [ ] Implement endpoints:
  - `GET /api/metrics/summary` - Summary stats
  - `GET /api/metrics/list` - Recent requests
  - `GET /api/metrics/by-model` - Model breakdown
  - `GET /api/metrics/by-endpoint` - Endpoint breakdown
  - `GET /api/metrics/hourly` - Hourly trends
  - `DELETE /api/metrics` - Clear metrics
- [ ] Add time range filtering (1h, 6h, 12h, 24h, 48h)
- [ ] Compute percentiles (P50, P95, P99)

#### 4.3 Frontend: History Tab
**Priority:** Medium | **Effort:** 4 hours

**Tasks:**
- [ ] Add History nav link and tab panel
- [ ] Add `initHistoryUI()` function
- [ ] Implement paginated entry list
- [ ] Implement filtering (endpoint, model, status)
- [ ] Implement entry detail view
- [ ] Implement replay functionality
- [ ] Add star/annotation features

#### 4.4 Frontend: Dashboard Tab
**Priority:** Medium | **Effort:** 5 hours

**Tasks:**
- [ ] Add Dashboard nav link and tab panel
- [ ] Add `initDashboardUI()` function
- [ ] Implement summary statistics cards
- [ ] Implement model breakdown table
- [ ] Implement endpoint breakdown table
- [ ] Implement hourly trends chart (CSS/SVG based)
- [ ] Implement recent requests table
- [ ] Add time range selector
- [ ] Add refresh and clear buttons

---

### Phase 5: Feature Enhancements (Week 5-6)

#### 5.1 Playground Enhancements
**Priority:** High | **Effort:** 4 hours

Per documentation, add missing features:

**Tasks:**
- [ ] File attachment support (images, text files)
- [ ] Attachment preview and removal
- [ ] AI-powered prompt improvement modal
- [ ] Copy to clipboard for responses
- [ ] Character count tracking

#### 5.2 Prompt Builder Enhancements
**Priority:** High | **Effort:** 3 hours

**Tasks:**
- [ ] Expand to 20+ preset templates
- [ ] Add category filtering (CoT, Few-Shot, Role-Play, General, Custom)
- [ ] Add template preview before applying
- [ ] Add export template functionality

#### 5.3 A/B Tester Enhancements
**Priority:** Medium | **Effort:** 3 hours

**Tasks:**
- [ ] Add feedback system (👍/👎 buttons)
- [ ] Add vote tracking and storage
- [ ] Add comparison annotations
- [ ] Add export results functionality

#### 5.4 Orchestrator Enhancements
**Priority:** Medium | **Effort:** 4 hours

**Tasks:**
- [ ] Improve drag-and-drop for nodes
- [ ] Add zoom/pan support for canvas
- [ ] Add condition node operators (contains, equals, startswith, etc.)
- [ ] Add visual edge arrows with labels
- [ ] Add execution log panel

#### 5.5 Evaluation Enhancements
**Priority:** High | **Effort:** 4 hours

**Tasks:**
- [ ] Add all 8 dataset templates
- [ ] Add custom code-based evaluators
- [ ] Add evaluation job history
- [ ] Add detailed results breakdown

---

### Phase 6: Testing & Documentation (Week 6-7)

#### 6.1 Testing Infrastructure
**Priority:** High | **Effort:** 6 hours

**Tasks:**
- [ ] Set up pytest test structure
- [ ] Add API endpoint tests for each router
- [ ] Add store unit tests
- [ ] Add integration tests for workflows
- [ ] Add frontend E2E tests (optional)

#### 6.2 Documentation Updates
**Priority:** Medium | **Effort:** 4 hours

**Tasks:**
- [ ] Update `debugging-guide.md` with new tabs
- [ ] Add API reference documentation
- [ ] Add contributing guidelines
- [ ] Add changelog

#### 6.3 Error Handling & Edge Cases
**Priority:** High | **Effort:** 4 hours

**Tasks:**
- [ ] Add proper error responses for all endpoints
- [ ] Add input validation for all request models
- [ ] Add graceful handling for LM Studio disconnection
- [ ] Add proper cleanup for orphaned data

---

## 📋 Implementation Checklist

### Immediate Priorities (This Sprint)

- [ ] Create `base_store.py` with generic CRUD
- [ ] Update existing stores to use BaseStore
- [ ] Implement Chat Lab (router, store, frontend)
- [ ] Implement Guardrails (router, store, frontend)
- [ ] Create missing JSON data files

### Short-term (Next Sprint)

- [ ] Implement History (router, store, frontend)
- [ ] Implement Metrics/Dashboard (router, store, frontend)
- [ ] Add file attachment support to Playground
- [ ] Expand prompt template library

### Medium-term (Following Sprints)

- [ ] Enhanced A/B testing with feedback
- [ ] Improved workflow orchestrator
- [ ] Testing infrastructure
- [ ] Performance optimizations

---

## 🔧 Technical Debt to Address

1. **Store Inconsistency**: Not all stores follow BaseStore pattern
2. **Missing Data Files**: Some JSON files referenced in docs don't exist
3. **Frontend Organization**: `main.js` at 4000+ lines needs modularization
4. **Error Handling**: Inconsistent error responses across endpoints
5. **Type Hints**: Some Python files missing complete type annotations
6. **CSS Consistency**: Some components may deviate from dark theme

---

## 📂 Files to Create/Modify

### New Files to Create

```
app/
├── models/
│   ├── base_store.py          # Generic CRUD base class
│   ├── chat_lab_store.py      # Conversation tree storage
│   ├── guardrails_store.py    # Rules and tests storage
│   ├── history_store.py       # History entries storage
│   └── metrics_store.py       # Metrics data storage
├── routers/
│   ├── chat_lab.py            # Chat Lab endpoints
│   ├── guardrails.py          # Guardrails endpoints
│   ├── history.py             # History endpoints
│   └── metrics.py             # Metrics endpoints
└── data/
    ├── chat_lab.json          # Conversation trees
    ├── guardrails.json        # Safety rules
    ├── guardrail_tests.json   # Test cases
    ├── history.json           # Request history
    └── metrics.json           # Usage metrics
```

### Files to Modify

```
app/
├── main.py                    # Register new routers
├── config.py                  # Add file paths
├── schemas/
│   ├── requests.py            # Add new request models
│   └── responses.py           # Add new response models
├── models/
│   ├── service.py             # Add logging, integrate new features
│   ├── tools_store.py         # Update to use BaseStore
│   ├── workflow_store.py      # Update to use BaseStore
│   ├── eval_store.py          # Update to use BaseStore
│   └── prompt_templates_store.py  # Update to use BaseStore
└── static/
    ├── index.html             # Add new tab links and panels
    ├── main.js                # Add init functions for new tabs
    └── style.css              # Add styles for new components
```

---

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --port 8000

# Run tests (once implemented)
pytest tests/ -v

# Validate JSON files
python -c "import json; import pathlib; [json.loads(f.read_text()) for f in pathlib.Path('app/data').glob('*.json')]"
```

---

## 📞 Dependencies

Current (`requirements.txt`):
- fastapi
- uvicorn[standard]
- jinja2
- httpx

No additional dependencies needed for planned features.

---

## 📝 Notes

1. **Streaming Pattern**: All bulk operations and LLM calls should use SSE
2. **ID Management**: Never manually manage IDs - use BaseStore
3. **Service Singleton**: Access via `get_service()` from routers/__init__.py
4. **Dark Theme**: Maintain consistency (bg: #0f172a, cards: #1e293b, borders: #374151)
5. **No Build Step**: Keep frontend vanilla JS without npm/webpack

---

*Generated from analysis of docs/ folder on 2025-11-26*
