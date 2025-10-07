"""
Generate comprehensive dataset statistics
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_statistics():
    """Generate comprehensive statistics"""
    
    logger.info("=" * 60)
    logger.info("GENERATING DATASET STATISTICS")
    logger.info("=" * 60)
    
    # Load datasets
    cs_file = Path("data/processed/cs_detection_dataset.csv")
    qa_file = Path("data/processed/financial_qa_dataset.csv")
    
    if not cs_file.exists() or not qa_file.exists():
        logger.error("Datasets not found!")
        return
    
    cs_df = pd.read_csv(cs_file)
    qa_df = pd.read_csv(qa_file)
    
    # CS Dataset Statistics
    logger.info("\n" + "-" * 60)
    logger.info("CODE-SWITCHING DETECTION DATASET")
    logger.info("-" * 60)
    
    logger.info(f"Total samples: {len(cs_df):,}")
    logger.info(f"Code-switched: {cs_df['has_code_switching'].sum():,} ({cs_df['has_code_switching'].mean()*100:.1f}%)")
    logger.info(f"Non-CS: {(~cs_df['has_code_switching']).sum():,} ({(~cs_df['has_code_switching']).mean()*100:.1f}%)")
    
    # Text length statistics
    cs_df['text_length'] = cs_df['text'].str.len()
    cs_df['word_count'] = cs_df['text'].str.split().str.len()
    
    logger.info(f"\nText Length:")
    logger.info(f"  Mean: {cs_df['text_length'].mean():.0f} characters")
    logger.info(f"  Median: {cs_df['text_length'].median():.0f} characters")
    logger.info(f"  Min: {cs_df['text_length'].min()}")
    logger.info(f"  Max: {cs_df['text_length'].max()}")
    
    logger.info(f"\nWord Count:")
    logger.info(f"  Mean: {cs_df['word_count'].mean():.1f} words")
    logger.info(f"  Median: {cs_df['word_count'].median():.0f} words")
    
    # Source distribution
    logger.info(f"\nSource Distribution:")
    print(cs_df['source'].value_counts())
    
    # Financial Q&A Statistics
    logger.info("\n" + "-" * 60)
    logger.info("FINANCIAL Q&A DATASET")
    logger.info("-" * 60)
    
    logger.info(f"Total Q&A pairs: {len(qa_df):,}")
    
    logger.info(f"\nSource Distribution:")
    print(qa_df['source'].value_counts())
    
    if 'category' in qa_df:
        logger.info(f"\nTop Categories:")
        print(qa_df['category'].value_counts().head(10))
    
    # Create visualizations
    results_dir = Path("results/dataset_stats")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    # Plot 1: CS Distribution
    plt.figure(figsize=(10, 6))
    cs_df['has_code_switching'].value_counts().plot(kind='bar')
    plt.title('Code-Switching Distribution')
    plt.xlabel('Has Code-Switching')
    plt.ylabel('Count')
    plt.xticks([0, 1], ['No', 'Yes'], rotation=0)
    plt.tight_layout()
    plt.savefig(results_dir / 'cs_distribution.png')
    logger.info(f"\n✓ Saved: cs_distribution.png")
    
    # Plot 2: Text Length Distribution
    plt.figure(figsize=(10, 6))
    plt.hist(cs_df['text_length'], bins=50, edgecolor='black')
    plt.title('Text Length Distribution')
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(results_dir / 'text_length_dist.png')
    logger.info(f"✓ Saved: text_length_dist.png")
    
    # Plot 3: Source Distribution
    plt.figure(figsize=(10, 6))
    cs_df['source'].value_counts().plot(kind='bar')
    plt.title('Dataset Source Distribution')
    plt.xlabel('Source')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(results_dir / 'source_distribution.png')
    logger.info(f"✓ Saved: source_distribution.png")
    
    logger.info(f"\n✓ All statistics saved to: {results_dir}/")

if __name__ == "__main__":
    generate_statistics()