"""
Logging configuration
"""

import logging
import logging.config
from pathlib import Path
from config.settings import LOG_CONFIG, LOGS_DIR

def setup_logging():
    """Setup logging configuration"""
    
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Configure logging
    logging.config.dictConfig(LOG_CONFIG)
    
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    
    return logger

def get_logger(name):
    """Get a logger with specified name"""
    return logging.getLogger(name)