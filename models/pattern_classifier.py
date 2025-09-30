import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from typing import Dict, List, Tuple
import logging

from config.settings import MODELS_DIR, ANNOTATION_CONFIG

logger = logging.getLogger(__name__)

class CodeSwitchingPatternClassifier:
    """Classify types of code-switching patterns"""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
        self.pattern_types = ANNOTATION_CONFIG['switching_types']
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract features for pattern classification"""
        logger.info("Preparing pattern classification features...")
        
        feature_df = pd.DataFrame()
        
        # Basic features
        feature_df['word_count'] = df['word_count']
        feature_df['switching_score'] = df['switching_score']
        feature_df['english_ratio'] = df['english_ratio']
        feature_df['swahili_ratio'] = df['swahili_ratio']
        
        # Calculate switching frequency
        feature_df['switching_frequency'] = df['cleaned_text'].apply(
            self.calculate_switching_frequency
        )
        
        # Position of switches
        feature_df['switches_at_start'] = df['cleaned_text'].apply(
            lambda x: self.has_switch_at_position(x, 'start')
        )
        feature_df['switches_at_end'] = df['cleaned_text'].apply(
            lambda x: self.has_switch_at_position(x, 'end')
        )
        
        # Sentence complexity
        feature_df['num_sentences'] = df['cleaned_text'].apply(
            lambda x: len(x.split('.'))
        )
        
        # Target variable
        if 'switching_type' in df.columns:
            feature_df['switching_type'] = df['switching_type']
        
        self.feature_names = [col for col in feature_df.columns if col != 'switching_type']
        
        return feature_df
    
    def calculate_switching_frequency(self, text: str) -> float:
        """Calculate how often language switches occur"""
        words = text.lower().split()
        if len(words) < 2:
            return 0.0
        
        # Simple heuristic based on language indicators
        swahili_words = ['na', 'ni', 'ya', 'kwa', 'sana', 'tu', 'pesa', 'akiba']
        
        switches = 0
        prev_is_swahili = False
        
        for word in words:
            is_swahili = word in swahili_words
            if is_swahili != prev_is_swahili:
                switches += 1
            prev_is_swahili = is_swahili
        
        return switches / len(words)
    
    def has_switch_at_position(self, text: str, position: str) -> int:
        """Check if code-switching occurs at specific position"""
        words = text.lower().split()
        if len(words) < 3:
            return 0
        
        swahili_words = ['na', 'ni', 'ya', 'kwa', 'sana', 'tu', 'pesa', 'akiba']
        
        if position == 'start':
            # Check first 3 words
            check_words = words[:3]
        else:  # end
            # Check last 3 words
            check_words = words[-3:]
        
        has_swahili = any(w in swahili_words for w in check_words)
        has_english = any(w not in swahili_words for w in check_words)
        
        return 1 if (has_swahili and has_english) else 0
    
    def train(self, df: pd.DataFrame) -> Dict:
        """Train pattern classifier"""
        logger.info("Training pattern classifier...")
        
        # Prepare features
        feature_df = self.prepare_features(df)
        
        # Filter to only rows with switching
        feature_df = feature_df[feature_df['switching_type'].isin(self.pattern_types)]
        
        if len(feature_df) < 50:
            logger.warning(f"Insufficient data for training: {len(feature_df)} samples")
            return {"status": "insufficient_data"}
        
        # Split data
        X = feature_df[self.feature_names]
        y = feature_df['switching_type']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Train Accuracy: {train_score:.4f}")
        logger.info(f"Test Accuracy: {test_score:.4f}")
        
        # Detailed evaluation
        y_pred = self.model.predict(X_test)
        
        results = {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }
        
        return results
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict switching patterns"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        feature_df = self.prepare_features(df)
        X = feature_df[self.feature_names]
        
        return self.model.predict(X)
    
    def save_model(self, filename: str = 'pattern_classifier.pkl'):
        """Save model"""
        if self.model is None:
            raise ValueError("No model to save")
        
        filepath = MODELS_DIR / filename
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'pattern_types': self.pattern_types
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = 'pattern_classifier.pkl'):
        """Load model"""
        filepath = MODELS_DIR / filename
        data = joblib.load(filepath)
        self.model = data['model']
        self.feature_names = data['feature_names']
        self.pattern_types = data['pattern_types']
        logger.info(f"Model loaded from {filepath}")

if __name__ == "__main__":
    from config.settings import PROCESSED_DATA_DIR
    
    # Load data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_analyzed.csv")
    
    # Initialize and train
    classifier = CodeSwitchingPatternClassifier()
    results = classifier.train(df)
    
    print("\n" + "="*70)
    print("PATTERN CLASSIFIER RESULTS")
    print("="*70)
    print(f"Train Accuracy: {results['train_accuracy']:.4f}")
    print(f"Test Accuracy: {results['test_accuracy']:.4f}")
    
    # Save model
    classifier.save_model()