"""
InsolvencyBot API

This module provides a FastAPI-based REST API for the InsolvencyBot, allowing
developers to integrate InsolvencyBot's capabilities with their own applications.

The API includes endpoints for:
- Getting information about the API
- Processing insolvency law questions
- Retrieving available models
"""

import os
import time
from enum import Enum
from typing import Dict, List, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, Header, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field

from src.hoi_insolvencybot.insolvency_bot import answer_question
from src.hoi_insolvencybot.logging_config import setup_logging, get_logger
from src.hoi_insolvencybot.config import config
from src.hoi_insolvencybot.monitoring import RequestTracker, metrics as tracker

# Set up logging
setup_logging()
logger = get_logger(__name__)

# Setup tracking variables
start_time = time.time()
request_count = 0
success_count = 0
error_count = 0
model_usage = {
    "gpt-3.5-turbo": 0,
    "gpt-4": 0,
    "gpt-4o": 0
}

# Create FastAPI app
app = FastAPI(
    title="InsolvencyBot API",
    description="API for the InsolvencyBot, providing insolvency law guidance with citations to legislation, cases, and forms.",
    version="1.0.0",
    contact={
        "name": "Fast Data Science",
        "url": "https://fastdatascience.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (consider restricting in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits = {}  # IP -> (last_request_time, request_count)
        self.rate_window = 60  # 1 minute window
        self.rate_max = 10     # 10 requests per minute
    
    async def dispatch(self, request: Request, call_next):
        """Process each request to apply rate limiting."""
        # Skip rate limiting for non-API endpoints
        if not request.url.path.startswith("/ask"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        current_time = time.time()
        
        # Check rate limit
        if client_ip in self.rate_limits:
            last_time, count = self.rate_limits[client_ip]
            # If within current time window
            if current_time - last_time < self.rate_window:
                if count >= self.rate_max:
                    logger.warning(f"Rate limit exceeded for {client_ip}")
                    return JSONResponse(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        content={"detail": "Rate limit exceeded. Please try again later."}
                    )
                else:
                    # Update count
                    self.rate_limits[client_ip] = (last_time, count + 1)
            else:
                # New window
                self.rate_limits[client_ip] = (current_time, 1)
        else:
            # First request from this IP
            self.rate_limits[client_ip] = (current_time, 1)
        
        # Continue processing the request
        return await call_next(request)

# Define API models

class ModelEnum(str, Enum):
    """Supported models for InsolvencyBot."""
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4O = "gpt-4o"

class QuestionRequest(BaseModel):
    """Request body for question processing."""
    question: str = Field(
        ...,
        title="Question",
        description="The insolvency-related legal question to process",
        min_length=10,
        example="What happens if my company can't pay its debts?"
    )
    model: ModelEnum = Field(
        default=ModelEnum.GPT_35_TURBO,
        title="Model",
        description="The model to use for generating the response"
    )

class Citation(BaseModel):
    """A citation to a legal source."""
    type: str = Field(..., title="Type", description="Type of citation (legislation, case, or form)")
    text: str = Field(..., title="Text", description="Text of the citation")

class QuestionResponse(BaseModel):
    """Response body for question processing."""
    response: str = Field(..., title="Response", description="The response to the question")
    legislation: List[str] = Field(default_factory=list, title="Legislation", description="Cited legislation")
    cases: List[str] = Field(default_factory=list, title="Cases", description="Cited cases")
    forms: List[str] = Field(default_factory=list, title="Forms", description="Cited forms")
    response_time: float = Field(..., title="Response Time", description="Time taken to process the question (seconds)")
    model: str = Field(..., title="Model", description="The model used to generate the response")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "When a company cannot pay its debts, it may be considered insolvent. The Insolvency Act 1986 provides several options...",
                "legislation": ["Insolvency Act 1986", "Companies Act 2006"],
                "cases": ["Salomon v A Salomon & Co Ltd"],
                "forms": ["Form 1.1 (Scot)"],
                "response_time": 3.45,
                "model": "gpt-4"
            }
        }

class APIError(BaseModel):
    """Error response model."""
    detail: str = Field(..., title="Detail", description="Error details")

class ModelInfo(BaseModel):
    """Model information."""
    id: str = Field(..., title="ID", description="Model ID")
    name: str = Field(..., title="Name", description="Human-readable name")
    description: str = Field(..., title="Description", description="Model description")
    
class ModelsResponse(BaseModel):
    """Response containing available models."""
    models: List[ModelInfo] = Field(..., title="Models", description="List of available models")

# API key validation
def get_api_key(api_key: str = Header(None)) -> str:
    """Validate the API key if configured."""
    # If INSOLVENCYBOT_API_KEY is set, require a matching API key
    required_api_key = os.environ.get("INSOLVENCYBOT_API_KEY")
    if required_api_key and api_key != required_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return api_key

# Define API routes

@app.get(
    "/",
    summary="API Information",
    description="Returns basic information about the InsolvencyBot API",
    response_model=Dict[str, Any]
)
async def root():
    """Get API information."""
    return {
        "name": "InsolvencyBot API",
        "version": "1.0.0",
        "description": "API for the InsolvencyBot, providing insolvency law guidance with citations to legislation, cases, and forms.",
        "documentation": "/docs"
    }

@app.get(
    "/models",
    summary="Get Available Models",
    description="Returns a list of available models for question processing",
    response_model=ModelsResponse
)
async def get_models(api_key: str = Depends(get_api_key)):
    """Get available models."""
    models = [
        ModelInfo(
            id=ModelEnum.GPT_35_TURBO,
            name="GPT-3.5 Turbo",
            description="Faster and more economical model, suitable for straightforward questions"
        ),
        ModelInfo(
            id=ModelEnum.GPT_4,
            name="GPT-4",
            description="More advanced model with better reasoning capabilities"
        ),
        ModelInfo(
            id=ModelEnum.GPT_4O,
            name="GPT-4o",
            description="Latest model with the most comprehensive capabilities"
        )
    ]
    return ModelsResponse(models=models)

@app.post(
    "/ask",
    summary="Process Question",
    description="Process an insolvency-related legal question and return a structured response",
    response_model=QuestionResponse,
    responses={
        400: {"model": APIError, "description": "Bad Request"},
        401: {"model": APIError, "description": "Unauthorized"},
        500: {"model": APIError, "description": "Internal Server Error"},
        503: {"model": APIError, "description": "Service Unavailable"}
    }
)
async def process_question(
    request: QuestionRequest,
    test_connection: bool = Query(False, description="Test API connectivity only"),
    api_key: str = Depends(get_api_key)
):
    """Process an insolvency-related legal question."""
    # Handle connection test request
    if test_connection:
        logger.info("Connection test received")
        return QuestionResponse(
            response="API connection successful",
            legislation=[],
            cases=[],
            forms=[],
            response_time=0.0,
            model=request.model
        )
    
    # Validate OpenAI API key
    if not config.openai_api_key:
        logger.error("OPENAI_API_KEY environment variable is not set")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured"
        )
    
    # Log the request
    logger.info(f"Processing question with model {request.model}")
    
    # Update metrics
    global request_count, model_usage
    request_count += 1
    model_usage[request.model] = model_usage.get(request.model, 0) + 1
    
    try:
        # Process the question using tracker context manager
        with RequestTracker(model=request.model) as req_tracker:
            start_time_req = time.time()
            result = answer_question(
                request.question, 
                verbose=False, 
                model=request.model,
                max_retries=3  # Default max retries
            )
            elapsed_time = time.time() - start_time_req
            
            # Prepare the response
            response = QuestionResponse(
                response=result["_response"],
                legislation=result["legislation"],
                cases=result["cases"],
                forms=result["forms"],
                response_time=elapsed_time,
                model=request.model
            )
            
            # Update success metrics
            global success_count
            success_count += 1
            
            # Log the success
            logger.info(f"Question processed successfully in {elapsed_time:.2f}s")
            return response
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        tracker.record_error(status_code=400)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        tracker.record_error(status_code=500)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )

