# Contributing to InsolvencyBot

Thank you for your interest in contributing to InsolvencyBot! We welcome contributions from everyone, regardless of skill level.

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- An OpenAI API key for development and testing

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally
   ```bash
   git clone https://github.com/YOUR-USERNAME/hoi-InsolvencyBot.git
   cd hoi-InsolvencyBot
   ```
3. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```
4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
5. Set up environment variables
   ```bash
   export OPENAI_API_KEY=your_api_key  # On Windows, use `set OPENAI_API_KEY=your_api_key`
   ```

## Development Process

### Code Style

We follow PEP 8 style guide for Python code. We recommend using tools like `flake8` and `black` to ensure your code follows the style guide.

```bash
# Check code style
flake8 src/ tests/

# Format code
black src/ tests/
```

### Testing

Always write tests for your code. We use `unittest` for testing.

```bash
# Run tests
make test
```

### Pull Request Process

1. Create a new branch for your feature or bugfix
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them with a descriptive commit message
3. Push your branch to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
4. Create a pull request to the `main` branch of the original repository
5. Make sure all tests pass in the CI/CD pipeline
6. Wait for review by maintainers

## Running the Application

### Local Development

```bash
# Run the Flask web demo
python app.py

# Run the CLI version with specific model
python -m src.hoi_insolvencybot gpt-3.5-turbo test
```

### Using Docker

```bash
# Build Docker image
make docker

# Run with Docker Compose
make docker-run
```

## Documentation

We use Sphinx for generating API documentation. Please update documentation when adding or modifying features.

```bash
# Generate documentation
make docs
```

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for your contributions!
