"""
Validate all collected datasets
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_all_datasets():
    """Check all datasets are ready"""
    
    print("\n" + "=" * 70)
    print(" 📊 DATASET VALIDATION")
    print("=" * 70)
    
    datasets = {}
    
    # 1. Synthetic CS
    synthetic_file = Path("data/processed/synthetic_cs_financial.csv")
    if synthetic_file.exists():
        df = pd.read_csv(synthetic_file)
        datasets['Synthetic CS'] = {
            'status': '✓',
            'file': synthetic_file,
            'rows': len(df),
            'cs_samples': df['has_code_switching'].sum() if 'has_code_switching' in df else 0
        }
    else:
        datasets['Synthetic CS'] = {'status': '✗', 'error': 'File not found'}
    
    # 2. Reddit
    reddit_dir = Path("data/raw/reddit_extended")
    if reddit_dir.exists():
        posts_file = reddit_dir / "reddit_posts_extended.csv"
        comments_file = reddit_dir / "reddit_comments_extended.csv"
        
        total_rows = 0
        if posts_file.exists():
            total_rows += len(pd.read_csv(posts_file))
        if comments_file.exists():
            total_rows += len(pd.read_csv(comments_file))
        
        if total_rows > 0:
            datasets['Reddit Extended'] = {
                'status': '✓',
                'rows': total_rows
            }
        else:
            datasets['Reddit Extended'] = {'status': '⚠', 'error': 'No data'}
    else:
        datasets['Reddit Extended'] = {'status': '✗', 'error': 'Directory not found'}
    
    # 3. Bitext
    bitext_file = Path("data/raw/bitext_banking/bitext_banking_full.csv")
    if bitext_file.exists():
        df = pd.read_csv(bitext_file)
        datasets['Bitext Banking'] = {
            'status': '✓',
            'file': bitext_file,
            'rows': len(df)
        }
    else:
        datasets['Bitext Banking'] = {'status': '✗', 'error': 'File not found'}
    
    # 4. Bank FAQs
    faq_file = Path("data/raw/kenyan_banks_faq/kenyan_banks_faqs.csv")
    if faq_file.exists():
        df = pd.read_csv(faq_file)
        datasets['Bank FAQs'] = {
            'status': '✓',
            'file': faq_file,
            'rows': len(df)
        }
    else:
        datasets['Bank FAQs'] = {'status': '✗', 'error': 'File not found'}
    
    # Print results
    total_samples = 0
    for name, info in datasets.items():
        print(f"\n{name}:")
        if info['status'] == '✓':
            print(f"  Status: ✓ READY")
            print(f"  Rows: {info['rows']:,}")
            total_samples += info['rows']
            if 'cs_samples' in info:
                print(f"  CS Samples: {info['cs_samples']:,}")
        else:
            print(f"  Status: {info['status']} {info.get('error', '')}")
    
    print("\n" + "=" * 70)
    print(f" 📊 TOTAL SAMPLES: {total_samples:,}")
    print("=" * 70)
    
    ready_count = sum(1 for d in datasets.values() if d['status'] == '✓')
    print(f"\n✓ {ready_count}/4 datasets ready")
    
    if ready_count >= 3:
        print("\n🎉 SUFFICIENT DATA TO PROCEED!")
    else:
        print("\n⚠️  Need more datasets")
    
    return datasets, total_samples

if __name__ == "__main__":
    validate_all_datasets()