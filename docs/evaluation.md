# Evaluation Tab

## Overview
Comprehensive evaluation suite for testing LLM performance with datasets and evaluators.

## Features

### Dataset Management
- Create/edit/delete datasets
- JSONL format support
- Query/response/ground_truth structure
- 8 built-in templates:
  - Factual Q&A
  - Math Q&A
  - Summarization
  - Sentiment Analysis
  - Translation (EN→ES)
  - Code Generation
  - Text Classification
  - RAG (Retrieval QA)

### Bulk Generation
- Run all queries through model/agent
- SSE streaming with live progress
- Real-time response preview
- Progress bar with counts
- Auto-populate responses

### Evaluators
**Built-in:**
- Exact match
- Contains check
- Similarity scoring
- Length validation

**Custom LLM-based:**
- Define evaluation prompt
- AI-powered scoring
- Natural language criteria

**Custom Code-based:**
- Python code evaluators
- Custom scoring logic
- Flexible evaluation

### Evaluation Jobs
- Create evaluation jobs
- Apply multiple evaluators
- Dataset-wide scoring
- Aggregate results
- Pass/fail per row
- Job history
- Detailed results view

## API Endpoints
- `GET /api/datasets` - List datasets
- `POST /api/datasets` - Create dataset
- `PUT /api/datasets/{id}` - Update dataset
- `DELETE /api/datasets/{id}` - Delete dataset
- `POST /api/datasets/{id}/bulk-run-stream` - Bulk generation with streaming
- `GET /api/evaluators` - List evaluators
- `POST /api/evaluators/custom` - Create custom evaluator
- `GET /api/eval-jobs` - List evaluation jobs
- `POST /api/eval-jobs` - Create job
- `POST /api/eval-jobs/{id}/run` - Run evaluation
