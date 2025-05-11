# InsolvencyBot Architecture

This document provides an overview of the InsolvencyBot system architecture.

## System Overview

InsolvencyBot is a multi-component system designed to provide legal guidance on insolvency-related questions. It uses Large Language Models (LLMs) to generate responses and extracts relevant legal references.

![Architecture Diagram](architecture_diagram.png)

## Core Components

### 1. Core Engine (`src/hoi_insolvencybot/insolvency_bot.py`)

The central component that processes questions and generates responses using OpenAI's LLMs. Key responsibilities:

- Question processing
- Prompt engineering for legal guidance
- Response generation
- Reference extraction (legislation, cases, forms)
- Error handling and retries

### 2. Web Interface (`app.py`)

A Flask-based web application providing a user-friendly interface for:

- Submitting questions
- Displaying responses with highlighted references
- Model selection
- Mobile-responsive design

### 3. REST API (`api.py`)

A FastAPI-based REST API enabling programmatic access:

- Question processing endpoint (`/ask`)
- Model information endpoint (`/models`)
- API key authentication
- OpenAPI documentation

### 4. CLI Interface (`cli.py`)

A command-line interface for interactive usage:

- REPL (read-eval-print loop) for questions
- Colored output
- Model selection
- History tracking

### 5. Benchmarking Tools (`benchmark.py`)

Tools for performance evaluation:

- Response time measurement
- Model comparison
- Question batch processing
- Results reporting

## Data Flow

1. **User Input**: A question is submitted through one of the interfaces (Web, API, CLI)
2. **Question Processing**: The core engine formats the prompt for the LLM
3. **API Call**: The question is sent to OpenAI's API
4. **Response Processing**: The response is processed to extract references
5. **Structured Output**: A structured response is returned with extracted references
6. **Presentation**: The interface presents the response to the user

## Integration Points

- **OpenAI API**: Primary LLM provider
- **Web Browsers**: For the web interface
- **API Clients**: For programmatic access
- **Command Line**: For CLI usage
- **Docker**: For containerized deployment

## Configuration

Configuration is managed through:

- Environment variables (`OPENAI_API_KEY`, `PORT`, `INSOLVENCYBOT_API_KEY`)
- Command-line arguments (model selection, mode)
- Configuration files (logging configuration)

## Deployment

The system can be deployed in multiple ways:

- **Local Development**: Using direct Python execution
- **Docker Containers**: Using Docker Compose for the full stack
- **Production Server**: Using the deployment scripts

## Security Considerations

- API key authentication for the REST API
- Secure handling of OpenAI API keys
- Input validation
- Error handling to prevent information leakage

## Logging and Monitoring

- Structured logging with timestamps and levels
- Configurable log destinations
- Performance metric collection
- Error tracking and reporting
