"""
Production-Grade Intent Analyzer
Comprehensive pattern matching for all financial queries
"""

import re
from typing import Dict, Optional, List

class IntentAnalyzer:
    """
    Bulletproof intent detection with comprehensive patterns
    
    Handles:
    - All financial intents
    - Code-switching (English/Swahili)
    - Ambiguous queries
    - Short responses
    - Context-dependent interpretation
    """
    
    def __init__(self):
        """Initialize with exhaustive intent patterns"""
        
        # Intent patterns (ORDER MATTERS - specific to general)
        self.intent_patterns = {
            # Affirmations (highest priority for short responses)
            'affirmation': [
                r'^yes$', r'^yeah$', r'^yep$', r'^sure$', r'^ok$', r'^okay$',
                r'^ndio$', r'^sawa$', r'^ndiyo$', r'^eeh$', r'^ehe$',
                r'^no$', r'^nope$', r'^nah$', r'^hapana$', r'^la$'
            ],
            
            # Option selection
            'option_selection': [
                r'\boption\s*[123]', r'\b[123]\b', r'\bone\b', r'\btwo\b', r'\bthree\b',
                r'\bfirst\b', r'\bsecond\b', r'\bthird\b', r'\bya\s*kwanza\b'
            ],
            
            # MMF queries (very specific)
            'mmf_query': [
                r'mmf', r'money\s*market\s*fund', r'money\s*market', r'best\s*mmf',
                r'which\s*mmf', r'mmf\s*rate', r'compare\s*mmf',
                r'sanlam', r'cic\s*money', r'britam\s*money'
            ],
            
            # Bank comparison
            'bank_comparison': [
                r'bank\s*(gani|ya|mzuri)', r'which\s*bank', r'best\s*bank',
                r'benki\s*gani', r'compare\s*bank', r'good\s*bank',
                r'kuweka.*bank', r'weka.*bank', r'bank.*kuweka'
            ],
            
            # Treasury queries
            'treasury_query': [
                r't-?bill', r'treasury\s*bill', r'treasury\s*bond', r'government\s*bond',
                r'cbk', r'central\s*bank', r'treasury\s*rate'
            ],
            
            # Stock recommendations (specific)
            'stock_recommendation': [
                r'which\s*stock', r'which\s*share', r'recommend.*stock', r'suggest.*stock',
                r'best\s*stock', r'good\s*stock', r'stock.*buy', r'share.*buy',
                r'top\s*stock', r'stock.*today', r'buy.*stock'
            ],
            
            # General stock queries
            'stock_query': [
                r'\bstock', r'\bshare', r'\bnse\b', r'\bhisa\b', r'\bipo\b',
                r'safaricom', r'equity.*bank', r'kcb', r'dividend',
                r'how.*buy.*stock', r'stock\s*market'
            ],
            
            # ETF queries
            'etf_query': [
                r'\betf', r'index\s*fund', r'mutual\s*fund', r'unit\s*trust',
                r'vanguard', r'\bspy\b', r'tracker\s*fund'
            ],
            
            # Global stocks
            'global_stocks_query': [
                r'international\s*stock', r'global\s*stock', r'us\s*stock',
                r'nasdaq', r'nyse', r'wall\s*street',
                r'apple\s*stock', r'tesla', r'amazon', r'microsoft',
                r'google\s*stock', r'foreign\s*stock'
            ],
            
            # Investment advice (broad)
            'investment_advice': [
                r'invest', r'\bweka\b', r'\bakiba\b', r'save', r'saving',
                r'uwekezaji', r'\bput\b', r'place', r'\bwapi\b', r'where',
                r'invest.*wapi', r'niweke\s*wapi', r'should.*invest',
                r'how.*invest', r'where.*put'
            ],
            
            # Loan requests
            'loan_request': [
                r'\bloan\b', r'\bmkopo\b', r'\bkopa\b', r'kukopa', r'borrow',
                r'need.*loan', r'get.*loan', r'nataka.*mkopo'
            ],
            
            # M-Pesa queries
            'mpesa_query': [
                r'm-?pesa', r'send.*money', r'\btuma\b', r'kutuma',
                r'fuliza', r'm-?shwari', r'safaricom', r'mpesa\s*charge'
            ],
            
            # Account opening
            'account_opening': [
                r'open\s*account', r'fungua.*account', r'create\s*account',
                r'new\s*account', r'register', r'signup'
            ],
            
            # SACCO info
            'sacco_info': [
                r'\bsacco\b', r'cooperative', r'join.*sacco', r'sacco.*account'
            ],
            
            # Chama info
            'chama_info': [
                r'\bchama\b', r'savings?\s*group', r'vikundi', r'join.*chama'
            ],
            
            # Return/profit calculations
            'return_calculation': [
                r'how\s*much.*get', r'nitapata', r'\breturn', r'\bprofit',
                r'expect.*after', r'after.*year', r'get\s*back',
                r'\bmapato\b', r'\bfaida\b', r'calculate'
            ]
        }
    
    def analyze(self, text: str, context=None) -> Dict:
        """
        Comprehensive analysis with context awareness
        
        Args:
            text: User's message
            context: ConversationContext object for context-aware analysis
        
        Returns:
            Rich analysis dict
        """
        
        text_lower = text.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(text_lower, context)
        
        # Extract amount
        amount = self._extract_amount(text)
        
        # Detect goal
        goal = self._detect_goal(text_lower)
        
        # Detect urgency
        urgency = self._detect_urgency(text_lower)
        
        # Additional metadata
        is_short_query = len(text.split()) <= 3
        is_follow_up = context.is_follow_up_question(text) if context and context.has_context() else False
        
        return {
            'intent': intent,
            'amount': amount,
            'goal': goal,
            'urgency': urgency,
            'is_short': is_short_query,
            'is_follow_up': is_follow_up,
            'original_text': text,
            'confidence': self._calculate_confidence(text_lower, intent)
        }
    
    def _detect_intent(self, text: str, context=None) -> str:
        """Detect intent with context awareness"""
        
        scores = {}
        
        # Score each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                scores[intent] = score
        
        # Context-based boosting
        if context and context.has_context():
            # If waiting for option selection
            if context.state == 'waiting_for_choice':
                if 'option_selection' in scores:
                    scores['option_selection'] += 10
            
            # If last question asked for yes/no
            if context.last_bot_question and '?' in context.last_bot_question:
                if any(word in text for word in ['yes', 'no', 'ndio', 'hapana']):
                    scores['affirmation'] = scores.get('affirmation', 0) + 10
        
        if not scores:
            return 'general_query'
        
        return max(scores, key=scores.get)
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """
        Extract monetary amounts - ALL formats
        
        Handles:
        - 100k, 100K, 100 k
        - 100,000, 100000
        - niko na 50k
        - nina 200,000 bob
        - 1 laki, 5 million
        - Just "100k" with nothing else
        """
        
        patterns = [
            # Code-switching patterns
            (r'(?:niko|nina|i\s*have|got|na)\s*(?:na\s*)?(\d+)k\b', 1000),
            (r'(?:niko|nina|i\s*have|got|na)\s*(?:na\s*)?(\d{1,3}(?:,\d{3})*)', 1),
            
            # Standard patterns
            (r'(\d+)\s*k\b', 1000),  # 100k
            (r'(\d{1,3}(?:,\d{3})+)', 1),  # 100,000
            (r'(\d+)\s*thousand', 1000),
            (r'(\d+)\s*million', 1000000),
            (r'(\d+)\s*laki', 100000),
            (r'(\d+)\s*elfu', 1000),
            
            # Bare numbers (3+ digits)
            (r'\b(\d{3,})\b', 1),
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = int(amount_str) * multiplier
                    if 10 <= amount <= 10000000000:  # Sanity check
                        return amount
                except ValueError:
                    continue
        
        return None
    
    def _detect_goal(self, text: str) -> Optional[str]:
        """Detect financial goal"""
        
        goals = {
            'emergency': [
                r'emergency', r'urgent', r'dharura', r'haraka', r'sudden', r'asap'
            ],
            'business': [
                r'business', r'biashara', r'startup', r'company', r'venture'
            ],
            'education': [
                r'school', r'education', r'fees', r'college', r'university', r'masomo'
            ],
            'property': [
                r'house', r'land', r'plot', r'nyumba', r'shamba', r'property'
            ],
            'wedding': [
                r'wedding', r'harusi', r'marriage', r'marry'
            ],
            'retirement': [
                r'retirement', r'pension', r'old\s*age', r'future'
            ]
        }
        
        for goal, keywords in goals.items():
            for keyword in keywords:
                if re.search(keyword, text):
                    return goal
        
        return None
    
    def _detect_urgency(self, text: str) -> str:
        """Detect timeline urgency"""
        
        if re.search(r'now|today|asap|urgent|immediately|haraka|sasa', text):
            return 'immediate'
        elif re.search(r'soon|months?|weeks?|short', text):
            return 'short_term'
        elif re.search(r'years?|long|eventually|decades?', text):
            return 'long_term'
        
        return 'flexible'
    
    def _calculate_confidence(self, text: str, intent: str) -> float:
        """Calculate confidence score for intent"""
        
        if intent == 'general_query':
            return 0.5
        
        # Count pattern matches
        patterns = self.intent_patterns.get(intent, [])
        matches = sum(1 for pattern in patterns if re.search(pattern, text))
        
        # Confidence based on matches
        if matches >= 3:
            return 0.95
        elif matches == 2:
            return 0.85
        elif matches == 1:
            return 0.70
        
        return 0.60