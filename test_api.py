#!/usr/bin/env python3
"""
API Integration Test Script

This script tests the InsolvencyBot API with a sample question.
"""

import requests
import sys
import json
import time
import os
from typing import Dict, Any

API_URL = "http://localhost:8000"
API_KEY = os.environ.get("INSOLVENCYBOT_API_KEY", "test-api-key")

def test_api_info():
    """Test the API info endpoint."""
    print("Testing API info endpoint...")
    response = requests.get(f"{API_URL}/")
    if response.status_code == 200:
        print("✅ API info endpoint is working")
        print(f"API version: {response.json().get('version')}")
    else:
        print(f"❌ API info endpoint failed: {response.status_code}")
        sys.exit(1)

def test_models_endpoint():
    """Test the models endpoint."""
    print("\nTesting models endpoint...")
    headers = {"api-key": API_KEY}
    response = requests.get(f"{API_URL}/models", headers=headers)
    if response.status_code == 200:
        print("✅ Models endpoint is working")
        models = response.json().get("models", [])
        print(f"Available models: {', '.join(model['id'] for model in models)}")
    else:
        print(f"❌ Models endpoint failed: {response.status_code}")
        sys.exit(1)

def test_ask_endpoint():
    """Test the ask endpoint with a sample question."""
    sample_question = "What happens if my company can't pay its debts?"
    model = "gpt-3.5-turbo"
    
    print(f"\nTesting ask endpoint with question: '{sample_question}'")
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "question": sample_question,
        "model": model
    }
    
    try:
        response = requests.post(f"{API_URL}/ask", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Ask endpoint is working")
            print(f"Response time: {result.get('response_time', 0):.2f}s")
            print(f"Model used: {result.get('model')}")
            print(f"References: {len(result.get('legislation', []))} legislation, {len(result.get('cases', []))} cases, {len(result.get('forms', []))} forms")
            print("\nSample of response:")
            print(f"{result.get('response', '')[:200]}...\n")
        elif response.status_code == 503:
            print("⚠️ Ask endpoint returned 503 - this might be because the OpenAI API key is not valid or set")
            print(f"Response: {response.text}")
        else:
            print(f"❌ Ask endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Ask endpoint test error: {str(e)}")

def test_metrics_endpoint():
    """Test the metrics endpoint."""
    print("\nTesting metrics endpoint...")
    headers = {"api-key": API_KEY}
    response = requests.get(f"{API_URL}/metrics", headers=headers)
    if response.status_code == 200:
        print("✅ Metrics endpoint is working")
        metrics = response.json()
        print(f"Uptime: {metrics.get('uptime', 0):.2f}s")
        print(f"Total requests: {metrics.get('requests', {}).get('total', 0)}")
    else:
        print(f"❌ Metrics endpoint failed: {response.status_code}")
        print(f"Response: {response.text}")

def run_all_tests():
    """Run all API tests."""
    print("🚀 Starting InsolvencyBot API tests\n")
    
    test_api_info()
    test_models_endpoint()
    test_metrics_endpoint()
    test_ask_endpoint()
    
    print("\n✨ All tests completed")

if __name__ == "__main__":
    run_all_tests()
