# Advanced Usage Examples

This document provides advanced examples and techniques for using InsolvencyBot in various scenarios.

## API Integration Examples

### Python Web Application (Flask)

```python
from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

# InsolvencyBot API configuration
INSOLVENCY_API_URL = os.environ.get("INSOLVENCY_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("INSOLVENCY_API_KEY", "")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
def ask_question():
    data = request.json
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["api-key"] = API_KEY
        
    response = requests.post(
        f"{INSOLVENCY_API_URL}/ask",
        json={
            "question": data.get("question"),
            "model": data.get("model", "gpt-3.5-turbo")
        },
        headers=headers
    )
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            "error": f"API Error: {response.status_code}",
            "details": response.text
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
```

### Node.js Example

```javascript
const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// InsolvencyBot API configuration
const INSOLVENCY_API_URL = process.env.INSOLVENCY_API_URL || 'http://localhost:8000';
const API_KEY = process.env.INSOLVENCY_API_KEY || '';

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

app.post('/api/ask', async (req, res) => {
  try {
    const headers = {};
    if (API_KEY) {
      headers['api-key'] = API_KEY;
    }
    
    const response = await axios.post(
      `${INSOLVENCY_API_URL}/ask`,
      {
        question: req.body.question,
        model: req.body.model || 'gpt-3.5-turbo'
      },
      { headers }
    );
    
    res.json(response.data);
  } catch (error) {
    console.error('API Error:', error.message);
    res.status(500).json({
      error: 'API Error',
      details: error.response ? error.response.data : error.message
    });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
```

## Batch Processing Example

This script processes multiple questions in batch mode:

```python
import os
import csv
import json
import time
from typing import List, Dict
import requests

# Configuration
API_URL = os.environ.get("INSOLVENCY_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("INSOLVENCY_API_KEY", "")
INPUT_FILE = "questions.csv"
OUTPUT_FILE = "responses.csv"
MODEL = "gpt-4"  # or "gpt-3.5-turbo" or "gpt-4o"

def process_batch(questions: List[str]) -> List[Dict]:
    """Process a batch of questions through the InsolvencyBot API."""
    results = []
    
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["api-key"] = API_KEY
    
    for question in questions:
        print(f"Processing: {question[:50]}...")
        
        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question, "model": MODEL},
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                result["question"] = question
                results.append(result)
                print(f"✓ Success ({len(result['legislation'])} legislation refs, "
                      f"{len(result['cases'])} case refs)")
            else:
                print(f"✗ Error: {response.status_code} - {response.text}")
                results.append({
                    "question": question,
                    "error": f"API Error: {response.status_code}",
                    "response": "",
                    "legislation": [],
                    "cases": [],
                    "forms": []
                })
                
            # Add delay to prevent rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ Exception: {str(e)}")
            results.append({
                "question": question,
                "error": str(e),
                "response": "",
                "legislation": [],
                "cases": [],
                "forms": []
            })
    
    return results

def main():
    """Main function to process batch questions."""
    # Read questions
    questions = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            questions.append(row["question"])
    
    print(f"Processing {len(questions)} questions with model {MODEL}...")
    results = process_batch(questions)
    
    # Write results
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["question", "response", "legislation", "cases", "forms", "response_time", "model"])
        
        for result in results:
            writer.writerow([
                result.get("question", ""),
                result.get("response", ""),
                "|".join(result.get("legislation", [])),
                "|".join(result.get("cases", [])),
                "|".join(result.get("forms", [])),
                result.get("response_time", 0),
                result.get("model", MODEL)
            ])
    
    print(f"Results written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
```

## Advanced Docker Compose Setup

For production deployment with reverse proxy and HTTPS:

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certificates:/etc/nginx/certificates:ro
    depends_on:
      - api
      - web
    restart: always

  api:
    build: .
    restart: always
    environment:
      - PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - INSOLVENCYBOT_API_KEY=${INSOLVENCYBOT_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    command: ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]

  web:
    build: .
    restart: always
    environment:
      - PORT=5000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - INSOLVENCY_API_URL=http://api:8000
      - INSOLVENCY_API_KEY=${INSOLVENCYBOT_API_KEY}
    volumes:
      - ./logs:/app/logs
    command: ["python", "app.py"]

  redis:
    image: redis:alpine
    restart: always
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

Example `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name insolvencybot.example.com;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        server_name insolvencybot.example.com;

        ssl_certificate /etc/nginx/certificates/cert.pem;
        ssl_certificate_key /etc/nginx/certificates/key.pem;

        # API
        location /api/ {
            proxy_pass http://api:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Web UI
        location / {
            proxy_pass http://web:5000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Command-line Scripting

Advanced usage of the CLI with input/output redirection:

```bash
# Process a single question and save the result
echo "What happens if my company can't pay its debts?" | python cli.py --no-interactive --model gpt-4 > result.txt

# Process a batch of questions from a file
cat questions.txt | python cli.py --batch --model gpt-4o > results.txt

# Extract only legislation references from the response
echo "What is wrongful trading?" | python cli.py --no-interactive --model gpt-4 | grep "^Legislation:" > legislation_refs.txt
```

## API Rate Limiting Example

To implement rate limiting in a production environment, add Redis integration:

```python
import redis
from fastapi import HTTPException, Request, status
from fastapi.middleware.base import BaseHTTPMiddleware

# Initialize Redis client
redis_client = redis.Redis(host='redis', port=6379, db=0)

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract client IP
        client_ip = request.client.host
        
        # Rate limit configuration
        rate_limit = 60  # requests
        per_minute = 60  # seconds
        
        # Create a Redis key for this IP
        key = f"rate_limit:{client_ip}"
        
        # Check if key exists
        current = redis_client.get(key)
        
        if current is not None and int(current) >= rate_limit:
            # Too many requests
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Increment the counter
        if current is None:
            # First request from this IP
            redis_client.set(key, 1, ex=per_minute)
        else:
            # Increment existing counter
            redis_client.incr(key)
        
        # Process the request
        response = await call_next(request)
        return response

# Add this middleware to your FastAPI app
app.add_middleware(RateLimitMiddleware)
```
