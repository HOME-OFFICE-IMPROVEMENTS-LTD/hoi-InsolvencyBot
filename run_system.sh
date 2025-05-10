#!/bin/bash
# run_system.sh - Start both the InsolvencyBot API and Web Interface

# Text formatting
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}Starting InsolvencyBot System${NC}"
echo "================================="

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Check for critical environment variables
if [ -z "$OPENAI_API_KEY" ]; then
  echo -e "${YELLOW}Warning: OPENAI_API_KEY environment variable not set.${NC}"
  echo "The system will not be able to process questions without it."
fi

# Set default ports if not specified
export PORT=${PORT:-8000}  # API port
export FLASK_PORT=${FLASK_PORT:-5000}  # Web interface port

# Configure API URL for web interface
export INSOLVENCYBOT_API_URL="http://localhost:$PORT"
echo -e "${GREEN}✓ API URL set to${NC} $INSOLVENCYBOT_API_URL"

# Start API server in the background
echo -e "\n${GREEN}Starting API server on port $PORT...${NC}"
./run_api.sh &
API_PID=$!

# Wait a moment for API to initialize
sleep 3

# Check if API server is running
if ps -p $API_PID > /dev/null; then
  # Test API connection
  API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/ 2>/dev/null)
  if [ "$API_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ API server started successfully${NC} (PID: $API_PID)"
    echo -e "  API documentation: ${BOLD}http://localhost:$PORT/docs${NC}"
    echo -e "  API diagnostic: ${BOLD}http://localhost:$PORT/diagnostic${NC}"
  else
    echo -e "${YELLOW}⚠ API server started but returned code $API_RESPONSE${NC} (PID: $API_PID)"
  fi
  
  # Start web interface in the background
  echo -e "\n${GREEN}Starting web interface on port $FLASK_PORT...${NC}"
  ./run_web.sh &
  WEB_PID=$!
  
  # Wait a moment for web interface to initialize
  sleep 3
  
  # Check if web interface is running and responding
  if ps -p $WEB_PID > /dev/null; then
    # Test web interface connection
    WEB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$FLASK_PORT/ 2>/dev/null)
    if [ "$WEB_RESPONSE" = "200" ]; then
      echo -e "${GREEN}✓ Web interface started successfully${NC} (PID: $WEB_PID)"
      echo -e "  Web interface: ${BOLD}http://localhost:$FLASK_PORT${NC}"
      echo -e "  Status page: ${BOLD}http://localhost:$FLASK_PORT/status${NC}"
    else
      echo -e "${YELLOW}⚠ Web interface started but returned code $WEB_RESPONSE${NC} (PID: $WEB_PID)"
    fi
    
    echo -e "\n${GREEN}${BOLD}InsolvencyBot system is now running!${NC}"
    echo -e "${GREEN}✓ API:${NC} http://localhost:$PORT"
    echo -e "${GREEN}✓ Web:${NC} http://localhost:$FLASK_PORT"
    echo -e "${GREEN}✓ Status:${NC} http://localhost:$FLASK_PORT/status"
    echo -e "${GREEN}✓ Documentation:${NC} http://localhost:$PORT/docs"
    
    echo -e "\n${BLUE}===============================${NC}"
    echo -e "Run ${BOLD}./check_status.sh${NC} anytime to verify system health"
    echo -e "Press ${BOLD}Ctrl+C${NC} to stop all services"
    echo -e "${BLUE}===============================${NC}"
    
    # Trap Ctrl+C to ensure clean shutdown of both services
    trap "echo -e '\n${BLUE}Shutting down InsolvencyBot...${NC}'; kill $API_PID $WEB_PID; echo -e '${GREEN}System stopped.${NC}'; exit 0" SIGINT
    
    # Keep script running
    wait
  else
    echo -e "${RED}✗ Failed to start web interface${NC}"
    echo "Check logs for details"
    echo -e "${YELLOW}Shutting down API...${NC}"
    kill $API_PID  # Kill API since web interface failed
    exit 1
  fi
else
  echo -e "${RED}✗ Failed to start API server${NC}"
  echo "Check logs for details"
  exit 1
fi
