"""
API and Web UI Tests for InsolvencyBot

This script tests the InsolvencyBot's API and web interface for basic functionality.
"""

import os
import sys
import time
import unittest
import requests
import subprocess
import threading
import signal
from urllib.parse import urlparse

# Set the path to include the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class InsolvencyBotAPITests(unittest.TestCase):
    """Test cases for the InsolvencyBot API."""
    
    @classmethod
    def setUpClass(cls):
        """Start the API server for testing."""
        # Check if OPENAI_API_KEY is set
        if not os.environ.get("OPENAI_API_KEY"):
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
        
        # Start API server in a separate process
        cls.api_process = subprocess.Popen(
            ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        
        # Wait for server to start
        time.sleep(2)
        cls.api_url = "http://localhost:8001"
        
        # Check if server is running
        tries = 0
        while tries < 5:
            try:
                response = requests.get(f"{cls.api_url}/")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(2)
            tries += 1
        else:
            raise RuntimeError("Failed to start API server")
    
    @classmethod
    def tearDownClass(cls):
        """Stop the API server."""
        if hasattr(cls, "api_process") and cls.api_process:
            os.killpg(os.getpgid(cls.api_process.pid), signal.SIGTERM)
            cls.api_process.wait(timeout=5)
    
    def test_api_info(self):
        """Test the API info endpoint."""
        response = requests.get(f"{self.api_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertEqual(data["name"], "InsolvencyBot API")
    
    def test_models_endpoint(self):
        """Test the models endpoint."""
        response = requests.get(f"{self.api_url}/models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("models", data)
        self.assertIsInstance(data["models"], list)
        self.assertGreater(len(data["models"]), 0)
        
        # Check model structure
        model = data["models"][0]
        self.assertIn("id", model)
        self.assertIn("name", model)
        self.assertIn("description", model)
    
    def test_ask_endpoint_validation(self):
        """Test validation on the ask endpoint."""
        # Test with empty request
        response = requests.post(f"{self.api_url}/ask", json={})
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity
        
        # Test with invalid model
        response = requests.post(
            f"{self.api_url}/ask", 
            json={"question": "Test question", "model": "invalid-model"}
        )
        self.assertEqual(response.status_code, 422)
        
        # Test with short question
        response = requests.post(
            f"{self.api_url}/ask", 
            json={"question": "Hi", "model": "gpt-3.5-turbo"}
        )
        self.assertEqual(response.status_code, 422)
    
    def test_ask_endpoint_success(self):
        """Test the ask endpoint with a valid request."""
        # Skip this test if we don't want to make actual API calls
        if os.environ.get("SKIP_OPENAI_TESTS") == "1":
            self.skipTest("Skipping test that makes OpenAI API calls")
        
        response = requests.post(
            f"{self.api_url}/ask", 
            json={"question": "What happens if my company can't pay its debts?", "model": "gpt-3.5-turbo"}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check response structure
        self.assertIn("response", data)
        self.assertIn("legislation", data)
        self.assertIn("cases", data)
        self.assertIn("forms", data)
        self.assertIn("response_time", data)
        self.assertIn("model", data)
        
        # Verify response content
        self.assertGreater(len(data["response"]), 100)  # Should have a substantial response
        self.assertEqual(data["model"], "gpt-3.5-turbo")

if __name__ == "__main__":
    unittest.main()
