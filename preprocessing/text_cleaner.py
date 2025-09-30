import re
import pandas as pd
from typing import List, Dict
import emoji
import logging

logger = logging.getLogger(__name__)

class MultilingualTextCleaner:
    """Clean and normalize multilingual financial text"""
    
    def __init__(self):
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.mention_pattern = re.compile(r'@[\w]+')
        self.hashtag_pattern = re.compile(r'#')
        
    def clean_dataset(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """Clean entire dataset"""
        logger.info(f"Cleaning {len(df)} texts...")
        
        df = df.copy()
        df['original_text'] = df[text_column]
        df['cleaned_text'] = df[text_column].apply(self.clean_text)
        df['word_count'] = df['cleaned_text'].apply(lambda x: len(x.split()))
        
        return df
    
    def clean_text(self, text: str) -> str:
        """Clean individual text"""
        if not isinstance(text, str):
            return ""
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove mentions but keep the text
        text = self.mention_pattern.sub('', text)
        
        # Remove hashtag symbol but keep the word
        text = self.hashtag_pattern.sub('', text)
        
        # Convert emojis to text
        text = emoji.demojize(text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        return text.strip()
    
    def normalize_financial_terms(self, text: str) -> str:
        """Normalize common financial term variations"""
        replacements = {
            'mpesa': 'M-Pesa',
            'm-pesa': 'M-Pesa',
            'ksh': 'KES',
            'kes': 'KES',
            'ugx': 'UGX',
            'tzs': 'TZS',
            'rwf': 'RWF',
        }
        
        text_lower = text.lower()
        for old, new in replacements.items():
            text_lower = text_lower.replace(old, new)
        
        return text_lower

if __name__ == "__main__":
    from config.settings import PROCESSED_DATA_DIR
    
    # Load validated data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_validated.csv")
    
    # Clean
    cleaner = MultilingualTextCleaner()
    df_cleaned = cleaner.clean_dataset(df)
    
    # Save
    output_file = PROCESSED_DATA_DIR / "tweets_cleaned.csv"
    df_cleaned.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"Cleaned {len(df_cleaned)} tweets")
    print(f"Saved to {output_file}")