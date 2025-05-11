#!/bin/bash

# Launch the InsolvencyBot CLI
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OPENAI_API_KEY environment variable is not set."
  echo "Please set your OpenAI API key first:"
  echo "export OPENAI_API_KEY=your_api_key_here"
  exit 1
fi

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

echo "Starting InsolvencyBot CLI..."
python cli.py "$@"
