import pandas as pd
from langdetect import detect, DetectorFactory
from typing import List, Dict, Tuple
import logging
import re

# Ensure consistent results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

class CodeSwitchingDetector:
    """Detect code-switching patterns in text"""
    
    def __init__(self):
        # Common Swahili words
        self.swahili_indicators = [
            'pesa', 'akiba', 'mkopo', 'bajeti', 'biashara', 'benki',
            'fedha', 'uwekezaji', 'ni', 'na', 'ya', 'kwa', 'sana',
            'tu', 'za', 'au', 'lakini', 'pia'
        ]
        
        # Common English financial terms
        self.english_indicators = [
            'savings', 'investment', 'budget', 'loan', 'bank',
            'money', 'finance', 'business', 'the', 'and', 'is',
            'for', 'to', 'in', 'that', 'with'
        ]
    
    def analyze_dataset(self, df: pd.DataFrame, text_column: str = 'cleaned_text') -> pd.DataFrame:
        """Analyze language patterns in dataset"""
        logger.info("Analyzing language patterns...")
        
        df = df.copy()
        
        # Detect overall language
        df['detected_language'] = df[text_column].apply(self.detect_language_safe)
        
        # Detect code-switching
        df['has_code_switching'] = df[text_column].apply(self.has_code_switching)
        df['switching_score'] = df[text_column].apply(self.calculate_switching_score)
        
        # Detailed analysis
        switching_analysis = df[text_column].apply(self.analyze_switching_pattern)
        df['english_ratio'] = switching_analysis.apply(lambda x: x['english_ratio'])
        df['swahili_ratio'] = switching_analysis.apply(lambda x: x['swahili_ratio'])
        df['switching_type'] = switching_analysis.apply(lambda x: x['switching_type'])
        
        return df
    
    def detect_language_safe(self, text: str) -> str:
        """Safely detect language with fallback"""
        try:
            if not isinstance(text, str) or len(text) < 10:
                return 'unknown'
            return detect(text)
        except:
            return 'unknown'
    
    def has_code_switching(self, text: str) -> bool:
        """Check if text contains code-switching"""
        if not isinstance(text, str):
            return False
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count language indicators
        swahili_count = sum(1 for word in words if word in self.swahili_indicators)
        english_count = sum(1 for word in words if word in self.english_indicators)
        
        # Code-switching if both languages present significantly
        return swahili_count >= 2 and english_count >= 2
    
    def calculate_switching_score(self, text: str) -> float:
        """Calculate code-switching intensity score (0-1)"""
        if not isinstance(text, str):
            return 0.0
        
        text_lower = text.lower()
        words = text_lower.split()
        
        if len(words) < 5:
            return 0.0
        
        swahili_count = sum(1 for word in words if word in self.swahili_indicators)
        english_count = sum(1 for word in words if word in self.english_indicators)
        
        # Score based on balance of both languages
        total_indicators = swahili_count + english_count
        if total_indicators == 0:
            return 0.0
        
        # Higher score when both languages are balanced
        balance = min(swahili_count, english_count) / max(swahili_count, english_count, 1)
        coverage = total_indicators / len(words)
        
        return min(balance * coverage * 2, 1.0)
    
    def analyze_switching_pattern(self, text: str) -> Dict:
        """Detailed analysis of switching patterns"""
        if not isinstance(text, str):
            return {
                'english_ratio': 0,
                'swahili_ratio': 0,
                'switching_type': 'none'
            }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        if len(words) < 5:
            return {
                'english_ratio': 0,
                'swahili_ratio': 0,
                'switching_type': 'none'
            }
        
        swahili_count = sum(1 for word in words if word in self.swahili_indicators)
        english_count = sum(1 for word in words if word in self.english_indicators)
        
        total = len(words)
        english_ratio = english_count / total
        swahili_ratio = swahili_count / total
        
        # Determine switching type
        if swahili_count < 2 and english_count < 2:
            switching_type = 'none'
        elif english_ratio > 0.7:
            switching_type = 'mostly_english'
        elif swahili_ratio > 0.7:
            switching_type = 'mostly_swahili'
        elif 0.3 <= english_ratio <= 0.7:
            switching_type = 'balanced_mixing'
        else:
            switching_type = 'tag_switching'
        
        return {
            'english_ratio': english_ratio,
            'swahili_ratio': swahili_ratio,
            'switching_type': switching_type
        }

if __name__ == "__main__":
    from config.settings import PROCESSED_DATA_DIR
    
    # Load cleaned data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_cleaned.csv")
    
    # Analyze
    detector = CodeSwitchingDetector()
    df_analyzed = detector.analyze_dataset(df)
    
    # Save
    output_file = PROCESSED_DATA_DIR / "tweets_analyzed.csv"
    df_analyzed.to_csv(output_file, index=False, encoding='utf-8')
    
    # Show statistics
    print("\nCode-Switching Analysis:")
    print(f"Total tweets: {len(df_analyzed)}")
    print(f"Has code-switching: {df_analyzed['has_code_switching'].sum()}")
    print(f"Average switching score: {df_analyzed['switching_score'].mean():.3f}")
    print("\nSwitching types:")
    print(df_analyzed['switching_type'].value_counts())