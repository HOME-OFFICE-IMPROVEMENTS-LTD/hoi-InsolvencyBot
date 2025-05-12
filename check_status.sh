#!/bin/bash
# check_status.sh - Enhanced script to check the status of InsolvencyBot services

# Text formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}InsolvencyBot Service Status Check${NC}"
echo "=================================="
echo -e "Time: $(date '+%Y-%m-%d %H:%M:%S')\n"

# Check if the API is running
API_PORT=${API_PORT:-8000}
if pgrep -f "uvicorn api:app.*$API_PORT" > /dev/null; then
    echo -e "${GREEN}✓ API server${NC} is running on port $API_PORT"
    
    # Check if API is responding
    API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$API_PORT/ 2>/dev/null)
    if [ "$API_RESPONSE" = "200" ]; then
        echo -e "  ${GREEN}✓ API is responding correctly${NC}"
        
        # Check if authentication is working
        AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "api-key: test-api-key" http://localhost:$API_PORT/models 2>/dev/null)
        if [ "$AUTH_RESPONSE" = "200" ]; then
            echo -e "  ${GREEN}✓ API authentication is working${NC}"
        else
            echo -e "  ${YELLOW}⚠ API authentication check failed (response: $AUTH_RESPONSE)${NC}"
        fi
        
        # Check API health endpoint
        HEALTH_RESPONSE=$(curl -s http://localhost:$API_PORT/api/health 2>/dev/null)
        if [ -n "$HEALTH_RESPONSE" ]; then
            echo -e "  ${GREEN}✓ Health monitoring is available${NC}"
            # Extract some basic metrics
            UPTIME=$(echo $HEALTH_RESPONSE | grep -o '"uptime":"[^"]*"' | awk -F'"' '{print $4}')
            MEMORY=$(echo $HEALTH_RESPONSE | grep -o '"memory_usage_mb":[0-9.]*' | awk -F':' '{printf "%.2f MB", $2}')
            CPU=$(echo $HEALTH_RESPONSE | grep -o '"cpu_percent":[0-9.]*' | awk -F':' '{printf "%.1f%%", $2}')
            
            echo -e "     Uptime: ${BOLD}$UPTIME${NC}"
            echo -e "     Memory: ${BOLD}$MEMORY${NC}"
            echo -e "     CPU: ${BOLD}$CPU${NC}"
        else
            echo -e "  ${YELLOW}⚠ API health endpoint is not available${NC}"
        fi
        fi
    else
        echo -e "  ${RED}✗ API is not responding (response: $API_RESPONSE)${NC}"
    fi
else
    echo -e "${RED}✗ API server${NC} is not running"
fi

echo 

# Check if the web server is running
WEB_PORT=${FLASK_PORT:-5000}
if pgrep -f "python app.py.*$WEB_PORT" > /dev/null; then
    echo -e "${GREEN}✓ Web server${NC} is running on port $WEB_PORT"
    
    # Check if web server is responding
    WEB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$WEB_PORT/ 2>/dev/null)
    if [ "$WEB_RESPONSE" = "200" ]; then
        echo -e "  ${GREEN}✓ Web interface is accessible${NC}"
        
        # Check feedback API endpoint
        FEEDBACK_TEST=$(curl -s -X POST -H "Content-Type: application/json" \
                     -d '{"feedback_type":"test","question":"test","model":"test"}' \
                     http://localhost:$WEB_PORT/api/feedback 2>/dev/null)
                     
        if [ $? -eq 0 ] && [[ "$FEEDBACK_TEST" == *"success"* ]]; then
          echo -e "  ${GREEN}✓ Feedback API endpoint working${NC}"
        else
          echo -e "  ${YELLOW}⚠ Feedback API endpoint not implemented or not working${NC}"
        fi
        
        # Check status page
        STATUS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$WEB_PORT/status 2>/dev/null)
        if [ "$STATUS_RESPONSE" = "200" ]; then
            echo -e "  ${GREEN}✓ Status monitoring page is accessible${NC}"
        else
            echo -e "  ${RED}✗ Status monitoring page not responding${NC}"
        fi
    else
        echo -e "  ${RED}✗ Web interface is not responding (response: $WEB_RESPONSE)${NC}"
    fi
else
    echo -e "${RED}✗ Web server${NC} is not running"
fi

echo 
echo "=================================="
echo -e "${BLUE}Environment Information:${NC}"
echo 

# OpenAI API key check
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠ OPENAI_API_KEY${NC} is not set in the environment"
else
    echo -e "${GREEN}✓ OPENAI_API_KEY${NC} is set in the environment"
fi

# API key check
if [ -z "$INSOLVENCYBOT_API_KEY" ]; then
    echo -e "${YELLOW}⚠ INSOLVENCYBOT_API_KEY${NC} is not set in the environment"
else
    echo -e "${GREEN}✓ INSOLVENCYBOT_API_KEY${NC} is set in the environment"
fi

echo 
echo -e "${BLUE}To start the services:${NC}"
echo "  ./run_api.sh     # Start the API server"
echo "  ./run_web.sh     # Start the web interface"
