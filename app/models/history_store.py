"""
History & Replay Store
Logs all LLM requests and responses for debugging and replay.
"""

import json
import time
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime


class HistoryEntry(BaseModel):
    """A single request/response log entry."""
    id: int
    timestamp: float = Field(default_factory=time.time)
    endpoint: str  # generate, chat, ab_test, chat_lab, workflow, etc.
    
    # Request details
    model: Optional[str] = None
    agent_id: Optional[str] = None
    prompt: Optional[str] = None
    system_prompt: Optional[str] = None
    messages: Optional[List[Dict[str, str]]] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)  # max_tokens, temperature, etc.
    
    # Response details
    response: Optional[str] = None
    response_messages: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None
    
    # Metrics
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    success: bool = True
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    notes: str = ""
    starred: bool = False


class HistoryFilter(BaseModel):
    """Filter criteria for history queries."""
    endpoint: Optional[str] = None
    model: Optional[str] = None
    success: Optional[bool] = None
    starred: Optional[bool] = None
    tags: Optional[List[str]] = None
    from_timestamp: Optional[float] = None
    to_timestamp: Optional[float] = None
    search: Optional[str] = None  # Search in prompt/response


class HistoryStore:
    """Persists history entries to JSON with search and filter capabilities."""
    
    MAX_ENTRIES = 10000  # Maximum entries to keep
    
    def __init__(self, data_dir: str = "app/data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._data_dir / "history.json"
        self._entries: List[HistoryEntry] = []
        self._next_id = 1
        self._load()
    
    def _load(self):
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                for item in data.get("entries", []):
                    entry = HistoryEntry(**item)
                    self._entries.append(entry)
                    if entry.id >= self._next_id:
                        self._next_id = entry.id + 1
            except Exception:
                pass
    
    def _save(self):
        data = {"entries": [e.model_dump() for e in self._entries]}
        self._file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def _enforce_limit(self):
        """Remove oldest entries if over limit."""
        if len(self._entries) > self.MAX_ENTRIES:
            # Keep starred entries and newest entries
            starred = [e for e in self._entries if e.starred]
            non_starred = [e for e in self._entries if not e.starred]
            
            # Sort non-starred by timestamp (newest first)
            non_starred.sort(key=lambda e: e.timestamp, reverse=True)
            
            # Keep as many as we can
            keep_count = self.MAX_ENTRIES - len(starred)
            if keep_count > 0:
                self._entries = starred + non_starred[:keep_count]
            else:
                # Too many starred, keep newest starred
                starred.sort(key=lambda e: e.timestamp, reverse=True)
                self._entries = starred[:self.MAX_ENTRIES]
    
    def record(self, 
               endpoint: str,
               model: str = None,
               agent_id: str = None,
               prompt: str = None,
               system_prompt: str = None,
               messages: List[Dict] = None,
               parameters: Dict = None,
               response: str = None,
               response_messages: List[Dict] = None,
               error: str = None,
               latency_ms: float = None,
               prompt_tokens: int = None,
               completion_tokens: int = None,
               total_tokens: int = None,
               success: bool = True,
               tags: List[str] = None) -> HistoryEntry:
        """Record a new history entry."""
        entry = HistoryEntry(
            id=self._next_id,
            endpoint=endpoint,
            model=model,
            agent_id=agent_id,
            prompt=prompt,
            system_prompt=system_prompt,
            messages=messages,
            parameters=parameters or {},
            response=response,
            response_messages=response_messages,
            error=error,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            success=success,
            tags=tags or []
        )
        
        self._entries.append(entry)
        self._next_id += 1
        self._enforce_limit()
        self._save()
        return entry
    
    def list(self, 
             filter: HistoryFilter = None,
             limit: int = 100,
             offset: int = 0) -> List[HistoryEntry]:
        """List history entries with optional filtering."""
        entries = self._entries.copy()
        
        if filter:
            if filter.endpoint:
                entries = [e for e in entries if e.endpoint == filter.endpoint]
            if filter.model:
                entries = [e for e in entries if e.model == filter.model]
            if filter.success is not None:
                entries = [e for e in entries if e.success == filter.success]
            if filter.starred is not None:
                entries = [e for e in entries if e.starred == filter.starred]
            if filter.tags:
                entries = [e for e in entries if any(t in e.tags for t in filter.tags)]
            if filter.from_timestamp:
                entries = [e for e in entries if e.timestamp >= filter.from_timestamp]
            if filter.to_timestamp:
                entries = [e for e in entries if e.timestamp <= filter.to_timestamp]
            if filter.search:
                search_lower = filter.search.lower()
                entries = [e for e in entries if (
                    (e.prompt and search_lower in e.prompt.lower()) or
                    (e.response and search_lower in e.response.lower()) or
                    (e.system_prompt and search_lower in e.system_prompt.lower())
                )]
        
        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply pagination
        return entries[offset:offset + limit]
    
    def get(self, entry_id: int) -> Optional[HistoryEntry]:
        """Get a specific history entry."""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def update(self, entry_id: int, **kwargs) -> Optional[HistoryEntry]:
        """Update a history entry (notes, tags, starred)."""
        for entry in self._entries:
            if entry.id == entry_id:
                for key, value in kwargs.items():
                    if key in ("notes", "tags", "starred"):
                        setattr(entry, key, value)
                self._save()
                return entry
        return None
    
    def delete(self, entry_id: int) -> bool:
        """Delete a history entry."""
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                del self._entries[i]
                self._save()
                return True
        return False
    
    def clear(self, keep_starred: bool = True) -> int:
        """Clear history entries. Returns count of deleted entries."""
        if keep_starred:
            original_count = len(self._entries)
            self._entries = [e for e in self._entries if e.starred]
            deleted = original_count - len(self._entries)
        else:
            deleted = len(self._entries)
            self._entries = []
        
        self._save()
        return deleted
    
    def get_stats(self) -> Dict[str, Any]:
        """Get history statistics."""
        if not self._entries:
            return {
                "total_entries": 0,
                "endpoints": {},
                "models": {},
                "success_rate": 0,
                "avg_latency_ms": 0,
                "total_tokens": 0,
                "starred_count": 0,
            }
        
        endpoints = {}
        models = {}
        success_count = 0
        latencies = []
        total_tokens = 0
        starred_count = 0
        
        for entry in self._entries:
            endpoints[entry.endpoint] = endpoints.get(entry.endpoint, 0) + 1
            if entry.model:
                models[entry.model] = models.get(entry.model, 0) + 1
            if entry.success:
                success_count += 1
            if entry.latency_ms:
                latencies.append(entry.latency_ms)
            if entry.total_tokens:
                total_tokens += entry.total_tokens
            if entry.starred:
                starred_count += 1
        
        return {
            "total_entries": len(self._entries),
            "endpoints": endpoints,
            "models": models,
            "success_rate": (success_count / len(self._entries) * 100) if self._entries else 0,
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "total_tokens": total_tokens,
            "starred_count": starred_count,
            "oldest_entry": min(e.timestamp for e in self._entries),
            "newest_entry": max(e.timestamp for e in self._entries),
        }
    
    def get_endpoints(self) -> List[str]:
        """Get list of unique endpoints."""
        return list(set(e.endpoint for e in self._entries))
    
    def get_models(self) -> List[str]:
        """Get list of unique models used."""
        return list(set(e.model for e in self._entries if e.model))
