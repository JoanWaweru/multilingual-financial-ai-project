"""
Process KenCorpus - 4,837 text files
Efficiently processes thousands of small text files
"""

from pathlib import Path
import pandas as pd
import logging
from tqdm import tqdm
import re
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KenCorpusProcessor:
    """Process KenCorpus with 4,837 text files"""
    
    def __init__(self, raw_path="data/raw/kencorpus", output_path="data/processed"):
        self.raw_path = Path(raw_path)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True, parents=True)
        
        # Language markers for detection
        self.swahili_markers = [
            'ni', 'na', 'ya', 'wa', 'kwa', 'lakini', 'sana', 'tu',
            'sasa', 'hiyo', 'hii', 'ile', 'hizo', 'vile', 'nini',
            'wapi', 'kama', 'pia', 'au', 'ndiyo', 'hapana', 'kwanza',
            'pesa', 'bei', 'akiba', 'mkopo', 'benki', 'nina', 'wewe',
            'mimi', 'yeye', 'sisi', 'wao', 'huyu', 'yule'
        ]
        
        self.english_markers = [
            'the', 'is', 'are', 'and', 'but', 'very', 'just', 'can',
            'will', 'have', 'has', 'been', 'my', 'your', 'this', 'that',
            'what', 'where', 'how', 'when', 'who', 'which', 'there',
            'their', 'they', 'them', 'these', 'those'
        ]
        
        self.financial_keywords = [
            # English
            'money', 'bank', 'account', 'savings', 'loan', 'credit',
            'investment', 'budget', 'payment', 'transfer', 'deposit',
            # Swahili
            'pesa', 'benki', 'akiba', 'mkopo', 'uwekezaji', 'bajeti',
            'malipo', 'hesabu', 'fedha',
            # Kenyan specific
            'mpesa', 'm-pesa', 'chama', 'sacco', 'equity', 'kcb',
            'cooperative', 'fuliza', 'mshwari', 'airtel money'
        ]
    
    def find_all_txt_files(self):
        """Find all .txt files in the directory"""
        
        # Look for .txt files in main directory and subdirectories
        txt_files = list(self.raw_path.rglob("*.txt"))
        
        logger.info(f"Found {len(txt_files)} .txt files")
        
        if len(txt_files) == 0:
            logger.error(f"No .txt files found in {self.raw_path}")
            logger.info("Make sure you've extracted the zip file!")
            return []
        
        return txt_files
    
    def read_file_content(self, file_path):
        """Read file content with multiple encoding attempts"""
        
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.debug(f"Error reading {file_path.name}: {e}")
                continue
        
        logger.warning(f"Could not read {file_path.name} with any encoding")
        return None
    
    def split_into_sentences(self, text):
        """Split text into sentences"""
        
        # Simple sentence splitter (can be improved)
        sentences = re.split(r'[.!?]+', text)
        
        # Clean sentences
        cleaned = []
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 20:  # Minimum length
                cleaned.append(sent)
        
        return cleaned
    
    def detect_language(self, text):
        """Detect if text contains English, Swahili, or both"""
        
        if not text or len(text) < 10:
            return 'unknown'
        
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count language markers
        swahili_count = sum(1 for word in words if word in self.swahili_markers)
        english_count = sum(1 for word in words if word in self.english_markers)
        
        total_markers = swahili_count + english_count
        
        if total_markers == 0:
            return 'unknown'
        
        # Calculate percentages
        sw_pct = swahili_count / total_markers if total_markers > 0 else 0
        en_pct = english_count / total_markers if total_markers > 0 else 0
        
        # Classify
        if swahili_count > 0 and english_count > 0:
            return 'code_switched'
        elif swahili_count > english_count:
            return 'swahili'
        elif english_count > swahili_count:
            return 'english'
        else:
            return 'unknown'
    
    def is_financial_content(self, text):
        """Check if text contains financial keywords"""
        
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Count financial keywords
        count = sum(1 for keyword in self.financial_keywords if keyword in text_lower)
        
        return count > 0
    
    def process_all_files(self):
        """Process all 4,837 text files"""
        
        logger.info("=" * 60)
        logger.info("PROCESSING KENCORPUS - 4,837 TEXT FILES")
        logger.info("=" * 60)
        
        # Find all files
        txt_files = self.find_all_txt_files()
        
        if not txt_files:
            return None
        
        # Process files with progress bar
        all_data = []
        files_processed = 0
        files_with_errors = 0
        
        logger.info(f"\nProcessing {len(txt_files)} files...")
        
        for file_path in tqdm(txt_files, desc="Processing files"):
            try:
                # Read file
                content = self.read_file_content(file_path)
                
                if content is None:
                    files_with_errors += 1
                    continue
                
                # Split into sentences
                sentences = self.split_into_sentences(content)
                
                # Process each sentence
                for sentence in sentences:
                    
                    # Detect language
                    language = self.detect_language(sentence)
                    
                    # Check if financial
                    is_financial = self.is_financial_content(sentence)
                    
                    # Add to data
                    all_data.append({
                        'text': sentence,
                        'file_name': file_path.name,
                        'language': language,
                        'has_code_switching': language == 'code_switched',
                        'is_financial': is_financial,
                        'text_length': len(sentence),
                        'word_count': len(sentence.split())
                    })
                
                files_processed += 1
                
            except Exception as e:
                files_with_errors += 1
                logger.debug(f"Error processing {file_path.name}: {e}")
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        logger.info(f"\n✓ Files processed: {files_processed}")
        logger.info(f"✗ Files with errors: {files_with_errors}")
        logger.info(f"✓ Total sentences extracted: {len(df)}")
        
        return df
    
    def filter_and_save(self, df):
        """Filter data and save different versions"""
        
        logger.info("\n" + "=" * 60)
        logger.info("FILTERING AND SAVING")
        logger.info("=" * 60)
        
        # Statistics
        logger.info(f"\nLanguage Distribution:")
        logger.info(df['language'].value_counts())
        
        logger.info(f"\nCode-switching samples: {df['has_code_switching'].sum()}")
        logger.info(f"Financial samples: {df['is_financial'].sum()}")
        
        # 1. Save ALL processed data
        output_file = self.output_path / "kencorpus_all.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved all data: {output_file}")
        logger.info(f"  Total: {len(df)} samples")
        
        # 2. Save CODE-SWITCHING data
        cs_df = df[df['has_code_switching'] == True].copy()
        output_file = self.output_path / "kencorpus_code_switched.csv"
        cs_df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved code-switching data: {output_file}")
        logger.info(f"  Total: {len(cs_df)} samples")
        
        # 3. Save FINANCIAL data
        fin_df = df[df['is_financial'] == True].copy()
        output_file = self.output_path / "kencorpus_financial.csv"
        fin_df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved financial data: {output_file}")
        logger.info(f"  Total: {len(fin_df)} samples")
        
        # 4. Save CODE-SWITCHING + FINANCIAL (BEST FOR YOUR PROJECT!)
        cs_fin_df = df[(df['has_code_switching'] == True) & (df['is_financial'] == True)].copy()
        output_file = self.output_path / "kencorpus_cs_financial.csv"
        cs_fin_df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved code-switching + financial data: {output_file}")
        logger.info(f"  Total: {len(cs_fin_df)} samples")
        logger.info(f"  ⭐ THIS IS YOUR PRIMARY DATASET!")
        
        # 5. Save sample for inspection
        sample_df = df.head(1000)
        output_file = self.output_path / "kencorpus_sample.csv"
        sample_df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved sample: {output_file}")
        
        # Show sample entries
        logger.info("\n" + "=" * 60)
        logger.info("SAMPLE ENTRIES")
        logger.info("=" * 60)
        
        if len(cs_fin_df) > 0:
            logger.info("\nCode-switched + Financial examples:")
            for i in range(min(5, len(cs_fin_df))):
                logger.info(f"\n{i+1}. {cs_fin_df.iloc[i]['text'][:150]}...")
        
        return df, cs_df, fin_df, cs_fin_df
    
    def generate_statistics(self, df):
        """Generate detailed statistics"""
        
        logger.info("\n" + "=" * 60)
        logger.info("DETAILED STATISTICS")
        logger.info("=" * 60)
        
        stats = {
            'total_sentences': len(df),
            'total_words': df['word_count'].sum(),
            'avg_sentence_length': df['word_count'].mean(),
            'code_switched_count': df['has_code_switching'].sum(),
            'code_switched_pct': df['has_code_switching'].mean() * 100,
            'financial_count': df['is_financial'].sum(),
            'financial_pct': df['is_financial'].mean() * 100,
            'cs_and_financial': ((df['has_code_switching']) & (df['is_financial'])).sum()
        }
        
        logger.info(f"\nTotal sentences: {stats['total_sentences']:,}")
        logger.info(f"Total words: {stats['total_words']:,}")
        logger.info(f"Avg sentence length: {stats['avg_sentence_length']:.1f} words")
        logger.info(f"\nCode-switched: {stats['code_switched_count']:,} ({stats['code_switched_pct']:.1f}%)")
        logger.info(f"Financial content: {stats['financial_count']:,} ({stats['financial_pct']:.1f}%)")
        logger.info(f"Both CS + Financial: {stats['cs_and_financial']:,}")
        
        # Save statistics
        stats_file = self.output_path / "kencorpus_statistics.json"
        import json
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"\n✓ Statistics saved: {stats_file}")
        
        return stats
    
    def run(self):
        """Complete processing pipeline"""
        
        # Process all files
        df = self.process_all_files()
        
        if df is None or len(df) == 0:
            logger.error("No data processed!")
            return None
        
        # Filter and save
        df, cs_df, fin_df, cs_fin_df = self.filter_and_save(df)
        
        # Generate statistics
        stats = self.generate_statistics(df)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ PROCESSING COMPLETE!")
        logger.info("=" * 60)
        logger.info("\nOutput files in: data/processed/")
        logger.info("  1. kencorpus_all.csv              - All data")
        logger.info("  2. kencorpus_code_switched.csv    - Code-switching only")
        logger.info("  3. kencorpus_financial.csv        - Financial only")
        logger.info("  4. kencorpus_cs_financial.csv     - ⭐ BEST (CS + Financial)")
        logger.info("  5. kencorpus_sample.csv           - First 1000 samples")
        logger.info("  6. kencorpus_statistics.json      - Statistics")
        
        return df

if __name__ == "__main__":
    processor = KenCorpusProcessor()
    df = processor.run()