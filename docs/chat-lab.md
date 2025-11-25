# Chat Lab Tab

## Overview

Multi-turn branching conversation system with tree visualization.

## Features

### Conversation Trees

- Create named conversations
- Model selection
- System prompt configuration
- Conversation metadata
- Multiple independent trees

### Branching System

- Create branches from any message
- Multiple conversation paths
- Branch from specific nodes
- Switch between branches
- Visual branch indicators

### Message Management

- Send user messages
- Receive LLM responses
- View conversation history
- Message metadata (latency, tokens, model)
- Copy message content
- Delete nodes and branches

### Tree Visualization

- Hierarchical tree display
- User/assistant role indicators
- Content preview in nodes
- Active path highlighting
- Branch name labels
- Click nodes to switch paths

### Navigation

- Switch to any node
- Follow conversation threads
- View full history up to node
- Active conversation tracking

### Message Actions

- 🌿 Branch from message
- 📋 Copy message text
- View message metadata
- Navigate tree structure

## API Endpoints

- `GET /api/chat-lab/trees` - List conversation trees
- `POST /api/chat-lab/trees` - Create tree
- `GET /api/chat-lab/trees/{id}` - Get tree details
- `PUT /api/chat-lab/trees/{id}` - Update tree
- `DELETE /api/chat-lab/trees/{id}` - Delete tree
- `GET /api/chat-lab/trees/{id}/structure` - Get tree structure
- `GET /api/chat-lab/trees/{id}/history` - Get conversation history
- `POST /api/chat-lab/trees/{id}/messages` - Send message
- `POST /api/chat-lab/trees/{id}/branch` - Create branch
- `POST /api/chat-lab/trees/{id}/switch` - Switch active path
- `DELETE /api/chat-lab/trees/{id}/nodes/{node_id}` - Delete node
