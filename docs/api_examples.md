# InsolvencyBot API Examples

This document provides examples of how to use the InsolvencyBot API with various programming languages and tools.

## cURL Examples

### Get API Information

```bash
curl -X GET http://localhost:8000/
```

### Get Available Models

```bash
curl -X GET http://localhost:8000/models

# With API key
curl -X GET http://localhost:8000/models \
  -H "api-key: your-api-key"
```

### Process a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What happens if my company can'\''t pay its debts?",
    "model": "gpt-3.5-turbo"
  }'

# With API key
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -H "api-key: your-api-key" \
  -d '{
    "question": "What happens if my company can'\''t pay its debts?",
    "model": "gpt-3.5-turbo"
  }'
```

## JavaScript Example

```javascript
// Using Fetch API
async function askInsolvencyBot(question, model = "gpt-3.5-turbo", apiKey = null) {
  const headers = {
    "Content-Type": "application/json"
  };
  
  // Add API key if provided
  if (apiKey) {
    headers["api-key"] = apiKey;
  }
  
  try {
    const response = await fetch("http://localhost:8000/ask", {
      method: "POST",
      headers: headers,
      body: JSON.stringify({
        question: question,
        model: model
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`API Error: ${errorData.detail || response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error calling InsolvencyBot API:", error);
    throw error;
  }
}

// Example usage
askInsolvencyBot("What happens if my company can't pay its debts?")
  .then(data => {
    console.log("Response:", data.response);
    console.log("Legislation:", data.legislation);
    console.log("Cases:", data.cases);
    console.log("Forms:", data.forms);
  })
  .catch(error => {
    console.error("Failed to get response:", error);
  });
```

## Python Example

```python
import requests

def ask_insolvency_bot(question, model="gpt-3.5-turbo", api_key=None, api_url="http://localhost:8000"):
    """
    Ask a question to InsolvencyBot API.
    
    Args:
        question: The insolvency-related legal question to process
        model: The model to use (gpt-3.5-turbo, gpt-4, gpt-4o)
        api_key: Optional API key for authentication
        api_url: The base URL of the API server
    
    Returns:
        Dict containing the structured response
    """
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["api-key"] = api_key
        
    data = {
        "question": question,
        "model": model
    }
    
    try:
        response = requests.post(f"{api_url}/ask", headers=headers, json=data)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Error: Authentication failed. Check your API key.")
        elif response.status_code == 503:
            print("Error: Service unavailable. Check if the OpenAI API key is configured.")
        else:
            print(f"HTTP Error: {e}")
        
        try:
            error_detail = response.json().get("detail", "Unknown error")
            print(f"API Error details: {error_detail}")
        except:
            pass
        
        raise
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server. Is it running?")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Example usage
try:
    result = ask_insolvency_bot("What happens if my company can't pay its debts?")
    print(f"Response: {result['response']}")
    print(f"Legislation cited: {', '.join(result['legislation'])}")
    print(f"Cases cited: {', '.join(result['cases'])}")
    print(f"Forms cited: {', '.join(result['forms'])}")
except Exception as e:
    print(f"Failed to get response: {e}")
```

## Node.js Example

```javascript
const axios = require('axios');

/**
 * Ask a question to InsolvencyBot API
 * @param {string} question - The insolvency-related legal question
 * @param {string} model - The model to use (gpt-3.5-turbo, gpt-4, gpt-4o)
 * @param {string} apiKey - Optional API key for authentication
 * @param {string} apiUrl - The base URL of the API server
 * @returns {Promise<Object>} - The structured response
 */
async function askInsolvencyBot(question, model = "gpt-3.5-turbo", apiKey = null, apiUrl = "http://localhost:8000") {
  const headers = {
    "Content-Type": "application/json"
  };
  
  if (apiKey) {
    headers["api-key"] = apiKey;
  }
  
  try {
    const response = await axios.post(`${apiUrl}/ask`, {
      question,
      model
    }, {
      headers
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      // The request was made and the server responded with an error status
      if (error.response.status === 401) {
        console.error("Authentication failed. Check your API key.");
      } else if (error.response.status === 503) {
        console.error("Service unavailable. Check if the OpenAI API key is configured.");
      }
      
      console.error("API Error details:", error.response.data.detail || "Unknown error");
    } else if (error.request) {
      // The request was made but no response was received
      console.error("Could not connect to the API server. Is it running?");
    } else {
      // Something happened in setting up the request
      console.error("Error setting up the request:", error.message);
    }
    
    throw error;
  }
}

// Example usage with async/await
async function main() {
  try {
    const result = await askInsolvencyBot("What happens if my company can't pay its debts?");
    console.log("Response:", result.response);
    console.log("Legislation cited:", result.legislation.join(", "));
    console.log("Cases cited:", result.cases.join(", "));
    console.log("Forms cited:", result.forms.join(", "));
  } catch (error) {
    console.error("Failed to get response:", error);
  }
}

main();
```

## Using with Docker

If you're running the API using Docker, you can communicate with it as follows:

```bash
# Start the API service using docker-compose
docker-compose up api

# Make a request to the API (from outside the container)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What happens if my company can'\''t pay its debts?",
    "model": "gpt-3.5-turbo"
  }'
```
