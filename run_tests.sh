#!/bin/bash
# Run all tests for the project
# Usage: bash run_tests.sh

echo "Running InsolvencyBot tests..."
python -m unittest discover -s tests

# If we want to add pytest in the future, uncomment:
# echo "Running pytest tests..."
# python -m pytest tests/
