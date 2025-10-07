"""
Check for potential data leakage
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_leakage():
    """Check for data leakage between splits"""
    
    logger.info("=" * 70)
    logger.info(" 🔍 CHECKING FOR DATA LEAKAGE")
    logger.info("=" * 70)
    
    splits_path = Path("data/splits")
    
    # Load splits
    train_df = pd.read_csv(splits_path / "train.csv")
    val_df = pd.read_csv(splits_path / "val.csv")
    test_df = pd.read_csv(splits_path / "test.csv")
    
    logger.info(f"\nDataset sizes:")
    logger.info(f"  Train: {len(train_df)}")
    logger.info(f"  Val: {len(val_df)}")
    logger.info(f"  Test: {len(test_df)}")
    
    # Check for exact duplicates
    logger.info(f"\n" + "=" * 70)
    logger.info(" 🔎 CHECKING EXACT DUPLICATES")
    logger.info("=" * 70)
    
    train_texts = set(train_df['text'].values)
    val_texts = set(val_df['text'].values)
    test_texts = set(test_df['text'].values)
    
    train_val_overlap = train_texts.intersection(val_texts)
    train_test_overlap = train_texts.intersection(test_texts)
    val_test_overlap = val_texts.intersection(test_texts)
    
    logger.info(f"Train-Val overlap: {len(train_val_overlap)} samples")
    logger.info(f"Train-Test overlap: {len(train_test_overlap)} samples")
    logger.info(f"Val-Test overlap: {len(val_test_overlap)} samples")
    
    if len(train_val_overlap) > 0:
        logger.warning("⚠️ Found duplicates between train and val!")
        logger.info("Example duplicates:")
        for text in list(train_val_overlap)[:3]:
            logger.info(f"  - {text[:100]}...")
    
    # Check class distribution
    logger.info(f"\n" + "=" * 70)
    logger.info(" 📊 CLASS DISTRIBUTION")
    logger.info("=" * 70)
    
    if 'has_code_switching' in train_df.columns:
        logger.info("\nTrain set:")
        print(train_df['has_code_switching'].value_counts(normalize=True))
        
        logger.info("\nVal set:")
        print(val_df['has_code_switching'].value_counts(normalize=True))
        
        logger.info("\nTest set:")
        print(test_df['has_code_switching'].value_counts(normalize=True))
    
    # Check if synthetic data dominates
    logger.info(f"\n" + "=" * 70)
    logger.info(" 🔬 DATA SOURCE ANALYSIS")
    logger.info("=" * 70)
    
    if 'source' in train_df.columns:
        logger.info("\nTrain sources:")
        print(train_df['source'].value_counts())
        
        logger.info("\nVal sources:")
        print(val_df['source'].value_counts())
        
        logger.info("\nTest sources:")
        print(test_df['source'].value_counts())

if __name__ == "__main__":
    check_leakage()