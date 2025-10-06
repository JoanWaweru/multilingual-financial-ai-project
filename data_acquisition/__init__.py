"""
Data collection module for gathering financial tweets from East Africa
Includes Twitter API integration, validation, and storage
"""

try:
    from .twitter_collector import TwitterFinancialCollector
    from .data_validator import DataValidator
    
    __all__ = [
        'TwitterFinancialCollector',
        'DataValidator'
    ]
    
except ImportError as e:
    print(f"Warning: Could not import data collection modules: {e}")
    __all__ = []

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Data Collection Module
=====================

This module provides functionality for:
- Collecting financial tweets from Twitter API
- Filtering and validating tweet content
- Storing data in SQLite database
- Quality control and data cleaning

Main Classes:
- TwitterFinancialCollector: Main collection engine
- DataValidator: Validation and quality control

Usage:
    from data_collection import TwitterFinancialCollector
    
    collector = TwitterFinancialCollector()
    tweets_df = collector.collect_all_tweets()
"""