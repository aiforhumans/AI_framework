"""Metrics store for tracking latency, token usage, and performance metrics."""

import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class MetricEntry(BaseModel):
    """Single metric entry for a request."""
    id: int = 0
    timestamp: str = ""
    endpoint: str = ""  # e.g., "chat", "generate", "ab-test", "workflow", "eval"
    model_name: str = ""
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    
    # Latency metrics
    latency_ms: float = 0.0
    time_to_first_token_ms: Optional[float] = None
    
    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Request info
    prompt_length: int = 0
    response_length: int = 0
    max_tokens_requested: int = 0
    temperature: float = 0.7
    
    # Status
    success: bool = True
    error: Optional[str] = None
    
    # Additional context
    metadata: Dict[str, Any] = {}


class MetricsSummary(BaseModel):
    """Aggregated metrics summary."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Latency stats
    avg_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Token stats
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    avg_prompt_tokens: float = 0.0
    avg_completion_tokens: float = 0.0
    
    # Throughput
    tokens_per_second: float = 0.0
    requests_per_minute: float = 0.0
    
    # Time range
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class ModelMetrics(BaseModel):
    """Metrics grouped by model."""
    model_name: str
    request_count: int = 0
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    success_rate: float = 0.0
    avg_tokens_per_request: float = 0.0


class EndpointMetrics(BaseModel):
    """Metrics grouped by endpoint."""
    endpoint: str
    request_count: int = 0
    avg_latency_ms: float = 0.0
    success_rate: float = 0.0


class HourlyMetrics(BaseModel):
    """Metrics for a specific hour."""
    hour: str  # ISO format hour
    request_count: int = 0
    avg_latency_ms: float = 0.0
    total_tokens: int = 0
    error_count: int = 0


class MetricsStore:
    """Store for performance metrics with file persistence."""
    
    def __init__(self, file_path: str = "app/data/metrics.json"):
        self.file_path = file_path
        self._metrics: List[MetricEntry] = []
        self._next_id = 1
        self._max_entries = 10000  # Keep last 10k entries
        self._load()

    def _load(self):
        """Load metrics from file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                self._metrics = [MetricEntry(**m) for m in data.get("metrics", [])]
                self._next_id = data.get("next_id", 1)
            except Exception:
                self._metrics = []
                self._next_id = 1

    def _save(self):
        """Save metrics to file."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump({
                "metrics": [m.model_dump() for m in self._metrics],
                "next_id": self._next_id,
            }, f, indent=2)

    def record(
        self,
        endpoint: str,
        model_name: str,
        latency_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        prompt_length: int = 0,
        response_length: int = 0,
        max_tokens_requested: int = 0,
        temperature: float = 0.7,
        agent_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        success: bool = True,
        error: Optional[str] = None,
        time_to_first_token_ms: Optional[float] = None,
        metadata: Dict[str, Any] = None,
    ) -> MetricEntry:
        """Record a new metric entry."""
        entry = MetricEntry(
            id=self._next_id,
            timestamp=datetime.now().isoformat(),
            endpoint=endpoint,
            model_name=model_name,
            agent_id=agent_id,
            agent_name=agent_name,
            latency_ms=latency_ms,
            time_to_first_token_ms=time_to_first_token_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            prompt_length=prompt_length,
            response_length=response_length,
            max_tokens_requested=max_tokens_requested,
            temperature=temperature,
            success=success,
            error=error,
            metadata=metadata or {},
        )
        
        self._metrics.append(entry)
        self._next_id += 1
        
        # Trim old entries if needed
        if len(self._metrics) > self._max_entries:
            self._metrics = self._metrics[-self._max_entries:]
        
        self._save()
        return entry

    def list_all(self, limit: int = 100, offset: int = 0) -> List[MetricEntry]:
        """List metrics with pagination (newest first)."""
        sorted_metrics = sorted(self._metrics, key=lambda m: m.timestamp, reverse=True)
        return sorted_metrics[offset:offset + limit]

    def list_by_endpoint(self, endpoint: str, limit: int = 100) -> List[MetricEntry]:
        """List metrics for a specific endpoint."""
        filtered = [m for m in self._metrics if m.endpoint == endpoint]
        return sorted(filtered, key=lambda m: m.timestamp, reverse=True)[:limit]

    def list_by_model(self, model_name: str, limit: int = 100) -> List[MetricEntry]:
        """List metrics for a specific model."""
        filtered = [m for m in self._metrics if m.model_name == model_name]
        return sorted(filtered, key=lambda m: m.timestamp, reverse=True)[:limit]

    def list_by_time_range(self, start: str, end: str) -> List[MetricEntry]:
        """List metrics within a time range (ISO format)."""
        return [
            m for m in self._metrics
            if start <= m.timestamp <= end
        ]

    def get_summary(self, hours: int = 24) -> MetricsSummary:
        """Get aggregated metrics summary for the last N hours."""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        recent = [m for m in self._metrics if m.timestamp >= cutoff]
        
        if not recent:
            return MetricsSummary()
        
        # Calculate stats
        latencies = [m.latency_ms for m in recent]
        latencies_sorted = sorted(latencies)
        
        successful = [m for m in recent if m.success]
        failed = [m for m in recent if not m.success]
        
        # Percentiles
        def percentile(data, p):
            if not data:
                return 0.0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f + 1 < len(data) else f
            return data[f] + (data[c] - data[f]) * (k - f) if c < len(data) else data[f]
        
        total_time_ms = sum(m.latency_ms for m in recent)
        total_tokens = sum(m.total_tokens for m in recent)
        
        # Time range
        timestamps = [m.timestamp for m in recent]
        start_time = min(timestamps)
        end_time = max(timestamps)
        
        # Calculate throughput
        try:
            time_span_seconds = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds()
            tokens_per_second = total_tokens / time_span_seconds if time_span_seconds > 0 else 0
            requests_per_minute = (len(recent) / time_span_seconds) * 60 if time_span_seconds > 0 else 0
        except Exception:
            tokens_per_second = 0.0
            requests_per_minute = 0.0
        
        return MetricsSummary(
            total_requests=len(recent),
            successful_requests=len(successful),
            failed_requests=len(failed),
            avg_latency_ms=sum(latencies) / len(latencies) if latencies else 0.0,
            min_latency_ms=min(latencies) if latencies else 0.0,
            max_latency_ms=max(latencies) if latencies else 0.0,
            p50_latency_ms=percentile(latencies_sorted, 50),
            p95_latency_ms=percentile(latencies_sorted, 95),
            p99_latency_ms=percentile(latencies_sorted, 99),
            total_prompt_tokens=sum(m.prompt_tokens for m in recent),
            total_completion_tokens=sum(m.completion_tokens for m in recent),
            total_tokens=total_tokens,
            avg_prompt_tokens=sum(m.prompt_tokens for m in recent) / len(recent) if recent else 0.0,
            avg_completion_tokens=sum(m.completion_tokens for m in recent) / len(recent) if recent else 0.0,
            tokens_per_second=tokens_per_second,
            requests_per_minute=requests_per_minute,
            start_time=start_time,
            end_time=end_time,
        )

    def get_model_breakdown(self, hours: int = 24) -> List[ModelMetrics]:
        """Get metrics broken down by model."""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        recent = [m for m in self._metrics if m.timestamp >= cutoff]
        
        # Group by model
        by_model: Dict[str, List[MetricEntry]] = {}
        for m in recent:
            if m.model_name not in by_model:
                by_model[m.model_name] = []
            by_model[m.model_name].append(m)
        
        results = []
        for model_name, entries in by_model.items():
            successful = sum(1 for e in entries if e.success)
            results.append(ModelMetrics(
                model_name=model_name,
                request_count=len(entries),
                avg_latency_ms=sum(e.latency_ms for e in entries) / len(entries) if entries else 0.0,
                total_tokens=sum(e.total_tokens for e in entries),
                success_rate=successful / len(entries) if entries else 0.0,
                avg_tokens_per_request=sum(e.total_tokens for e in entries) / len(entries) if entries else 0.0,
            ))
        
        return sorted(results, key=lambda x: x.request_count, reverse=True)

    def get_endpoint_breakdown(self, hours: int = 24) -> List[EndpointMetrics]:
        """Get metrics broken down by endpoint."""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        recent = [m for m in self._metrics if m.timestamp >= cutoff]
        
        # Group by endpoint
        by_endpoint: Dict[str, List[MetricEntry]] = {}
        for m in recent:
            if m.endpoint not in by_endpoint:
                by_endpoint[m.endpoint] = []
            by_endpoint[m.endpoint].append(m)
        
        results = []
        for endpoint, entries in by_endpoint.items():
            successful = sum(1 for e in entries if e.success)
            results.append(EndpointMetrics(
                endpoint=endpoint,
                request_count=len(entries),
                avg_latency_ms=sum(e.latency_ms for e in entries) / len(entries) if entries else 0.0,
                success_rate=successful / len(entries) if entries else 0.0,
            ))
        
        return sorted(results, key=lambda x: x.request_count, reverse=True)

    def get_hourly_breakdown(self, hours: int = 24) -> List[HourlyMetrics]:
        """Get metrics broken down by hour."""
        from datetime import timedelta
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        recent = [m for m in self._metrics if m.timestamp >= cutoff]
        
        # Group by hour
        by_hour: Dict[str, List[MetricEntry]] = {}
        for m in recent:
            hour = m.timestamp[:13]  # YYYY-MM-DDTHH
            if hour not in by_hour:
                by_hour[hour] = []
            by_hour[hour].append(m)
        
        results = []
        for hour, entries in by_hour.items():
            error_count = sum(1 for e in entries if not e.success)
            results.append(HourlyMetrics(
                hour=hour,
                request_count=len(entries),
                avg_latency_ms=sum(e.latency_ms for e in entries) / len(entries) if entries else 0.0,
                total_tokens=sum(e.total_tokens for e in entries),
                error_count=error_count,
            ))
        
        return sorted(results, key=lambda x: x.hour)

    def clear(self):
        """Clear all metrics."""
        self._metrics = []
        self._next_id = 1
        self._save()

    def count(self) -> int:
        """Get total count of metrics."""
        return len(self._metrics)
