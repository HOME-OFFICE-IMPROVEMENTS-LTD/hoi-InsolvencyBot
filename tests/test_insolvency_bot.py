"""
Basic test suite for the Insolvency Bot functionality.

This module contains tests for the core functionality of the Insolvency Bot,
focusing on response parsing and generation.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hoi_insolvencybot.insolvency_bot import answer_question

class TestInsolvencyBot(unittest.TestCase):
    """Test cases for the Insolvency Bot."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
        self.env_patcher.start()
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()

    @patch('src.hoi_insolvencybot.insolvency_bot.openai.ChatCompletion.create')
    def test_answer_question_basic(self, mock_create):
        """Test basic functionality of answer_question with a mocked response."""
        # Mock the OpenAI response
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': 'This is a test response'
                    }
                }
            ]
        }
        mock_create.return_value = mock_response
        
        # Call the function with a test question
        result = answer_question("What is insolvency?", verbose=True, model="gpt-4")
        
        # Verify the result structure (not exact values since they're hardcoded in the function)
        self.assertEqual(result["_response"], 'This is a test response')
        self.assertIsInstance(result["legislation"], list)
        self.assertIsInstance(result["cases"], list)
        self.assertIsInstance(result["forms"], list)
        
        # Verify the API was called with expected parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4")
        self.assertTrue(any("What is insolvency?" in msg["content"] for msg in call_args["messages"]))

    @patch('src.hoi_insolvencybot.insolvency_bot.openai.ChatCompletion.create')
    def test_answer_question_format(self, mock_create):
        """Test that the answer_question function returns properly formatted responses."""
        # Mock the OpenAI response with a longer, more realistic response
        mock_response = {
            'choices': [
                {
                    'message': {
                        'content': (
                            "Insolvency is a situation where a company or individual cannot pay their debts "
                            "when they fall due. Under the Insolvency Act 1986, there are various procedures "
                            "to handle insolvency cases, including administration, CVAs, and liquidation. "
                            "The case of Salomon v A Salomon & Co Ltd established the principle of separate "
                            "corporate personality. For formal proceedings, you might need to use Form 4.19 (Scot)."
                        )
                    }
                }
            ]
        }
        mock_create.return_value = mock_response
        
        # Call the function with a test question
        result = answer_question("Explain insolvency and its procedures.", verbose=False, model="gpt-4")
        
        # Verify response format and structure
        self.assertIn("_response", result)
        self.assertIn("legislation", result)
        self.assertIn("cases", result)
        self.assertIn("forms", result)
        
        # Verify types
        self.assertIsInstance(result["_response"], str)
        self.assertIsInstance(result["legislation"], list)
        self.assertIsInstance(result["cases"], list)
        self.assertIsInstance(result["forms"], list)
        
        # Verify non-empty content
        self.assertTrue(len(result["_response"]) > 0)

    @patch('src.hoi_insolvencybot.insolvency_bot.openai.ChatCompletion.create')
    def test_answer_question_error_handling(self, mock_create):
        """Test that the answer_question function handles errors gracefully."""
        # Mock the OpenAI API to raise an exception
        mock_create.side_effect = Exception("API Error")
        
        # Call the function with a test question and expect an exception
        with self.assertRaises(Exception) as context:
            answer_question("What is insolvency?", verbose=True, model="gpt-4")
        
        # Verify the exception is passed through
        self.assertIn("API Error", str(context.exception))

    @patch('src.hoi_insolvencybot.insolvency_bot.openai.ChatCompletion.create')
    def test_model_selection(self, mock_create):
        """Test that different models can be selected."""
        # Set up the mock
        mock_response = {
            'choices': [{'message': {'content': 'Test response'}}]
        }
        mock_create.return_value = mock_response
        
        # Test with gpt-3.5-turbo
        answer_question("Question?", model="gpt-3.5-turbo")
        mock_create.assert_called_with(
            model="gpt-3.5-turbo",
            messages=mock_create.call_args[1]['messages'],
            temperature=0.7,
            max_tokens=1200
        )
        
        # Test with gpt-4
        answer_question("Question?", model="gpt-4")
        mock_create.assert_called_with(
            model="gpt-4",
            messages=mock_create.call_args[1]['messages'],
            temperature=0.7,
            max_tokens=1200
        )
        
        # Test with gpt-4o
        answer_question("Question?", model="gpt-4o")
        mock_create.assert_called_with(
            model="gpt-4o",
            messages=mock_create.call_args[1]['messages'],
            temperature=0.7,
            max_tokens=1200
        )

if __name__ == '__main__':
    unittest.main()
