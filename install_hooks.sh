#!/bin/bash
#
# Install git hooks for development

echo "Installing git hooks for InsolvencyBot development..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy pre-commit hook
cp hooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks installed successfully!"
echo "The pre-commit hook will run before each commit to check code quality."
echo "To skip the hooks for a specific commit, use: git commit --no-verify"
