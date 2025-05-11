"""
Configuration Manager for InsolvencyBot

This module provides centralized configuration management for the InsolvencyBot
application, handling environment variables, settings, and defaults.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """
    Configuration manager for InsolvencyBot.
    
    This class provides access to application settings with proper defaults,
    validation, and type conversion.
    """
    
    # Singleton instance
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration values."""
        # API configuration
        self.api_port = int(os.getenv("PORT", 8000))
        self.api_host = os.getenv("HOST", "0.0.0.0")
        self.api_workers = int(os.getenv("WORKERS", 1))
        self.api_key = os.getenv("INSOLVENCYBOT_API_KEY")
        
        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        
        # Application settings
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.max_retries = int(os.getenv("MAX_RETRIES", 3))
        
        # Paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.log_dir = self.project_root / "logs"
        
        # Create directories if they don't exist
        self.log_dir.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        valid = True
        
        # Check for required settings
        if not self.openai_api_key:
            logging.warning("OPENAI_API_KEY environment variable is not set")
            valid = False
        
        return valid
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as a dictionary
        """
        return {
            "api": {
                "port": self.api_port,
                "host": self.api_host,
                "workers": self.api_workers,
                "auth_enabled": self.api_key is not None
            },
            "models": {
                "default": self.default_model,
                "openai_api_available": self.openai_api_key is not None
            },
            "app": {
                "debug_mode": self.debug_mode,
                "log_level": self.log_level,
                "max_retries": self.max_retries
            }
        }
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        # Include only non-sensitive information
        return (f"Config(api_port={self.api_port}, "
                f"api_host={self.api_host}, "
                f"default_model={self.default_model}, "
                f"debug_mode={self.debug_mode}, "
                f"log_level={self.log_level})")


# Export singleton instance
config = Config()
