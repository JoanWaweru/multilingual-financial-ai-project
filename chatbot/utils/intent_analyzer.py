"""
Analyze user intent and extract financial entities
"""

import re
from typing import Dict, Optional

class IntentAnalyzer:
    """Extract intent and entities from user queries"""
    
    def __init__(self):
        # Financial intents with keywords
        self.intent_patterns = {
            'investment_advice': [
                'invest', 'weka', 'akiba', 'save', 'saving', 'kuweka',
                'investment', 'uwekezaji', 'put', 'place', 'wapi', 'where',
                'should i invest', 'where to put', 'where should i'
            ],
            'stock_query': [
                'stock', 'stocks', 'shares', 'nse', 'nairobi securities',
                'equity', 'safaricom', 'buy shares', 'hisa', 'dividend',
                'blue chip', 'ipo', 'portfolio', 'shareholding'
            ],
            'etf_query': [
                'etf', 'etfs', 'index fund', 'mutual fund', 'unit trust',
                'exchange traded', 'vanguard', 'spy', 'tracker fund'
            ],
            'global_stocks_query': [
                'international', 'global', 'us stocks', 'american stocks',
                'nasdaq', 'nyse', 'apple', 'tesla', 'amazon', 'microsoft',
                'foreign stocks', 'overseas', 'wall street', 'google',
                'facebook', 'meta', 'netflix'
            ],
            'broker_query': [
                'broker', 'brokerage', 'which broker', 'best broker',
                'interactive brokers', 'td ameritrade', 'genghis',
                'cds account', 'how to open', 'platform', 'exness'
            ],
            'loan_request': [
                'loan', 'mkopo', 'kopa', 'kukopa', 'borrow', 'lend',
                'credit', 'owe', 'debt', 'nataka mkopo'
            ],
            'mpesa_query': [
                'mpesa', 'm-pesa', 'send', 'tuma', 'kutuma', 'transfer',
                'mobile money', 'safaricom', 'fuliza', 'm-shwari',
                'kutuma pesa'
            ],
            'bank_comparison': [
                'bank', 'benki', 'which bank', 'best bank', 'gani',
                'compare', 'banks', 'bank account'
            ],
            'account_opening': [
                'open account', 'fungua', 'create account', 'register',
                'signup', 'new account', 'fungua account'
            ],
            'balance_check': [
                'balance', 'check', 'angalia', 'how much', 'statement',
                'account balance', 'check balance'
            ],
            'chama_info': [
                'chama', 'group', 'savings group', 'vikundi', 'join',
                'start chama'
            ],
            'sacco_info': [
                'sacco', 'cooperative', 'shares', 'dividends', 'join sacco'
            ]
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze user message for intent and entities
        
        Returns:
            dict with 'intent', 'amount', 'goal', 'urgency'
        """
        
        text_lower = text.lower()
        
        # Detect intent
        intent = self._detect_intent(text_lower)
        
        # Extract amount
        amount = self._extract_amount(text)
        
        # Detect goal/purpose
        goal = self._detect_goal(text_lower)
        
        # Detect urgency
        urgency = self._detect_urgency(text_lower)
        
        return {
            'intent': intent,
            'amount': amount,
            'goal': goal,
            'urgency': urgency,
            'original_text': text
        }
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect primary intent from text
        """
    
        # First check for specific financial terms mentioned
        text_words = text.lower().split()
    
        # Check for ETF mentions specifically
        etf_terms = ['etf', 'etfs']
        if any(term in text.lower() for term in etf_terms):
            return 'etf_query'
    
        # Check for stock mentions
        stock_terms = ['stock', 'stocks', 'shares', 'nse', 'safaricom', 'equity bank']
        if any(term in text.lower() for term in stock_terms):
            return 'stock_query'
    
        # Check for international stock mentions
        intl_terms = ['apple', 'tesla', 'microsoft', 'amazon', 'google', 'international', 'us stock', 'american stock']
        if any(term in text.lower() for term in intl_terms):
            return 'global_stocks_query'
    
        # Now do general scoring for other intents
        scores = {}
    
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text.lower())
        if score > 0:
            scores[intent] = score
    
        if not scores:
            return 'general_query'
    
        # Return intent with highest score
        return max(scores, key=scores.get)
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """Extract monetary amount from text"""
        
        # Patterns for amounts
        patterns = [
            (r'(\d+)k\s*(?:kes|ksh|shillings?|bob)?', 1000),  # 100k KES
            (r'(\d{1,3}(?:,\d{3})*)\s*(?:kes|ksh|shillings?|bob)', 1),  # 100,000 KES
            (r'(?:kes|ksh)\s*(\d+)', 1),  # KES 100000
            (r'(\d+)\s*thousand', 1000),  # 100 thousand
            (r'(\d+)\s*million', 1000000),  # 1 million
            (r'(\d+)\s*laki', 100000),  # 1 laki (100k)
            (r'(\d+)\s*elfu', 1000),  # elfu = thousand in Swahili
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = int(amount_str) * multiplier
                    return amount
                except ValueError:
                    continue
        
        return None
    
    def _detect_goal(self, text: str) -> Optional[str]:
        """Detect financial goal"""
        
        goals = {
            'emergency': ['emergency', 'urgent', 'dharura', 'haraka', 'sudden'],
            'business': ['business', 'biashara', 'company', 'startup', 'start business'],
            'education': ['school', 'education', 'fees', 'college', 'university', 'masomo'],
            'property': ['house', 'land', 'plot', 'nyumba', 'shamba', 'property', 'buy land'],
            'retirement': ['retirement', 'future', 'old age', 'pension', 'retire'],
            'wedding': ['wedding', 'harusi', 'marriage', 'wed'],
            'short_term': ['soon', 'quickly', 'short', 'months', 'haraka'],
            'long_term': ['future', 'years', 'long', 'eventually', 'baadaye']
        }
        
        for goal, keywords in goals.items():
            if any(keyword in text for keyword in keywords):
                return goal
        
        return None
    
    def _detect_urgency(self, text: str) -> str:
        """Detect how soon user needs the money"""
        
        urgent_words = ['now', 'today', 'asap', 'urgent', 'immediately', 'haraka', 'sasa']
        short_term_words = ['soon', 'next month', 'few weeks', 'short', 'months']
        long_term_words = ['future', 'years', 'eventually', 'long term', 'miaka']
        
        if any(word in text for word in urgent_words):
            return 'immediate'
        elif any(word in text for word in short_term_words):
            return 'short_term'
        elif any(word in text for word in long_term_words):
            return 'long_term'
        
        return 'flexible'

if __name__ == "__main__":
    # Test the analyzer
    analyzer = IntentAnalyzer()
    
    test_queries = [
        "niko na 100k KES, niweke pesa wapi?",
        "I have 50k shillings where should I invest?",
        "nina 200,000 bob, nataka kununua plot",
        "got 75k need to save for emergency",
        "want a loan of 100k",
        "how do I send money via mpesa?",
        "can I buy Apple stock from Kenya?",
        "what are ETFs?",
        "which broker is best for NSE stocks?"
    ]
    
    print("\n" + "=" * 60)
    print("TESTING INTENT ANALYZER")
    print("=" * 60)
    
    for query in test_queries:
        result = analyzer.analyze(query)
        print(f"\nQuery: {query}")
        print(f"  Intent: {result['intent']}")
        print(f"  Amount: {result['amount']}")
        print(f"  Goal: {result['goal']}")
        print(f"  Urgency: {result['urgency']}")