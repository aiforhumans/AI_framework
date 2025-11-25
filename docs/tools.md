# Tools Tab

## Overview
Tool configuration and management for function calling with models and agents.

## Features

### Tool Management
- Create new tools
- Edit existing tools
- Delete tools
- Enable/disable toggle
- Tools table with CRUD actions

### Tool Configuration
- **Name** - Tool identifier
- **Description** - Tool purpose and usage
- **Endpoint** - API URL for tool execution
- **Input Schema** - JSON schema for parameters
- **Models** - Associated model names (comma-separated)
- **Agents** - Associated agent IDs (comma-separated)
- **Enabled** - Active/inactive status

### Input Schema
- JSON-based parameter definition
- Schema validation
- Type specifications
- Required/optional parameters

### Model/Agent Associations
- Link tools to specific models
- Link tools to specific agents
- Comma-separated lists
- Multiple associations per tool

### Table View
- Tool ID
- Tool name
- Enabled status
- Action buttons (Edit, Toggle, Delete)

### Form Operations
- New tool creation
- Edit mode population
- Reset form
- Save with validation

## API Endpoints
- `GET /api/tools` - List all tools
- `POST /api/tools` - Create tool
- `PUT /api/tools/{id}` - Update tool
- `DELETE /api/tools/{id}` - Delete tool
- `POST /api/tools/{id}/toggle` - Toggle enabled status
