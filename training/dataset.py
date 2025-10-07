"""
PyTorch Dataset for code-switching detection
"""

import torch
from torch.utils.data import Dataset
import pandas as pd
from transformers import BertTokenizer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeSwitchingDataset(Dataset):
    """Dataset for BERT-based code-switching detection"""
    
    def __init__(self, csv_file, tokenizer, max_length=128):
        """
        Args:
            csv_file: Path to CSV file
            tokenizer: BERT tokenizer
            max_length: Maximum sequence length
        """
        self.df = pd.read_csv(csv_file)
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Create label mapping
        self.label2id = {
            'english': 0,
            'swahili': 1,
            'code_switched': 2,
            'mixed': 2,  # Treat 'mixed' as code_switched
            'unknown': 0  # Default to english
        }
        
        logger.info(f"Loaded {len(self.df)} samples from {csv_file}")
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        text = str(row['text'])
        
        # Get label
        if 'has_code_switching' in self.df.columns:
            # Binary label
            label = 2 if row['has_code_switching'] else 0
        elif 'language' in self.df.columns:
            # Multi-class label
            lang = str(row['language']).lower()
            label = self.label2id.get(lang, 0)
        else:
            label = 0
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def create_dataloaders(train_file, val_file, test_file, 
                       tokenizer, batch_size=32, max_length=128):
    """Create train/val/test dataloaders"""
    
    from torch.utils.data import DataLoader
    
    # Create datasets
    train_dataset = CodeSwitchingDataset(train_file, tokenizer, max_length)
    val_dataset = CodeSwitchingDataset(val_file, tokenizer, max_length)
    test_dataset = CodeSwitchingDataset(test_file, tokenizer, max_length)
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=2
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=2
    )
    
    logger.info(f"Created dataloaders:")
    logger.info(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
    logger.info(f"  Val: {len(val_dataset)} samples, {len(val_loader)} batches")
    logger.info(f"  Test: {len(test_dataset)} samples, {len(test_loader)} batches")
    
    return train_loader, val_loader, test_loader

if __name__ == "__main__":
    from transformers import BertTokenizer
    from pathlib import Path
    
    # Test dataset loading
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    
    train_file = Path("data/splits/train_processed.csv")
    if train_file.exists():
        dataset = CodeSwitchingDataset(train_file, tokenizer)
        print(f"\n✓ Dataset test successful!")
        print(f"  Total samples: {len(dataset)}")
        print(f"  Sample item: {dataset[0].keys()}")
    else:
        print(f"✗ File not found: {train_file}")