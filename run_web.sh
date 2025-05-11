#!/bin/bash

# Run the InsolvencyBot web frontend
# This script starts the Flask web interface that connects to the InsolvencyBot API

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Set default values for configuration
export FLASK_PORT=${FLASK_PORT:-5000}
export INSOLVENCYBOT_API_URL=${INSOLVENCYBOT_API_URL:-"http://localhost:8000"}

# Set start time for status page
export FLASK_START_TIME=$(date +'%Y-%m-%d %H:%M:%S')

# If .env file exists, load it
if [ -f ".env" ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Check if API key is set
if [ -z "$INSOLVENCYBOT_API_KEY" ]; then
  echo "Warning: INSOLVENCYBOT_API_KEY environment variable not set."
  echo "If the API requires authentication, requests will fail."
  echo "Set it using: export INSOLVENCYBOT_API_KEY=your_api_key"
fi

echo "Starting InsolvencyBot web interface on port $FLASK_PORT..."
echo "Using API at $INSOLVENCYBOT_API_URL"
echo "Open http://localhost:$FLASK_PORT in your browser"
echo "System status available at http://localhost:$FLASK_PORT/status"
python app.py
