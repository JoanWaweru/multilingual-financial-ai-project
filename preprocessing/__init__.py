"""
Preprocessing module for text cleaning and language analysis
Handles multilingual text processing and code-switching detection
"""

try:
    from .text_cleaner import MultilingualTextCleaner
    from .language_detector import CodeSwitchingDetector
    from .annotator_tool import AnnotationTool
    
    __all__ = [
        'MultilingualTextCleaner',
        'CodeSwitchingDetector',
        'AnnotationTool'
    ]
    
except ImportError as e:
    print(f"Warning: Could not import preprocessing modules: {e}")
    __all__ = []

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Preprocessing Module
===================

This module provides functionality for:
- Cleaning and normalizing multilingual text
- Detecting code-switching patterns
- Language identification
- Manual annotation support

Main Classes:
- MultilingualTextCleaner: Text preprocessing
- CodeSwitchingDetector: Language pattern detection
- AnnotationTool: Manual annotation interface

Usage:
    from preprocessing import MultilingualTextCleaner, CodeSwitchingDetector
    
    cleaner = MultilingualTextCleaner()
    detector = CodeSwitchingDetector()
    
    cleaned_df = cleaner.clean_dataset(df)
    analyzed_df = detector.analyze_dataset(cleaned_df)
"""