# Orchestrator Tab (Workflows)

## Overview
Visual workflow builder for creating complex multi-step agent orchestration.

## Features

### Visual Canvas
- Drag-and-drop nodes
- SVG edge rendering
- Node positioning
- Visual connections
- Zoom/pan support

### Node Types

**Start Node**
- Workflow entry point
- Input configuration

**Agent Node**
- Model selection
- System prompt
- Prompt template with `{{variables}}`

**Tool Node**
- Tool ID specification
- Input template
- Tool execution

**Condition Node**
- Expression-based routing
- Operators: contains, equals, startswith, endswith, >, <, >=, <=
- Conditional branching

**End Node**
- Workflow termination
- Output collection

### Edge Management
- Connect nodes
- Conditional edges
- Edge labels
- Remove connections
- Visual arrows

### Node Configuration
- Label editing
- Type-specific settings
- Config validation
- Delete nodes

### Workflow Execution
- Run workflows with input
- SSE streaming progress
- Step-by-step visualization
- Error tracking
- Final output display

### Workflow Management
- Save/load workflows
- Workflow library
- Run history
- Execution logs

## API Endpoints
- `GET /api/workflows` - List workflows
- `POST /api/workflows` - Create workflow
- `PUT /api/workflows/{id}` - Update workflow
- `DELETE /api/workflows/{id}` - Delete workflow
- `POST /api/workflows/{id}/run` - Execute workflow
- `GET /api/workflow-runs` - List runs
- `GET /api/workflow-runs/{id}` - Get run details
