"""
Production-Grade Kenyan Financial Chatbot
Complete conversational AI with live data and context awareness
"""

import sys
from pathlib import Path
import logging

# Fix imports
try:
    from chatbot.models.cs_detector import CodeSwitchingDetector
    from chatbot.knowledge.financial_kb import FinancialKnowledgeBase
    from chatbot.response_generator import ResponseGenerator
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.market_data import MarketDataFetcher
    from chatbot.utils.market_analyzer import MarketAnalyzer
    from chatbot.utils.context_manager import ConversationContext
except ModuleNotFoundError:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    from chatbot.models.cs_detector import CodeSwitchingDetector
    from chatbot.knowledge.financial_kb import FinancialKnowledgeBase
    from chatbot.response_generator import ResponseGenerator
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.market_data import MarketDataFetcher
    from chatbot.utils.market_analyzer import MarketAnalyzer
    from chatbot.utils.context_manager import ConversationContext

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KenyanFinancialChatbot:
    """
    Production-Grade Conversational Financial Chatbot
    
    Features:
    ✅ Code-switching detection (English/Swahili)
    ✅ Real-time market data (NSE, T-Bills, MMFs, Global)
    ✅ Conversational context tracking
    ✅ Natural dialogue flow
    ✅ User preference learning
    ✅ Follow-up question handling
    ✅ Option selection
    ✅ Affirmation handling (yes/no)
    ✅ Short query interpretation
    ✅ Intent-based routing
    """
    
    def __init__(self, model_path="saved_models/best_model.pt", use_live_data=True):
        """
        Initialize complete chatbot system
        
        Args:
            model_path: Path to CS detection model
            use_live_data: Enable real-time market data
        """
        
        logger.info("="*70)
        logger.info("🚀 INITIALIZING KENYAN FINANCIAL CHATBOT")
        logger.info("="*70)
        
        # Core NLP components
        logger.info("Loading NLP components...")
        self.cs_detector = CodeSwitchingDetector(model_path)
        self.knowledge_base = FinancialKnowledgeBase(use_bitext=False)
        self.response_generator = ResponseGenerator()
        self.intent_analyzer = IntentAnalyzer()
        
        # Conversation tracking
        self.context = ConversationContext()
        logger.info("✓ Conversation context initialized")
        
        # Real-time data components
        self.use_live_data = use_live_data
        if use_live_data:
            try:
                self.market_fetcher = MarketDataFetcher()
                self.market_analyzer = MarketAnalyzer()
                logger.info("✓ Live market data ENABLED")
            except Exception as e:
                logger.warning(f"⚠ Live data unavailable: {e}")
                logger.info("  Falling back to static mode")
                self.use_live_data = False
        else:
            logger.info("ℹ Live data DISABLED (static mode)")
        
        # Conversation history
        self.history = []
        
        logger.info("="*70)
        logger.info("✓ CHATBOT READY!")
        logger.info(f"  Mode: {'🔴 LIVE DATA' if self.use_live_data else '📚 STATIC'}")
        logger.info(f"  Model: {model_path}")
        logger.info("="*70)
    
    def chat(self, user_message: str) -> dict:
        """
        Process user message with full conversational intelligence
        
        This is the MAIN ENTRY POINT - handles everything
        
        Flow:
        1. Detect language (code-switching)
        2. Analyze intent with context
        3. Check for conversational patterns (yes/no, options, follow-ups)
        4. Fetch live data if needed
        5. Generate context-aware response
        6. Update conversation state
        7. Return rich response
        
        Args:
            user_message: User's input
        
        Returns:
            dict: Complete response with metadata
        """
        
        logger.info("")
        logger.info("="*70)
        logger.info(f"💬 USER: {user_message}")
        logger.info("="*70)
        
        # ====================================================================
        # STEP 1: DETECT CODE-SWITCHING
        # ====================================================================
        cs_result = self.cs_detector.detect(user_message)
        swahili_ratio = self.cs_detector.get_language_ratio(user_message)
        
        language_pattern = {
            'label': cs_result['label'],
            'swahili_ratio': swahili_ratio,
            'confidence': cs_result['confidence']
        }
        
        logger.info(f"🌐 Language: {cs_result['label']} (Swahili: {swahili_ratio:.0%})")
        
        # ====================================================================
        # STEP 2: ANALYZE INTENT WITH CONTEXT
        # ====================================================================
        analysis = self.intent_analyzer.analyze(user_message, self.context)
        
        logger.info(f"🎯 Intent: {analysis['intent']} (confidence: {analysis['confidence']:.0%})")
        if analysis['amount']:
            logger.info(f"💰 Amount: KSh {analysis['amount']:,}")
        if analysis['goal']:
            logger.info(f"🎨 Goal: {analysis['goal']}")
        if analysis['is_follow_up']:
            logger.info(f"🔗 Detected as follow-up query")
        
        # ====================================================================
        # STEP 3: FETCH LIVE DATA (if needed)
        # ====================================================================
        live_data = None
        
        if self.use_live_data and self._needs_live_data(analysis['intent']):
            logger.info("📊 Fetching live market data...")
            live_data = self._fetch_relevant_live_data(analysis['intent'], analysis['amount'])
            
            if live_data:
                logger.info("✓ Live data fetched")
            else:
                logger.warning("⚠ Live data fetch failed")
        
        # ====================================================================
        # STEP 4: CHECK FOR CONVERSATIONAL PATTERNS FIRST
        # This is what makes it truly conversational!
        # ====================================================================
        
        conversational_response = self.response_generator.generate_conversational_response(
            user_message,
            analysis,
            self.context,
            live_data,
            language_pattern
        )
        
        if conversational_response:
            # Conversational pattern detected!
            logger.info("💬 Using conversational response (context-aware)")
            response_text = conversational_response
            best_match = None
            match_score = 0.0
            used_live = live_data is not None
        
        # ====================================================================
        # STEP 5: AMOUNT-BASED ROUTING (Investment/Stock Advice)
        # ====================================================================
        elif analysis['amount'] is not None:
            logger.info(f"💵 Amount-based query: KSh {analysis['amount']:,}")
            
            # Route based on intent
            if analysis['intent'] in ['stock_query', 'stock_recommendation', 'global_stocks_query']:
                logger.info("📈 Routing to stock advisor")
                market = 'international' if analysis['intent'] == 'global_stocks_query' else 'nse'
                
                response_text = self.response_generator.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market=market,
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
            else:
                logger.info("💰 Routing to investment advisor")
                
                response_text = self.response_generator.advisor.generate_investment_advice(
                    amount=analysis['amount'],
                    goal=analysis['goal'],
                    urgency=analysis['urgency'],
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
            
            # Add greeting
            greeting = self.response_generator._add_greeting(language_pattern)
            response_text = f"{greeting} {response_text}"
            
            best_match = None
            match_score = 0.0
            used_live = live_data is not None
            
            # Save investment context
            if live_data and live_data.get('nse_analysis', {}).get('allocation'):
                self.context.save_investment_context(
                    analysis['amount'],
                    live_data['nse_analysis']['allocation']
                )
            else:
                self.context.save_investment_context(analysis['amount'], {})
        
        # ====================================================================
        # STEP 6: KNOWLEDGE BASE SEARCH (General Questions)
        # ====================================================================
        else:
            logger.info("📚 Searching knowledge base...")
            
            knowledge_results = self.knowledge_base.search(
                user_message,
                top_k=3,
                threshold=0.20
            )
            
            best_match = None
            if knowledge_results:
                top_result = knowledge_results[0]
                
                if top_result['score'] >= 0.30:
                    best_match = top_result
                    logger.info(f"✓ KB Match: {best_match['question'][:50]}... (score: {best_match['score']:.3f})")
                else:
                    logger.info(f"⚠ Low KB score ({top_result['score']:.3f}), using fallback")
            else:
                logger.info("⚠ No KB matches")
            
            match_score = best_match['score'] if best_match else 0.0
            
            # Generate response
            response_text = self.response_generator.generate_response(
                best_match,
                language_pattern,
                include_proverb=(best_match is not None and match_score > 0.40),
                user_query=user_message,
                live_data=live_data,
                context=self.context
            )
            
            used_live = live_data is not None and best_match is None
        
        # ====================================================================
        # STEP 7: ADD LIVE DATA SNIPPET (if relevant)
        # ====================================================================
        if live_data and self._should_add_live_update(analysis['intent']):
            market_update = self._generate_market_update(live_data)
            if market_update:
                response_text += f"\n\n{market_update}"
        
        # ====================================================================
        # STEP 8: UPDATE CONVERSATION CONTEXT
        # ====================================================================
        metadata = {
            'intent': analysis['intent'],
            'amount': analysis['amount'],
            'goal': analysis['goal'],
            'live_data_used': used_live
        }
        
        self.context.add_exchange(
            user_message,
            response_text,
            analysis['intent'],
            metadata
        )
        
        # ====================================================================
        # STEP 9: SAVE TO HISTORY
        # ====================================================================
        self.history.append({
            'user': user_message,
            'bot': response_text,
            'language': cs_result['label'],
            'confidence': cs_result['confidence'],
            'used_live_data': used_live,
            'intent': analysis['intent'],
            'amount': analysis['amount']
        })
        
        logger.info(f"✓ Response generated ({len(response_text)} chars)")
        logger.info("="*70)
        
        # ====================================================================
        # STEP 10: RETURN COMPLETE RESPONSE
        # ====================================================================
        return {
            'response': response_text,
            'detected_language': cs_result['label'],
            'confidence': cs_result['confidence'],
            'swahili_ratio': swahili_ratio,
            'knowledge_match': best_match['question'] if best_match else None,
            'match_score': match_score,
            'used_live_data': used_live,
            'intent': analysis['intent'],
            'user_preferences': self.context.get_user_preference_summary(),
            'conversation_state': self.context.state
        }
    
    def _needs_live_data(self, intent: str) -> bool:
        """Check if intent requires live data"""
        
        live_data_intents = [
            'investment_advice',
            'stock_query',
            'stock_recommendation',
            'global_stocks_query',
            'etf_query',
            'mmf_query',
            'treasury_query',
            'broker_query'
        ]
        
        return intent in live_data_intents
    
    def _fetch_relevant_live_data(self, intent: str, amount: int = None) -> dict:
        """
        Fetch relevant live data based on intent
        
        Smart fetching - only gets what's needed
        """
        
        try:
            live_data = {}
            
            # Always get market summary (lightweight)
            live_data['market_summary'] = self.market_fetcher.get_market_summary()
            
            # NSE data for stock/investment queries
            if intent in ['stock_query', 'stock_recommendation', 'investment_advice']:
                logger.info("  → Fetching NSE stocks...")
                nse_stocks = self.market_fetcher.get_nse_stocks()
                
                live_data['nse_analysis'] = self.market_analyzer.analyze_nse_stocks(
                    nse_stocks,
                    amount=amount
                )
                
                logger.info(f"  ✓ NSE: {len(nse_stocks)} stocks")
            
            # Investment data for investment queries
            if intent in ['investment_advice', 'mmf_query', 'treasury_query']:
                logger.info("  → Fetching investment data...")
                
                # MMF rates
                mmf_rates = self.market_fetcher.get_mmf_rates()
                live_data['mmf_analysis'] = self.market_analyzer.compare_mmfs(mmf_rates)
                live_data['mmf_rates'] = mmf_rates
                
                # Treasury rates
                treasury = self.market_fetcher.get_treasury_rates()
                live_data['treasury_rates'] = treasury
                
                logger.info("  ✓ MMF + Treasury rates")
            
            # Forex for global queries
            if intent in ['global_stocks_query', 'etf_query']:
                logger.info("  → Fetching forex...")
                live_data['forex_rate'] = self.market_fetcher.get_forex_rate('USD/KES')
                logger.info("  ✓ Forex rates")
            
            return live_data
        
        except Exception as e:
            logger.error(f"❌ Error fetching live data: {e}")
            return None
    
    def _should_add_live_update(self, intent: str) -> bool:
        """Check if should add market update snippet"""
        
        update_intents = [
            'stock_query',
            'stock_recommendation',
            'investment_advice',
            'etf_query'
        ]
        
        return intent in update_intents
    
    def _generate_market_update(self, live_data: dict) -> str:
        """Generate brief market update snippet"""
        
        if not live_data:
            return ""
        
        update_parts = []
        
        # Market sentiment
        market_summary = live_data.get('market_summary')
        if market_summary:
            emoji = market_summary.get('emoji', '➡️')
            sentiment = market_summary.get('sentiment', 'NEUTRAL')
            avg_change = market_summary.get('avg_change', 0)
            
            update_parts.append(f"📊 Live Update: NSE is {emoji} {sentiment} today (Avg: {avg_change:+.1f}%)")
        
        # Top MMF
        mmf_analysis = live_data.get('mmf_analysis', {})
        best_mmf = mmf_analysis.get('best')
        if best_mmf:
            update_parts.append(f"💰 Top MMF now: {best_mmf['name']} ({best_mmf['rate']}%)")
        
        return " ".join(update_parts) if update_parts else ""
    
    def get_welcome_message(self):
        """Get welcome message"""
        return self.response_generator.generate_welcome_message()
    
    def get_history(self):
        """Get conversation history"""
        return self.history
    
    def clear_history(self):
        """Clear conversation history and context"""
        self.history = []
        self.context.clear_context()
        logger.info("🗑️ History and context cleared")
    
    def get_market_status(self):
        """Get current market status"""
        
        if not self.use_live_data:
            return "📚 Static Mode"
        
        try:
            summary = self.market_fetcher.get_market_summary()
            return f"{summary['emoji']} {summary['sentiment']} - Gainers: {summary['gainers']}, Losers: {summary['losers']}"
        except:
            return "Market data unavailable"
    
    def get_conversation_context(self):
        """Get current conversation context (for debugging)"""
        
        return {
            'user_preferences': self.context.user_preferences,
            'last_topic': self.context.last_topic,
            'conversation_length': len(self.context.conversation_history),
            'last_amount': self.context.last_amount,
            'state': self.context.state,
            'preference_summary': self.context.get_user_preference_summary()
        }
    
    def close(self):
        """Clean up resources"""
        
        if self.use_live_data:
            try:
                self.market_fetcher.close()
                logger.info("✓ Market fetcher closed")
            except:
                pass
        
        logger.info("✓ Chatbot closed")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🤖 PRODUCTION KENYAN FINANCIAL CHATBOT")
    print("="*70)
    
    # Initialize
    chatbot = KenyanFinancialChatbot(use_live_data=True)
    
    # Welcome
    print(f"\n{chatbot.get_welcome_message()}")
    print(f"\n📊 Market Status: {chatbot.get_market_status()}")
    
    # Test conversations
    test_conversations = [
        # Conversation 1: Investment with disagreement
        {
            'name': 'Investment with Single Place Preference',
            'messages': [
                "niko na 100k, niweke wapi?",
                "in one place",
                "option 1 inabamba",
                "yes"
            ]
        },
        
        # Conversation 2: Bank query
        {
            'name': 'Bank Comparison',
            'messages': [
                "bank gani mzuri kuweka pesa",
                "equity ama kcb?",
                "how do I open account?"
            ]
        },
        
        # Conversation 3: MMF query
        {
            'name': 'MMF Query',
            'messages': [
                "which MMF has best rates?",
                "I have 50k",
                "how much will I get after 1 year?"
            ]
        },
        
        # Conversation 4: Short follow-ups
        {
            'name': 'Short Follow-ups',
            'messages': [
                "niko na pesa, invest wapi?",
                "75k",
                "option 2",
                "yes"
            ]
        }
    ]
    
    print("\n" + "="*70)
    print(" 💬 TESTING CONVERSATIONS")
    print("="*70)
    
    for conv_num, conversation in enumerate(test_conversations, 1):
        print(f"\n{'='*70}")
        print(f" CONVERSATION {conv_num}: {conversation['name']}")
        print(f"{'='*70}")
        
        for msg in conversation['messages']:
            print(f"\n👤 You: {msg}")
            print(f"{'-'*70}")
            
            result = chatbot.chat(msg)
            
            print(f"🤖 Bot: {result['response']}")
            print(f"\n📊 Meta:")
            print(f"   Language: {result['detected_language']} ({result['swahili_ratio']:.0%} Swahili)")
            print(f"   Intent: {result['intent']}")
            print(f"   Live: {'✓' if result['used_live_data'] else '✗'}")
            print(f"   State: {result['conversation_state']}")
            print(f"   Prefs: {result['user_preferences']}")
        
        # Clear between conversations
        chatbot.clear_history()
        print(f"\n{'='*70}")
        print(" [History cleared]")
    
    # Final stats
    print("\n" + "="*70)
    print(" 📈 SESSION COMPLETE")
    print("="*70)
    
    chatbot.close()
    print("\n✓ All tests complete!")