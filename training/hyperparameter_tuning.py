import pandas as pd
import numpy as np
import torch
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, f1_score, accuracy_score
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging
from typing import Dict, List, Tuple
import json
from datetime import datetime

from config.settings import MODELS_DIR, PROCESSED_DATA_DIR, LOGS_DIR
from models.code_switching_detector import BERTCodeSwitchingDetector, CodeSwitchingTrainer

logger = logging.getLogger(__name__)

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10

def evaluate_model(
    model_path: str = "best_model.pt",
    test_data_file: str = "tweets_analyzed.csv",
    output_dir: Path = None,
    test_size: int = 2000
) -> Dict:
    """
    Comprehensive model evaluation with visualizations
    
    Args:
        model_path: Path to saved model
        test_data_file: Test data file
        output_dir: Directory to save evaluation results
        test_size: Number of test samples per class
    
    Returns:
        Dictionary with evaluation metrics
    """
    
    if output_dir is None:
        output_dir = MODELS_DIR / "evaluation"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info("="*70)
    logger.info("STARTING MODEL EVALUATION")
    logger.info("="*70)
    
    # Load model
    logger.info(f"Loading model from {model_path}...")
    model = BERTCodeSwitchingDetector(n_classes=2)
    trainer = CodeSwitchingTrainer(model)
    
    try:
        trainer.load_model(model_path)
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return {"error": str(e)}
    
    # Load test data
    logger.info(f"Loading test data from {test_data_file}...")
    df = pd.read_csv(PROCESSED_DATA_DIR / test_data_file)
    logger.info(f"Total data: {len(df)} tweets")
    
    # Balance dataset for evaluation
    code_switched = df[df['has_code_switching'] == True]
    non_code_switched = df[df['has_code_switching'] == False]
    
    n_samples = min(len(code_switched), len(non_code_switched), test_size)
    
    code_switched_sample = code_switched.sample(n=n_samples, random_state=42)
    non_code_switched_sample = non_code_switched.sample(n=n_samples, random_state=42)
    
    test_df = pd.concat([code_switched_sample, non_code_switched_sample])
    test_df = test_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"Test set: {len(test_df)} tweets")
    logger.info(f"  Code-switched: {test_df['has_code_switching'].sum()}")
    logger.info(f"  Non code-switched: {(~test_df['has_code_switching']).sum()}")
    
    # Prepare data
    logger.info("Preparing test dataloader...")
    _, _, test_loader = trainer.prepare_data(test_df)
    
    # Evaluate
    logger.info("\nEvaluating model...")
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(trainer.device)
            attention_mask = batch['attention_mask'].to(trainer.device)
            labels = batch['label'].to(trainer.device)
            
            outputs = model(input_ids, attention_mask)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs[:, 1].cpu().numpy())  # Probability of positive class
    
    # Convert to numpy arrays
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    logger.info("✓ Evaluation complete")
    
    # Calculate metrics
    logger.info("\nCalculating metrics...")
    metrics = calculate_metrics(all_labels, all_preds, all_probs)
    
    # Generate visualizations
    logger.info("Generating visualizations...")
    generate_visualizations(all_labels, all_preds, all_probs, output_dir)
    
    # Generate report
    logger.info("Generating evaluation report...")
    generate_evaluation_report(metrics, output_dir / 'evaluation_report.txt')
    
    # Save metrics to JSON
    save_metrics_json(metrics, output_dir / 'metrics.json')
    
    # Additional analysis
    logger.info("Performing additional analysis...")
    additional_analysis = perform_additional_analysis(test_df, all_preds, all_labels)
    
    metrics['additional_analysis'] = additional_analysis
    
    logger.info(f"\n✓ Evaluation complete! Results saved to {output_dir}")
    
    return metrics

def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_probs: np.ndarray) -> Dict:
    """Calculate comprehensive evaluation metrics"""
    
    metrics = {}
    
    # Basic metrics
    metrics['accuracy'] = accuracy_score(y_true, y_pred)
    metrics['precision'] = precision_score(y_true, y_pred, average='binary', zero_division=0)
    metrics['recall'] = recall_score(y_true, y_pred, average='binary', zero_division=0)
    metrics['f1_score'] = f1_score(y_true, y_pred, average='binary', zero_division=0)
    
    # Per-class metrics
    class_names = ['No Code-Switching', 'Code-Switching']
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    metrics['classification_report'] = report
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    # Calculate specificity and sensitivity
    tn, fp, fn, tp = cm.ravel()
    metrics['specificity'] = tn / (tn + fp) if (tn + fp) > 0 else 0
    metrics['sensitivity'] = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    # ROC and AUC
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    roc_auc = auc(fpr, tpr)
    metrics['roc_auc'] = roc_auc
    metrics['fpr'] = fpr.tolist()
    metrics['tpr'] = tpr.tolist()
    
    # Precision-Recall curve
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = auc(recall, precision)
    metrics['pr_auc'] = pr_auc
    metrics['pr_precision'] = precision.tolist()
    metrics['pr_recall'] = recall.tolist()
    
    return metrics

