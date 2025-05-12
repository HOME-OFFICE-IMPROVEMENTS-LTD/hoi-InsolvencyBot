"""
InsolvencyBot API Client Example

This script demonstrates how to use the InsolvencyBot API from a client application.
"""

import argparse
import json
import os
import requests
from typing import Dict, Any, Optional

def get_api_info(api_url: str) -> Dict[str, Any]:
    """Get basic API information."""
    response = requests.get(f"{api_url}/")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get API info: {response.status_code} - {response.text}")

def get_available_models(api_url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Get available models."""
    headers = {}
    if api_key:
        headers["api-key"] = api_key
    
    response = requests.get(f"{api_url}/models", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get models: {response.status_code} - {response.text}")

def ask_question(api_url: str, question: str, model: str = "gpt-3.5-turbo", api_key: Optional[str] = None) -> Dict[str, Any]:
    """Process a legal question through the InsolvencyBot API."""
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["api-key"] = api_key
    
    data = {
        "question": question,
        "model": model
    }
    
    response = requests.post(f"{api_url}/ask", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to process question: {response.status_code} - {response.text}")

def format_response(response: Dict[str, Any]) -> str:
    """Format the API response for nice console output."""
    result = [
        "\n" + "=" * 80,
        f"INSOLVENCY BOT RESPONSE (using {response['model']})",
        "=" * 80,
        response['response'],
        "-" * 80,
        "REFERENCES:"
    ]
    
    if response['legislation']:
        result.append("\nLegislation:")
        for item in response['legislation']:
            result.append(f"  - {item}")
    
    if response['cases']:
        result.append("\nCases:")
        for item in response['cases']:
            result.append(f"  - {item}")
    
    if response['forms']:
        result.append("\nForms:")
        for item in response['forms']:
            result.append(f"  - {item}")
    
    result.append(f"\nResponse time: {response['response_time']:.2f}s")
    result.append("=" * 80)
    
    return "\n".join(result)

def main():
    parser = argparse.ArgumentParser(description="InsolvencyBot API Client Example")
    parser.add_argument("--url", default="http://localhost:8000", help="API server URL")
    parser.add_argument("--model", default="gpt-3.5-turbo", choices=["gpt-3.5-turbo", "gpt-4", "gpt-4o"], 
                        help="Model to use for generating the response")
    parser.add_argument("--api-key", default=os.environ.get("INSOLVENCYBOT_API_KEY"), 
                        help="API key (if required by server)")
    parser.add_argument("question", nargs="?", help="Insolvency question to process")
    
    args = parser.parse_args()
    
    try:
        # Get API info
        api_info = get_api_info(args.url)
        print(f"Connected to {api_info['name']} v{api_info['version']}")
        
        # Get available models
        models_info = get_available_models(args.url, args.api_key)
        print("\nAvailable models:")
        for model in models_info['models']:
            print(f"  - {model['name']} ({model['id']}): {model['description']}")
        
        # Process question if provided
        if args.question:
            print(f"\nProcessing question using {args.model}...")
            response = ask_question(args.url, args.question, args.model, args.api_key)
            print(format_response(response))
        else:
            print("\nNo question provided. Use --help for usage information.")
            print("Example: python api_client.py \"What happens if my company can't pay its debts?\"")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
