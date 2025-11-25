# Prompt Builder Tab

## Overview
Template system for creating reusable prompts with variable substitution.

## Features

### Template Management
- Create custom templates
- Edit existing templates
- Delete templates
- Template categories

### Categories
- **Chain-of-Thought (CoT)** - Step-by-step reasoning templates
- **Few-Shot** - Example-based learning templates
- **Role-Play** - Character/persona templates
- **General** - Standard purpose templates
- **Custom** - User-defined templates

### Preset Library
- 20+ built-in templates
- Category filtering
- Load presets as starting points
- Copy and customize presets

### Variable System
- `{{variable}}` placeholder syntax
- Live preview with substitution
- JSON variable input
- Multiple variable support

### Template Fields
- Name and description
- System prompt
- User prompt
- Variable list
- Category selection

### Integration
- Apply templates directly to Playground
- Export templates
- Template preview before applying

## API Endpoints
- `GET /api/prompt-templates` - List templates
- `GET /api/prompt-templates/categories` - List categories
- `POST /api/prompt-templates` - Create template
- `PUT /api/prompt-templates/{id}` - Update template
- `DELETE /api/prompt-templates/{id}` - Delete template
