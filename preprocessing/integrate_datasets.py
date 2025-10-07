"""
Integrate all datasets into unified format
Creates:
  1. Code-switching dataset (for training CS detector)
  2. Financial Q&A dataset (for chatbot knowledge base)
"""

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetIntegrator:
    """Integrate all collected datasets"""
    
    def __init__(self):
        self.processed_path = Path("data/processed")
        self.processed_path.mkdir(exist_ok=True, parents=True)
    
    def load_synthetic_cs(self):
        """Load synthetic code-switching data"""
        file_path = self.processed_path / "synthetic_cs_financial.csv"
        
        if not file_path.exists():
            logger.warning("Synthetic CS data not found")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"✓ Loaded Synthetic CS: {len(df)} samples")
        
        # Standardize columns
        df = df.rename(columns={'text': 'content'})
        df['dataset_source'] = 'synthetic'
        
        return df
    
    def load_reddit(self):
        """Load Reddit data"""
        reddit_path = Path("data/raw/reddit_extended")
        
        all_reddit = []
        
        # Load posts
        posts_file = reddit_path / "reddit_posts_extended.csv"
        if posts_file.exists():
            posts_df = pd.read_csv(posts_file)
            
            for _, row in posts_df.iterrows():
                # Combine title and text
                content = f"{row['title']}. {row['text']}" if pd.notna(row['text']) else row['title']
                
                all_reddit.append({
                    'content': content,
                    'has_code_switching': row.get('has_code_switching', False),
                    'is_financial': row.get('is_financial', True),
                    'dataset_source': 'reddit',
                    'type': 'post'
                })
        
        # Load comments
        comments_file = reddit_path / "reddit_comments_extended.csv"
        if comments_file.exists():
            comments_df = pd.read_csv(comments_file)
            
            for _, row in comments_df.iterrows():
                all_reddit.append({
                    'content': row['text'],
                    'has_code_switching': row.get('has_code_switching', False),
                    'is_financial': row.get('is_financial', True),
                    'dataset_source': 'reddit',
                    'type': 'comment'
                })
        
        df = pd.DataFrame(all_reddit)
        logger.info(f"✓ Loaded Reddit: {len(df)} samples")
        
        return df
    
    def load_bitext(self):
        """Load Bitext banking data"""
        file_path = Path("data/raw/bitext_banking/bitext_banking_full.csv")
        
        if not file_path.exists():
            logger.warning("Bitext data not found")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"✓ Loaded Bitext: {len(df)} samples")
        
        # Create Q&A pairs
        qa_pairs = []
        for _, row in df.iterrows():
            qa_pairs.append({
                'question': row['instruction'],
                'answer': row['response'],
                'category': row.get('category', 'general'),
                'intent': row.get('intent', ''),
                'dataset_source': 'bitext',
                'is_financial': True
            })
        
        return pd.DataFrame(qa_pairs)
    
    def load_bank_faqs(self):
        """Load Kenyan bank FAQs"""
        file_path = Path("data/raw/kenyan_banks_faq/kenyan_banks_faqs_manual.csv")
        
        if not file_path.exists():
            logger.warning("Bank FAQs not found")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        logger.info(f"✓ Loaded Bank FAQs: {len(df)} samples")
        
        # Standardize
        df['dataset_source'] = 'kenyan_banks'
        df['is_financial'] = True
        
        return df
    
    def create_cs_detection_dataset(self, synthetic_df, reddit_df):
        """Create dataset for code-switching detection training"""
        
        logger.info("\n" + "=" * 60)
        logger.info("CREATING CODE-SWITCHING DETECTION DATASET")
        logger.info("=" * 60)
        
        all_cs_data = []
        
        # Add synthetic data
        for _, row in synthetic_df.iterrows():
            all_cs_data.append({
                'text': row['content'],
                'language': row.get('language', 'unknown'),
                'has_code_switching': row.get('has_code_switching', False),
                'source': 'synthetic'
            })
        
        # Add Reddit data
        for _, row in reddit_df.iterrows():
            all_cs_data.append({
                'text': row['content'],
                'language': 'code_switched' if row.get('has_code_switching') else 'unknown',
                'has_code_switching': row.get('has_code_switching', False),
                'source': 'reddit'
            })
        
        df = pd.DataFrame(all_cs_data)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['text'])
        
        # Remove very short texts
        df = df[df['text'].str.len() > 20]
        
        logger.info(f"✓ Total samples: {len(df)}")
        logger.info(f"✓ Code-switched: {df['has_code_switching'].sum()}")
        logger.info(f"✓ Non-CS: {(~df['has_code_switching']).sum()}")
        
        # Save
        output_file = self.processed_path / "cs_detection_dataset.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"✓ Saved: {output_file}")
        
        return df
    
    def create_financial_qa_dataset(self, bitext_df, faq_df):
        """Create dataset for financial chatbot knowledge base"""
        
        logger.info("\n" + "=" * 60)
        logger.info("CREATING FINANCIAL Q&A DATASET")
        logger.info("=" * 60)
        
        all_qa = []
        
        # Add Bitext
        for _, row in bitext_df.iterrows():
            all_qa.append({
                'question': row['question'],
                'answer': row['answer'],
                'category': row.get('category', 'general'),
                'source': 'bitext',
                'is_kenyan_specific': False
            })
        
        # Add Bank FAQs
        for _, row in faq_df.iterrows():
            all_qa.append({
                'question': row['question'],
                'answer': row['answer'],
                'category': row.get('bank', 'general'),
                'source': 'kenyan_banks',
                'is_kenyan_specific': True
            })
        
        df = pd.DataFrame(all_qa)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['question'])
        
        logger.info(f"✓ Total Q&A pairs: {len(df)}")
        logger.info(f"✓ Bitext: {(df['source'] == 'bitext').sum()}")
        logger.info(f"✓ Kenyan Banks: {(df['source'] == 'kenyan_banks').sum()}")
        
        # Save
        output_file = self.processed_path / "financial_qa_dataset.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"✓ Saved: {output_file}")
        
        return df
    
    def create_master_dataset(self, cs_df, qa_df):
        """Create one master dataset with all data"""
        
        logger.info("\n" + "=" * 60)
        logger.info("CREATING MASTER DATASET")
        logger.info("=" * 60)
        
        # This combines everything for reference
        master_data = {
            'cs_detection_samples': len(cs_df),
            'financial_qa_pairs': len(qa_df),
            'total_samples': len(cs_df) + len(qa_df),
            'created_at': datetime.now().isoformat()
        }
        
        # Save metadata
        import json
        metadata_file = self.processed_path / "dataset_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(master_data, f, indent=2)
        
        logger.info(f"✓ CS Detection: {master_data['cs_detection_samples']:,}")
        logger.info(f"✓ Financial Q&A: {master_data['financial_qa_pairs']:,}")
        logger.info(f"✓ Total: {master_data['total_samples']:,}")
        logger.info(f"✓ Metadata saved: {metadata_file}")
        
        return master_data
    
    def integrate_all(self):
        """Complete integration pipeline"""
        
        logger.info("\n" + "=" * 70)
        logger.info(" 🔄 DATASET INTEGRATION PIPELINE")
        logger.info("=" * 70)
        
        # Load all datasets
        synthetic_df = self.load_synthetic_cs()
        reddit_df = self.load_reddit()
        bitext_df = self.load_bitext()
        faq_df = self.load_bank_faqs()
        
        # Create specialized datasets
        cs_dataset = self.create_cs_detection_dataset(synthetic_df, reddit_df)
        qa_dataset = self.create_financial_qa_dataset(bitext_df, faq_df)
        
        # Create master metadata
        master = self.create_master_dataset(cs_dataset, qa_dataset)
        
        logger.info("\n" + "=" * 70)
        logger.info(" ✓ INTEGRATION COMPLETE!")
        logger.info("=" * 70)
        logger.info("\nOutput files:")
        logger.info("  1. cs_detection_dataset.csv     - For training CS detector")
        logger.info("  2. financial_qa_dataset.csv     - For chatbot knowledge")
        logger.info("  3. dataset_metadata.json        - Dataset statistics")
        logger.info("\nLocation: data/processed/")
        
        return cs_dataset, qa_dataset, master

if __name__ == "__main__":
    integrator = DatasetIntegrator()
    integrator.integrate_all()