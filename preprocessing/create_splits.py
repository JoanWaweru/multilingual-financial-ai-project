"""
Create train/validation/test splits
"""

import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_splits():
    """Create train/val/test splits for CS detection dataset"""
    
    logger.info("=" * 60)
    logger.info("CREATING TRAIN/VAL/TEST SPLITS")
    logger.info("=" * 60)
    
    # Load CS detection dataset
    input_file = Path("data/processed/cs_detection_dataset.csv")
    
    if not input_file.exists():
        logger.error("CS detection dataset not found!")
        logger.info("Run: python preprocessing/integrate_datasets.py first")
        return
    
    df = pd.read_csv(input_file)
    logger.info(f"✓ Loaded {len(df)} samples")
    
    # Split: 70% train, 15% val, 15% test
    train_df, temp_df = train_test_split(
        df, 
        test_size=0.30, 
        random_state=42,
        stratify=df['has_code_switching']  # Maintain class balance
    )
    
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        stratify=temp_df['has_code_switching']
    )
    
    logger.info(f"\n✓ Train: {len(train_df)} samples ({len(train_df)/len(df)*100:.1f}%)")
    logger.info(f"✓ Val:   {len(val_df)} samples ({len(val_df)/len(df)*100:.1f}%)")
    logger.info(f"✓ Test:  {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}%)")
    
    # Check balance
    logger.info(f"\nClass balance:")
    logger.info(f"Train CS: {train_df['has_code_switching'].sum()} / {len(train_df)}")
    logger.info(f"Val CS:   {val_df['has_code_switching'].sum()} / {len(val_df)}")
    logger.info(f"Test CS:  {test_df['has_code_switching'].sum()} / {len(test_df)}")
    
    # Save splits
    splits_dir = Path("data/splits")
    splits_dir.mkdir(exist_ok=True, parents=True)
    
    train_df.to_csv(splits_dir / "train.csv", index=False)
    val_df.to_csv(splits_dir / "val.csv", index=False)
    test_df.to_csv(splits_dir / "test.csv", index=False)
    
    logger.info(f"\n✓ Splits saved to: {splits_dir}/")
    
    # Create sample files for quick testing
    train_sample = train_df.head(100)
    train_sample.to_csv(splits_dir / "train_sample.csv", index=False)
    logger.info(f"✓ Created train_sample.csv (100 samples) for quick testing")

if __name__ == "__main__":
    create_splits()