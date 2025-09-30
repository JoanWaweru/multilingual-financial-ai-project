import pandas as pd
import sqlite3
from typing import Dict, List
import logging
from pathlib import Path

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

class DataValidator:
    """Validate and clean collected tweet data"""
    
    def __init__(self):
        self.db_path = RAW_DATA_DIR / "tweets.db"
    
    def validate_dataset(self) -> pd.DataFrame:
        """Perform comprehensive data validation"""
        logger.info("Starting data validation...")
        
        # Load data
        df = self.load_from_database()
        initial_count = len(df)
        logger.info(f"Loaded {initial_count} tweets")
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['id'])
        logger.info(f"Removed {initial_count - len(df)} duplicates")
        
        # Remove too short texts
        df = df[df['text'].str.len() >= 30]
        logger.info(f"Removed tweets shorter than 30 characters")
        
        # Remove null texts
        df = df.dropna(subset=['text'])
        logger.info(f"Removed null texts")
        
        # Add validation flags
        df['is_valid'] = df['text'].apply(self.is_valid_tweet)
        valid_df = df[df['is_valid']].copy()
        
        logger.info(f"Final valid tweets: {len(valid_df)}")
        
        # Save cleaned data
        output_file = PROCESSED_DATA_DIR / "tweets_validated.csv"
        valid_df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Saved validated data to {output_file}")
        
        return valid_df
    
    def load_from_database(self) -> pd.DataFrame:
        """Load tweets from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM tweets", conn)
        conn.close()
        return df
    
    def is_valid_tweet(self, text: str) -> bool:
        """Check if tweet is valid for analysis"""
        if not isinstance(text, str):
            return False
        
        # Check length
        if len(text) < 30 or len(text) > 500:
            return False
        
        # Check for excessive special characters
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        if special_char_ratio > 0.3:
            return False
        
        # Check for repeated characters (spam indicator)
        if any(text.count(c*5) > 0 for c in 'abcdefghijklmnopqrstuvwxyz'):
            return False
        
        return True
    
    def get_validation_report(self, df: pd.DataFrame) -> Dict:
        """Generate validation report"""
        report = {
            'total_tweets': len(df),
            'valid_tweets': df['is_valid'].sum(),
            'invalid_tweets': (~df['is_valid']).sum(),
            'avg_length': df[df['is_valid']]['text'].str.len().mean(),
            'countries': df[df['is_valid']]['country'].value_counts().to_dict(),
            'languages': df[df['is_valid']]['language'].value_counts().to_dict(),
        }
        return report

if __name__ == "__main__":
    validator = DataValidator()
    valid_df = validator.validate_dataset()
    report = validator.get_validation_report(valid_df)
    
    print("\n" + "="*60)
    print("VALIDATION REPORT")
    print("="*60)
    for key, value in report.items():
        print(f"{key}: {value}")
    print("="*60)