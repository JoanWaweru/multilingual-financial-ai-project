"""
Configuration module for Multilingual Financial AI System
Contains settings, API keys, and configuration parameters
"""

from pathlib import Path

# Import settings
try:
    from .settings import (
        BASE_DIR,
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        MODELS_DIR,
        LOGS_DIR,
        DATA_COLLECTION,
        FINANCIAL_KEYWORDS,
        COUNTRIES,
        MODEL_CONFIG,
        ANNOTATION_CONFIG,
        CHATBOT_CONFIG
    )
    
    from .api_keys import TWITTER_BEARER_TOKEN
    
    __all__ = [
        'BASE_DIR',
        'DATA_DIR',
        'RAW_DATA_DIR',
        'PROCESSED_DATA_DIR',
        'MODELS_DIR',
        'LOGS_DIR',
        'DATA_COLLECTION',
        'FINANCIAL_KEYWORDS',
        'COUNTRIES',
        'MODEL_CONFIG',
        'ANNOTATION_CONFIG',
        'CHATBOT_CONFIG',
        'TWITTER_BEARER_TOKEN'
    ]
    
except ImportError as e:
    print(f"Warning: Could not import config settings: {e}")
    __all__ = []

# Version
__version__ = "1.0.0"