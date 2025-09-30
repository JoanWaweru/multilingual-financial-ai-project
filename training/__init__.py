"""
Training module for model training and evaluation
Provides scripts and utilities for ML model development
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .train_detector import train_code_switching_detector
    from .evaluation import evaluate_model, generate_evaluation_report
    
    __all__ = [
        'train_code_switching_detector',
        'evaluate_model',
        'generate_evaluation_report'
    ]
    
    logger.info("✓ Training modules loaded successfully")
    
except ImportError as e:
    logger.warning(f"Warning: Could not import training modules: {e}")
    __all__ = []

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Training Module
===============

This module provides functionality for:
- Training machine learning models
- Model evaluation and metrics
- Generating evaluation reports
- Hyperparameter tuning

Main Functions:
- train_code_switching_detector: Train BERT model
- evaluate_model: Comprehensive evaluation
- generate_evaluation_report: Create detailed reports

Usage:
    from training import train_code_switching_detector, evaluate_model
    
    # Train model
    trainer, results = train_code_switching_detector(
        data_file="tweets_analyzed.csv",
        balance_data=True,
        sample_size=5000
    )
    
    # Evaluate model
    metrics = evaluate_model(
        model_path="best_model.pt",
        test_data_file="tweets_analyzed.csv"
    )

Output:
- Trained model files
- Evaluation metrics (JSON)
- Visualization plots (PNG)
- Detailed text reports
"""