import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel, AdamW, get_linear_schedule_with_warmup
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple
import logging
from tqdm import tqdm

from config.settings import MODEL_CONFIG, MODELS_DIR

logger = logging.getLogger(__name__)

class CodeSwitchingDataset(Dataset):
    """Dataset for code-switching detection"""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

class BERTCodeSwitchingDetector(nn.Module):
    """BERT-based model for code-switching detection"""
    
    def __init__(self, n_classes: int = 2, dropout: float = 0.3):
        super(BERTCodeSwitchingDetector, self).__init__()
        
        self.bert = BertModel.from_pretrained(MODEL_CONFIG['bert_model'])
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, n_classes)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        pooled_output = outputs.pooler_output
        dropout_output = self.dropout(pooled_output)
        logits = self.classifier(dropout_output)
        
        return logits

class CodeSwitchingTrainer:
    """Trainer for code-switching detection model"""
    
    def __init__(self, model, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.tokenizer = BertTokenizer.from_pretrained(MODEL_CONFIG['bert_model'])
        
    def prepare_data(self, df: pd.DataFrame) -> Tuple[DataLoader, DataLoader, DataLoader]:
        """Prepare train, validation, and test dataloaders"""
        logger.info("Preparing data...")
        
        # Extract features and labels
        texts = df['cleaned_text'].tolist()
        labels = df['has_code_switching'].astype(int).tolist()
        
        # Split data
        X_train, X_temp, y_train, y_temp = train_test_split(
            texts, labels, 
            test_size=0.3, 
            random_state=MODEL_CONFIG['random_seed'],
            stratify=labels
        )
        
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=0.33,
            random_state=MODEL_CONFIG['random_seed'],
            stratify=y_temp
        )
        
        logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        # Create datasets
        train_dataset = CodeSwitchingDataset(X_train, y_train, self.tokenizer, MODEL_CONFIG['max_length'])
        val_dataset = CodeSwitchingDataset(X_val, y_val, self.tokenizer, MODEL_CONFIG['max_length'])
        test_dataset = CodeSwitchingDataset(X_test, y_test, self.tokenizer, MODEL_CONFIG['max_length'])
        
        # Create dataloaders
        train_loader = DataLoader(train_dataset, batch_size=MODEL_CONFIG['batch_size'], shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=MODEL_CONFIG['batch_size'])
        test_loader = DataLoader(test_dataset, batch_size=MODEL_CONFIG['batch_size'])
        
        return train_loader, val_loader, test_loader
    
    def train(self, train_loader, val_loader, epochs: int = None):
        """Train the model"""
        if epochs is None:
            epochs = MODEL_CONFIG['num_epochs']
        
        # Setup optimizer and scheduler
        optimizer = AdamW(self.model.parameters(), lr=MODEL_CONFIG['learning_rate'])
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        loss_fn = nn.CrossEntropyLoss()
        
        best_val_acc = 0
        
        for epoch in range(epochs):
            logger.info(f"\nEpoch {epoch + 1}/{epochs}")
            
            # Training
            self.model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0
            
            for batch in tqdm(train_loader, desc="Training"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(input_ids, attention_mask)
                loss = loss_fn(outputs, labels)
                
                loss.backward()
                optimizer.step()
                scheduler.step()
                
                train_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            train_acc = 100 * train_correct / train_total
            avg_train_loss = train_loss / len(train_loader)
            
            # Validation
            val_acc, val_loss = self.evaluate(val_loader, loss_fn)
            
            logger.info(f"Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.2f}%")
            logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
            
            # Save best model
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                self.save_model('best_model.pt')
                logger.info(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")
    
    def evaluate(self, data_loader, loss_fn):
        """Evaluate model"""
        self.model.eval()
        
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch in data_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                loss = loss_fn(outputs, labels)
                
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(data_loader)
        
        return accuracy, avg_loss
    
    def predict(self, texts: List[str]) -> List[int]:
        """Predict code-switching for new texts"""
        self.model.eval()
        
        predictions = []
        
        with torch.no_grad():
            for text in texts:
                encoding = self.tokenizer.encode_plus(
                    text,
                    add_special_tokens=True,
                    max_length=MODEL_CONFIG['max_length'],
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt'
                )
                
                input_ids = encoding['input_ids'].to(self.device)
                attention_mask = encoding['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids, attention_mask)
                _, predicted = torch.max(outputs, 1)
                
                predictions.append(predicted.item())
        
        return predictions
    
    def save_model(self, filename: str):
        """Save model to file"""
        filepath = MODELS_DIR / filename
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': MODEL_CONFIG
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filename: str):
        """Load model from file"""
        filepath = MODELS_DIR / filename
        checkpoint = torch.load(filepath, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        logger.info(f"Model loaded from {filepath}")

if __name__ == "__main__":
    from config.settings import PROCESSED_DATA_DIR
    
    # Load data
    df = pd.read_csv(PROCESSED_DATA_DIR / "tweets_analyzed.csv")
    
    # Filter to have balanced dataset
    code_switched = df[df['has_code_switching'] == True].sample(n=min(5000, len(df[df['has_code_switching'] == True])), random_state=42)
    non_code_switched = df[df['has_code_switching'] == False].sample(n=len(code_switched), random_state=42)
    balanced_df = pd.concat([code_switched, non_code_switched]).sample(frac=1, random_state=42)
    
    print(f"\nBalanced dataset: {len(balanced_df)} tweets")
    print(f"Code-switched: {balanced_df['has_code_switching'].sum()}")
    print(f"Non code-switched: {(~balanced_df['has_code_switching']).sum()}")
    
    # Initialize model
    model = BERTCodeSwitchingDetector(n_classes=2)
    trainer = CodeSwitchingTrainer(model)
    
    # Prepare data
    train_loader, val_loader, test_loader = trainer.prepare_data(balanced_df)
    
    # Train
    print("\n" + "="*70)
    print("TRAINING CODE-SWITCHING DETECTOR")
    print("="*70)
    trainer.train(train_loader, val_loader)
    
    # Test
    print("\n" + "="*70)
    print("TESTING MODEL")
    print("="*70)
    test_acc, test_loss = trainer.evaluate(test_loader, nn.CrossEntropyLoss())
    print(f"Test Accuracy: {test_acc:.2f}%")
    print(f"Test Loss: {test_loss:.4f}")