"""
Enhanced Conversational Kenyan Financial Chatbot
With real-time data, context awareness, and natural dialogue
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KenyanFinancialChatbot:
    """
    Enhanced Conversational Financial Chatbot
    
    Features:
    - Code-switching detection (English/Swahili)
    - Real-time market data (NSE, T-Bills, MMFs, Global stocks)
    - Conversational context tracking
    - Natural dialogue flow
    - User preference learning
    - Follow-up question handling
    """
    
    def __init__(self, model_path="saved_models/best_model.pt", use_live_data=True):
        """
        Initialize chatbot with all components
        
        Args:
            model_path: Path to trained CS detection model
            use_live_data: Enable real-time market data (default: True)
        """
        
        logger.info("🚀 Initializing Enhanced Conversational Financial Chatbot...")
        
        # Core NLP components
        self.cs_detector = CodeSwitchingDetector(model_path)
        self.knowledge_base = FinancialKnowledgeBase(use_bitext=False)
        self.response_generator = ResponseGenerator()
        self.intent_analyzer = IntentAnalyzer()
        
        # Conversation tracking
        self.context = ConversationContext()
        
        # Real-time data components
        self.use_live_data = use_live_data
        if use_live_data:
            try:
                self.market_fetcher = MarketDataFetcher()
                self.market_analyzer = MarketAnalyzer()
                logger.info("✓ Real-time market data ENABLED")
            except Exception as e:
                logger.warning(f"⚠ Real-time data unavailable: {e}")
                logger.info("  Falling back to static mode")
                self.use_live_data = False
        
        # Conversation history
        self.history = []
        
        logger.info("✓ Chatbot ready!")
        logger.info(f"  Mode: {'Live Data' if self.use_live_data else 'Static'}")
        logger.info(f"  Model: {model_path}")
    
    def chat(self, user_message):
        """
        Process user message with conversational awareness
        
        This is the main entry point for chat interactions.
        It handles:
        1. Language detection
        2. Intent analysis
        3. Context tracking
        4. Conversational flow
        5. Live data integration
        6. Response generation
        
        Args:
            user_message: User's input text
        
        Returns:
            dict with response and metadata
        """
        
        logger.info(f"\n{'='*70}")
        logger.info(f"💬 USER: {user_message}")
        logger.info(f"{'='*70}")
        
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
        
        logger.info(f"🌐 Language: {cs_result['label']} (Swahili: {swahili_ratio:.0%}, Confidence: {cs_result['confidence']:.1%})")
        
        # ====================================================================
        # STEP 2: ANALYZE INTENT & EXTRACT ENTITIES
        # ====================================================================
        analysis = self.intent_analyzer.analyze(user_message)
        
        logger.info(f"🎯 Intent: {analysis['intent']}")
        if analysis['amount']:
            logger.info(f"💰 Amount detected: KSh {analysis['amount']:,}")
        if analysis['goal']:
            logger.info(f"🎨 Goal: {analysis['goal']}")
        
        # ====================================================================
        # STEP 3: FETCH LIVE MARKET DATA (if applicable)
        # ====================================================================
        live_data = None
        
        if self.use_live_data and self._needs_live_data(analysis['intent']):
            logger.info("📊 Fetching live market data...")
            live_data = self._fetch_relevant_live_data(analysis['intent'], analysis['amount'])
            
            if live_data:
                logger.info("✓ Live data fetched successfully")
            else:
                logger.warning("⚠ Live data fetch failed, using cached/static data")
        
        # ====================================================================
        # STEP 4: CHECK FOR CONVERSATIONAL CONTEXT
        # This is what makes it feel like a real conversation!
        # ====================================================================
        
        # Update context with user preferences
        self.context.detect_investment_style_preference(user_message)
        
        # Check if user is disagreeing or asking follow-up
        is_disagreement = self.context.detect_disagreement(user_message)
        
        if is_disagreement:
            logger.info("🔄 User disagreement detected - adapting response")
        
        # Try to generate conversational response first
        conversational_response = self.response_generator.generate_conversational_response(
            user_message,
            analysis,
            self.context,
            live_data,
            language_pattern
        )
        
        if conversational_response:
            # User is continuing a conversation - use context-aware response
            logger.info("💬 Generated conversational response (context-aware)")
            response_text = conversational_response
            best_match = None
            match_score = 0.0
            used_live = live_data is not None
        
        # ====================================================================
        # STEP 5: AMOUNT-BASED ROUTING (Investment/Stock Advice)
        # ====================================================================
        elif analysis['amount'] is not None:
            logger.info(f"💵 Amount-based query detected: KSh {analysis['amount']:,}")
            
            # Route to stock or investment advisor based on intent
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
            
            # Save investment context for follow-up questions
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
                # Check relevance of top result
                top_result = knowledge_results[0]
                
                if top_result['score'] >= 0.30:
                    best_match = top_result
                    logger.info(f"✓ KB Match: {best_match['question'][:60]}... (score: {best_match['score']:.3f})")
                else:
                    logger.info(f"⚠ Low KB match score ({top_result['score']:.3f}), using fallback")
            else:
                logger.info("⚠ No KB matches found")
            
            match_score = best_match['score'] if best_match else 0.0
            
            # Generate response (with or without KB match)
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
        # STEP 7: ENHANCE WITH LIVE DATA SNIPPET (if applicable)
        # ====================================================================
        if live_data and self._should_add_live_update(analysis['intent']):
            market_update = self._generate_market_update(live_data)
            if market_update:
                response_text += f"\n\n{market_update}"
        
        # ====================================================================
        # STEP 8: SAVE CONVERSATION CONTEXT
        # ====================================================================
        self.context.add_exchange(
            user_message,
            response_text,
            analysis['intent']
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
        logger.info(f"{'='*70}\n")
        
        # ====================================================================
        # STEP 10: RETURN RESPONSE WITH METADATA
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
            'user_preferences': self.context.get_user_preference_summary()
        }
    
    def _needs_live_data(self, intent: str) -> bool:
        """
        Determine if intent requires live market data
        
        Args:
            intent: Detected intent
        
        Returns:
            bool: True if live data needed
        """
        
        live_data_intents = [
            'investment_advice',
            'stock_query',
            'stock_recommendation',
            'global_stocks_query',
            'etf_query',
            'broker_query'
        ]
        
        return intent in live_data_intents
    
    def _fetch_relevant_live_data(self, intent: str, amount: int = None) -> dict:
        """
        Fetch relevant live data based on intent
        
        This is smart - it only fetches what's needed for the query
        
        Args:
            intent: User's intent
            amount: Investment amount (if specified)
        
        Returns:
            dict with live data
        """
        
        try:
            live_data = {}
            
            # Always get market summary (lightweight)
            live_data['market_summary'] = self.market_fetcher.get_market_summary()
            
            # Get NSE data for stock queries
            if intent in ['stock_query', 'stock_recommendation', 'investment_advice']:
                logger.info("  Fetching NSE stocks...")
                nse_stocks = self.market_fetcher.get_nse_stocks()
                
                # Analyze stocks with amount context
                live_data['nse_analysis'] = self.market_analyzer.analyze_nse_stocks(
                    nse_stocks,
                    amount=amount
                )
                
                logger.info(f"  ✓ NSE: {len(nse_stocks)} stocks analyzed")
            
            # Get investment data for investment queries
            if intent == 'investment_advice':
                logger.info("  Fetching investment data...")
                
                # MMF rates
                mmf_rates = self.market_fetcher.get_mmf_rates()
                live_data['mmf_analysis'] = self.market_analyzer.compare_mmfs(mmf_rates)
                live_data['mmf_rates'] = mmf_rates
                
                # Treasury rates
                treasury = self.market_fetcher.get_treasury_rates()
                live_data['treasury_rates'] = treasury
                
                logger.info("  ✓ Investment data: MMF + Treasury rates")
            
            # Get forex for global queries
            if intent in ['global_stocks_query', 'etf_query']:
                logger.info("  Fetching forex rates...")
                live_data['forex_rate'] = self.market_fetcher.get_forex_rate('USD/KES')
            
            return live_data
        
        except Exception as e:
            logger.error(f"❌ Error fetching live data: {e}")
            return None
    
    def _should_add_live_update(self, intent: str) -> bool:
        """Check if we should add live market update to response"""
        
        # Add market update for these intents
        update_intents = [
            'stock_query',
            'stock_recommendation',
            'investment_advice',
            'etf_query'
        ]
        
        return intent in update_intents
    
    def _generate_market_update(self, live_data: dict) -> str:
        """
        Generate brief market update snippet
        
        Example: "📊 Live Update: NSE is 🟢 BULLISH today (Avg: +1.2%)"
        """
        
        if not live_data:
            return ""
        
        update = ""
        
        # Market sentiment
        market_summary = live_data.get('market_summary')
        if market_summary:
            emoji = market_summary.get('emoji', '➡️')
            sentiment = market_summary.get('sentiment', 'NEUTRAL')
            avg_change = market_summary.get('avg_change', 0)
            
            update += f"📊 **Live Update**: NSE is {emoji} {sentiment} today (Avg: {avg_change:+.1f}%)"
        
        # Top MMF
        mmf_analysis = live_data.get('mmf_analysis', {})
        best_mmf = mmf_analysis.get('best')
        if best_mmf:
            update += f"\n💰 Top MMF now: {best_mmf['name']} ({best_mmf['rate']}%)"
        
        return update
    
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
        logger.info("🗑️ Conversation history and context cleared")
    
    def get_market_status(self):
        """
        Get current market status string
        
        Returns:
            str: Market status summary
        """
        
        if not self.use_live_data:
            return "Static Mode (Live data disabled)"
        
        try:
            summary = self.market_fetcher.get_market_summary()
            return f"{summary['emoji']} {summary['sentiment']} - Gainers: {summary['gainers']}, Losers: {summary['losers']}"
        except:
            return "Market data unavailable"
    
    def get_conversation_context(self):
        """
        Get current conversation context
        
        Useful for debugging or understanding user preferences
        """
        
        return {
            'user_preferences': self.context.user_preferences,
            'last_topic': self.context.last_topic,
            'conversation_length': len(self.context.conversation_history),
            'preference_summary': self.context.get_user_preference_summary()
        }
    
    def close(self):
        """Clean up resources"""
        
        if self.use_live_data:
            try:
                self.market_fetcher.close()
                logger.info("✓ Market data fetcher closed")
            except:
                pass
        
        logger.info("✓ Chatbot closed")

# ============================================================================
# MAIN - FOR TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🤖 ENHANCED CONVERSATIONAL KENYAN FINANCIAL CHATBOT")
    print("="*70)
    
    # Initialize chatbot
    chatbot = KenyanFinancialChatbot(use_live_data=True)
    
    # Show welcome message
    print(f"\n{chatbot.get_welcome_message()}")
    
    # Show market status
    print(f"\n📊 Market Status: {chatbot.get_market_status()}")
    
    # Test conversations
    test_conversations = [
        # Conversation 1: Investment advice with disagreement
        [
            "I have 100k, where should I invest?",
            "No, I want to put all 100k in one place",
            "What are the returns with option 1?"
        ],
        
        # Conversation 2: Stock recommendations
        [
            "Which stocks should I buy today?",
            "I have 50k for stocks",
            "Which one has the highest dividend?"
        ],
        
        # Conversation 3: Code-switching
        [
            "niko na 75k, niweke wapi?",
            "hapana, nataka safe option",
            "nitapata how much after mwaka moja?"
        ]
    ]
    
    print("\n" + "="*70)
    print(" 💬 TEST CONVERSATIONS")
    print("="*70)
    
    for conv_num, conversation in enumerate(test_conversations, 1):
        print(f"\n{'='*70}")
        print(f" CONVERSATION {conv_num}")
        print(f"{'='*70}")
        
        for msg in conversation:
            print(f"\n👤 You: {msg}")
            print(f"{'-'*70}")
            
            result = chatbot.chat(msg)
            
            print(f"🤖 Bot: {result['response']}")
            print(f"\n📊 Metadata:")
            print(f"   Language: {result['detected_language']} ({result['swahili_ratio']:.0%} Swahili)")
            print(f"   Intent: {result['intent']}")
            print(f"   Live Data: {'✓' if result['used_live_data'] else '✗'}")
            print(f"   User Prefs: {result['user_preferences']}")
        
        # Clear history between conversations
        chatbot.clear_history()
        print(f"\n{'='*70}")
        print(" [Conversation ended - history cleared]")
    
    # Show final stats
    print("\n" + "="*70)
    print(" 📈 SESSION SUMMARY")
    print("="*70)
    print(f"Total messages processed: {len(chatbot.history)}")
    print(f"Market data mode: {'Live' if chatbot.use_live_data else 'Static'}")
    
    # Close chatbot
    chatbot.close()
    
    print("\n✓ Test complete!")