def generate_visualizations(y_true: np.ndarray, y_pred: np.ndarray, y_probs: np.ndarray, output_dir: Path):
    """Generate all evaluation visualizations"""
    
    class_names = ['No Code-Switching', 'Code-Switching']
    
    # 1. Confusion Matrix
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_true, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Count'})
    plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / 'confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Normalized Confusion Matrix
    plt.figure(figsize=(8, 6))
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    sns.heatmap(cm_normalized, annot=True, fmt='.2%', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names,
                cbar_kws={'label': 'Percentage'})
    plt.title('Normalized Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / 'confusion_matrix_normalized.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, 
             label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'roc_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_probs)
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color='blue', lw=2,
             label=f'PR curve (AUC = {pr_auc:.3f})')
    plt.xlabel('Recall', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Curve', fontsize=14, fontweight='bold')
    plt.legend(loc="lower left", fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'precision_recall_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Prediction Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Probability distribution for each class
    true_positive = y_probs[(y_true == 1)]
    true_negative = y_probs[(y_true == 0)]
    
    ax1.hist(true_negative, bins=30, alpha=0.6, label='No Code-Switching', color='blue')
    ax1.hist(true_positive, bins=30, alpha=0.6, label='Code-Switching', color='orange')
    ax1.set_xlabel('Predicted Probability', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.set_title('Prediction Probability Distribution', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Class distribution
    unique, counts = np.unique(y_pred, return_counts=True)
    ax2.bar(['No CS', 'CS'], counts, color=['blue', 'orange'], alpha=0.7)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Predicted Class Distribution', fontsize=12, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'prediction_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Performance Metrics Bar Chart
    from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
    
    metrics_values = [
        accuracy_score(y_true, y_pred),
        precision_score(y_true, y_pred, zero_division=0),
        recall_score(y_true, y_pred, zero_division=0),
        f1_score(y_true, y_pred, zero_division=0)
    ]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(['Accuracy', 'Precision', 'Recall', 'F1-Score'], 
                   metrics_values, 
                   color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                   alpha=0.8)
    
    # Add value labels on bars
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.3f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.ylabel('Score', fontsize=12)
    plt.title('Model Performance Metrics', fontsize=14, fontweight='bold')
    plt.ylim([0, 1.1])
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'performance_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"✓ Generated 6 visualization plots in {output_dir}")

def generate_evaluation_report(metrics: Dict, output_file: Path):
    """Generate detailed text evaluation report"""
    
    report = []
    report.append("="*70)
    report.append("MODEL EVALUATION REPORT")
    report.append("="*70)
    report.append("")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    report.append("-"*70)
    report.append("OVERALL PERFORMANCE METRICS")
    report.append("-"*70)
    report.append(f"Accuracy:    {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    report.append(f"Precision:   {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
    report.append(f"Recall:      {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
    report.append(f"F1-Score:    {metrics['f1_score']:.4f} ({metrics['f1_score']*100:.2f}%)")
    report.append(f"Specificity: {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
    report.append(f"Sensitivity: {metrics['sensitivity']:.4f} ({metrics['sensitivity']*100:.2f}%)")
    report.append(f"ROC-AUC:     {metrics['roc_auc']:.4f}")
    report.append(f"PR-AUC:      {metrics['pr_auc']:.4f}")
    report.append("")
    
    report.append("-"*70)
    report.append("CONFUSION MATRIX")
    report.append("-"*70)
    cm = np.array(metrics['confusion_matrix'])
    report.append(f"                  Predicted")
    report.append(f"                  No CS    CS")
    report.append(f"Actual  No CS     {cm[0][0]:5d}   {cm[0][1]:5d}")
    report.append(f"        CS        {cm[1][0]:5d}   {cm[1][1]:5d}")
    report.append("")
    
    # Calculate additional metrics from confusion matrix
    tn, fp, fn, tp = cm.ravel()
    report.append(f"True Negatives:  {tn} (Correctly identified no code-switching)")
    report.append(f"False Positives: {fp} (Incorrectly predicted code-switching)")
    report.append(f"False Negatives: {fn} (Missed code-switching)")
    report.append(f"True Positives:  {tp} (Correctly identified code-switching)")
    report.append("")
    
    report.append("-"*70)
    report.append("PER-CLASS DETAILED METRICS")
    report.append("-"*70)
    
    cr = metrics['classification_report']
    class_names = ['No Code-Switching', 'Code-Switching']
    
    for class_name in class_names:
        if class_name in cr:
            report.append(f"\n{class_name}:")
            report.append(f"  Precision: {cr[class_name]['precision']:.4f}")
            report.append(f"  Recall:    {cr[class_name]['recall']:.4f}")
            report.append(f"  F1-Score:  {cr[class_name]['f1-score']:.4f}")
            report.append(f"  Support:   {cr[class_name]['support']}")
    
    report.append("")
    report.append("-"*70)
    report.append("MODEL INTERPRETATION")
    report.append("-"*70)
    
    # Add interpretations
    if metrics['accuracy'] >= 0.90:
        interpretation = "Excellent performance"
    elif metrics['accuracy'] >= 0.85:
        interpretation = "Very good performance"
    elif metrics['accuracy'] >= 0.80:
        interpretation = "Good performance"
    elif metrics['accuracy'] >= 0.75:
        interpretation = "Acceptable performance"
    else:
        interpretation = "Needs improvement"
    
    report.append(f"Overall Assessment: {interpretation}")
    report.append("")
    
    # Balanced accuracy
    balanced_acc = (metrics['sensitivity'] + metrics['specificity']) / 2
    report.append(f"Balanced Accuracy: {balanced_acc:.4f}")
    report.append("")
    
    # Recommendations
    report.append("-"*70)
    report.append("RECOMMENDATIONS")
    report.append("-"*70)
    
    if metrics['precision'] < metrics['recall']:
        report.append("• Model has more false positives - consider adjusting threshold")
    elif metrics['recall'] < metrics['precision']:
        report.append("• Model has more false negatives - may need more training data")
    
    if metrics['accuracy'] < 0.85:
        report.append("• Consider collecting more training data")
        report.append("• Try data augmentation techniques")
        report.append("• Experiment with different model architectures")
    
    if fp > fn:
        report.append("• Many false positives - tighten classification threshold")
    elif fn > fp:
        report.append("• Many false negatives - lower classification threshold")
    
    report.append("")
    report.append("="*70)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    logger.info(f"✓ Evaluation report saved to {output_file}")
    
    # Also print summary to console
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    print(f"Accuracy:  {metrics['accuracy']*100:.2f}%")
    print(f"Precision: {metrics['precision']*100:.2f}%")
    print(f"Recall:    {metrics['recall']*100:.2f}%")
    print(f"F1-Score:  {metrics['f1_score']*100:.2f}%")
    print(f"ROC-AUC:   {metrics['roc_auc']:.3f}")
    print("="*70)

def save_metrics_json(metrics: Dict, output_file: Path):
    """Save metrics to JSON file"""
    
    # Convert numpy types to native Python types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj
    
    serializable_metrics = convert_to_serializable(metrics)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_metrics, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Metrics saved to {output_file}")

def perform_additional_analysis(df: pd.DataFrame, y_pred: np.ndarray, y_true: np.ndarray) -> Dict:
    """Perform additional analysis on predictions"""
    
    analysis = {}
    
    # Add predictions to dataframe
    df_copy = df.copy()
    df_copy['predicted'] = y_pred
    df_copy['actual'] = y_true
    df_copy['correct'] = (y_pred == y_true)
    
    # Analyze by country
    if 'country' in df_copy.columns:
        country_accuracy = df_copy.groupby('country')['correct'].mean()
        analysis['accuracy_by_country'] = country_accuracy.to_dict()
    
    # Analyze by text length
    if 'word_count' in df_copy.columns:
        df_copy['length_category'] = pd.cut(df_copy['word_count'], 
                                             bins=[0, 10, 20, 50, 1000],
                                             labels=['Short', 'Medium', 'Long', 'Very Long'])
        length_accuracy = df_copy.groupby('length_category')['correct'].mean()
        analysis['accuracy_by_length'] = length_accuracy.to_dict()
    
    # Analyze false positives and false negatives
    false_positives = df_copy[(df_copy['predicted'] == 1) & (df_copy['actual'] == 0)]
    false_negatives = df_copy[(df_copy['predicted'] == 0) & (df_copy['actual'] == 1)]
    
    analysis['false_positive_count'] = len(false_positives)
    analysis['false_negative_count'] = len(false_negatives)
    
    # Sample errors for manual inspection
    if len(false_positives) > 0:
        fp_samples = false_positives.sample(n=min(5, len(false_positives)))['cleaned_text'].tolist()
        analysis['false_positive_samples'] = fp_samples
    
    if len(false_negatives) > 0:
        fn_samples = false_negatives.sample(n=min(5, len(false_negatives)))['cleaned_text'].tolist()
        analysis['false_negative_samples'] = fn_samples
    
    return analysis

if __name__ == "__main__":
    # Run evaluation
    print("\n" + "="*70)
    print("STARTING MODEL EVALUATION")
    print("="*70)
    
    metrics = evaluate_model(
        model_path="best_model.pt",
        test_data_file="tweets_analyzed.csv",
        test_size=2000
    )
    
    if 'error' not in metrics:
        print("\n✓ Evaluation completed successfully!")
        print(f"Results saved to: {MODELS_DIR / 'evaluation'}")
    else:
        print(f"\n✗ Evaluation failed: {metrics['error']}")