# Using the InsolvencyBot API

This guide provides step-by-step instructions for using the InsolvencyBot API.

## Prerequisites

- Python 3.7+
- `requests` library (`pip install requests`)

## Quick Start

### 1. Start the API Server

```bash
# From the project root
./run_api.sh
```

This will start the API server on port 8000.

### 2. Use the API Client

The simplest way to use the API is through the provided client:

```bash
python api_client.py "What happens if my company can't pay its debts?"
```

### 3. API Client Options

```
usage: api_client.py [-h] [--url URL] [--model {gpt-3.5-turbo,gpt-4,gpt-4o}] [--api-key API_KEY] [question]

InsolvencyBot API Client Example

positional arguments:
  question              Insolvency question to process

optional arguments:
  -h, --help            show this help message and exit
  --url URL             API server URL (default: http://localhost:8000)
  --model {gpt-3.5-turbo,gpt-4,gpt-4o}
                        Model to use for generating the response
  --api-key API_KEY     API key (if required by server)
```

## Direct API Integration

### 1. Get API Information

```python
import requests

response = requests.get("http://localhost:8000/")
api_info = response.json()
print(f"Connected to {api_info['name']} v{api_info['version']}")
```

### 2. Get Available Models

```python
response = requests.get("http://localhost:8000/models")
models = response.json()
for model in models['models']:
    print(f"{model['name']}: {model['description']}")
```

### 3. Process a Question

```python
data = {
    "question": "What happens if my company can't pay its debts?",
    "model": "gpt-3.5-turbo"  # Optional, defaults to gpt-3.5-turbo
}

response = requests.post("http://localhost:8000/ask", json=data)
result = response.json()

print(result["response"])
print("\nLegislation cited:", ", ".join(result["legislation"]))
print("Cases cited:", ", ".join(result["cases"]))
print("Forms cited:", ", ".join(result["forms"]))
print(f"Response time: {result['response_time']:.2f}s")
```

## Using with Authentication

If API key authentication is enabled on the server (via `INSOLVENCYBOT_API_KEY` environment variable), 
include the API key in your requests:

```python
headers = {
    "Content-Type": "application/json",
    "api-key": "your-api-key-here"
}

response = requests.post("http://localhost:8000/ask", 
                        headers=headers,
                        json={"question": "What happens if my company can't pay its debts?"})
```

## Example Integration with a Web Application

```python
from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    
    insolvency_api_url = "http://localhost:8000/ask"
    response = requests.post(insolvency_api_url, json=data)
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": f"API Error: {response.status_code}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Common Error Handling

```python
try:
    response = requests.post("http://localhost:8000/ask", json=data)
    response.raise_for_status()  # Raises an exception for 4XX/5XX responses
    result = response.json()
    # Process result...
    
except requests.exceptions.HTTPError as e:
    if response.status_code == 401:
        print("Authentication failed. Check your API key.")
    elif response.status_code == 400:
        print("Bad request. Check your input parameters.")
    elif response.status_code == 503:
        print("Service unavailable. The API server might not have an OpenAI API key configured.")
    else:
        print(f"HTTP Error: {e}")
        
except requests.exceptions.ConnectionError:
    print("Connection error. Make sure the API server is running.")
    
except requests.exceptions.Timeout:
    print("Request timed out. Try again later.")
    
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

## Next Steps

For a full API reference, see the [API Reference](api_reference.md) documentation.
