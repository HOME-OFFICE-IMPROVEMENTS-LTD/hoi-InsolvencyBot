"""
Logging configuration for the InsolvencyBot project.

This module configures logging for the entire project with different handlers
for console output and file-based logs.
"""

import os
import logging
import logging.config
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Get current date for the log filename
current_date = datetime.now().strftime('%Y-%m-%d')

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'logs/insolvencybot_{current_date}.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
        'error_file': {
            'level': 'ERROR',
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': f'logs/error_{current_date}.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 10,
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'src.hoi_insolvencybot': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

def setup_logging():
    """Configure logging for the application."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging configured successfully")
    return logging.getLogger(__name__)

# Function to get a logger for a module
def get_logger(name):
    """
    Get a logger with the given name.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)
