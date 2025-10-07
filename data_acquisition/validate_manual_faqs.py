"""
Validate manually collected FAQs
"""

import pandas as pd
from pathlib import Path

def validate_manual_faqs():
    file_path = Path("data/raw/kenyan_banks_faq/kenyan_banks_faqs_manual.csv")
    
    if not file_path.exists():
        # Try the automated one
        file_path = Path("data/raw/kenyan_banks_faq/kenyan_banks_faqs.csv")
    
    if not file_path.exists():
        print("❌ No FAQ file found!")
        print("Please create: data/raw/kenyan_banks_faq/kenyan_banks_faqs_manual.csv")
        return
    
    df = pd.read_csv(file_path)
    
    print("\n" + "=" * 60)
    print(" ✓ FAQ VALIDATION")
    print("=" * 60)
    
    print(f"\nTotal FAQs: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    
    if 'bank' in df.columns:
        print(f"\nBreakdown by bank:")
        print(df['bank'].value_counts())
    
    # Check quality
    print(f"\nQuality checks:")
    print(f"  Questions with < 10 chars: {(df['question'].str.len() < 10).sum()}")
    print(f"  Answers with < 20 chars: {(df['answer'].str.len() < 20).sum()}")
    print(f"  Missing questions: {df['question'].isna().sum()}")
    print(f"  Missing answers: {df['answer'].isna().sum()}")
    
    # Show samples
    print(f"\n" + "=" * 60)
    print(" SAMPLE FAQs")
    print("=" * 60)
    for i in range(min(3, len(df))):
        print(f"\n{i+1}. Bank: {df.iloc[i]['bank']}")
        print(f"   Q: {df.iloc[i]['question']}")
        print(f"   A: {df.iloc[i]['answer'][:80]}...")
    
    # Recommendation
    print("\n" + "=" * 60)
    if len(df) >= 30:
        print(" ✅ EXCELLENT! You have enough FAQs for your thesis.")
    elif len(df) >= 20:
        print(" ✅ GOOD! This is sufficient, but 10-15 more would be ideal.")
    else:
        print(" ⚠️  Consider adding more FAQs (target: 30-50)")
    print("=" * 60)

if __name__ == "__main__":
    validate_manual_faqs()