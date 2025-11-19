"""
Prepare Bitext dataset as knowledge base for chatbot
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_bitext_kb():
    """Convert Bitext dataset to chatbot-friendly format"""
    
    logger.info("=" * 60)
    logger.info("PREPARING BITEXT KNOWLEDGE BASE")
    logger.info("=" * 60)
    
    # Load Bitext dataset
    bitext_path = Path("data/raw/bitext_banking/bitext_banking_full.csv")
    
    if not bitext_path.exists():
        logger.error(f"Bitext dataset not found: {bitext_path}")
        return
    
    df = pd.read_csv(bitext_path)
    logger.info(f"Loaded {len(df)} Q&A pairs from Bitext")
    
    # Check columns
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Standardize column names
    if 'instruction' in df.columns:
        df = df.rename(columns={'instruction': 'question'})
    elif 'questions' in df.columns:
        df = df.rename(columns={'questions': 'question'})
    
    if 'response' in df.columns:
        df = df.rename(columns={'response': 'answer'})
    elif 'answers' in df.columns:
        df = df.rename(columns={'answers': 'answer'})
    
    # Keep only question and answer
    if 'question' not in df.columns or 'answer' not in df.columns:
        logger.error("Could not find question/answer columns!")
        logger.info("Available columns:", df.columns.tolist())
        return
    
    # Select relevant columns
    kb_df = df[['question', 'answer']].copy()
    
    # Add category (optional - extract from intent if available)
    if 'intent' in df.columns:
        kb_df['category'] = df['intent']
    else:
        kb_df['category'] = 'general'
    
    # Add metadata
    kb_df['is_kenyan_specific'] = False  # Bitext is general banking
    kb_df['source'] = 'bitext'
    
    # Clean data
    kb_df = kb_df.dropna(subset=['question', 'answer'])
    kb_df = kb_df[kb_df['question'].str.len() > 5]
    kb_df = kb_df[kb_df['answer'].str.len() > 10]
    
    # Remove duplicates
    original_len = len(kb_df)
    kb_df = kb_df.drop_duplicates(subset=['question'])
    logger.info(f"Removed {original_len - len(kb_df)} duplicate questions")
    
    # Sample some Q&As to review
    logger.info("\n" + "=" * 60)
    logger.info("SAMPLE Q&As:")
    logger.info("=" * 60)
    for i, row in kb_df.head(5).iterrows():
        print(f"\nQ: {row['question'][:100]}...")
        print(f"A: {row['answer'][:150]}...")
    
    # Save
    output_path = Path("data/processed/chatbot_knowledge_base.csv")
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    kb_df.to_csv(output_path, index=False)
    logger.info(f"\n✓ Saved {len(kb_df)} Q&As to {output_path}")
    
    return kb_df

if __name__ == "__main__":
    prepare_bitext_kb() 