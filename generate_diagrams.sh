#!/bin/bash
#
# Generate architecture diagrams from Mermaid markdown
# Requires Node.js and mmdc (Mermaid CLI)
#

# Check if Node.js is installed
if ! command -v node &>/dev/null; then
  echo "Error: Node.js is required but not installed."
  echo "Please install Node.js: https://nodejs.org/"
  exit 1
fi

# Check if mmdc is installed, install if not
if ! command -v mmdc &>/dev/null; then
  echo "Installing Mermaid CLI..."
  npm install -g @mermaid-js/mermaid-cli
  if [ $? -ne 0 ]; then
    echo "Failed to install Mermaid CLI. Please install it manually:"
    echo "npm install -g @mermaid-js/mermaid-cli"
    exit 1
  fi
fi

# Create diagrams directory if it doesn't exist
mkdir -p docs/images

# Extract Mermaid diagram from markdown and generate PNG
echo "Generating architecture diagram..."
mmdc -i docs/architecture_diagram.md -o docs/images/architecture_diagram.png -b transparent

if [ $? -eq 0 ]; then
  echo "✅ Diagram generated successfully: docs/images/architecture_diagram.png"
  
  # Update architecture.md to reference the generated image
  sed -i 's|!\[Architecture Diagram\](architecture_diagram.png)|![Architecture Diagram](images/architecture_diagram.png)|g' docs/architecture.md
  
  echo "✅ Updated architecture.md to reference the generated image"
else
  echo "❌ Failed to generate diagram"
fi
