import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "saved_models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# Data collection settings
DATA_COLLECTION = {
    "target_tweets": 80000,
    "tweets_per_country": {
        "Kenya": 35000,
        "Uganda": 20000,
        "Tanzania": 20000,
        "Rwanda": 5000
    },
    "collection_period_months": 3,
    "languages": ["en", "sw", "und"],
}

# Financial keywords for collection
FINANCIAL_KEYWORDS = {
    "english": [
        "savings", "investment", "budget", "loan", "mpesa",
        "mobile money", "bank", "finance", "money", "business"
    ],
    "swahili": [
        "pesa", "akiba", "mkopo", "bajeti", "biashara", 
        "benki", "fedha", "uwekezaji"
    ],
    "hashtags": [
        "#PersonalFinance", "#MoneyTips", "#Investment",
        "#Savings", "#MobileMoney", "#Mpesa"
    ]
}

# Countries configuration
COUNTRIES = {
    "Kenya": {"code": "KE", "currency": "KES"},
    "Uganda": {"code": "UG", "currency": "UGX"},
    "Tanzania": {"code": "TZ", "currency": "TZS"},
    "Rwanda": {"code": "RW", "currency": "RWF"}
}

# Model configuration
MODEL_CONFIG = {
    "bert_model": "bert-base-multilingual-cased",
    "max_length": 128,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_epochs": 5,
    "validation_split": 0.2,
    "test_split": 0.1,
    "random_seed": 42
}

# Annotation configuration
ANNOTATION_CONFIG = {
    "language_labels": ["EN", "SW", "MIXED", "OTHER"],
    "switching_types": [
        "intra_sentential",  # Within sentence
        "inter_sentential",  # Between sentences
        "tag_switching",     # Single word/phrase
        "cultural_bridge"    # Cultural concept explanation
    ],
    "min_annotators": 2,  # For inter-annotator agreement
}

# Chatbot configuration
CHATBOT_CONFIG = {
    "max_history": 5,
    "response_max_length": 150,
    "temperature": 0.8,
    "cultural_context_weight": 0.3
}