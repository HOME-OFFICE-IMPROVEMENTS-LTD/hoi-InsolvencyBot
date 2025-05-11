"""
Monitoring and Metrics for InsolvencyBot

This module provides monitoring and metrics collection for the InsolvencyBot
application, tracking performance, usage patterns, and errors.
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Metrics collector for tracking API usage and performance.
    
    This class collects metrics on:
    - Request count
    - Response times
    - Error rates
    - Model usage
    - Rate limit encounters
    """
    
    def __init__(self, window_size: int = 60):
        """
        Initialize the metrics collector.
        
        Args:
            window_size: Size of the rolling window in minutes for stats
        """
        self.window_size = window_size
        self.request_count = 0
        self.error_count = 0
        self.model_usage: Dict[str, int] = defaultdict(int)
        self.status_codes: Dict[int, int] = defaultdict(int)
        
        # Time-based metrics with rolling window
        self.response_times: deque = deque(maxlen=1000)
        self.requests_by_minute: Dict[datetime, int] = defaultdict(int)
        self.errors_by_minute: Dict[datetime, int] = defaultdict(int)
        
        # Rate limiting
        self.rate_limit_encounters = 0
        
        # Thread lock for thread safety
        self.lock = threading.RLock()
        
        # Periodic cleanup for time-based metrics
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start a thread to periodically clean up old metrics data."""
        def cleanup():
            while True:
                time.sleep(60)  # Run every minute
                self._cleanup_old_data()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_old_data(self):
        """Remove data older than window_size minutes."""
        with self.lock:
            cutoff = datetime.now() - timedelta(minutes=self.window_size)
            
            # Clean up time-based metrics
            self.requests_by_minute = {k: v for k, v in self.requests_by_minute.items() 
                                    if k >= cutoff}
            self.errors_by_minute = {k: v for k, v in self.errors_by_minute.items() 
                                  if k >= cutoff}
    
    def record_request(self, model: str = "unknown"):
        """
        Record a new request.
        
        Args:
            model: The model used for the request
        """
        with self.lock:
            self.request_count += 1
            self.model_usage[model] += 1
            
            # Record by time
            now = datetime.now().replace(second=0, microsecond=0)
            if now not in self.requests_by_minute:
                self.requests_by_minute[now] = 0
            self.requests_by_minute[now] += 1
    
    def record_response_time(self, duration: float):
        """
        Record a response time.
        
        Args:
            duration: Response time in seconds
        """
        with self.lock:
            self.response_times.append(duration)
    
    def record_error(self, status_code: int = 500):
        """
        Record an error.
        
        Args:
            status_code: HTTP status code of the error
        """
        with self.lock:
            self.error_count += 1
            self.status_codes[status_code] += 1
            
            # Record by time
            now = datetime.now().replace(second=0, microsecond=0)
            if now not in self.errors_by_minute:
                self.errors_by_minute[now] = 0
            self.errors_by_minute[now] += 1
    
    def record_rate_limit(self):
        """Record a rate limit encounter."""
        with self.lock:
            self.rate_limit_encounters += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected metrics.
        
        Returns:
            Dict containing summary metrics
        """
        with self.lock:
            response_times = list(self.response_times)
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": self.error_count / self.request_count if self.request_count else 0,
                "average_response_time": avg_response_time,
                "rate_limit_encounters": self.rate_limit_encounters,
                "model_usage": dict(self.model_usage),
                "status_codes": dict(self.status_codes),
                "requests_per_minute": {time.strftime("%H:%M"): count 
                                     for time, count in self.requests_by_minute.items()},
                "errors_per_minute": {time.strftime("%H:%M"): count 
                                   for time, count in self.errors_by_minute.items()},
            }
    
    def reset(self):
        """Reset all metrics."""
        with self.lock:
            self.request_count = 0
            self.error_count = 0
            self.model_usage.clear()
            self.status_codes.clear()
            self.response_times.clear()
            self.requests_by_minute.clear()
            self.errors_by_minute.clear()
            self.rate_limit_encounters = 0


# Create a global metrics collector instance
metrics = MetricsCollector()


class RequestTracker:
    """Context manager to track request performance and outcomes."""
    
    def __init__(self, model: str = "unknown"):
        """
        Initialize a request tracker.
        
        Args:
            model: The model used for the request
        """
        self.model = model
        self.start_time = None
        self.error_status = None
    
    def __enter__(self):
        """Start tracking the request."""
        self.start_time = time.time()
        metrics.record_request(model=self.model)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Finish tracking the request.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        duration = time.time() - self.start_time
        metrics.record_response_time(duration)
        
        if exc_val:
            metrics.record_error()
            
            # Track rate limit errors specifically
            if hasattr(exc_val, "status_code") and exc_val.status_code == 429:
                metrics.record_rate_limit()
            
            # Log the error
            logger.error(f"Error processing request: {exc_val}")
        
        if self.error_status:
            metrics.record_error(status_code=self.error_status)
    
    def record_error(self, status_code: int = 500):
        """
        Record an error with a specific status code.
        
        Args:
            status_code: HTTP status code of the error
        """
        self.error_status = status_code
