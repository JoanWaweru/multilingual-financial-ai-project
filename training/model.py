"""
BERT-based code-switching detection model
"""

import torch
import torch.nn as nn
from transformers import BertModel, BertConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BERTCodeSwitchingModel(nn.Module):
    """BERT model for code-switching detection"""
    
    def __init__(self, num_labels=3, dropout=0.1):
        """
        Args:
            num_labels: Number of classes (3: English, Swahili, Code-switched)
            dropout: Dropout probability
        """
        super(BERTCodeSwitchingModel, self).__init__()
        
        # Load pre-trained BERT
        self.bert = BertModel.from_pretrained('bert-base-multilingual-cased')
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)
        
        logger.info(f"Initialized BERT model with {num_labels} labels")
    
    def forward(self, input_ids, attention_mask):
        """Forward pass"""
        
        # Get BERT outputs
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Use [CLS] token representation
        pooled_output = outputs.pooler_output
        
        # Apply dropout and classifier
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        return logits

if __name__ == "__main__":
    # Test model initialization
    model = BERTCodeSwitchingModel(num_labels=3)
    print(f"\n✓ Model test successful!")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")