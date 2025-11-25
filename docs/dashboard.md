# Dashboard Tab (Metrics)

## Overview
Latency and usage metrics dashboard with charts and breakdowns.

## Features

### Summary Statistics
- Total requests count
- Success rate percentage
- Average latency
- P95 latency percentile
- P99 latency percentile
- Total tokens consumed
- Tokens per second
- Requests per minute

### Model Breakdown Table
- Request count per model
- Average latency per model
- Total tokens per model
- Success rate per model
- Visual success rate bars

### Endpoint Breakdown Table
- Request count per endpoint
- Average latency per endpoint
- Success rate per endpoint
- Visual rate indicators

### Hourly Trends Chart
- Bar chart visualization
- Request volume over time
- Average latency per hour
- Hover tooltips with details
- Time axis labels

### Recent Requests Table
- Last 50 requests
- Time ago display
- Endpoint and model info
- Latency values with color coding
- Token usage
- Success/error badges

### Time Range Selection
- Last 1 hour
- Last 6 hours
- Last 12 hours
- Last 24 hours (default)
- Last 48 hours

### Data Management
- Refresh metrics
- Clear all metrics
- Auto-refresh capability

### Visual Indicators
- Color-coded latency (fast/medium/slow)
- Success rate bars
- Status badges
- Icon indicators

## API Endpoints
- `GET /api/metrics/summary` - Get summary stats
- `GET /api/metrics/list` - Get recent metrics
- `GET /api/metrics/by-model` - Model breakdown
- `GET /api/metrics/by-endpoint` - Endpoint breakdown
- `GET /api/metrics/hourly` - Hourly trends
- `DELETE /api/metrics` - Clear all metrics
