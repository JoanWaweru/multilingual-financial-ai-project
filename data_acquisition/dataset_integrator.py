"""
Integrate all three datasets into unified format
"""

import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetIntegrator:
    """Integrate KenCorpus, Bitext, and Bank FAQs"""
    
    def __init__(self):
        self.raw_path = Path("data/raw")
        self.processed_path = Path("data/processed")
        self.processed_path.mkdir(exist_ok=True, parents=True)
    
    def load_kencorpus(self):
        """Load processed KenCorpus"""
        file_path = self.processed_path / "kencorpus_processed.csv"
        
        if not file_path.exists():
            logger.warning("KenCorpus not found. Run process_kencorpus.py first")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"Loaded KenCorpus: {len(df)} samples")
        
        # Standardize columns
        df = df.rename(columns={'text': 'content'})
        df['dataset'] = 'kencorpus'
        df['type'] = 'code_switching'
        
        return df[['content', 'dataset', 'type', 'has_code_switching']]
    
    def load_bitext(self):
        """Load Bitext banking data"""
        file_path = self.raw_path / "bitext_banking" / "bitext_banking_full.csv"
        
        if not file_path.exists():
            logger.warning("Bitext not found. Run download_bitext.py first")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"Loaded Bitext: {len(df)} samples")
        
        # Create Q&A pairs
        qa_data = []
        for _, row in df.iterrows():
            qa_data.append({
                'question': row['instruction'],
                'answer': row['response'],
                'category': row.get('category', ''),
                'intent': row.get('intent', ''),
                'dataset': 'bitext',
                'type': 'financial_qa'
            })
        
        return pd.DataFrame(qa_data)
    
    def load_bank_faqs(self):
        """Load Kenyan bank FAQs"""
        file_path = self.raw_path / "kenyan_banks_faq" / "kenyan_banks_faqs.csv"
        
        if not file_path.exists():
            logger.warning("Bank FAQs not found. Run scrape_bank_faqs.py first")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"Loaded Bank FAQs: {len(df)} samples")
        
        # Standardize columns
        df = df.rename(columns={'bank': 'source_bank'})
        df['dataset'] = 'kenyan_banks'
        df['type'] = 'financial_qa'
        
        return df[['question', 'answer', 'source_bank', 'dataset', 'type']]
    
    def create_code_switching_dataset(self, kencorpus_df):
        """Create dataset for code-switching detection"""
        
        if kencorpus_df.empty:
            logger.error("No KenCorpus data available")
            return None
        
        # Filter for code-switching samples
        cs_df = kencorpus_df[kencorpus_df['has_code_switching'] == True].copy()
        
        logger.info(f"Code-switching dataset: {len(cs_df)} samples")
        
        # Save
        output_file = self.processed_path / "code_switching_data.csv"
        cs_df.to_csv(output_file, index=False)
        logger.info(f"Saved to: {output_file}")
        
        return cs_df
    
    def create_financial_qa_dataset(self, bitext_df, faq_df):
        """Create dataset for financial Q&A"""
        
        if bitext_df.empty and faq_df.empty:
            logger.error("No financial Q&A data available")
            return None
        
        # Combine Bitext and FAQs
        all_qa = []
        
        # Add Bitext
        for _, row in bitext_df.iterrows():
            all_qa.append({
                'question': row['question'],
                'answer': row['answer'],
                'category': row.get('category', ''),
                'source': 'bitext'
            })
        
        # Add Bank FAQs
        for _, row in faq_df.iterrows():
            all_qa.append({
                'question': row['question'],
                'answer': row['answer'],
                'category': row.get('source_bank', 'general'),
                'source': 'kenyan_banks'
            })
        
        qa_df = pd.DataFrame(all_qa)
        logger.info(f"Financial Q&A dataset: {len(qa_df)} pairs")
        
        # Save
        output_file = self.processed_path / "financial_qa_pairs.csv"
        qa_df.to_csv(output_file, index=False)
        logger.info(f"Saved to: {output_file}")
        
        return qa_df
    
    def integrate_all(self):
        """Integrate all datasets"""
        
        logger.info("=" * 60)
        logger.info("INTEGRATING ALL DATASETS")
        logger.info("=" * 60)
        
        # Load all datasets
        kencorpus_df = self.load_kencorpus()
        bitext_df = self.load_bitext()
        faq_df = self.load_bank_faqs()
        
        # Create specialized datasets
        cs_dataset = self.create_code_switching_dataset(kencorpus_df)
        qa_dataset = self.create_financial_qa_dataset(bitext_df, faq_df)
        
        # Summary statistics
        logger.info("\n" + "=" * 60)
        logger.info("INTEGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Code-switching samples: {len(cs_dataset) if cs_dataset is not None else 0}")
        logger.info(f"Financial Q&A pairs: {len(qa_dataset) if qa_dataset is not None else 0}")
        logger.info(f"Total samples: {(len(cs_dataset) if cs_dataset is not None else 0) + (len(qa_dataset) if qa_dataset is not None else 0)}")
        
        logger.info("\nFiles saved to: data/processed/")
        logger.info("  - code_switching_data.csv")
        logger.info("  - financial_qa_pairs.csv")
        
        return cs_dataset, qa_dataset

if __name__ == "__main__":
    integrator = DatasetIntegrator()
    integrator.integrate_all()