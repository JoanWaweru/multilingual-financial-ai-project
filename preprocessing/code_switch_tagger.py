import pandas as pd
import json
from pathlib import Path
from typing import Dict, List
import random
import logging

from config.settings import PROCESSED_DATA_DIR, ANNOTATION_CONFIG

logger = logging.getLogger(__name__)

class AnnotationTool:
    """Tool for manual annotation of code-switching patterns"""
    
    def __init__(self):
        self.annotation_file = PROCESSED_DATA_DIR / "annotations.json"
        self.annotations = self.load_annotations()
    
    def load_annotations(self) -> Dict:
        """Load existing annotations"""
        if self.annotation_file.exists():
            with open(self.annotation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_annotations(self):
        """Save annotations to file"""
        with open(self.annotation_file, 'w', encoding='utf-8') as f:
            json.dump(self.annotations, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(self.annotations)} annotations")
    
    def prepare_annotation_sample(self, df: pd.DataFrame, sample_size: int = 500) -> pd.DataFrame:
        """Prepare stratified sample for annotation"""
        logger.info(f"Preparing {sample_size} tweets for annotation...")
        
        # Stratified sampling by switching type
        samples = []
        
        if 'switching_type' in df.columns:
            for switch_type in df['switching_type'].unique():
                type_df = df[df['switching_type'] == switch_type]
                n_samples = min(len(type_df), sample_size // len(df['switching_type'].unique()))
                samples.append(type_df.sample(n=n_samples, random_state=42))
        else:
            samples = [df.sample(n=min(sample_size, len(df)), random_state=42)]
        
        sample_df = pd.concat(samples).drop_duplicates(subset=['id'])
        
        # Save sample
        output_file = PROCESSED_DATA_DIR / "annotation_sample.csv"
        sample_df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Saved annotation sample to {output_file}")
        
        return sample_df
    
    def annotate_interactive(self, tweet_id: str, text: str):
        """Interactive annotation interface (command-line)"""
        print("\n" + "="*70)
        print(f"Tweet ID: {tweet_id}")
        print("-"*70)
        print(f"Text: {text}")
        print("-"*70)
        
        # Language labels
        print("\nLanguage labels (space-separated word indices):")
        print("Example: EN:0,1,2 SW:3,4 MIXED:5")
        print("Labels:", ", ".join(ANNOTATION_CONFIG['language_labels']))
        language_annotation = input("Enter annotation (or 'skip'): ").strip()
        
        if language_annotation.lower() == 'skip':
            return None
        
        # Switching type
        print("\nSwitching type:")
        for i, stype in enumerate(ANNOTATION_CONFIG['switching_types'], 1):
            print(f"{i}. {stype}")
        switching_choice = input("Select switching type (1-4): ").strip()
        
        try:
            switching_type = ANNOTATION_CONFIG['switching_types'][int(switching_choice) - 1]
        except (ValueError, IndexError):
            switching_type = "unknown"
        
        # Save annotation
        annotation = {
            'tweet_id': tweet_id,
            'text': text,
            'language_annotation': language_annotation,
            'switching_type': switching_type,
            'annotator': 'default',  # Can be customized
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        self.annotations[tweet_id] = annotation
        self.save_annotations()
        
        print("\n✓ Annotation saved!")
        return annotation
    
    def export_annotations_for_training(self) -> pd.DataFrame:
        """Export annotations in format suitable for model training"""
        if not self.annotations:
            logger.warning("No annotations found!")
            return pd.DataFrame()
        
        annotations_list = []
        for tweet_id, annotation in self.annotations.items():
            annotations_list.append({
                'id': tweet_id,
                'text': annotation['text'],
                'switching_type': annotation['switching_type'],
                'language_annotation': annotation['language_annotation']
            })
        
        df = pd.DataFrame(annotations_list)
        
        # Save
        output_file = PROCESSED_DATA_DIR / "training_annotations.csv"
        df.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Exported {len(df)} annotations for training")
        
        return df
    
    def get_annotation_statistics(self) -> Dict:
        """Get statistics about annotations"""
        if not self.annotations:
            return {'total': 0}
        
        df = pd.DataFrame(list(self.annotations.values()))
        
        stats = {
            'total_annotations': len(df),
            'switching_types': df['switching_type'].value_counts().to_dict(),
            'annotators': df['annotator'].value_counts().to_dict() if 'annotator' in df.columns else {}
        }
        
        return stats

if __name__ == "__main__":
    from config.settings import PROCESSED_DATA_DIR
    
    # Load analyzed data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_analyzed.csv")
    
    # Initialize annotator
    annotator = AnnotationTool()
    
    # Prepare sample
    sample_df = annotator.prepare_annotation_sample(df, sample_size=100)
    
    print("\n" + "="*70)
    print("ANNOTATION TOOL")
    print("="*70)
    print(f"Sample prepared: {len(sample_df)} tweets")
    print(f"Existing annotations: {len(annotator.annotations)}")
    print("="*70)
    
    # Interactive annotation (example for first 5 tweets)
    print("\nStarting annotation session (first 5 tweets)...")
    print("Type 'skip' to skip a tweet, 'quit' to exit")
    
    for idx, row in sample_df.head(5).iterrows():
        user_input = input("\nPress Enter to annotate next tweet (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        
        annotator.annotate_interactive(row['id'], row['cleaned_text'])
    
    # Show statistics
    stats = annotator.get_annotation_statistics()
    print("\n" + "="*70)
    print("ANNOTATION STATISTICS")
    print("="*70)
    for key, value in stats.items():
        print(f"{key}: {value}")