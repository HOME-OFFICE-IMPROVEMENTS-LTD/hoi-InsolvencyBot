# Makefile for hoi-InsolvencyBot project

# Variables
PYTHON = python3
PIP = pip

# Default goal
.DEFAULT_GOAL := help

# Help
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install       - Install dependencies"
	@echo "  test          - Run tests"
	@echo "  report        - Generate test report"
	@echo "  docs          - Generate API documentation"
	@echo "  diagrams      - Generate architecture diagrams"
	@echo "  run           - Run the evaluation with all models"
	@echo "  cli           - Start the interactive CLI"
	@echo "  benchmark     - Run performance benchmarks"
	@echo "  web           - Start the web application"
	@echo "  api           - Start the API server"
	@echo "  docker        - Build Docker image"
	@echo "  docker-run    - Run Docker container"
	@echo "  clean         - Clean output files"
	@echo "  format        - Format code with black"
	@echo "  lint          - Run linting checks"
	@echo "  diagrams      - Generate architecture diagrams"

# Install dependencies
.PHONY: install
install:
	$(PIP) install -r requirements.txt

# Run tests
.PHONY: test
test:
	$(PIP) install coverage
	$(PYTHON) -m coverage run -m unittest discover -s tests
	$(PYTHON) -m coverage report
	$(PYTHON) -m coverage html

# Generate test report
.PHONY: report
report:
	$(PYTHON) generate_test_report.py

# Generate API documentation
.PHONY: docs
docs:
	$(PYTHON) generate_docs.py

# Run evaluation with all models
.PHONY: run
run:
	bash run_all_models.sh

# Run the interactive CLI
.PHONY: cli
cli:
	$(PYTHON) cli.py

# Run performance benchmarks
.PHONY: benchmark
benchmark:
	$(PYTHON) benchmark.py --questions 3 --runs 1

# Start the web application
.PHONY: web
web:
	$(PYTHON) app.py

# Start the API server
.PHONY: api
api:
	bash run_api.sh

# Docker build
.PHONY: docker
docker:
	docker build -t insolvency-bot .

# Docker run
.PHONY: docker-run
docker-run:
	docker-compose up

# Clean output files
.PHONY: clean
clean:
	rm -f output_*.csv
	rm -f scores_*.csv

# Format code with black
.PHONY: format
format:
	$(PIP) install black
	black src/ tests/ *.py

# Run linting checks
.PHONY: lint
lint:
	$(PIP) install flake8
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

# Generate architecture diagrams
.PHONY: diagrams
diagrams:
	bash generate_diagrams.sh
