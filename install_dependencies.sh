#!/bin/bash
# install_dependencies.sh - Install all necessary dependencies for InsolvencyBot

# Text formatting
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BLUE}${BOLD}InsolvencyBot - Installing Dependencies${NC}"
echo "==========================================="
echo

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ $(echo "$PYTHON_VERSION >= 3.7" | bc -l) -eq 0 ]]; then
    echo -e "${YELLOW}Warning: Python 3.7+ is recommended. You have Python $PYTHON_VERSION${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "\n${BLUE}Creating virtual environment...${NC}"
    python3 -m venv .venv
    
    if [ ! -d ".venv" ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        echo "Trying to install venv package..."
        
        # Try to install venv
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-venv
            python3 -m venv .venv
        elif command -v pip3 &> /dev/null; then
            pip3 install virtualenv
            python3 -m virtualenv .venv
        else
            echo -e "${RED}Error: Could not install virtualenv. Please install manually:${NC}"
            echo "pip3 install virtualenv"
            exit 1
        fi
    fi
fi

# Activate virtual environment
echo -e "\n${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

if ! command -v pip &> /dev/null; then
    echo -e "${RED}Error: pip not available in virtual environment.${NC}"
    exit 1
fi

# Upgrade pip
echo -e "\n${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "\n${BLUE}Installing requirements...${NC}"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}All dependencies installed successfully!${NC}"
    echo "You can now run the InsolvencyBot system with:"
    echo -e "${BOLD}./run_system.sh${NC}"
    echo
    echo "Or run individual components:"
    echo -e "- API server: ${BOLD}./run_api.sh${NC}"
    echo -e "- Web interface: ${BOLD}./run_web.sh${NC}"
    echo
    echo -e "${YELLOW}Note: Don't forget to set your OPENAI_API_KEY environment variable:${NC}"
    echo "export OPENAI_API_KEY=your-key-here"
else
    echo -e "\n${RED}${BOLD}Error installing dependencies.${NC}"
    echo "Please check the error messages above and try again."
    exit 1
fi
