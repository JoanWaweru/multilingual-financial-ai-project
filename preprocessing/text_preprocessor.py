"""
Text preprocessing for Kenyan code-switching data
"""

import re
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Preprocess text for model training"""
    
    def __init__(self):
        # Kenyan-specific patterns to preserve
        self.kenyan_terms = [
            'mpesa', 'm-pesa', 'chama', 'sacco', 'shilling', 'ksh',
            'akiba', 'mkopo', 'pesa', 'benki', 'uwekezaji', 'bajeti'
        ]
    
    def clean_text(self, text, preserve_case=True):
        """Clean text while preserving important features"""
        
        if pd.isna(text):
            return ""
        
        text = str(text)
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove URLs (optional)
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove email addresses (optional)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Preserve Kenyan terms case
        if not preserve_case:
            # Lowercase but preserve Kenyan terms
            words = text.split()
            words = [w if w.lower() in self.kenyan_terms else w.lower() for w in words]
            text = ' '.join(words)
        
        # Remove extra spaces again
        text = ' '.join(text.split())
        
        return text.strip()
    
    def filter_length(self, df, text_col='text', min_len=10, max_len=512):
        """Filter texts by length"""
        
        df = df.copy()
        df['text_length'] = df[text_col].str.len()
        
        original_len = len(df)
        df = df[(df['text_length'] >= min_len) & (df['text_length'] <= max_len)]
        filtered_len = len(df)
        
        logger.info(f"Filtered {original_len - filtered_len} samples by length")
        logger.info(f"Remaining: {filtered_len} samples")
        
        return df.drop(columns=['text_length'])
    
    def preprocess_dataset(self, input_file, output_file):
        """Preprocess entire dataset"""
        
        logger.info(f"Processing: {input_file}")
        
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} samples")
        
        # Clean text
        df['text'] = df['text'].apply(self.clean_text)
        
        # Filter by length
        df = self.filter_length(df)
        
        # Remove duplicates
        original_len = len(df)
        df = df.drop_duplicates(subset=['text'])
        logger.info(f"Removed {original_len - len(df)} duplicates")
        
        # Remove empty texts
        df = df[df['text'].str.len() > 0]
        
        # Save
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} samples to {output_file}")
        
        return df
    
    def preprocess_all_splits(self):
        """Preprocess train/val/test splits"""
        
        logger.info("=" * 60)
        logger.info("PREPROCESSING ALL SPLITS")
        logger.info("=" * 60)
        
        splits_path = Path("data/splits")
        
        for split_name in ['train', 'val', 'test']:
            input_file = splits_path / f"{split_name}.csv"
            output_file = splits_path / f"{split_name}_processed.csv"
            
            if input_file.exists():
                self.preprocess_dataset(input_file, output_file)
            else:
                logger.warning(f"{split_name}.csv not found!")
        
        logger.info("\n✓ PREPROCESSING COMPLETE!")

if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    preprocessor.preprocess_all_splits()