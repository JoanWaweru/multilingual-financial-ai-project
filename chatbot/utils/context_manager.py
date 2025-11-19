"""
Production-Grade Conversation Context Manager
Tracks EVERYTHING needed for natural dialogue
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class ConversationContext:
    """
    Complete conversation state management
    
    Tracks:
    - Full conversation history
    - User preferences and style
    - Investment context
    - Pending questions/topics
    - User's last stated amounts, goals, etc.
    """
    
    def __init__(self):
        # Investment context
        self.last_investment_advice = None
        self.last_amount = None
        self.last_allocation = None
        self.last_options_shown = []  # Track what options we showed
        
        # User preferences
        self.user_preferences = {
            'risk_tolerance': None,
            'investment_style': None,
            'liquidity_need': None,
            'rejected_options': [],
            'preferred_options': [],
            'time_horizon': None
        }
        
        # Conversation state
        self.conversation_history = []
        self.last_topic = None
        self.last_bot_question = None  # What did we ask?
        self.waiting_for_response_type = None  # What are we waiting for?
        
        # Track state
        self.state = 'initial'  # initial, discussing_options, waiting_for_choice, etc.
    
    def add_exchange(self, user_message: str, bot_response: str, intent: str, metadata: Dict = None):
        """Record conversation exchange with rich metadata"""
        
        exchange = {
            'user': user_message.lower(),
            'bot': bot_response,
            'intent': intent,
            'timestamp': datetime.now(),
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(exchange)
        self.last_topic = intent
        
        # Extract what we asked from bot response
        if '?' in bot_response:
            self.last_bot_question = bot_response.split('?')[0].split('\n')[-1] + '?'
        
        # Keep last 20 exchanges
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def get_last_exchange(self) -> Optional[Dict]:
        """Get most recent exchange"""
        return self.conversation_history[-1] if self.conversation_history else None
    
    def get_last_n_exchanges(self, n: int = 3) -> List[Dict]:
        """Get last N exchanges"""
        return self.conversation_history[-n:] if self.conversation_history else []
    
    def detect_disagreement(self, user_message: str) -> bool:
        """
        Comprehensive disagreement detection
        
        Detects: no, but, instead, prefer, rather, not that, etc.
        """
        
        disagreement_signals = [
            # Direct negation
            r'\bno\b', r'\bnope\b', r'\bnah\b', r'\bhapana\b',
            
            # Preference/alternative
            r'\bbut\b', r'\binstead\b', r'\bprefer\b', r'\brather\b',
            r'\bningependa\b', r'\bnataka\b.*\bnot\b',
            
            # Rejection
            r"i don'?t want", r"sitaki", r"not interested",
            r"si\s+hii", r"sio\s+hii",
            
            # Single place preference
            r'\bone\s+place\b', r'\bsingle\b', r'\ball\s+of\s+it\b',
            r'\bwhole\b', r'\beverything\s+in\b', r'\bmahali\s+pamoja\b'
        ]
        
        user_lower = user_message.lower()
        return any(re.search(pattern, user_lower) for pattern in disagreement_signals)
    
    def detect_affirmation(self, user_message: str) -> Optional[str]:
        """
        Detect yes/no/agreement
        
        Returns: 'yes', 'no', or None
        """
        
        user_lower = user_message.lower().strip()
        
        # Must be short (1-3 words)
        if len(user_lower.split()) > 3:
            return None
        
        yes_patterns = [
            r'^yes$', r'^yeah$', r'^yep$', r'^yup$', r'^sure$',
            r'^ok$', r'^okay$', r'^ndio$', r'^sawa$', r'^ndiyo$',
            r'^eeh?$', r'^ehe$', r'^hapana$'
        ]
        
        no_patterns = [
            r'^no$', r'^nope$', r'^nah$', r'^hapana$',
            r'^la$', r'^sitaki$', r'^ala$'
        ]
        
        if any(re.match(pattern, user_lower) for pattern in yes_patterns):
            return 'yes'
        elif any(re.match(pattern, user_lower) for pattern in no_patterns):
            return 'no'
        
        return None
    
    def detect_option_selection(self, user_message: str) -> Optional[int]:
        """
        Detect option selection (1, 2, 3, first, second, etc.)
        
        Returns: Option number (1, 2, 3) or None
        """
        
        user_lower = user_message.lower().strip()
        
        # Must be short
        if len(user_lower.split()) > 4:
            return None
        
        # Pattern matching for options
        patterns = {
            1: [r'\b1\b', r'\bone\b', r'\bfirst\b', r'\boption\s*1\b', r'\bchoice\s*1\b', r'\bya\s*kwanza\b'],
            2: [r'\b2\b', r'\btwo\b', r'\bsecond\b', r'\boption\s*2\b', r'\bchoice\s*2\b', r'\bya\s*pili\b'],
            3: [r'\b3\b', r'\bthree\b', r'\bthird\b', r'\boption\s*3\b', r'\bchoice\s*3\b', r'\bya\s*tatu\b']
        }
        
        for option_num, option_patterns in patterns.items():
            if any(re.search(pattern, user_lower) for pattern in option_patterns):
                return option_num
        
        return None
    
    def detect_investment_style_preference(self, user_message: str):
        """Learn investment preferences from user's message"""
        
        user_lower = user_message.lower()
        
        # Single investment preference
        if any(phrase in user_lower for phrase in [
            'one place', 'single', 'whole', 'all of it', 'everything in',
            'mahali pamoja', 'moja', 'yote', 'all at once'
        ]):
            self.user_preferences['investment_style'] = 'single'
        
        # Diversification preference
        elif any(phrase in user_lower for phrase in [
            'diversify', 'spread', 'multiple', 'different', 'split',
            'gawa', 'tofauti', 'separate'
        ]):
            self.user_preferences['investment_style'] = 'diversified'
        
        # Risk tolerance
        if any(phrase in user_lower for phrase in [
            'safe', 'low risk', 'secure', 'guarantee', 'salama',
            'hakuna risk', 'no risk', 'protected'
        ]):
            self.user_preferences['risk_tolerance'] = 'low'
        elif any(phrase in user_lower for phrase in [
            'aggressive', 'high return', 'maximum', 'risk', 'zaidi',
            'more risk', 'hatari', 'growth'
        ]):
            self.user_preferences['risk_tolerance'] = 'high'
        
        # Liquidity needs
        if any(phrase in user_lower for phrase in [
            'emergency', 'access', 'withdraw', 'anytime', 'dharura',
            'haraka', 'quick', 'liquid', 'flexible'
        ]):
            self.user_preferences['liquidity_need'] = 'immediate'
        elif any(phrase in user_lower for phrase in [
            'lock', 'long term', 'years', 'miaka', 'locked',
            'cant touch', "won't need", 'future'
        ]):
            self.user_preferences['liquidity_need'] = 'locked'
    
    def save_investment_context(self, amount: int, allocation: dict, options: List[str] = None):
        """Save investment advice context"""
        
        self.last_amount = amount
        self.last_allocation = allocation
        self.last_investment_advice = {
            'amount': amount,
            'allocation': allocation,
            'timestamp': datetime.now()
        }
        
        if options:
            self.last_options_shown = options
            self.state = 'waiting_for_choice'
    
    def calculate_expected_returns(self) -> Optional[Dict]:
        """Calculate expected returns from last advice"""
        
        if not self.last_amount:
            return None
        
        # Return rates
        return_rates = {
            'treasury': 0.175,
            't-bill': 0.175,
            'tbill': 0.175,
            'sacco': 0.10,
            'mmf': 0.11,
            'money market': 0.11,
            'stocks': 0.20,
            'nse': 0.20
        }
        
        returns = {}
        total_return = 0
        
        if isinstance(self.last_allocation, dict):
            for key, value in self.last_allocation.items():
                if isinstance(value, dict) and 'amount' in value:
                    amount = value['amount']
                    name = value.get('name', key)
                    
                    # Find rate
                    rate = 0.10  # default
                    for invest_type, r in return_rates.items():
                        if invest_type in name.lower():
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
        else:
            # Simple case - single investment
            rate = return_rates.get(str(self.last_allocation).lower(), 0.10)
            total_return = self.last_amount * rate
            returns['investment'] = {
                'invested': self.last_amount,
                'rate': rate,
                'return': int(total_return),
                'total': int(self.last_amount + total_return)
            }
        
        return {
            'initial_amount': self.last_amount,
            'total_return': int(total_return),
            'final_amount': int(self.last_amount + total_return),
            'breakdown': returns,
            'overall_rate': (total_return / self.last_amount * 100) if self.last_amount else 0
        }
    
    def is_follow_up_question(self, user_message: str) -> bool:
        """Check if message is a follow-up to previous topic"""
        
        # Very short messages are likely follow-ups
        if len(user_message.split()) <= 3:
            return True
        
        # Contains reference words
        reference_words = [
            'that', 'this', 'it', 'them', 'those', 'these',
            'hii', 'hiyo', 'ile', 'hizo'
        ]
        
        return any(word in user_message.lower() for word in reference_words)
    
    def get_user_preference_summary(self) -> str:
        """Human-readable preference summary"""
        
        prefs = []
        
        if self.user_preferences['investment_style'] == 'single':
            prefs.append("prefers single investment")
        elif self.user_preferences['investment_style'] == 'diversified':
            prefs.append("wants diversification")
        
        if self.user_preferences['risk_tolerance'] == 'low':
            prefs.append("low risk")
        elif self.user_preferences['risk_tolerance'] == 'high':
            prefs.append("high risk")
        
        if self.user_preferences['liquidity_need'] == 'immediate':
            prefs.append("needs liquidity")
        
        return ", ".join(prefs) if prefs else "no preferences set"
    
    def has_context(self) -> bool:
        """Check if there's conversation context"""
        return len(self.conversation_history) > 0 or self.last_investment_advice is not None
    
    def clear_context(self):
        """Reset everything"""
        self.__init__()