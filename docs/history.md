# History Tab

## Overview
Request/response logging system with replay and annotation capabilities.

## Features

### Entry Browsing
- Paginated list (20 per page)
- Chronological ordering
- Entry selection
- Detailed view

### Filtering
- Filter by endpoint
- Filter by model
- Filter by success/error status
- Filter by starred status
- Text search across content
- Combined filters

### Metadata Tracking
- Timestamp and "time ago" display
- Endpoint and model used
- Latency measurement
- Token usage (prompt, completion, total)
- Success/error status
- Request/response content
- Error messages

### Annotations
- Add/edit notes
- Star/unstar entries
- Tag support
- Keep starred on clear

### Replay Functionality
- Replay historical requests
- Compare original vs new responses
- Override parameters
- Latency comparison

### Statistics Dashboard
- Total entries count
- Success rate percentage
- Average latency
- Total tokens used
- Starred entries count

### Bulk Operations
- Clear all history
- Keep starred option
- Mass delete

### Entry Details View
- Full request payload
- System prompt
- User prompt/messages
- Complete response
- Metrics breakdown
- Notes editor

## API Endpoints
- `GET /api/history` - List history entries
- `GET /api/history/stats` - Get statistics
- `GET /api/history/endpoints` - List unique endpoints
- `GET /api/history/models` - List unique models
- `GET /api/history/{id}` - Get entry details
- `PUT /api/history/{id}` - Update entry (notes, starred, tags)
- `DELETE /api/history/{id}` - Delete entry
- `POST /api/history/clear` - Clear history
- `POST /api/history/replay` - Replay request
