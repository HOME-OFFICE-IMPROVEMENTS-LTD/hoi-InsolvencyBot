FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY pyproject.toml .
COPY README.md .
COPY run_all_models.sh .

# Set environment variables
ENV PYTHONPATH=/app

# Set default command
CMD ["python", "-m", "src.hoi_insolvencybot"]
