import torch
import pandas as pd
from pathlib import Path
import logging
from datetime import datetime

from models.code_switching_detector import BERTCodeSwitchingDetector, CodeSwitchingTrainer
from config.settings import PROCESSED_DATA_DIR, MODELS_DIR, MODEL_CONFIG

logger = logging.getLogger(__name__)

def train_code_switching_detector(
    data_file: str = "tweets_analyzed.csv",
    balance_data: bool = True,
    sample_size: int = 10000,
    save_model: bool = True
):
    """
    Main training function for code-switching detector
    
    Args:
        data_file: Name of the data file in PROCESSED_DATA_DIR
        balance_data: Whether to balance the dataset
        sample_size: Maximum samples per class
        save_model: Whether to save the trained model
    
    Returns:
        Trained model and evaluation metrics
    """
    
    print("\n" + "="*70)
    print("TRAINING CODE-SWITCHING DETECTOR")
    print("="*70)
    
    # Load data
    logger.info(f"Loading data from {data_file}...")
    df = pd.read_csv(PROCESSED_DATA_DIR / data_file)
    logger.info(f"Loaded {len(df)} tweets")
    
    # Balance dataset
    if balance_data:
        logger.info("Balancing dataset...")
        code_switched = df[df['has_code_switching'] == True]
        non_code_switched = df[df['has_code_switching'] == False]
        
        # Sample to balance
        n_samples = min(len(code_switched), len(non_code_switched), sample_size)
        
        code_switched_sample = code_switched.sample(n=n_samples, random_state=42)
        non_code_switched_sample = non_code_switched.sample(n=n_samples, random_state=42)
        
        df = pd.concat([code_switched_sample, non_code_switched_sample])
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info(f"Balanced dataset: {len(df)} tweets")
        logger.info(f"  Code-switched: {df['has_code_switching'].sum()}")
        logger.info(f"  Non code-switched: {(~df['has_code_switching']).sum()}")
    
    # Initialize model
    logger.info("Initializing BERT model...")
    model = BERTCodeSwitchingDetector(n_classes=2)
    trainer = CodeSwitchingTrainer(model)
    
    # Prepare data
    logger.info("Preparing dataloaders...")
    train_loader, val_loader, test_loader = trainer.prepare_data(df)
    
    # Train
    print("\n" + "-"*70)
    print("TRAINING")
    print("-"*70)
    
    trainer.train(train_loader, val_loader, epochs=MODEL_CONFIG['num_epochs'])
    
    # Test
    print("\n" + "-"*70)
    print("TESTING")
    print("-"*70)
    
    import torch.nn as nn
    test_acc, test_loss = trainer.evaluate(test_loader, nn.CrossEntropyLoss())
    
    print(f"\nFinal Test Accuracy: {test_acc:.2f}%")
    print(f"Final Test Loss: {test_loss:.4f}")
    
    # Save model
    if save_model:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"code_switching_detector_{timestamp}.pt"
        trainer.save_model(model_name)
        logger.info(f"Model saved as {model_name}")
    
    results = {
        "test_accuracy": test_acc,
        "test_loss": test_loss,
        "train_size": len(train_loader.dataset),
        "val_size": len(val_loader.dataset),
        "test_size": len(test_loader.dataset)
    }
    
    return trainer, results

if __name__ == "__main__":
    trainer, results = train_code_switching_detector(
        balance_data=True,
        sample_size=5000,
        save_model=True
    )
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE")
    print("="*70)
    print(f"Test Accuracy: {results['test_accuracy']:.2f}%")
    print(f"Dataset sizes:")
    print(f"  Train: {results['train_size']}")
    print(f"  Validation: {results['val_size']}")
    print(f"  Test: {results['test_size']}")