"""
Main chatbot class integrating all components
"""

from chatbot.models.cs_detector import CodeSwitchingDetector
from chatbot.knowledge.financial_kb import FinancialKnowledgeBase
from chatbot.response_generator import ResponseGenerator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KenyanFinancialChatbot:
    """Multilingual financial chatbot for Kenya"""
    
    def __init__(self, model_path="saved_models/best_model.pt"):
        """Initialize chatbot"""
        
        logger.info("Initializing Kenyan Financial Chatbot...")
        
        # Load components
        self.cs_detector = CodeSwitchingDetector(model_path)
        self.knowledge_base = FinancialKnowledgeBase()
        self.response_generator = ResponseGenerator()
        
        # Conversation history
        self.history = []
        
        logger.info("✓ Chatbot ready!")
    
    def chat(self, user_message):
        """
        Process user message and generate response
        
        Args:
            user_message: User's input text
        
        Returns:
            dict with 'response', 'detected_language', 'confidence'
        """
        
        # 1. Detect code-switching pattern
        cs_result = self.cs_detector.detect(user_message)
        swahili_ratio = self.cs_detector.get_language_ratio(user_message)
        
        language_pattern = {
            'label': cs_result['label'],
            'swahili_ratio': swahili_ratio,
            'confidence': cs_result['confidence']
        }
        
        # 2. Search knowledge base
        knowledge_results = self.knowledge_base.search(user_message, top_k=1)
        
        best_match = knowledge_results[0] if knowledge_results else None
        
        # 3. Generate response
        response_text = self.response_generator.generate_response(
            best_match,
            language_pattern,
            include_proverb=(best_match is not None and best_match['score'] > 0.3)
        )
        
        # 4. Save to history
        self.history.append({
            'user': user_message,
            'bot': response_text,
            'language': cs_result['label'],
            'confidence': cs_result['confidence']
        })
        
        return {
            'response': response_text,
            'detected_language': cs_result['label'],
            'confidence': cs_result['confidence'],
            'swahili_ratio': swahili_ratio,
            'knowledge_match': best_match['question'] if best_match else None,
            'match_score': best_match['score'] if best_match else 0.0
        }
    
    def get_welcome_message(self):
        """Get welcome message"""
        return self.response_generator.generate_welcome_message()
    
    def get_history(self):
        """Get conversation history"""
        return self.history
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []

if __name__ == "__main__":
    # Test the chatbot
    print("\n" + "=" * 70)
    print(" 🤖 KENYAN FINANCIAL CHATBOT - TEST")
    print("=" * 70)
    
    chatbot = KenyanFinancialChatbot()
    
    print(chatbot.get_welcome_message())
    
    test_messages = [
        "How do I save money?",
        "Ninataka kuweka pesa kwa benki",
        "What is a chama?",
        "Nataka kukopa pesa, how can I get a loan?",
        "Tell me about M-Pesa"
    ]
    
    print("\n" + "=" * 70)
    print(" 💬 TEST CONVERSATIONS")
    print("=" * 70)
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        
        result = chatbot.chat(msg)
        
        print(f"🤖 Bot: {result['response']}")
        print(f"   [Detected: {result['detected_language']}, "
              f"Confidence: {result['confidence']:.2%}, "
              f"Swahili: {result['swahili_ratio']:.0%}]")