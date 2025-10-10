"""
Adaptive response generator with code-switching
"""

import random
from chatbot.knowledge.kenyan_phrases import KenyanPhrases

class ResponseGenerator:
    """Generate responses with adaptive code-switching"""
    
    def __init__(self):
        self.phrases = KenyanPhrases()
        
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
                         include_proverb=False):
        """
        Generate response matching user's language pattern
        
        Args:
            knowledge_result: Dict with 'answer', 'category', etc.
            user_language_pattern: Dict with 'label' and 'swahili_ratio'
            include_proverb: Whether to add a proverb
        
        Returns:
            str: Generated response
        """
        
        if not knowledge_result:
            return self._generate_fallback_response(user_language_pattern)
        
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
            return self.phrases.get_transition()  # "Sawa," "Poa,"
        elif swahili_ratio < 0.3:
            return random.choice(['Okay,', 'Alright,', 'Sure,'])
        else:
            return self.phrases.get_transition()
    
    def _adapt_language(self, text, language_pattern):
        """
        Adapt response language to match user's pattern
        
        Simple approach: Mix in Swahili terms based on user's ratio
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        label = language_pattern.get('label', 'english')
        
        # If user speaks mostly Swahili or code-switches, add Swahili terms
        if swahili_ratio > 0.4 or label == 'code_switched':
            # Replace some English terms with Swahili
            for eng, sw in self.swahili_terms.items():
                if random.random() < swahili_ratio:
                    # Replace first occurrence
                    text = text.replace(eng, sw, 1)
        
        return text
    
    def _generate_fallback_response(self, language_pattern):
        """Generate fallback when no knowledge match found"""
    
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
    
        if swahili_ratio > 0.6:
            responses = [
            "Pole, sina information hiyo saa hii. But I can help with savings, M-Pesa, loans, chamas, na banking. Try asking about those topics! 😊",
            "Samahani, sijui about that topic yet. Lakini I know about akiba, M-Pesa, mikopo, chamas na banks. Ask me about those!",
            "Nimeskia swali lako, but sina answer for that. I can help with savings, loans, M-Pesa, and chamas though. What would you like to know about those?"
        ]
        elif swahili_ratio < 0.3:
            responses = [
            "I don't have that information yet, but I can help with savings, M-Pesa, loans, chamas, and banking. What would you like to know about those topics? 😊",
            "I'm still learning about that topic! But I'm great with questions about savings, M-Pesa, loans, and chamas. Try asking about those!",
            "That's a great question, but I don't have that answer yet. I can help with savings accounts, M-Pesa, loans, chamas, and SACCOs though. Interested in any of those?"
        ]
        else:
            responses = [
            "Pole, I don't have that info yet. But I can help na savings, M-Pesa, loans, chamas, and banking. What would you like to know? 😊",
            "Samahani, sina answer ya that question. Lakini I know about akiba, M-Pesa, loans, and banks. Ask me something about those!",
            "Good question! But sina that information. I can help with savings, M-Pesa, mikopo, chamas na banking though. Try asking about those topics!"
        ]
    
        return random.choice(responses)
    
    def generate_welcome_message(self):
        """Generate welcome message"""
        
        return """Habari! Welcome to the Kenyan Financial Advisor chatbot. 🇰🇪

I can help you with:
💰 Savings and akiba
📱 M-Pesa and mobile money
🏦 Banking and bank accounts
💵 Loans and mikopo
👥 Chamas and SACCOs
📊 Budgeting and planning

Feel free to ask in English, Swahili, or mix them (code-switching)! 

What would you like to know? 😊"""

if __name__ == "__main__":
    # Test response generator
    generator = ResponseGenerator()
    
    print("\n" + "=" * 60)
    print("TESTING RESPONSE GENERATOR")
    print("=" * 60)
    
    # Test with different language patterns
    test_cases = [
        {
            'knowledge': {
                'answer': 'You can save money by opening a bank account at Equity or KCB.',
                'category': 'savings'
            },
            'pattern': {
                'label': 'code_switched',
                'swahili_ratio': 0.6
            }
        },
        {
            'knowledge': {
                'answer': 'M-Pesa allows you to send money using your phone.',
                'category': 'mpesa'
            },
            'pattern': {
                'label': 'english',
                'swahili_ratio': 0.2
            }
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Pattern: {case['pattern']['label']}, Swahili: {case['pattern']['swahili_ratio']:.0%}")
        response = generator.generate_response(
            case['knowledge'],
            case['pattern'],
            include_proverb=True
        )
        print(f"  Response: {response}")