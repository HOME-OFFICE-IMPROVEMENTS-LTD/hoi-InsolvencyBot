# InsolvencyBot API Documentation

This document provides comprehensive documentation for the InsolvencyBot API.

## Overview

The InsolvencyBot API is a RESTful service that provides legal guidance on insolvency-related questions, 
with references to relevant UK legislation, case law, and forms. It supports multiple AI models and provides 
structured responses for easy integration with other applications.

## Base URL

When running locally: `http://localhost:8000`

## Authentication

API authentication is optional and can be enabled by setting the `INSOLVENCYBOT_API_KEY` environment variable. 
When enabled, clients must include the API key in the request header:

```
api-key: YOUR_API_KEY
```

## Endpoints

### GET /

Get basic API information.

**Response**:
```json
{
  "name": "InsolvencyBot API",
  "version": "1.0.0",
  "description": "API for the InsolvencyBot, providing insolvency law guidance with citations to legislation, cases, and forms.",
  "documentation": "/docs"
}
```

### GET /models

Get a list of available models.

**Headers**:
- `api-key`: (Optional) API key for authentication

**Response**:
```json
{
  "models": [
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "description": "Faster and more economical model, suitable for straightforward questions"
    },
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "description": "More advanced model with better reasoning capabilities"
    },
    {
      "id": "gpt-4o",
      "name": "GPT-4o",
      "description": "Latest model with the most comprehensive capabilities"
    }
  ]
}
```

### POST /ask

Process an insolvency-related legal question and return a structured response.

**Headers**:
- `api-key`: (Optional) API key for authentication
- `Content-Type`: `application/json`

**Request Body**:
```json
{
  "question": "What happens if my company can't pay its debts?",
  "model": "gpt-4"
}
```

**Query Parameters**:
- `test_connection` (boolean, optional): If set to `true`, the endpoint will only verify API connectivity without processing a question

**Body Parameters**:
- `question` (string, required): The insolvency-related legal question to process
- `model` (string, optional): The model to use for generating the response. One of: `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`. Defaults to `gpt-3.5-turbo`.

**Response**:
```json
{
  "response": "When a company cannot pay its debts, it may be considered insolvent. The Insolvency Act 1986 provides several options...",
  "legislation": ["Insolvency Act 1986", "Companies Act 2006"],
  "cases": ["Salomon v A Salomon & Co Ltd"],
  "forms": ["Form 1.1 (Scot)"],
  "response_time": 3.45,
  "model": "gpt-4"
}
```

### GET /metrics

Get API usage metrics and performance statistics.

**Headers**:
- `api-key`: (Optional) API key for authentication

**Response**:
```json
{
  "uptime": 3600.45,
  "requests": {
    "total": 25,
    "success": 23,
    "failed": 2
  },
  "models": {
    "gpt-3.5-turbo": 10,
    "gpt-4": 12,
    "gpt-4o": 3
  },
  "api_version": "1.0.0"
}
```

### GET /diagnostic

Get system diagnostic information including performance metrics, usage statistics, and environment details.

**Auth Required**: Yes (if API authentication is enabled)

**Parameters**: None

