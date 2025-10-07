"""
Train BERT-based code-switching detector
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from transformers import BertTokenizer, AdamW, get_linear_schedule_with_warmup
from pathlib import Path
import logging
from tqdm import tqdm
import json

from training.model import BERTCodeSwitchingModel
from training.dataset import create_dataloaders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Trainer:
    """Trainer for code-switching detection"""
    
    def __init__(self, model, train_loader, val_loader, device, 
                 learning_rate=2e-5, num_epochs=5):
        
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.device = device
        self.num_epochs = num_epochs
        
        # Optimizer
        self.optimizer = AdamW(model.parameters(), lr=learning_rate)
        
        # Scheduler
        total_steps = len(train_loader) * num_epochs
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=500,
            num_training_steps=total_steps
        )
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Tracking
        self.best_val_loss = float('inf')
        self.training_stats = []
    
    def train_epoch(self, epoch):
        """Train for one epoch"""
        
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        progress_bar = tqdm(self.train_loader, desc=f"Epoch {epoch+1}/{self.num_epochs}")
        
        for batch in progress_bar:
            # Move to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            logits = self.model(input_ids, attention_mask)
            loss = self.criterion(logits, labels)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()
            self.scheduler.step()
            
            # Track metrics
            total_loss += loss.item()
            predictions = torch.argmax(logits, dim=1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': loss.item(),
                'acc': correct/total
            })
        
        avg_loss = total_loss / len(self.train_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def validate(self):
        """Validate model"""
        
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in tqdm(self.val_loader, desc="Validating"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                logits = self.model(input_ids, attention_mask)
                loss = self.criterion(logits, labels)
                
                total_loss += loss.item()
                predictions = torch.argmax(logits, dim=1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(self.val_loader)
        accuracy = correct / total
        
        return avg_loss, accuracy
    
    def train(self):
        """Complete training loop"""
        
        logger.info("=" * 60)
        logger.info("STARTING TRAINING")
        logger.info("=" * 60)
        
        for epoch in range(self.num_epochs):
            # Train
            train_loss, train_acc = self.train_epoch(epoch)
            
            # Validate
            val_loss, val_acc = self.validate()
            
            # Log
            logger.info(f"\nEpoch {epoch+1}/{self.num_epochs}")
            logger.info(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
            logger.info(f"  Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            # Save stats
            self.training_stats.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc
            })
            
            # Save best model
            if val_loss < self.best_val_loss:
                self.best_val_loss = val_loss
                self.save_model('best_model.pt')
                logger.info(f"  ✓ Saved best model (val_loss: {val_loss:.4f})")
        
        logger.info("\n" + "=" * 60)
        logger.info("TRAINING COMPLETE!")
        logger.info("=" * 60)
        
        return self.training_stats
    
    def save_model(self, filename):
        """Save model checkpoint"""
        
        models_dir = Path("saved_models")
        models_dir.mkdir(exist_ok=True, parents=True)
        
        filepath = models_dir / filename
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'training_stats': self.training_stats
        }, filepath)

def main():
    """Main training function"""
    
    # Hyperparameters
    BATCH_SIZE = 32
    LEARNING_RATE = 2e-5
    NUM_EPOCHS = 5
    MAX_LENGTH = 128
    
    # Setup device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Load tokenizer
    logger.info("Loading tokenizer...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    # Create dataloaders
    logger.info("Creating dataloaders...")
    splits_path = Path("data/splits")
    
    train_file = splits_path / "train_processed.csv"
    val_file = splits_path / "val_processed.csv"
    test_file = splits_path / "test_processed.csv"
    
    # Check if processed files exist, otherwise use original
    if not train_file.exists():
        train_file = splits_path / "train.csv"
        val_file = splits_path / "val.csv"
        test_file = splits_path / "test.csv"
    
    train_loader, val_loader, test_loader = create_dataloaders(
        train_file, val_file, test_file,
        tokenizer, batch_size=BATCH_SIZE, max_length=MAX_LENGTH
    )
    
    # Create model
    logger.info("Creating model...")
    model = BERTCodeSwitchingModel(num_labels=3, dropout=0.1)
    
    # Create trainer
    trainer = Trainer(
        model, train_loader, val_loader, device,
        learning_rate=LEARNING_RATE, num_epochs=NUM_EPOCHS
    )
    
    # Train
    stats = trainer.train()
    
    # Save final stats
    results_dir = Path("results/training")
    results_dir.mkdir(exist_ok=True, parents=True)
    
    with open(results_dir / "training_stats.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"\n✓ Training stats saved to: {results_dir}/training_stats.json")

if __name__ == "__main__":
    main()