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

**Parameters**:
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

**Error Responses**:
- `400 Bad Request`: Invalid input parameters
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: OpenAI API key not configured or service unavailable
