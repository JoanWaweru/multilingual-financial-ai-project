"""
Project settings and configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ANNOTATIONS_DIR = DATA_DIR / "annotations"
SPLITS_DIR = DATA_DIR / "splits"
MODELS_DIR = BASE_DIR / "saved_models"
LOGS_DIR = BASE_DIR / "logs"
RESULTS_DIR = BASE_DIR / "results"

# Create directories
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, ANNOTATIONS_DIR, 
                 SPLITS_DIR, MODELS_DIR, LOGS_DIR, RESULTS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# API Keys
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')

# Data sources
DATA_SOURCES = {
    'kencorpus': RAW_DATA_DIR / 'kencorpus',
    'bitext_banking': RAW_DATA_DIR / 'bitext_banking',
    'kenyan_banks_faq': RAW_DATA_DIR / 'kenyan_banks_faq'
}

# Preprocessing configuration
PREPROCESSING_CONFIG = {
    'max_length': 512,
    'min_length': 10,
    'remove_urls': True,
    'remove_mentions': True,
    'remove_hashtags': False,
    'lowercase': False,  # Preserve case for language detection
    'remove_punctuation': False,
    'remove_numbers': False,
    'languages': ['en', 'sw']  # English and Swahili
}

# Model configuration
MODEL_CONFIG = {
    'bert_model': 'bert-base-multilingual-cased',
    'max_seq_length': 128,
    'num_labels': 3,  # English, Swahili, Mixed
    'hidden_dropout_prob': 0.1,
    'attention_probs_dropout_prob': 0.1
}

# Training configuration
TRAINING_CONFIG = {
    'batch_size': 32,
    'learning_rate': 2e-5,
    'num_epochs': 10,
    'warmup_steps': 500,
    'weight_decay': 0.01,
    'max_grad_norm': 1.0,
    'device': 'cuda' if os.getenv('CUDA_AVAILABLE', 'False') == 'True' else 'cpu',
    'seed': 42
}

# Annotation configuration
ANNOTATION_CONFIG = {
    'min_annotators': 2,
    'target_agreement': 0.80,  # Cohen's kappa
    'batch_size': 100,
    'languages': ['english', 'swahili', 'mixed']
}

# Chatbot configuration
CHATBOT_CONFIG = {
    'max_history': 10,
    'response_max_length': 200,
    'temperature': 0.7,
    'top_p': 0.9,
    'default_language_mix': 'balanced'  # balanced, english_heavy, swahili_heavy
}

# Financial keywords (Kenyan context)
FINANCIAL_KEYWORDS = {
    'english': [
        'money', 'bank', 'account', 'savings', 'loan', 'credit',
        'debit', 'investment', 'budget', 'finance', 'payment'
    ],
    'swahili': [
        'pesa', 'benki', 'akiba', 'mkopo', 'uwekezaji', 'bajeti',
        'malipo', 'hesabu', 'fedha'
    ],
    'kenyan_specific': [
        'mpesa', 'm-pesa', 'chama', 'sacco', 'equity', 'kcb',
        'cooperative', 'fuliza', 'mshwari', 'kcb-mpesa'
    ]
}

# Logging configuration
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'app.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Export all settings
__all__ = [
    'BASE_DIR', 'DATA_DIR', 'RAW_DATA_DIR', 'PROCESSED_DATA_DIR',
    'MODELS_DIR', 'LOGS_DIR', 'RESULTS_DIR',
    'HUGGINGFACE_TOKEN', 'DATA_SOURCES',
    'PREPROCESSING_CONFIG', 'MODEL_CONFIG', 'TRAINING_CONFIG',
    'ANNOTATION_CONFIG', 'CHATBOT_CONFIG', 'FINANCIAL_KEYWORDS',
    'LOG_CONFIG'
]