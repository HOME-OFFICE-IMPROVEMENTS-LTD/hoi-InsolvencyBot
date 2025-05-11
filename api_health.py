"""
InsolvencyBot API Health Check Endpoints

This module adds diagnostic and monitoring endpoints to the InsolvencyBot API.
These endpoints allow checking the health of the API and its components.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import time
import os
import platform
import sys
import psutil
from starlette.middleware.base import BaseHTTPMiddleware

# Create router
health_router = APIRouter()

# Global metrics for monitoring
api_metrics = {
    "start_time": time.time(),
    "requests": 0,
    "errors": 0,
    "average_response_time": 0,
    "total_response_time": 0,
    "response_times": [],  # Keep track of recent response times
    "last_error": None,
    "last_error_time": None
}

def format_uptime(seconds):
    """
    Format uptime seconds into a human-readable string.
    
    Args:
        seconds: Uptime in seconds
        
    Returns:
        str: Formatted uptime string (e.g. "2d 5h 30m 10s")
    """
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

@health_router.get("/health", summary="Get API health status")
async def get_health() -> Dict[str, Any]:
    """
    Check the health status of the API and return diagnostic information.
    
    Returns:
        Dict[str, Any]: Health check results
    """
    # Current system information
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Calculate uptime
    uptime_seconds = time.time() - api_metrics["start_time"]
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_formatted = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    
    return {
        "status": "healthy",
        "uptime": uptime_formatted,
        "uptime_seconds": uptime_seconds,
        "system_info": {
            "python_version": sys.version,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "process_info": {
            "memory_usage_mb": memory_info.rss / (1024 * 1024),
            "cpu_percent": process.cpu_percent(interval=0.5),
            "threads": process.num_threads()
        },
        "disk_usage": {
            "percent": psutil.disk_usage('/').percent,
            "free_gb": psutil.disk_usage('/').free / (1024 * 1024 * 1024)
        },
        "metrics": {
            "total_requests": api_metrics["requests"],
            "total_errors": api_metrics["errors"],
            "average_response_time_ms": api_metrics["average_response_time"]
        }
    }

@health_router.get("/metrics", summary="Get API usage metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get detailed metrics about API usage and performance.
    
    Returns:
        Dict[str, Any]: Metrics data
    """
    return {
        "requests": api_metrics["requests"],
        "errors": api_metrics["errors"],
        "average_response_time_ms": api_metrics["average_response_time"],
        "uptime_seconds": time.time() - api_metrics["start_time"],
        "last_error": api_metrics["last_error"],
        "last_error_time": api_metrics["last_error_time"]
    }

@health_router.get("/diagnostic", summary="Get simplified system diagnostic information")
async def get_diagnostic() -> Dict[str, Any]:
    """
    Get simplified diagnostic information about the system and API.
    
    Returns:
        Dict[str, Any]: Basic system metrics
    """
    try:
        # Current system information
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Calculate uptime
        uptime_seconds = time.time() - api_metrics["start_time"]
        
        return {
            "status": "operational",
            "uptime_formatted": format_uptime(uptime_seconds),
            "uptime_seconds": int(uptime_seconds),
            "memory_mb": round(memory_info.rss / (1024 * 1024), 2),
            "cpu_percent": round(process.cpu_percent(interval=0.1), 1),
            "disk_percent": round(psutil.disk_usage('/').percent, 1),
            "requests_total": api_metrics["requests"],
            "errors_total": api_metrics["errors"],
            "python_version": sys.version.split()[0],
            "platform": platform.system()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Utility function to update metrics
def track_request(duration_ms: float, is_error: bool = False, error_message: str = None):
    """
    Update API usage metrics.
    
    Args:
        duration_ms: Request processing time in milliseconds
        is_error: Whether the request resulted in an error
        error_message: Error message if is_error is True
    """
    api_metrics["requests"] += 1
    api_metrics["total_response_time"] += duration_ms
    api_metrics["average_response_time"] = api_metrics["total_response_time"] / api_metrics["requests"]
    
    if is_error:
        api_metrics["errors"] += 1
        api_metrics["last_error"] = error_message
        api_metrics["last_error_time"] = time.time()

# Middleware class for tracking requests
class TrackRequestsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track request metrics.
    """
    async def dispatch(self, request, call_next):
        """
        Process the request and track metrics.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next handler
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Track response time
            duration_ms = (time.time() - start_time) * 1000
            
            # Keep track of recent response times (last 100)
            api_metrics["response_times"].append(duration_ms)
            if len(api_metrics["response_times"]) > 100:
                api_metrics["response_times"].pop(0)
                
            # Update metrics
            is_error = response.status_code >= 400
            track_request(duration_ms, is_error, f"Status code: {response.status_code}" if is_error else None)
            
            return response
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            track_request(duration_ms, is_error=True, error_message=str(e))
            raise  # Re-raise the exception to be handled by FastAPI
