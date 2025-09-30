import torch
from typing import List, Dict, Optional
import logging
from datetime import datetime
import random

from chatbot.response_generator import ResponseGenerator
from chatbot.cultural_knowledge import CulturalKnowledgeBase

try:
    from models.code_switching_detector import BERTCodeSwitchingDetector, CodeSwitchingTrainer
except ImportError:
    BERTCodeSwitchingDetector = None
    CodeSwitchingTrainer = None

from config.settings import CHATBOT_CONFIG, MODELS_DIR

logger = logging.getLogger(__name__)

class MultilingualFinancialChatbot:
    """Main chatbot engine with code-switching capabilities"""
    
    def __init__(self):
        logger.info("Initializing Multilingual Financial Chatbot...")
        
        self.response_generator = ResponseGenerator()
        self.cultural_kb = CulturalKnowledgeBase()
        self.conversation_history = []
        self.user_profile = {
            'preferred_language_mix': 'balanced',
            'topics_discussed': [],
            'experience_level': 'beginner',
            'country': None
        }
        
        # Load code-switching detector if available
        self.cs_detector = None
        self.load_cs_detector()
        
        # Financial topic keywords
        self.topic_keywords = {
            "savings": ["save", "saving", "savings", "akiba", "kuweka", "hifadhi", "account", "deposit"],
            "investment": ["invest", "investment", "stock", "hisa", "uwekezaji", "shares", "bond", "portfolio", "dividends"],
            "budget": ["budget", "budgeting", "bajeti", "mpango", "planning", "expense", "matumizi", "track"],
            "loan": ["loan", "borrow", "mkopo", "credit", "debt", "deni", "owe", "interest", "riba"],
            "mpesa": ["mpesa", "m-pesa", "mobile money", "send money", "tuma pesa", "airtel money", "mtn"],
            "business": ["business", "biashara", "entrepreneur", "startup", "mfanyabiashara", "company"],
            "chama": ["chama", "group saving", "table banking", "merry-go-round", "investment club", "sacco"],
            "insurance": ["insurance", "bima", "cover", "policy", "protection", "life insurance", "health insurance"]
        }
        
        logger.info("✓ Chatbot initialized successfully")
    
    def load_cs_detector(self):
        """Load trained code-switching detector if available"""
        if BERTCodeSwitchingDetector is None:
            logger.warning("Code-switching detector not available")
            return
        
        try:
            model = BERTCodeSwitchingDetector(n_classes=2)
            trainer = CodeSwitchingTrainer(model)
            model_path = MODELS_DIR / 'best_model.pt'
            
            if model_path.exists():
                trainer.load_model('best_model.pt')
                self.cs_detector = trainer
                logger.info("✓ Code-switching detector loaded")
            else:
                logger.warning("Code-switching model not found. Chatbot will work without it.")
        except Exception as e:
            logger.warning(f"Could not load CS detector: {e}")
    
    def detect_topic(self, message: str) -> Optional[str]:
        """Detect financial topic from message"""
        message_lower = message.lower()
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return None
    
    def detect_user_preference(self, message: str) -> str:
        """Detect user's code-switching preference from their message"""
        message_lower = message.lower()
        
        # Swahili indicators
        swahili_indicators = [
            'pesa', 'sana', 'na', 'ni', 'ya', 'kwa', 'tu', 'za',
            'akiba', 'mkopo', 'bajeti', 'biashara', 'lakini', 'pia',
            'fedha', 'benki', 'uwekezaji', 'faida', 'hasara'
        ]
        
        words = message_lower.split()
        if len(words) == 0:
            return "balanced"
        
        swahili_count = sum(1 for word in words if word in swahili_indicators)
        swahili_ratio = swahili_count / len(words)
        
        if swahili_ratio > 0.3:
            return "high"
        elif swahili_ratio > 0.1:
            return "balanced"
        else:
            return "low"
    
    def detect_country(self, message: str) -> Optional[str]:
        """Detect country from user message"""
        message_lower = message.lower()
        
        country_indicators = {
            "Kenya": ["kenya", "kenyan", "nairobi", "mombasa", "kes", "ksh", "nse"],
            "Uganda": ["uganda", "ugandan", "kampala", "ugx", "use"],
            "Tanzania": ["tanzania", "tanzanian", "dar es salaam", "tzs", "dse"],
            "Rwanda": ["rwanda", "rwandan", "kigali", "rwf", "rse"]
        }
        
        for country, indicators in country_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                return country
        
        return None
    
    def chat(self, user_message: str) -> str:
        """Main chat method - processes user input and generates response"""
        logger.info(f"User: {user_message}")
        
        # Update user profile
        self.update_user_profile(user_message)
        
        # Detect topic and user preference
        topic = self.detect_topic(user_message)
        cs_preference = self.detect_user_preference(user_message)
        
        logger.info(f"Detected - Topic: {topic}, CS preference: {cs_preference}")
        
        # Check for specific intents first
        response = self.handle_specific_intents(user_message, topic)
        
        if not response:
            # Generate response using AI
            response = self.response_generator.generate_response(
                user_message,
                context=self.conversation_history[-CHATBOT_CONFIG['max_history']:],
                code_switching_level=cs_preference
            )
            
            # Enhance with cultural context
            if topic and random.random() > 0.5:  # 50% chance to add proverb
                response = self.cultural_kb.enhance_response_with_culture(
                    response, topic, add_proverb=True
                )
        
        # Update history
        self.conversation_history.append(user_message)
        self.conversation_history.append(response)
        
        logger.info(f"Bot: {response[:100]}...")
        
        return response
    
    def handle_specific_intents(self, message: str, topic: Optional[str]) -> Optional[str]:
        """Handle specific user intents with predefined high-quality responses"""
        message_lower = message.lower()
        
        # === GREETINGS ===
        greetings = ['hello', 'hi', 'hey', 'habari', 'mambo', 'sasa', 'niaje', 'good morning', 'good evening', 'jambo']
        if any(greeting in message_lower.split() for greeting in greetings):
            return self.cultural_kb.get_contextual_greeting()
        
        # === HELP REQUEST ===
        help_keywords = ['help', 'assist', 'saidia', 'msaada', 'what can you do', 'how do you work']
        if any(keyword in message_lower for keyword in help_keywords):
            return (
                "Karibu! I can help you with:\n\n"
                "💰 **Savings** (Akiba) - How to save money effectively\n"
                "📈 **Investment** (Uwekezaji) - Where and how to invest\n"
                "📊 **Budgeting** (Bajeti) - Managing your pesa wisely\n"
                "💳 **M-Pesa & Mobile Money** - Digital finance tips\n"
                "🏦 **Banking** - Account types, loans, services\n"
                "🤝 **Chamas & Groups** - Traditional savings groups\n"
                "🏢 **Business** (Biashara) - Small business finance\n"
                "📋 **Insurance** (Bima) - Protection and coverage\n\n"
                "Just ask me anything! For example:\n"
                "• 'How can I save money?'\n"
                "• 'Explain chama to me'\n"
                "• 'I want to start investing'\n"
                "• 'Nisaidie na bajeti'"
            )
        
        # === TRADITIONAL CONCEPTS ===
        if 'chama' in message_lower and any(word in message_lower for word in ['what', 'explain', 'ni nini', 'tell me']):
            return self.cultural_kb.explain_traditional_concept('chama')
        
        if 'harambee' in message_lower and any(word in message_lower for word in ['what', 'explain', 'ni nini', 'tell me']):
            return self.cultural_kb.explain_traditional_concept('harambee')
        
        if 'table banking' in message_lower:
            return self.cultural_kb.explain_traditional_concept('table banking')
        
        if 'merry-go-round' in message_lower or 'merry go round' in message_lower:
            return self.cultural_kb.explain_traditional_concept('merry-go-round')
        
        # === COUNTRY-SPECIFIC INFO ===
        country = self.detect_country(message)
        if country and any(word in message_lower for word in ['invest', 'bank', 'stock', 'exchange']):
            country_info = self.cultural_kb.get_country_info(country)
            if country_info:
                return (
                    f"**Financial Information for {country}:**\n\n"
                    f"💱 Currency: {country_info['currency']}\n"
                    f"📱 Mobile Money: {country_info['mobile_money']}\n"
                    f"📊 Stock Exchange: {country_info['stock_exchange']}\n"
                    f"🏦 Popular Banks: {country_info['popular_banks']}\n"
                    f"💰 Savings Options: {country_info['savings_options']}\n\n"
                    f"💡 Tip: {country_info['investment_tip']}"
                )
        
        # === TOPIC-SPECIFIC RESPONSES ===
        if topic == "savings":
            tip = self.cultural_kb.get_financial_tip("beginner")
            proverb = self.cultural_kb.get_proverb("savings")
            return (
                f"**Savings Tips:**\n\n{tip}\n\n"
                f"Here are practical steps:\n"
                f"1. **Open separate account** - Weka pesa mbali from spending account\n"
                f"2. **Automate savings** - Standing order or auto-transfer\n"
                f"3. **Start small** - Even 500 KES weekly = 26,000 KES yearly!\n"
                f"4. **Join a chama** - Accountability na peer support\n"
                f"5. **Track progress** - Celebrate milestones\n\n"
                f"💡 *{proverb}*"
            )
        
        if topic == "investment":
            level = self.user_profile['experience_level']
            tip = self.cultural_kb.get_financial_tip(level)
            return (
                f"**Investment Guidance:**\n\n{tip}\n\n"
                f"For beginners in East Africa:\n"
                f"• **Government Bonds** - Safe, 10-14% returns\n"
                f"• **Money Market Funds** - Liquid, 8-12% returns\n"
                f"• **Stock Market** (NSE/USE/DSE) - Higher risk/reward\n"
                f"• **SACCOs** - Community investment with dividends\n"
                f"• **Real Estate** - Long-term wealth building\n\n"
                f"💡 Remember: Usifte mayai yako kwenye kikapu kimoja! Diversify your investments."
            )
        
        if topic == "budget":
            return (
                f"**Budgeting Made Simple:**\n\n"
                f"1. **Track expenses** - Record kila kitu for 1 month\n"
                f"2. **Use 50/30/20 rule**:\n"
                f"   • 50% - Needs (rent, food, bills)\n"
                f"   • 30% - Wants (entertainment, shopping)\n"
                f"   • 20% - Savings & debt repayment\n\n"
                f"3. **Cash envelope method** - Physical cash for categories\n"
                f"4. **Review weekly** - Adjust as needed\n"
                f"5. **Use apps** - M-Pesa statement, budgeting apps\n\n"
                f"💡 Discipline inaleta freedom! Start today, even with small amounts."
            )
        
        if topic == "mpesa":
            return (
                f"**M-Pesa Smart Tips:**\n\n"
                f"💰 **Save on fees**:\n"
                f"   • Bank transfer cheaper for large amounts\n"
                f"   • Agent withdrawal cheaper than ATM\n"
                f"   • Bundle transactions to reduce fees\n\n"
                f"🔒 **Security**:\n"
                f"   • Never share PIN with anyone\n"
                f"   • Confirm recipient details always\n"
                f"   • Set transaction limits\n\n"
                f"📊 **Grow money**:\n"
                f"   • M-Shwari/KCB M-Pesa for savings (interest)\n"
                f"   • M-Pesa to bank for better rates\n\n"
                f"⚡ **Instant loans**: Use M-Pesa regularly to qualify for higher limits\n\n"
                f"M-Pesa ni safe na convenient - tumia wisely!"
            )
        
        if topic == "loan":
            return (
                f"**Smart Borrowing Guide:**\n\n"
                f"⚠️ **Before taking a loan:**\n"
                f"1. Calculate total cost (principal + interest + fees)\n"
                f"2. Ensure monthly payment < 30% of income\n"
                f"3. Have repayment plan\n"
                f"4. Compare rates from different sources\n\n"
                f"💡 **Best loan sources:**\n"
                f"• **SACCOs** - Lowest rates (10-12% annually)\n"
                f"• **Banks** - Medium rates (13-20% annually)\n"
                f"• **Microfinance** - Higher but accessible (18-25%)\n"
                f"• **Mobile apps** - Quick but expensive (15-30%)\n\n"
                f"🚫 **Avoid**: Shylocks and unregistered lenders\n\n"
                f"Mkopo ni rahisi kuchukua lakini hard kulipa. Borrow wisely!"
            )
        
        if topic == "business":
            return (
                f"**Starting a Business:**\n\n"
                f"1. **Start small** - Test idea without huge capital\n"
                f"2. **Keep records** - Separate business na personal pesa\n"
                f"3. **Understand market** - Who are your customers?\n"
                f"4. **Reinvest profits** - Don't eat all the profits early\n"
                f"5. **Build relationships** - Customer loyalty ni key\n\n"
                f"💡 **Funding options:**\n"
                f"• Personal savings (best option)\n"
                f"• Chama or group funding\n"
                f"• Youth/Women Enterprise Fund\n"
                f"• Bank SME loans\n"
                f"• Angel investors for tech startups\n\n"
                f"Biashara ni marathon, sio sprint. Patience na consistency!"
            )
        
        if topic == "chama":
            return (
                f"**Chama Guide:**\n\n"
                f"{self.cultural_kb.explain_traditional_concept('chama')}\n\n"
                f"**Tips for starting/joining:**\n"
                f"1. Choose trusted members (10-30 people ideal)\n"
                f"2. Set clear rules - contributions, meetings, loans\n"
                f"3. Keep good records - treasurer na secretary\n"
                f"4. Meet regularly - weekly or monthly\n"
                f"5. Start investment projects together\n\n"
                f"💡 Chamas work because of trust na accountability. Choose members wisely!"
            )
        
        if topic == "insurance":
            return (
                f"**Insurance Basics:**\n\n"
                f"**Why you need bima:**\n"
                f"• Protects against unexpected costs\n"
                f"• Peace of mind for you na family\n"
                f"• Some are mandatory (car insurance, NHIF)\n\n"
                f"**Types to consider:**\n"
                f"1. **Health Insurance** - Medical costs are expensive\n"
                f"2. **Life Insurance** - Protect your dependents\n"
                f"3. **Car Insurance** - Third party is mandatory\n"
                f"4. **Home/Property** - Protect your assets\n\n"
                f"💡 **Start with**: NHIF (mandatory), then add private health cover if you can afford.\n\n"
                f"Insurance ni investment in protection, not expense!"
            )
        
        # === EMERGENCY / URGENT ===
        if any(word in message_lower for word in ['emergency', 'urgent', 'help now', 'dharura', 'haraka']):
            return (
                f"🚨 **Emergency Financial Help:**\n\n"
                f"If you need quick funds:\n"
                f"1. **M-Shwari/KCB M-Pesa** - Instant loan if you qualify\n"
                f"2. **Chama/Family** - Ask trusted circle first\n"
                f"3. **SACCO loan** - If you're a member\n"
                f"4. **Employer advance** - Request salary advance\n"
                f"5. **Sell assets** - Non-essential items\n\n"
                f"⚠️ **Avoid**: Loan sharks na shylocks - their interest is too high!\n\n"
                f"**For future**: Build 3-6 month emergency fund to avoid panic borrowing."
            )
        
        # === GRATITUDE ===
        thanks = ['thank', 'asante', 'shukran', 'thanks', 'appreciate', 'hongera']
        if any(word in message_lower for word in thanks):
            encouragement = self.cultural_kb.get_encouragement()
            return f"You're welcome! {encouragement}"
        
        # === GOODBYE ===
        farewells = ['bye', 'goodbye', 'kwaheri', 'see you', 'tutaonana', 'later']
        if any(word in message_lower for word in farewells):
            return random.choice([
                "Kwaheri! Keep saving na investing. You're doing great! 💪",
                "Goodbye! Remember: Akiba haiozi. Stay financially wise! 💰",
                "See you! Continue building your wealth. Kwa heri! 🚀",
                "Tutaonana! Keep up the good financial habits. Hongera! 🎯"
            ])
        
        return None
    
    def update_user_profile(self, message: str):
        """Update user profile based on conversation"""
        # Update topics discussed
        topic = self.detect_topic(message)
        if topic and topic not in self.user_profile['topics_discussed']:
            self.user_profile['topics_discussed'].append(topic)
        
        # Update language preference
        preference = self.detect_user_preference(message)
        self.user_profile['preferred_language_mix'] = preference
        
        # Update country if detected
        country = self.detect_country(message)
        if country:
            self.user_profile['country'] = country
        
        # Infer experience level
        advanced_terms = [
            'portfolio', 'diversification', 'bonds', 'equity', 'dividends', 
            'compound interest', 'capital gains', 'asset allocation', 'roi',
            'derivatives', 'hedge', 'etf', 'reit'
        ]
        intermediate_terms = [
            'investment', 'stocks', 'mutual fund', 'interest rate', 
            'savings account', 'fixed deposit', 'unit trust'
        ]
        
        if any(term in message.lower() for term in advanced_terms):
            self.user_profile['experience_level'] = 'advanced'
        elif any(term in message.lower() for term in intermediate_terms):
            if self.user_profile['experience_level'] == 'beginner':
                self.user_profile['experience_level'] = 'intermediate'
        
        # Update based on conversation length
        if len(self.user_profile['topics_discussed']) > 5:
            if self.user_profile['experience_level'] == 'beginner':
                self.user_profile['experience_level'] = 'intermediate'
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.user_profile = {
            'preferred_language_mix': 'balanced',
            'topics_discussed': [],
            'experience_level': 'beginner',
            'country': None
        }
        logger.info("Conversation reset")
    
    def get_conversation_stats(self) -> Dict:
        """Get statistics about the conversation"""
        if not self.conversation_history:
            return {
                "messages": 0,
                "topics_discussed": [],
                "language_preference": "balanced",
                "experience_level": "beginner"
            }
        
        user_messages = self.conversation_history[::2]
        bot_responses = self.conversation_history[1::2]
        
        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len(user_messages),
            "bot_responses": len(bot_responses),
            "topics_discussed": self.user_profile['topics_discussed'],
            "language_preference": self.user_profile['preferred_language_mix'],
            "experience_level": self.user_profile['experience_level'],
            "country": self.user_profile['country'],
            "avg_user_length": sum(len(msg.split()) for msg in user_messages) / len(user_messages) if user_messages else 0,
            "avg_bot_length": sum(len(msg.split()) for msg in bot_responses) / len(bot_responses) if bot_responses else 0
        }
    
    def get_personalized_tip(self) -> str:
        """Get personalized tip based on user profile"""
        level = self.user_profile['experience_level']
        return self.cultural_kb.get_financial_tip(level)
    
    def get_next_topic_suggestion(self) -> str:
        """Suggest next topic based on conversation"""
        discussed = set(self.user_profile['topics_discussed'])
        all_topics = set(self.topic_keywords.keys())
        not_discussed = all_topics - discussed
        
        if not_discussed:
            topic = random.choice(list(not_discussed))
            suggestions = {
                "savings": "Would you like to learn about effective savings strategies?",
                "investment": "Shall we discuss investment opportunities?",
                "budget": "Want help creating a budget?",
                "loan": "Need information about loans na borrowing?",
                "mpesa": "Interested in M-Pesa tips and tricks?",
                "business": "Thinking about starting a biashara?",
                "chama": "Want to know more about chamas?",
                "insurance": "Should we talk about insurance protection?"
            }
            return suggestions.get(topic, "What else would you like to know?")
        
        return "You've covered many topics! Any specific area you'd like to dive deeper into?"

