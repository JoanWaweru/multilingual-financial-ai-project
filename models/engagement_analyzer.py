import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from typing import Dict, List
import logging

from config.settings import MODELS_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

class EngagementAnalyzer:
    """Analyze engagement patterns for code-switched content"""
    
    def __init__(self):
        self.model = None
        self.feature_names = []
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for engagement analysis"""
        logger.info("Preparing engagement features...")
        
        df = df.copy()
        
        # Calculate total engagement
        df['total_engagement'] = df['likes'] + df['retweets'] + df['replies'] + df['quotes']
        
        # Engagement rate (normalized by followers - use median if not available)
        df['engagement_rate'] = df['total_engagement'] / (df['word_count'] + 1)
        
        # Binary high engagement (above median)
        median_engagement = df['total_engagement'].median()
        df['high_engagement'] = (df['total_engagement'] > median_engagement).astype(int)
        
        # Features
        feature_df = pd.DataFrame()
        feature_df['word_count'] = df['word_count']
        feature_df['has_code_switching'] = df['has_code_switching'].astype(int)
        feature_df['switching_score'] = df['switching_score']
        feature_df['english_ratio'] = df['english_ratio']
        feature_df['swahili_ratio'] = df['swahili_ratio']
        
        # Switching type one-hot encoding
        switching_dummies = pd.get_dummies(df['switching_type'], prefix='switch_type')
        feature_df = pd.concat([feature_df, switching_dummies], axis=1)
        
        # Country one-hot encoding
        country_dummies = pd.get_dummies(df['country'], prefix='country')
        feature_df = pd.concat([feature_df, country_dummies], axis=1)
        
        # Target variable
        feature_df['high_engagement'] = df['high_engagement']
        
        self.feature_names = [col for col in feature_df.columns if col != 'high_engagement']
        
        logger.info(f"Created {len(self.feature_names)} features")
        
        return feature_df
    
    def train(self, df: pd.DataFrame):
        """Train engagement prediction model"""
        logger.info("Training engagement analyzer...")
        
        # Prepare features
        feature_df = self.prepare_features(df)
        
        # Split data
        X = feature_df[self.feature_names]
        y = feature_df['high_engagement']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Train Accuracy: {train_score:.4f}")
        logger.info(f"Test Accuracy: {test_score:.4f}")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5)
        logger.info(f"Cross-val Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Most Important Features:")
        print(feature_importance.head(10))
        
        # Detailed evaluation on test set
        y_pred = self.model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return test_score
    
    def analyze_code_switching_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze impact of code-switching on engagement"""
        logger.info("Analyzing code-switching impact...")
        
        results = {}
        
        # Calculate total engagement
        df['total_engagement'] = df['likes'] + df['retweets'] + df['replies'] + df['quotes']
        
        # Compare code-switched vs non-code-switched
        code_switched = df[df['has_code_switching'] == True]
        non_code_switched = df[df['has_code_switching'] == False]
        
        results['code_switched_avg_engagement'] = code_switched['total_engagement'].mean()
        results['non_code_switched_avg_engagement'] = non_code_switched['total_engagement'].mean()
        results['engagement_improvement'] = (
            (results['code_switched_avg_engagement'] - results['non_code_switched_avg_engagement']) 
            / results['non_code_switched_avg_engagement'] * 100
        )
        
        # By switching type
        switching_type_engagement = df.groupby('switching_type')['total_engagement'].mean().to_dict()
        results['by_switching_type'] = switching_type_engagement
        
        # By country
        country_engagement = df.groupby(['country', 'has_code_switching'])['total_engagement'].mean().to_dict()
        results['by_country'] = country_engagement
        
        return results
    
    def save_model(self, filename: str = 'engagement_analyzer.pkl'):
        """Save model to file"""
        if self.model is None:
            raise ValueError("No model to save. Train first!")
        
        filepath = MODELS_DIR / filename
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str = 'engagement_analyzer.pkl'):
        """Load model from file"""
        filepath = MODELS_DIR / filename
        data = joblib.load(filepath)
        self.model = data['model']
        self.feature_names = data['feature_names']
        logger.info(f"Model loaded from {filepath}")

if __name__ == "__main__":
    # Load data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_analyzed.csv")
    
    # Initialize analyzer
    analyzer = EngagementAnalyzer()
    
    # Train
    print("\n" + "="*70)
    print("TRAINING ENGAGEMENT ANALYZER")
    print("="*70)
    test_score = analyzer.train(df)
    
    # Analyze impact
    print("\n" + "="*70)
    print("CODE-SWITCHING IMPACT ANALYSIS")
    print("="*70)
    impact = analyzer.analyze_code_switching_impact(df)
    
    print(f"\nAverage Engagement (Code-switched): {impact['code_switched_avg_engagement']:.2f}")
    print(f"Average Engagement (Non code-switched): {impact['non_code_switched_avg_engagement']:.2f}")
    print(f"Improvement: {impact['engagement_improvement']:.2f}%")
    
    print("\nEngagement by Switching Type:")
    for switch_type, engagement in impact['by_switching_type'].items():
        print(f"  {switch_type}: {engagement:.2f}")
    
    # Save model
    analyzer.save_model()