"""
Download Bitext Retail Banking dataset from HuggingFace
"""

from datasets import load_dataset
import pandas as pd
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_bitext_banking():
    """Download Bitext Retail Banking dataset"""
    
    output_path = Path("data/raw/bitext_banking")
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("DOWNLOADING BITEXT RETAIL BANKING DATASET")
    logger.info("=" * 60)
    
    try:
        logger.info("\nConnecting to HuggingFace...")
        
        # Download from HuggingFace
        dataset = load_dataset("bitext/Bitext-retail-banking-llm-chatbot-training-dataset")
        
        logger.info("✓ Dataset downloaded successfully!")
        
        # Convert to pandas DataFrame
        train_df = pd.DataFrame(dataset['train'])
        
        logger.info(f"\n📊 Dataset Information:")
        logger.info(f"  Total samples: {len(train_df):,}")
        logger.info(f"  Columns: {list(train_df.columns)}")
        
        # Check for required columns
        required_cols = ['instruction', 'response']
        missing = [col for col in required_cols if col not in train_df.columns]
        
        if missing:
            logger.error(f"Missing required columns: {missing}")
            return None
        
        # Show sample
        logger.info(f"\n📝 Sample Entry:")
        logger.info(f"  Instruction: {train_df.iloc[0]['instruction']}")
        logger.info(f"  Response: {train_df.iloc[0]['response'][:100]}...")
        
        if 'category' in train_df.columns:
            logger.info(f"\n📂 Categories:")
            logger.info(f"  Unique categories: {train_df['category'].nunique()}")
            logger.info(f"  Top 5 categories:")
            print(train_df['category'].value_counts().head())
        
        # Save full dataset
        logger.info(f"\n💾 Saving dataset...")
        output_file = output_path / "bitext_banking_full.csv"
        train_df.to_csv(output_file, index=False)
        logger.info(f"  ✓ Full dataset: {output_file}")
        logger.info(f"    Size: {len(train_df):,} rows")
        
        # Save sample for quick inspection
        sample_df = train_df.head(100)
        sample_file = output_path / "bitext_banking_sample.csv"
        sample_df.to_csv(sample_file, index=False)
        logger.info(f"  ✓ Sample dataset: {sample_file}")
        logger.info(f"    Size: 100 rows")
        
        # Save metadata
        metadata = {
            'total_samples': len(train_df),
            'columns': list(train_df.columns),
            'source': 'HuggingFace - bitext/Bitext-retail-banking-llm-chatbot-training-dataset',
            'download_date': pd.Timestamp.now().isoformat()
        }
        
        import json
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"  ✓ Metadata: {metadata_file}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ DOWNLOAD COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📁 Files saved to: {output_path}/")
        logger.info("  1. bitext_banking_full.csv")
        logger.info("  2. bitext_banking_sample.csv")
        logger.info("  3. metadata.json")
        
        return train_df
        
    except Exception as e:
        logger.error(f"\n✗ DOWNLOAD FAILED!")
        logger.error(f"Error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Check internet connection")
        logger.info("2. Verify HuggingFace token: huggingface-cli whoami")
        logger.info("3. Re-login: huggingface-cli login")
        return None

if __name__ == "__main__":
    df = download_bitext_banking()
    
    if df is not None:
        print("\n✓ SUCCESS! Bitext data ready to use.")
    else:
        print("\n✗ FAILED! Check errors above.")