@app.get(
    "/metrics",
    summary="Get API Metrics",
    description="Returns usage metrics and performance statistics for the API",
    response_model=Dict[str, Any]
)
async def get_metrics(api_key: str = Depends(get_api_key)):
    """Get API usage metrics and performance statistics."""
    # Require API key for metrics access
    required_api_key = os.environ.get("INSOLVENCYBOT_API_KEY")
    if required_api_key and (not api_key or api_key != required_api_key):
        logger.warning("Unauthorized metrics access attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required for metrics access",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Simple metrics for now
    system_metrics = {
        "uptime": time.time() - start_time,
        "requests": {
            "total": request_count,
            "success": success_count,
            "failed": error_count
        },
        "models": {
            "gpt-3.5-turbo": model_usage.get("gpt-3.5-turbo", 0),
            "gpt-4": model_usage.get("gpt-4", 0),
            "gpt-4o": model_usage.get("gpt-4o", 0)
        },
        "api_version": "1.0.0"
    }
    
    return system_metrics

@app.get(
    "/diagnostic",
    summary="API Diagnostics",
    description="Run diagnostic checks and return system status information",
    response_model=Dict[str, Any]
)
async def get_diagnostic(api_key: str = Depends(get_api_key)):
    """Get API diagnostic information for troubleshooting."""
    # Check basic environment setup
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    openai_api_key_status = "configured" if openai_api_key else "missing"
    
    # Check API settings
    api_auth_status = "enabled" if config.api_key else "disabled"
    
    # System information
    import platform
    import psutil
    
    try:
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": f"{memory.total / (1024**3):.2f}GB",
            "available": f"{memory.available / (1024**3):.2f}GB",
            "percent_used": f"{memory.percent}%"
        }
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total": f"{disk.total / (1024**3):.2f}GB",
            "free": f"{disk.free / (1024**3):.2f}GB",
            "percent_used": f"{disk.percent}%"
        }
        
        # Get CPU info
        cpu_usage = f"{psutil.cpu_percent()}%"
        cpu_count = psutil.cpu_count()
    except:
        # Fallback if psutil functions fail
        memory_usage = {"status": "unavailable"}
        disk_usage = {"status": "unavailable"}
        cpu_usage = "unavailable"
        cpu_count = "unavailable"
    
    # Collect all diagnostic information
    diagnostic = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_version": "1.0.0",
        "environment": {
            "openai_api_key": openai_api_key_status,
            "api_authentication": api_auth_status,
            "python_version": platform.python_version(),
            "os": platform.platform()
        },
        "system": {
            "uptime": time.time() - start_time,
            "memory": memory_usage,
            "disk": disk_usage,
            "cpu_usage": cpu_usage,
            "cpu_count": cpu_count
        },
        "usage": {
            "total_requests": request_count,
            "success_requests": success_count,
            "error_requests": error_count,
            "model_usage": model_usage
        },
        "status": "healthy" if config.openai_api_key else "degraded"
    }
    
    return diagnostic

# Exception handlers for better API error handling
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Track the error for diagnostics
    global error_count
    error_count += 1
    
    # Add request to tracker for monitoring
    tracker.track_error(request.url.path, str(exc))
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    
    # Track the error for diagnostics
    global error_count
    error_count += 1
    
    # Add request to tracker for monitoring
    tracker.track_error(request.url.path, f"{exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": "HTTPException",
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Check for API key and OpenAI API key
    if not config.openai_api_key:
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("The API will not be able to process questions without it.")
    
    # Log configuration settings
    logger.info(f"Starting InsolvencyBot API with configuration: {config}")
    
    if config.api_key:
        logger.info("API authentication is enabled")
    else:
        logger.warning("API authentication is disabled - consider enabling it for production")
    
    # Start the server
    uvicorn.run(
        app, 
        host=config.api_host, 
        port=config.api_port,
        workers=config.api_workers
    )
