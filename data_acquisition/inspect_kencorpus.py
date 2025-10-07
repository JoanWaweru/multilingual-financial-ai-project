"""
Quick inspection of processed KenCorpus
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_kencorpus():
    """Inspect processed KenCorpus files"""
    
    processed_path = Path("data/processed")
    
    files = {
        'All data': 'kencorpus_all.csv',
        'Code-switching': 'kencorpus_code_switched.csv',
        'Financial': 'kencorpus_financial.csv',
        'CS + Financial': 'kencorpus_cs_financial.csv'
    }
    
    print("\n" + "=" * 70)
    print(" 📊 KENCORPUS INSPECTION")
    print("=" * 70)
    
    for name, filename in files.items():
        file_path = processed_path / filename
        
        if file_path.exists():
            df = pd.read_csv(file_path)
            
            print(f"\n{name}:")
            print(f"  File: {filename}")
            print(f"  Rows: {len(df):,}")
            print(f"  Columns: {list(df.columns)}")
            
            if len(df) > 0:
                print(f"\n  Sample entries:")
                for i in range(min(3, len(df))):
                    text = df.iloc[i]['text']
                    print(f"    {i+1}. {text[:100]}...")
        else:
            print(f"\n{name}: NOT FOUND")
    
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    inspect_kencorpus()