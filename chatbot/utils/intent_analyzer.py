"""
Enhanced Intent Analyzer
Extracts user intent and financial entities from queries
Handles English, Swahili, and code-switched text
"""

import re
from typing import Dict, Optional

class IntentAnalyzer:
    """
    Analyze user intent and extract financial entities
    
    Features:
    - Multi-intent detection
    - Amount extraction (multiple formats)
    - Goal identification
    - Urgency detection
    - Code-switching support (English/Swahili)
    """
    
    def __init__(self):
        """Initialize with comprehensive intent patterns"""
        
        # Financial intents with keywords (ordered by priority)
        self.intent_patterns = {
            # MMF-specific queries (high priority)
            'mmf_query': [
                'mmf', 'money market fund', 'money market', 'best mmf',
                'which mmf', 'mmf rates', 'money market rates',
                'sanlam', 'cic money', 'britam money', 'old mutual money',
                'mmf interest', 'compare mmf'
            ],
            
            # Stock recommendations (specific)
            'stock_recommendation': [
                'which stocks', 'which shares', 'recommend', 'what stocks',
                'what shares', 'advice me', 'suggest', 'best stocks',
                'good stocks', 'stocks to buy', 'shares to buy', 'buy today',
                'top stocks', 'stock picks', 'share recommendations',
                'which stock', 'buy which', 'recommend stocks'
            ],
            
            # General stock queries
            'stock_query': [
                'stock', 'stocks', 'shares', 'nse', 'nairobi securities',
                'equity', 'safaricom', 'hisa', 'dividend', 'blue chip',
                'ipo', 'portfolio', 'how to buy stocks', 'buying stocks',
                'stock market', 'share price'
            ],
            
            # ETF queries
            'etf_query': [
                'etf', 'etfs', 'index fund', 'mutual fund', 'unit trust',
                'exchange traded', 'vanguard', 'spy', 'tracker fund',
                'etf ni nini', 'what are etfs', 'invest in etf'
            ],
            
            # Global/international stocks
            'global_stocks_query': [
                'international stocks', 'global stocks', 'us stocks', 'american stocks',
                'nasdaq', 'nyse', 'apple stock', 'tesla stock', 'amazon', 'microsoft',
                'foreign stocks', 'overseas stocks', 'wall street', 'google stock',
                'facebook', 'meta', 'netflix', 'buy apple', 'buy tesla'
            ],
            
            # Broker queries
            'broker_query': [
                'broker', 'brokerage', 'which broker', 'best broker',
                'interactive brokers', 'td ameritrade', 'genghis',
                'cds account', 'how to open', 'platform', 'exness',
                'stockbroker', 'hisa app'
            ],
            
            # Investment advice (broad)
            'investment_advice': [
                'invest', 'weka', 'akiba', 'save', 'saving', 'kuweka',
                'investment', 'uwekezaji', 'put', 'place', 'wapi', 'where',
                'should i invest', 'where to put', 'where should i',
                'best investment', 'invest wapi', 'niweke wapi'
            ],
            
            # Loan requests
            'loan_request': [
                'loan', 'mkopo', 'kopa', 'kukopa', 'borrow', 'lend',
                'credit', 'owe', 'debt', 'nataka mkopo', 'need loan',
                'get loan', 'apply loan'
            ],
            
            # M-Pesa queries
            'mpesa_query': [
                'mpesa', 'm-pesa', 'send', 'tuma', 'kutuma', 'transfer',
                'mobile money', 'safaricom', 'fuliza', 'm-shwari',
                'kutuma pesa', 'mpesa charges', 'send money'
            ],
            
            # Banking queries
            'bank_comparison': [
                'bank', 'benki', 'which bank', 'best bank', 'gani',
                'compare', 'banks', 'bank account', 'open account',
                'good bank', 'reliable bank'
            ],
            
            # Account opening
            'account_opening': [
                'open account', 'fungua', 'create account', 'register',
                'signup', 'new account', 'fungua account', 'start account'
            ],
            
            # Balance checking
            'balance_check': [
                'balance', 'check', 'angalia', 'how much', 'statement',
                'account balance', 'check balance', 'my balance'
            ],
            
            # Chama information
            'chama_info': [
                'chama', 'group', 'savings group', 'vikundi', 'join',
                'start chama', 'chama savings', 'group savings'
            ],
            
            # SACCO information
            'sacco_info': [
                'sacco', 'cooperative', 'shares', 'dividends', 'join sacco',
                'sacco account', 'cooperative bank'
            ],
            
            # Treasury Bills/Bonds
            'treasury_query': [
                'treasury', 't-bill', 't-bills', 'treasury bill', 'treasury bond',
                'government bond', 'cbk', 'central bank', 'treasury rates'
            ]
        }
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze user message for intent and entities
        
        Args:
            text: User's message
        
        Returns:
            dict: {
                'intent': str,
                'amount': int or None,
                'goal': str or None,
                'urgency': str
            }
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
        
        Uses scoring system to find best match
        """
        
        scores = {}
        
        # Score each intent
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return 'general_query'
        
        # Return intent with highest score
        return max(scores, key=scores.get)
    
    def _extract_amount(self, text: str) -> Optional[int]:
        """
        Extract monetary amount from text
        
        Handles multiple formats:
        - "100k" → 100,000
        - "100,000" → 100,000
        - "100 thousand" → 100,000
        - "niko na 50k" → 50,000
        - "1 laki" → 100,000
        """
        
        # Patterns for amounts (order matters!)
        patterns = [
            # Code-switching patterns (highest priority)
            (r'(?:niko|nina|i have|got)\s+(?:na\s+)?(\d+)k(?:\s*(?:kes|ksh|shillings?|bob))?', 1000),
            (r'(?:niko|nina|i have|got)\s+(?:na\s+)?(\d{1,3}(?:,\d{3})*)(?:\s*(?:kes|ksh|shillings?|bob))?', 1),
            
            # Standard patterns
            (r'(\d+)k\s*(?:kes|ksh|shillings?|bob)?', 1000),  # 100k KES
            (r'(\d{1,3}(?:,\d{3})*)\s*(?:kes|ksh|shillings?|bob)', 1),  # 100,000 KES
            (r'(?:kes|ksh)\s*(\d{1,3}(?:,\d{3})*)', 1),  # KES 100000
            (r'(\d+)\s*thousand', 1000),  # 100 thousand
            (r'(\d+)\s*million', 1000000),  # 1 million
            (r'(\d+)\s*laki', 100000),  # 1 laki (100k)
            (r'(\d+)\s*elfu', 1000),  # elfu = thousand in Swahili
            
            # Bare numbers (last resort - only if 3+ digits)
            (r'\b(\d{3,})\b', 1),  # Any 3+ digit number
        ]
        
        for pattern, multiplier in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = int(amount_str) * multiplier
                    
                    # Sanity check (10 to 10 billion KES)
                    if 10 <= amount <= 10000000000:
                        return amount
                except ValueError:
                    continue
        
        return None
    
    def _detect_goal(self, text: str) -> Optional[str]:
        """
        Detect financial goal/purpose
        
        Goals:
        - emergency: Urgent needs
        - business: Start/grow business
        - education: School fees
        - property: Buy land/house
        - retirement: Long-term savings
        - wedding: Marriage expenses
        - short_term: Near future (months)
        - long_term: Distant future (years)
        """
        
        goals = {
            'emergency': [
                'emergency', 'urgent', 'dharura', 'haraka', 'sudden',
                'asap', 'quickly', 'sasa hivi', 'immediately'
            ],
            'business': [
                'business', 'biashara', 'company', 'startup', 'start business',
                'kazi', 'enterprise', 'venture', 'store', 'shop'
            ],
            'education': [
                'school', 'education', 'fees', 'college', 'university', 'masomo',
                'tuition', '学校', 'campus', 'course', 'study'
            ],
            'property': [
                'house', 'land', 'plot', 'nyumba', 'shamba', 'property',
                'buy land', 'real estate', 'home', 'apartment', 'flat'
            ],
            'retirement': [
                'retirement', 'future', 'old age', 'pension', 'retire',
                'long term', 'baadaye', 'later', 'future security'
            ],
            'wedding': [
                'wedding', 'harusi', 'marriage', 'wed', 'marry',
                'bride', 'groom', 'ceremony'
            ],
            'short_term': [
                'soon', 'quickly', 'short', 'months', 'haraka',
                'few months', 'this year', 'near future'
            ],
            'long_term': [
                'future', 'years', 'long', 'eventually', 'baadaye',
                'decades', 'long term', 'far future'
            ]
        }
        
        for goal, keywords in goals.items():
            if any(keyword in text for keyword in keywords):
                return goal
        
        return None
    
    def _detect_urgency(self, text: str) -> str:
        """
        Detect timeline urgency
        
        Returns:
        - 'immediate': Need money now
        - 'short_term': Need in weeks/months
        - 'long_term': Need in years
        - 'flexible': No specific timeline
        """
        
        urgent_words = [
            'now', 'today', 'asap', 'urgent', 'immediately', 
            'haraka', 'sasa', 'sasa hivi', 'right now'
        ]
        
        short_term_words = [
            'soon', 'next month', 'few weeks', 'short', 'months',
            'this year', 'miezi', 'wiki'
        ]
        
        long_term_words = [
            'future', 'years', 'eventually', 'long term', 'miaka',
            'baadaye', 'decades', 'retirement'
        ]
        
        if any(word in text for word in urgent_words):
            return 'immediate'
        elif any(word in text for word in short_term_words):
            return 'short_term'
        elif any(word in text for word in long_term_words):
            return 'long_term'
        
        return 'flexible'

# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🔍 TESTING INTENT ANALYZER")
    print("="*70)
    
    analyzer = IntentAnalyzer()
    
    test_queries = [
        # Amount extraction tests
        "niko na 100k KES, niweke pesa wapi?",
        "I have 50k shillings where should I invest?",
        "nina 200,000 bob, nataka kununua plot",
        "got 75k need to save for emergency",
        
        # Intent detection tests
        "which MMF has the best rates?",
        "want a loan of 100k",
        "how do I send money via mpesa?",
        "can I buy Apple stock from Kenya?",
        "what are ETFs?",
        "which broker is best for NSE stocks?",
        "I have 100k, invest in one place",
        
        # Goal detection
        "I want to save for my wedding next year",
        "need money urgently for school fees",
        "looking to buy land in 5 years",
        
        # Edge cases
        "option 1",
        "treasury bills ni nini?",
        "compare SACCOs and banks"
    ]
    
    print("\nTEST RESULTS:")
    print("="*70)
    
    for query in test_queries:
        result = analyzer.analyze(query)
        
        print(f"\n📝 Query: {query}")
        print(f"   Intent: {result['intent']}")
        amount_str = f"KSh {result['amount']:,}" if result['amount'] else 'None'
        print(f"   Amount: {amount_str}")
        print(f"   Goal: {result['goal'] or 'None'}")
        print(f"   Urgency: {result['urgency']}")
    
    print("\n" + "="*70)
    print("✓ Intent Analyzer Test Complete!")