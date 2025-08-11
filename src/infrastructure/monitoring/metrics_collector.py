"""Metrics collector for monitoring application performance."""

from typing import Dict, Any
import time
from src.infrastructure.monitoring.logging_config import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
    
    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric.
        
        Args:
            name: The metric name
            value: The value to increment by
        """
        if name not in self.metrics:
            self.metrics[name] = 0
        self.metrics[name] += value
        logger.debug(f"Counter {name} incremented by {value}")
    
    def observe_histogram(self, name: str, value: float) -> None:
        """Observe a histogram metric.
        
        Args:
            name: The metric name
            value: The observed value
        """
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        logger.debug(f"Histogram {name} observed value {value}")
    
    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric.
        
        Args:
            name: The metric name
            value: The gauge value
        """
        self.metrics[name] = value
        logger.debug(f"Gauge {name} set to {value}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, metrics_collector: MetricsCollector, metric_name: str):
        self.metrics_collector = metrics_collector
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics_collector.observe_histogram(self.metric_name, duration)