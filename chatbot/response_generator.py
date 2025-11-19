"""
Adaptive response generator with code-switching and intelligent fallback
"""

import sys
from pathlib import Path
import random

# Fix imports
try:
    from chatbot.knowledge.kenyan_phrases import KenyanPhrases
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor
except ModuleNotFoundError:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    from chatbot.knowledge.kenyan_phrases import KenyanPhrases
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor

class ResponseGenerator:
    """Generate responses with adaptive code-switching"""
    
    def __init__(self):
        self.phrases = KenyanPhrases()
        self.intent_analyzer = IntentAnalyzer()
        self.advisor = DynamicFinancialAdvisor()
        
        # Swahili financial terms
        self.swahili_terms = {
            'money': 'pesa',
            'bank': 'benki',
            'save': 'weka',
            'savings': 'akiba',
            'loan': 'mkopo',
            'account': 'akaunti',
            'investment': 'uwekezaji',
            'budget': 'bajeti',
            'payment': 'malipo',
            'interest': 'riba'
        }
    
    def generate_response(self, knowledge_result, user_language_pattern, 
                         include_proverb=False, user_query=None):
        """
        Generate response matching user's language pattern
        
        Args:
            knowledge_result: Dict with 'answer', 'category', etc.
            user_language_pattern: Dict with 'label' and 'swahili_ratio'
            include_proverb: Whether to add a proverb
            user_query: Original user question (for intelligent fallback)
        
        Returns:
            str: Generated response
        """
        
        if not knowledge_result:
            return self._generate_fallback_response(user_language_pattern, user_query)
        
        # Start with greeting/transition
        response = self._add_greeting(user_language_pattern)
        
        # Get base answer
        base_answer = knowledge_result['answer']
        
        # Adapt answer based on user's language pattern
        adapted_answer = self._adapt_language(
            base_answer,
            user_language_pattern
        )
        
        response += " " + adapted_answer
        
        # Add encouragement
        if random.random() < 0.5:
            response += f" {self.phrases.get_encouragement()}"
        
        # Add proverb if requested
        if include_proverb and random.random() < 0.7:
            proverb = self.phrases.get_random_proverb()
            response += f"\n\n💡 Remember: \"{proverb['swahili']}\" ({proverb['english']}) - {proverb['meaning']}"
        
        return response
    
    def _add_greeting(self, language_pattern):
        """Add appropriate greeting based on language pattern"""
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        if swahili_ratio > 0.6:
            return self.phrases.get_transition()
        elif swahili_ratio < 0.3:
            return random.choice(['Okay,', 'Alright,', 'Sure,'])
        else:
            return self.phrases.get_transition()
    
    def _adapt_language(self, text, language_pattern):
        """Adapt response language to match user's pattern"""
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        label = language_pattern.get('label', 'english')
        
        # If user speaks mostly Swahili or code-switches, add Swahili terms
        if swahili_ratio > 0.4 or label == 'code_switched':
            for eng, sw in self.swahili_terms.items():
                if random.random() < swahili_ratio and eng in text.lower():
                    text = text.replace(eng, sw, 1)
        
        return text
    
    def _generate_fallback_response(self, language_pattern, user_query=None):
        """Generate intelligent fallback with context-aware advice"""
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        greeting = self.phrases.get_transition() if swahili_ratio > 0.5 else "Alright,"
        
        if user_query:
            analysis = self.intent_analyzer.analyze(user_query)
            
            # Handle investment advice
            if analysis['intent'] == 'investment_advice':
                advice = self.advisor.generate_investment_advice(
                    amount=analysis['amount'],
                    goal=analysis['goal'],
                    urgency=analysis['urgency'],
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"
            
            # Handle stock queries
            elif analysis['intent'] == 'stock_query':
                advice = self.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market='nse',
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"
            
            # Handle ETF queries
            elif analysis['intent'] == 'etf_query':
                if swahili_ratio > 0.5:
                    return f"{greeting} ETFs (Exchange Traded Funds) ni baskets za stocks unazinunua kama investment moja. Instead of buying individual stocks, you get pieces of many companies at once!\n\n**Benefits:** Diversification (spread risk), lower fees, trade like stocks.\n\n**In Kenya:** Limited local ETFs (like NewGold), but you can access US ETFs (S&P 500, Vanguard) through international brokers like Interactive Brokers. **Minimum:** $100-500 (~KSh 15k-75k).\n\n**Easier alternative:** Try local unit trusts (CIC, Sanlam) - similar concept, easier to access from Kenya!"
                else:
                    return f"{greeting} ETFs (Exchange Traded Funds) are baskets of stocks you buy as one investment. Instead of buying individual stocks, you get instant exposure to many companies!\n\n**Benefits:** Instant diversification, lower fees than mutual funds, trade like stocks.\n\n**In Kenya:** We have limited local ETFs (like NewGold ETF), but you can access global ETFs through international brokers:\n- **S&P 500 ETFs** (SPY, VOO) - 500 US companies\n- **Total market ETFs** (VTI) - entire US market\n- **International ETFs** - global markets\n\n**Requirements:** International broker account (Interactive Brokers), minimum $100-500. **Easier alternative:** Local unit trusts (CIC, Sanlam, Old Mutual) work similarly and are easier to access!"
            
            # Handle global stocks
            elif analysis['intent'] == 'global_stocks_query':
                advice = self.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market='international',
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"
            
            # Handle broker queries
            elif analysis['intent'] == 'broker_query':
                if swahili_ratio > 0.5:
                    return f"{greeting} For NSE: Use Hisa app (easiest, start with KSh 100), or traditional brokers (Genghis Capital, Dyer & Blair). For US/international stocks: Interactive Brokers (most popular with Kenyans), TD Ameritrade, Exness. Wire fees: KSh 3k-5k."
                else:
                    return f"{greeting} For NSE stocks: Hisa app is easiest (minimum KSh 100), or use brokers like Genghis Capital, Sterling, Dyer & Blair. For international: Interactive Brokers (most popular), TD Ameritrade, or Exness. Expect wire fees of KSh 3k-5k."
            
            # Handle loan requests
            elif analysis['intent'] == 'loan_request':
                if swahili_ratio > 0.5:
                    return f"{greeting} Kuhusu mikopo! You can get loans from: 1) SACCOs (cheap, 10-12% interest), 2) Banks (need good credit), 3) Mobile apps (Tala, Branch, M-Shwari - fast but expensive). Qualify faster by: saving regularly, paying bills on time. How much do you need?"
                else:
                    return f"{greeting} About loans! Options: 1) SACCOs (affordable, 10-12% interest), 2) Banks (need good credit), 3) Mobile apps (Tala, Branch, M-Shwari - quick but expensive). Build credit by saving regularly. How much are you looking for?"
            
            # Handle M-Pesa queries
            elif analysis['intent'] == 'mpesa_query':
                if swahili_ratio > 0.5:
                    return f"{greeting} Kuhusu M-Pesa! To send money: Dial *334#, select Send Money, enter number na amount. To check balance: *334# then My Account. To borrow: Try M-Shwari or Fuliza. Charges start from KSh 11. What specifically do you need help with?"
                else:
                    return f"{greeting} About M-Pesa! To send: Dial *334#, select Send Money, enter number and amount. To check balance: *334# then My Account. For loans: Try M-Shwari or Fuliza. Charges start at KSh 11. What do you need help with?"
            
            # Handle chama queries
            elif analysis['intent'] == 'chama_info':
                if swahili_ratio > 0.5:
                    return f"{greeting} About chamas! A chama is a savings group where friends contribute monthly (like KSh 5,000 each) and members take turns receiving the pooled money. Great for buying land, starting business. To start: gather 5-15 people, agree on amount, choose leaders. Very popular in Kenya!"
                else:
                    return f"{greeting} About chamas! A chama is a savings group where members contribute regularly and take turns receiving pooled funds. Great for achieving goals like buying land or starting business. To start: gather 5-15 trusted people and agree on contribution amounts!"
            
            # Handle banking queries
            elif analysis['intent'] == 'bank_comparison':
                if swahili_ratio > 0.5:
                    return f"{greeting} About banks! Popular: Equity (low fees), KCB (many branches), Co-op (SACCO-friendly), NCBA (good app). To open account: Go with ID, deposit KSh 100-1000. Some let you open via app!"
                else:
                    return f"{greeting} About banking! Top banks: Equity (low fees, accessible), KCB (nationwide branches), Co-op (great for groups), NCBA (strong digital). To open account: Visit with ID and deposit KSh 100-1000. Some allow mobile registration!"
            
            # Handle SACCO queries
            elif analysis['intent'] == 'sacco_info':
                if swahili_ratio > 0.5:
                    return f"{greeting} About SACCOs! They're member-owned cooperatives offering: savings (8-12% interest), cheap loans (10-12%), dividends. Popular: Stima, Mwalimu, Kenya Police. To join: Pay registration (KSh 500-1k), buy shares (KSh 5k-10k), start saving. After 6 months, qualify for loans!"
                else:
                    return f"{greeting} About SACCOs! They offer: high interest savings (8-12%), affordable loans (10-12%), and dividends. Popular ones: Stima, Mwalimu, Kenya Police. To join: Pay registration (KSh 500-1k), buy shares (KSh 5k-10k). You qualify for loans after 6 months!"
        
        # Generic fallback
        if swahili_ratio > 0.6:
            return "Pole, nisaidie na details zaidi. What specifically do you want to know? Stocks? Savings? M-Pesa? Loans? How much pesa do you have? 😊"
        elif swahili_ratio < 0.3:
            return "I'd love to help! What specifically would you like to know? Stocks, savings, M-Pesa, loans, chamas? How much money are you working with? 😊"
        else:
            return "Pole, nisaidie with more details. What do you want to know? Stocks, savings, M-Pesa, loans? How much pesa are you working with? 😊"
    
    def generate_welcome_message(self):
        """Generate welcome message"""
        
        return """Habari! Welcome to the Kenyan Financial Advisor chatbot. 🇰🇪

I can help you with:
💰 Savings and akiba
📱 M-Pesa and mobile money
🏦 Banking and bank accounts
💵 Loans and mikopo
👥 Chamas and SACCOs
📈 Stocks, ETFs, and investments
📊 Budgeting and planning

Feel free to ask in English, Swahili, or mix them (code-switching)! 

What would you like to know? 😊"""

if __name__ == "__main__":
    # Test response generator
    generator = ResponseGenerator()
    
    print("\n" + "=" * 60)
    print("TESTING RESPONSE GENERATOR")
    print("=" * 60)
    
    print("\n" + generator.generate_welcome_message())
    
    # Test fallback with different queries
    test_queries = [
        ("niko na 100k, niweke wapi?", {'label': 'code_switched', 'swahili_ratio': 0.6}),
        ("How do I buy Apple stock?", {'label': 'english', 'swahili_ratio': 0.1}),
        ("What are ETFs?", {'label': 'english', 'swahili_ratio': 0.0})
    ]
    
    for query, pattern in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Pattern: {pattern}")
        print(f"{'='*60}")
        
        response = generator._generate_fallback_response(pattern, query)
        print(response)