**Response**:
```json
{
  "api": {
    "version": "1.0.0",
    "uptime": "3h 12m 45s",
    "start_time": "2023-06-15T10:30:22Z"
  },
  "system": {
    "cpu_usage": 34.2,
    "memory_usage": {
      "used": 3850,
      "total": 8192,
      "percent": 47.0
    },
    "disk_usage": {
      "used": 24.5,
      "total": 100.0,
      "percent": 24.5
    },
    "platform": "Linux-5.15.0-generic-x86_64",
    "python_version": "3.11.4"
  },
  "usage": {
    "total_requests": 245,
    "successful_requests": 238,
    "failed_requests": 7,
    "success_rate": 97.14,
    "model_usage": {
      "gpt-3.5-turbo": 175,
      "gpt-4": 63,
      "gpt-4o": 7
    }
  },
  "environment": {
    "config_loaded": true,
    "debug_mode": false,
    "models_available": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: OpenAI API key not configured or service unavailable

### POST /api/feedback (Web Interface Only)

Submit user feedback about responses.

**Headers**:
- `Content-Type`: `application/json`

**Request Body**:
```json
{
  "feedback_type": "helpful", // or "not_helpful"
  "question": "What happens if my company can't pay its debts?",
  "model": "gpt-4o"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

**Error Response** (Status 500):
```json
{
  "status": "error",
  "message": "Error description"
}
```

### GET /status (Web Interface Only)

Get system status information including API connection status, web interface metrics, and system diagnostics.

This endpoint renders an HTML page showing:
- API status and version
- Web application status and uptime
- System resource utilization
- Diagnostic information

### Submit Feedback

`POST /api/feedback`

Submit user feedback about a response generated by the system.

#### Request

```json
{
  "feedback_type": "helpful",  // Can be "helpful" or "not_helpful"
  "question": "What are the requirements for a company voluntary arrangement?",
  "model": "gpt-4"             // The model that generated the response
}
```

#### Response

```json
{
  "status": "success",
  "message": "Feedback recorded"
}
```

#### Status Codes

- `200 OK`: Feedback successfully recorded
- `500 Internal Server Error`: Error processing the feedback request

## Using the API Client

A Python client is provided for easy interaction with the API.

```python
from api_client import ask_question

response = ask_question(
    api_url="http://localhost:8000",
    question="What happens if my company can't pay its debts?",
    model="gpt-4",
    api_key="your_api_key_if_required"
)

print(response["response"])
print("Legislation cited:", response["legislation"])
print("Cases cited:", response["cases"])
print("Forms cited:", response["forms"])
```

You can also use the client from the command line:

```bash
python api_client.py --url http://localhost:8000 --model gpt-4 "What happens if my company can't pay its debts?"
```

## Performance Considerations

- The API response time depends on the model used and the complexity of the question
- `gpt-3.5-turbo` is the fastest and most economical model
- `gpt-4` and `gpt-4o` provide more comprehensive and accurate responses but have higher latency

## Rate Limiting

The API implements exponential backoff for retrying OpenAI API calls in case of rate limiting or service unavailability.

## Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: OpenAI API key not configured or service unavailable

## Security Considerations

### API Key Authentication

When deploying the API in production, it is strongly recommended to enable API key authentication by setting the `INSOLVENCYBOT_API_KEY` environment variable. This provides a basic level of access control to prevent unauthorized use.

Example setting up API key:
```bash
export INSOLVENCYBOT_API_KEY="your-secure-random-api-key"
```

### Rate Limiting

The API implements exponential backoff for OpenAI API calls to handle rate limits. However, it's recommended to implement additional rate limiting at the infrastructure level (e.g., using Nginx, API Gateway, or a similar tool) to prevent abuse.

### Environment Variables

Never hardcode sensitive information like API keys in your code or commit them to version control. Always use environment variables or secure secret management solutions.

Production environment variables:
- `OPENAI_API_KEY`: Required for accessing OpenAI's models
- `INSOLVENCYBOT_API_KEY`: Optional but strongly recommended for API authentication
- `PORT`: Optional, defaults to 8000

### CORS Configuration

By default, CORS is configured to allow requests from any origin (`*`). In production, you should restrict this to only the domains that need to access your API:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com", "https://app.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Data Protection

Remember that questions sent to the API may contain sensitive legal information. Ensure your deployment complies with relevant data protection regulations (GDPR, etc.) and consider implementing:

1. Encryption in transit (HTTPS)
2. Proper access logging
3. Data retention policies
4. User consent mechanisms if storing data

## Web Interface

The InsolvencyBot includes a web interface that integrates with the API for easy testing and demonstration. The web interface provides:

- A simple UI for asking questions and receiving formatted responses
- API connectivity status indicators 
- A system status page for monitoring API and web service health

### Running the Web Interface

To start the web interface:

```bash
./run_web.sh
```

This will start a Flask server on port 5000 by default. The web interface will automatically attempt to connect to the API at http://localhost:8000.

### Status Page

The status page is available at `http://localhost:5000/status` and provides:

- Real-time API connectivity status
- Web interface information
- System metrics (CPU, memory, disk usage)
- API usage statistics
- Environment details

This page automatically refreshes every 30 seconds to provide up-to-date monitoring.

## System Monitoring Endpoints

### GET /api/health

Get detailed health status and diagnostic information about the API service.

**Response**:
```json
{
  "status": "healthy",
  "uptime": "2d 5h 30m 15s",
  "uptime_seconds": 186615,
  "system_info": {
    "python_version": "3.11.4 (main, Jul 25 2023, 17:27:09) [GCC 12.2.0]",
    "platform": "Linux-6.2.0-39-generic-x86_64-with-glibc2.36",
    "cpu_count": 8
  },
  "process_info": {
    "memory_usage_mb": 128.45,
    "cpu_percent": 2.5,
    "threads": 6
  },
  "disk_usage": {
    "percent": 45.2,
    "free_gb": 25.8
  },
  "metrics": {
    "total_requests": 1254,
    "total_errors": 23,
    "average_response_time_ms": 245.32
  }
}
```

### GET /api/metrics

Get detailed usage metrics and statistics for the API.

**Response**:
```json
{
  "requests": 1254,
  "errors": 23,
  "average_response_time_ms": 245.32,
  "uptime_seconds": 186615,
  "last_error": "Connection timeout",
  "last_error_time": 1714051245.123
}
```

### Complete System

To run the complete system (API + Web Interface) with a single command:

```bash
./run_system.sh
```

This script will:
1. Start the API server
2. Start the web interface
3. Provide URLs for accessing all components
4. Handle graceful shutdown of all services with Ctrl+C
