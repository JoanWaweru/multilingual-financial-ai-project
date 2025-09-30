import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not TWITTER_BEARER_TOKEN:
    raise ValueError("TWITTER_BEARER_TOKEN not found in environment variables")