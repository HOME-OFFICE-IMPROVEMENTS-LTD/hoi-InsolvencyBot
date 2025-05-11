#!/bin/bash

# Launch the InsolvencyBot API server
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY environment variable is not set."
  echo "The API will not be able to process questions without it."
fi

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Set default port if not specified
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-1}
export DEBUG=${DEBUG:-false}

# Load environment variables from .env file
if [ -f ".env" ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Check for API authentication
if [ -n "$INSOLVENCYBOT_API_KEY" ]; then
  echo "API authentication is enabled."
else
  echo "Warning: API authentication is not enabled. Consider setting INSOLVENCYBOT_API_KEY for security."
fi

echo "Starting InsolvencyBot API server on $HOST:$PORT with $WORKERS worker(s)..."

if [ "$DEBUG" = "true" ]; then
  echo "Running in DEBUG mode with hot-reloading enabled..."
  python -m uvicorn api:app --host $HOST --port $PORT --reload
else
  # Production mode with specified number of workers
  python -m uvicorn api:app --host $HOST --port $PORT --workers $WORKERS
fi
