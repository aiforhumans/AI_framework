# Playground Tab

## Overview
Interactive multi-turn chat interface for testing LLM responses with streaming support.

## Features

### Chat Interface
- Multi-turn conversation support
- Streaming and non-streaming modes
- Chat history persistence
- Clear chat functionality

### Model Configuration
- Model selection dropdown
- Agent selection with custom instructions
- System prompt/agent instructions editor
- Temperature control
- Max tokens configuration

### Prompt Management
- Auto-resizing textarea
- Character count tracking
- Shift+Enter for newlines, Enter to send
- AI-powered prompt improvement

### File Attachments
- Image file support
- Text file support
- Attachment preview
- Remove attachments functionality

### AI Prompt Generator
- Improve system prompts
- Improve user prompts
- Copy generated prompts
- Apply to system or message fields
- Modal dialog interface

## API Endpoints
- `GET /api/models` - List available models
- `POST /api/generate` - Single-turn generation
- `POST /api/chat` - Multi-turn chat (streaming/non-streaming)
- `POST /api/prompt-generator` - AI prompt improvement
