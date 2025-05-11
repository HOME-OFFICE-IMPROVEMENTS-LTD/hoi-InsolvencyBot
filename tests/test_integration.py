"""
Integration tests for the InsolvencyBot application.

These tests verify that the main application flows work end-to-end.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hoi_insolvencybot.__main__ import main

class TestMainApp(unittest.TestCase):
    """Integration tests for the main application."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'})
        self.env_patcher.start()
        
        # Mock sys.argv
        self.orig_argv = sys.argv
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.env_patcher.stop()
        sys.argv = self.orig_argv

    @patch('os.path.exists')
    def test_command_line_validation(self, mock_exists):
        """Test that the main function validates command line arguments."""
        # Make file checks pass
        mock_exists.return_value = False  # Fail at file check to avoid further execution
        
        # Test with no arguments
        sys.argv = ['script_name']
        with self.assertRaises(SystemExit) as context:
            with patch('builtins.print'):  # Suppress print output
                main()
        self.assertEqual(context.exception.code, 1)
        
        # Test with invalid model
        sys.argv = ['script_name', 'invalid-model', 'test']
        with self.assertRaises(SystemExit) as context:
            with patch('builtins.print'):  # Suppress print output
                main()
        self.assertEqual(context.exception.code, 1)

    @patch('os.environ.get')
    def test_openai_key_validation(self, mock_get_env):
        """Test that the main function validates the OPENAI_API_KEY."""
        # Test with no API key
        mock_get_env.return_value = None
        sys.argv = ['script_name', 'gpt-4', 'test']
        with self.assertRaises(SystemExit) as context:
            with patch('builtins.print'):  # Suppress print output
                main()
        self.assertEqual(context.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
