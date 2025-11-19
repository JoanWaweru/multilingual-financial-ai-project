"""
Enhanced Conversation Context Manager
Tracks conversation flow and user preferences
"""

from typing import Dict, List, Optional
from datetime import datetime

class ConversationContext:
    """Track full conversation context for natural dialogue"""
    
    def __init__(self):
        # Investment context
        self.last_investment_advice = None
        self.last_amount = None
        self.last_allocation = None
        
        # User preferences learned during conversation
        self.user_preferences = {
            'risk_tolerance': None,  # 'low', 'medium', 'high'
            'investment_style': None,  # 'diversified', 'concentrated', 'single'
            'liquidity_need': None,  # 'immediate', 'flexible', 'locked'
            'rejected_options': [],  # What user said NO to
            'preferred_options': []  # What user is interested in
        }
        
        # Conversation state
        self.conversation_history = []
        self.last_topic = None
        self.user_asked_for_alternatives = False
        
    def add_exchange(self, user_message: str, bot_response: str, intent: str):
        """Record conversation exchange"""
        
        self.conversation_history.append({
            'user': user_message.lower(),
            'bot': bot_response,
            'intent': intent,
            'timestamp': datetime.now()
        })
        
        self.last_topic = intent
        
        # Keep only last 10 exchanges
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def detect_disagreement(self, user_message: str) -> bool:
        """
        Detect if user is disagreeing/rejecting advice
        
        Signals: "no", "but", "i don't want", "not interested", etc.
        """
        
        disagreement_signals = [
            'no', 'nope', 'nah', 'but', 'however',
            "i don't", "i dont", 'hapana', 'sitaki',
            'not interested', 'dont want', "don't want",
            'instead', 'prefer', 'rather', 'ningependa',
            'whole', 'all of it', 'everything', 'one place'
        ]
        
        user_lower = user_message.lower()
        
        return any(signal in user_lower for signal in disagreement_signals)
    
    def detect_investment_style_preference(self, user_message: str):
        """Learn user's investment style from their message"""
        
        user_lower = user_message.lower()
        
        # Single investment preference
        if any(word in user_lower for word in ['one place', 'single', 'whole', 'all of it', 'everything in']):
            self.user_preferences['investment_style'] = 'single'
        
        # Diversification preference
        elif any(word in user_lower for word in ['diversify', 'spread', 'multiple', 'different']):
            self.user_preferences['investment_style'] = 'diversified'
        
        # Risk tolerance
        if any(word in user_lower for word in ['safe', 'low risk', 'secure', 'guarantee']):
            self.user_preferences['risk_tolerance'] = 'low'
        elif any(word in user_lower for word in ['aggressive', 'high return', 'maximum']):
            self.user_preferences['risk_tolerance'] = 'high'
        
        # Liquidity needs
        if any(word in user_lower for word in ['emergency', 'access', 'withdraw', 'anytime']):
            self.user_preferences['liquidity_need'] = 'immediate'
        elif any(word in user_lower for word in ['lock', 'long term', 'years']):
            self.user_preferences['liquidity_need'] = 'locked'
    
    def get_user_preference_summary(self) -> str:
        """Generate human-readable preference summary"""
        
        prefs = []
        
        if self.user_preferences['investment_style'] == 'single':
            prefs.append("prefers putting all money in one place")
        elif self.user_preferences['investment_style'] == 'diversified':
            prefs.append("wants to diversify")
        
        if self.user_preferences['risk_tolerance'] == 'low':
            prefs.append("low risk tolerance")
        elif self.user_preferences['risk_tolerance'] == 'high':
            prefs.append("high risk tolerance")
        
        return ", ".join(prefs) if prefs else "no strong preferences yet"
    
    def was_topic_just_discussed(self, topic: str) -> bool:
        """Check if we just talked about this topic"""
        
        if not self.conversation_history:
            return False
        
        # Check last 3 exchanges
        recent = self.conversation_history[-3:]
        
        return any(topic in exchange['intent'] for exchange in recent)
    
    def save_investment_context(self, amount: int, allocation: dict):
        """Save investment advice context"""
        
        self.last_amount = amount
        self.last_allocation = allocation
        self.last_investment_advice = {
            'amount': amount,
            'allocation': allocation,
            'timestamp': datetime.now()
        }
    
    def calculate_expected_returns(self) -> Optional[Dict]:
        """Calculate expected returns from last advice"""
        
        if not self.last_allocation:
            return None
        
        # Return rates for different investments
        return_rates = {
            'T-Bills': 0.175,
            'Treasury Bills': 0.175,
            'SACCO': 0.10,
            'MMF': 0.11,
            'Money Market Fund': 0.11,
            'Sanlam': 0.112,
            'CIC': 0.108,
            'Stocks': 0.20,
            'NSE': 0.20
        }
        
        returns = {}
        total_return = 0
        
        # If allocation is a dict with investment breakdown
        if isinstance(self.last_allocation, dict):
            for key, value in self.last_allocation.items():
                if isinstance(value, dict) and 'amount' in value:
                    amount = value['amount']
                    name = value.get('name', key)
                    
                    # Find matching rate
                    rate = 0.10  # default
                    for invest_type, r in return_rates.items():
                        if invest_type.lower() in name.lower():
                            rate = r
                            break
                    
                    expected = amount * rate
                    returns[name] = {
                        'invested': amount,
                        'rate': rate,
                        'return': int(expected),
                        'total': int(amount + expected)
                    }
                    total_return += expected
        
        return {
            'initial_amount': self.last_amount,
            'total_return': int(total_return),
            'final_amount': int(self.last_amount + total_return),
            'breakdown': returns,
            'overall_rate': (total_return / self.last_amount * 100) if self.last_amount else 0
        }
    
    def has_context(self) -> bool:
        """Check if there's saved context"""
        return len(self.conversation_history) > 0 or self.last_investment_advice is not None
    
    def clear_context(self):
        """Reset conversation context"""
        self.__init__()