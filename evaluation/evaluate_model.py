"""
Evaluate trained model on test set
"""

import torch
import torch.nn as nn
from transformers import BertTokenizer
from pathlib import Path
import logging
from tqdm import tqdm
import json
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

from training.model import BERTCodeSwitchingModel
from training.dataset import CodeSwitchingDataset
from torch.utils.data import DataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_model(model, test_loader, device):
    """Evaluate model on test set"""
    
    model.eval()
    all_predictions = []
    all_labels = []
    total_loss = 0
    criterion = nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating"):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            
            total_loss += loss.item()
            predictions = torch.argmax(logits, dim=1)
            
            all_predictions.extend(predictions.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(test_loader)
    accuracy = np.mean(np.array(all_predictions) == np.array(all_labels))
    
    return avg_loss, accuracy, all_predictions, all_labels

def main():
    """Main evaluation function"""
    
    logger.info("=" * 70)
    logger.info(" 🔍 MODEL EVALUATION ON TEST SET")
    logger.info("=" * 70)
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Load tokenizer
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    # Load test data
    splits_path = Path("data/splits")
    test_file = splits_path / "test_processed.csv"
    if not test_file.exists():
        test_file = splits_path / "test.csv"
    
    logger.info(f"Loading test data from: {test_file}")
    test_dataset = CodeSwitchingDataset(test_file, tokenizer, max_length=128)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Load model
    model = BERTCodeSwitchingModel(num_labels=3)
    model_path = Path("saved_models/best_model.pt")
    
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return
    
    logger.info(f"Loading model from: {model_path}")
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    
    # Evaluate
    logger.info("\nEvaluating on test set...")
    test_loss, test_acc, predictions, labels = evaluate_model(model, test_loader, device)
    
    # Print results
    logger.info("\n" + "=" * 70)
    logger.info(" 📊 TEST SET RESULTS")
    logger.info("=" * 70)
    logger.info(f"Test Loss: {test_loss:.4f}")
    logger.info(f"Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    
    # Classification report
    label_names = ['English/Non-CS', 'Swahili', 'Code-Switched']
    
    logger.info("\n" + "=" * 70)
    logger.info(" 📈 CLASSIFICATION REPORT")
    logger.info("=" * 70)
    print(classification_report(labels, predictions, target_names=label_names, digits=4))
    
    # Confusion matrix
    logger.info("\n" + "=" * 70)
    logger.info(" 🔢 CONFUSION MATRIX")
    logger.info("=" * 70)
    cm = confusion_matrix(labels, predictions)
    print("\n", cm)
    print("\nRows: True labels | Columns: Predictions")
    print(f"Labels: {label_names}")
    
    # Check class distribution
    logger.info("\n" + "=" * 70)
    logger.info(" 📊 CLASS DISTRIBUTION")
    logger.info("=" * 70)
    unique, counts = np.unique(labels, return_counts=True)
    for label_id, count in zip(unique, counts):
        logger.info(f"  {label_names[label_id]}: {count} samples ({count/len(labels)*100:.1f}%)")
    
    # Save results
    results_dir = Path("results/evaluation")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    results = {
        'test_loss': float(test_loss),
        'test_accuracy': float(test_acc),
        'classification_report': classification_report(labels, predictions, 
                                                       target_names=label_names, 
                                                       output_dict=True),
        'confusion_matrix': cm.tolist(),
        'class_distribution': {label_names[i]: int(c) for i, c in zip(unique, counts)}
    }
    
    with open(results_dir / "test_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\n✓ Results saved to: {results_dir}/test_results.json")
    
    # Final verdict
    logger.info("\n" + "=" * 70)
    logger.info(" 🎯 VERDICT")
    logger.info("=" * 70)
    
    if test_acc > 0.95:
        logger.info("✅ EXCELLENT! Model generalizes very well.")
        logger.info("   However, verify it's not due to data leakage.")
    elif test_acc > 0.85:
        logger.info("✅ VERY GOOD! Model performance is strong.")
    elif test_acc > 0.75:
        logger.info("✅ GOOD! Model performance is acceptable.")
    else:
        logger.info("⚠️ NEEDS IMPROVEMENT. Consider:")
        logger.info("   - More training data")
        logger.info("   - Longer training")
        logger.info("   - Hyperparameter tuning")

if __name__ == "__main__":
    main()