from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from typing import List, Dict, Optional
import random
import logging

from config.settings import CHATBOT_CONFIG, MODELS_DIR

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generate code-switched financial responses"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        logger.info(f"Using device: {self.device}")
        
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name).to(self.device)
            
            # Set pad token
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id
            
            logger.info(f"✓ Loaded model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
        
        # Financial response templates
        self.templates = {
            "savings": [
                "To save money effectively, {advice}. Kama wanavyosema, akiba haiozi!",
                "Savings ni muhimu sana. {advice}. Start small, even 500 KES helps.",
                "Here's a savings tip: {advice}. Consistency is key!"
            ],
            "investment": [
                "For investment, {advice}. Remember: usifte mayai yako kwenye kikapu kimoja!",
                "Investment strategy: {advice}. Diversification ni muhimu.",
                "Consider this investment approach: {advice}. Think long-term!"
            ],
            "budget": [
                "Budgeting tips: {advice}. Track kila expense to understand your spending.",
                "For better budget management: {advice}. Use the 50/30/20 rule.",
                "Budget advice: {advice}. Discipline inaleta freedom!"
            ],
            "mpesa": [
                "About M-Pesa: {advice}. It's safe na convenient for daily transactions.",
                "M-Pesa tips: {advice}. Always confirm details kabla ya sending pesa.",
                "Using mobile money: {advice}. Keep your PIN secret!"
            ]
        }
    
    def generate_response(self, user_message: str, context: List[str] = None, 
                         code_switching_level: str = "balanced") -> str:
        """Generate response with code-switching"""
        
        if context is None:
            context = []
        
        # Check for template-based responses first
        template_response = self.get_template_response(user_message)
        if template_response:
            return self.apply_code_switching(template_response, code_switching_level)
        
        try:
            # Build conversation history
            conversation = context + [user_message]
            input_text = " ".join(conversation[-CHATBOT_CONFIG['max_history']:])
            
            # Encode
            input_ids = self.tokenizer.encode(
                input_text + self.tokenizer.eos_token, 
                return_tensors='pt'
            ).to(self.device)
            
            # Generate with sampling
            with torch.no_grad():
                output = self.model.generate(
                    input_ids,
                    max_length=min(input_ids.shape[1] + CHATBOT_CONFIG['response_max_length'], 512),
                    temperature=CHATBOT_CONFIG['temperature'],
                    top_p=0.9,
                    top_k=50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3
                )
            
            # Decode
            response = self.tokenizer.decode(
                output[0][input_ids.shape[1]:], 
                skip_special_tokens=True
            )
            
            # Apply code-switching
            response = self.apply_code_switching(response, code_switching_level)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self.get_fallback_response(user_message)
    
    def get_template_response(self, message: str) -> Optional[str]:
        """Get template-based response for common queries"""
        message_lower = message.lower()
        
        # Detect topic and generate appropriate response
        if any(word in message_lower for word in ['save', 'saving', 'akiba']):
            advice = random.choice([
                "start by setting aside at least 10% of your income",
                "automate your savings through standing orders",
                "join a chama or savings group for accountability"
            ])
            return random.choice(self.templates['savings']).format(advice=advice)
        
        elif any(word in message_lower for word in ['invest', 'investment', 'uwekezaji', 'hisa']):
            advice = random.choice([
                "consider index funds for steady long-term growth",
                "start with government bonds if you're risk-averse",
                "diversify across stocks, bonds, and real estate"
            ])
            return random.choice(self.templates['investment']).format(advice=advice)
        
        elif any(word in message_lower for word in ['budget', 'bajeti', 'plan']):
            advice = random.choice([
                "list all income sources and expenses",
                "use the 50/30/20 rule: 50% needs, 30% wants, 20% savings",
                "track every shilling for at least one month"
            ])
            return random.choice(self.templates['budget']).format(advice=advice)
        
        elif any(word in message_lower for word in ['mpesa', 'm-pesa', 'mobile money']):
            advice = random.choice([
                "use M-Pesa for quick transfers but watch the transaction fees",
                "link your M-Pesa to a savings account for better interest",
                "always verify recipient details before sending money"
            ])
            return random.choice(self.templates['mpesa']).format(advice=advice)
        
        return None
    
    def apply_code_switching(self, text: str, level: str = "balanced") -> str:
        """Apply code-switching patterns to text"""
        
        # Swahili translations for financial terms
        translations = {
            'money': 'pesa',
            'savings': 'akiba',
            'save': 'hifadhi',
            'loan': 'mkopo',
            'budget': 'bajeti',
            'business': 'biashara',
            'bank': 'benki',
            'investment': 'uwekezaji',
            'invest': 'wekeza',
            'income': 'mapato',
            'expense': 'matumizi',
            'profit': 'faida',
            'loss': 'hasara',
            'interest': 'riba',
            'account': 'akaunti'
        }
        
        # Swahili connectors and fillers
        connectors = {
            'and': 'na',
            'or': 'au',
            'but': 'lakini',
            'also': 'pia',
            'very': 'sana',
            'just': 'tu',
            'only': 'tu'
        }
        
        words = text.split()
        switched_words = []
        
        for word in words:
            word_lower = word.lower().strip('.,!?')
            
            if level == "high":
                # More Swahili mixing
                if word_lower in translations and random.random() > 0.3:
                    switched_words.append(translations[word_lower])
                elif word_lower in connectors and random.random() > 0.4:
                    switched_words.append(connectors[word_lower])
                else:
                    switched_words.append(word)
            
            elif level == "balanced":
                # Balanced mixing
                if word_lower in translations and random.random() > 0.6:
                    switched_words.append(translations[word_lower])
                elif word_lower in connectors and random.random() > 0.7:
                    switched_words.append(connectors[word_lower])
                else:
                    switched_words.append(word)
            
            else:  # level == "low"
                # Minimal mixing - just occasional Swahili
                if word_lower in translations and random.random() > 0.85:
                    switched_words.append(translations[word_lower])
                else:
                    switched_words.append(word)
        
        return " ".join(switched_words)
    
    def get_fallback_response(self, message: str) -> str:
        """Fallback response when generation fails"""
        fallbacks = [
            "That's an interesting question about pesa! Could you tell me more?",
            "I understand you're asking about finances. Let me help - can you be more specific?",
            "Pole, I didn't quite get that. Could you rephrase your question about savings, investment, or budgeting?",
            "Interesting! Tell me more about what financial topic you'd like to discuss."
        ]
        return random.choice(fallbacks)

if __name__ == "__main__":
    # Test the generator
    generator = ResponseGenerator()
    
    test_messages = [
        "How can I save money?",
        "Tell me about investment",
        "I want to create a budget",
        "What is M-Pesa?"
    ]
    
    print("\n" + "="*70)
    print("TESTING RESPONSE GENERATOR")
    print("="*70)
    
    for msg in test_messages:
        print(f"\nUser: {msg}")
        response = generator.generate_response(msg, code_switching_level="balanced")
        print(f"Bot: {response}")