if __name__ == "__main__":
    # Initialize chatbot
    chatbot = MultilingualFinancialChatbot()
    
    print("\n" + "="*70)
    print("MULTILINGUAL FINANCIAL CHATBOT")
    print("East African Code-Switching Assistant")
    print("="*70)
    print("Commands:")
    print("  'quit' or 'exit' - Exit chatbot")
    print("  'reset' - Start new conversation")
    print("  'stats' - Show conversation statistics")
    print("  'tip' - Get personalized financial tip")
    print("  'suggest' - Get topic suggestion")
    print("="*70 + "\n")
    
    # Welcome message
    print(f"Bot: {chatbot.cultural_kb.get_contextual_greeting()}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print(f"\nBot: {chatbot.cultural_kb.get_encouragement()}")
                print("Asante sana! Kwaheri! 👋\n")
                break
            
            if user_input.lower() == 'reset':
                chatbot.reset_conversation()
                print("\n✓ Conversation reset. Let's start fresh!")
                print(f"Bot: {chatbot.cultural_kb.get_contextual_greeting()}\n")
                continue
            
            if user_input.lower() == 'stats':
                stats = chatbot.get_conversation_stats()
                print("\n📊 Conversation Statistics:")
                print(f"  Total messages: {stats['total_messages']}")
                print(f"  Topics discussed: {', '.join(stats['topics_discussed']) if stats['topics_discussed'] else 'None yet'}")
                print(f"  Language preference: {stats['language_preference']}")
                print(f"  Experience level: {stats['experience_level']}")
                if stats['country']:
                    print(f"  Country: {stats['country']}")
                print()
                continue
            
            if user_input.lower() == 'tip':
                tip = chatbot.get_personalized_tip()
                print(f"\n💡 {tip}\n")
                continue
            
            if user_input.lower() == 'suggest':
                suggestion = chatbot.get_next_topic_suggestion()
                print(f"\nBot: {suggestion}\n")
                continue
            
            # Get response
            response = chatbot.chat(user_input)
            print(f"\nBot: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nAsante! Kwaheri! 👋\n")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}", exc_info=True)
            print(f"\nPole! An error occurred: {str(e)}")
            print("Please try again or type 'reset' to start over.\n")