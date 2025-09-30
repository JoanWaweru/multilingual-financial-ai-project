"""
Chatbot module for multilingual financial assistance
Provides AI-powered conversational interface with code-switching support
"""

import logging

logger = logging.getLogger(__name__)

try:
    from .chatbot_engine import MultilingualFinancialChatbot
    from .response_generator import ResponseGenerator
    from .cultural_knowledge import CulturalKnowledgeBase
    
    __all__ = [
        'MultilingualFinancialChatbot',
        'ResponseGenerator',
        'CulturalKnowledgeBase'
    ]
    
    logger.info("✓ Chatbot modules loaded successfully")
    
except ImportError as e:
    logger.warning(f"Warning: Could not import chatbot modules: {e}")
    __all__ = []

# Module version
__version__ = "1.0.0"

# Module description
__doc__ = """
Chatbot Module
==============

This module provides an intelligent multilingual chatbot for:
- Financial advice and education
- Code-switching conversation
- Cultural context integration
- Topic detection and user profiling

Main Classes:
- MultilingualFinancialChatbot: Main chatbot engine
- ResponseGenerator: AI-powered response generation
- CulturalKnowledgeBase: Traditional financial wisdom

Features:
- Adaptive code-switching (English-Swahili)
- Cultural proverbs and concepts
- Financial topic expertise
- Conversation history management
- User experience personalization

Supported Topics:
- Savings (Akiba)
- Investment (Uwekezaji)
- Budgeting (Bajeti)
- Loans (Mikopo)
- M-Pesa & Mobile Money
- Business (Biashara)
- Chamas & Group Savings
- Insurance (Bima)

Usage:
    from chatbot import MultilingualFinancialChatbot
    
    chatbot = MultilingualFinancialChatbot()
    response = chatbot.chat("How can I save money?")
    print(response)
    
    # Get statistics
    stats = chatbot.get_conversation_stats()
    print(stats)

Example Conversation:
    User: "Nisaidie na akiba"
    Bot: "To save money effectively, start by setting aside at least 10% 
          of your income. Automate your savings through standing orders. 
          Kama wahenga walivyosema: 'Akiba haiozi - Savings never rot!'"
"""

# Chatbot configuration
CHATBOT_INFO = {
    'name': 'Multilingual Financial Assistant',
    'version': '1.0.0',
    'languages': ['English', 'Swahili'],
    'topics': [
        'savings', 'investment', 'budget', 'loan', 
        'mpesa', 'business', 'chama', 'insurance'
    ],
    'features': [
        'Code-switching support',
        'Cultural knowledge integration',
        'Real-time conversation',
        'User profiling',
        'Topic detection'
    ]
}

def get_chatbot_info() -> dict:
    """Get chatbot information and capabilities"""
    return CHATBOT_INFO