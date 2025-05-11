#!/bin/bash
#
# Deploy the InsolvencyBot API in a production environment
#

# Configuration
# Uncomment and set these variables according to your environment
#export PORT=8000
#export INSOLVENCYBOT_API_KEY="your-secure-api-key"
export OPENAI_API_KEY="${OPENAI_API_KEY}"

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OPENAI_API_KEY environment variable is not set."
  echo "Please set it before running this script."
  exit 1
fi

# Function to display setup progress
function display_step {
  echo
  echo "========================================================="
  echo "  $1"
  echo "========================================================="
}

# Make sure we're in the project root
cd "$(dirname "$0")"

# Setup environment
display_step "Setting up environment"

# Check if virtual environment exists, create it if it doesn't
if [ ! -d ".venv" ]; then
  display_step "Creating virtual environment"
  python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Install dependencies
display_step "Installing dependencies"
pip install -r requirements.txt || { echo "Failed to install dependencies"; exit 1; }

# Set up log directory
display_step "Setting up log directory"
mkdir -p logs

# Start the API service
display_step "Starting InsolvencyBot API"
PORT="${PORT:-8000}"
echo "InsolvencyBot API will be available at http://localhost:$PORT"
echo "OpenAPI documentation will be available at http://localhost:$PORT/docs"

# Start with nohup to keep running after terminal closes
nohup python -m uvicorn api:app --host 0.0.0.0 --port $PORT > logs/api.log 2>&1 &

# Save PID for later management
echo $! > .api.pid
echo "API server started with PID $(cat .api.pid)"
echo "View logs with: tail -f logs/api.log"
echo
echo "To stop the server, run: kill $(cat .api.pid)"
