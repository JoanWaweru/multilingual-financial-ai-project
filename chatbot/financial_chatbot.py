"""
Production Kenyan Financial Chatbot
Complete conversational AI with semantic understanding and real-time data
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Optional, List
from datetime import datetime

# Fix imports
try:
    from chatbot.models.cs_detector import CodeSwitchingDetector
    from chatbot.knowledge.financial_kb import FinancialKnowledgeBase
    from chatbot.response_generator import ResponseGenerator
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.market_data import MarketDataFetcher
    from chatbot.utils.market_analyzer import MarketAnalyzer
    from chatbot.utils.context_manager import ConversationContext
    from chatbot.utils.bank_data_fetcher import BankDataFetcher
    from chatbot.utils.semantic_matcher import SemanticMatcher
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
    from chatbot.utils.bank_data_fetcher import BankDataFetcher
    from chatbot.utils.semantic_matcher import SemanticMatcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KenyanFinancialChatbot:
    """
    Production-Grade Conversational Financial Chatbot
    
    🎯 FEATURES:
    ✅ Semantic understanding (no pattern matching hell)
    ✅ Real-time market data (NSE, T-Bills, MMFs, Global stocks)
    ✅ Dynamic bank recommendations (real ratings & fees)
    ✅ Conversational context tracking
    ✅ Natural dialogue flow (yes/no, options, follow-ups)
    ✅ Code-switching (English/Swahili/mixed)
    ✅ User preference learning
    ✅ Intent-based routing
    
    🏗️ ARCHITECTURE:
    ┌─────────────────────────────────────────────────┐
    │                                                 │
    │           USER MESSAGE                          │
    │                 ↓                               │
    │       [Code-Switching Detection]                │
    │                 ↓                               │
    │       [Semantic Intent Analysis]                │
    │                 ↓                               │
    │    ┌────────────────────────────┐              │
    │    │  Conversational Patterns?  │              │
    │    │  (yes/no, options, etc)    │              │
    │    └────────────┬───────────────┘              │
    │                 │ No                            │
    │                 ↓                               │
    │    ┌────────────────────────────┐              │
    │    │  Amount-based routing?     │              │
    │    │  (investment/stock advice) │              │
    │    └────────────┬───────────────┘              │
    │                 │ No                            │
    │                 ↓                               │
    │    ┌────────────────────────────┐              │
    │    │  Knowledge Base Search     │              │
    │    └────────────┬───────────────┘              │
    │                 │                               │
    │                 ↓                               │
    │       [Live Data Integration]                   │
    │                 ↓                               │
    │       [Response Generation]                     │
    │                 ↓                               │
    │       [Context Update]                          │
    │                 ↓                               │
    │           RESPONSE                              │
    │                                                 │
    └─────────────────────────────────────────────────┘
    """
    
    def __init__(self, model_path="saved_models/best_model.pt", use_live_data=True):
        """
        Initialize complete chatbot system
        
        Args:
            model_path: Path to code-switching detection model
            use_live_data: Enable real-time market data
        """
        
        logger.info("")
        logger.info("="*80)
        logger.info(" 🚀 INITIALIZING KENYAN FINANCIAL CHATBOT (PRODUCTION)")
        logger.info("="*80)
        
        # ====================================================================
        # CORE NLP COMPONENTS
        # ====================================================================
        logger.info("📚 Loading core NLP components...")
        
        self.cs_detector = CodeSwitchingDetector(model_path)
        logger.info("   ✓ Code-switching detector loaded")
        
        self.knowledge_base = FinancialKnowledgeBase(use_bitext=False)
        logger.info("   ✓ Knowledge base loaded")
        
        self.response_generator = ResponseGenerator()
        logger.info("   ✓ Response generator loaded")
        
        self.intent_analyzer = IntentAnalyzer()
        logger.info("   ✓ Intent analyzer loaded")
        
        # ====================================================================
        # INTELLIGENT SYSTEMS (NEW!)
        # ====================================================================
        logger.info("🧠 Loading intelligent systems...")
        
        try:
            self.semantic_matcher = SemanticMatcher()
            logger.info("   ✓ Semantic matcher loaded (BERT-based)")
        except Exception as e:
            logger.error(f"   ✗ Semantic matcher failed: {e}")
            raise
        
        try:
            self.bank_fetcher = BankDataFetcher()
            logger.info("   ✓ Bank data fetcher loaded (real-time)")
        except Exception as e:
            logger.warning(f"   ⚠ Bank fetcher failed: {e}")
            self.bank_fetcher = None
        
        # ====================================================================
        # CONVERSATION TRACKING
        # ====================================================================
        logger.info("💬 Initializing conversation system...")
        
        self.context = ConversationContext()
        logger.info("   ✓ Conversation context initialized")
        
        # ====================================================================
        # REAL-TIME DATA COMPONENTS
        # ====================================================================
        self.use_live_data = use_live_data
        
        if use_live_data:
            logger.info("📊 Initializing live data systems...")
            try:
                self.market_fetcher = MarketDataFetcher()
                self.market_analyzer = MarketAnalyzer()
                logger.info("   ✓ Live market data ENABLED")
                logger.info("     • NSE stocks: ENABLED")
                logger.info("     • Treasury rates: ENABLED")
                logger.info("     • MMF rates: ENABLED")
                logger.info("     • Global markets: ENABLED")
            except Exception as e:
                logger.warning(f"   ⚠ Live data unavailable: {e}")
                logger.info("     Falling back to static mode")
                self.use_live_data = False
        else:
            logger.info("📚 Live data DISABLED (static mode)")
        
        # ====================================================================
        # CONVERSATION HISTORY
        # ====================================================================
        self.history = []
        self.session_start = datetime.now()
        
        # ====================================================================
        # STARTUP COMPLETE
        # ====================================================================
        logger.info("="*80)
        logger.info("✅ CHATBOT READY FOR PRODUCTION")
        logger.info(f"   Mode: {'🔴 LIVE DATA' if self.use_live_data else '📚 STATIC'}")
        logger.info(f"   Model: {model_path}")
        logger.info(f"   Session ID: {self.session_start.strftime('%Y%m%d-%H%M%S')}")
        logger.info("="*80)
        logger.info("")
    
    def chat(self, user_message: str) -> Dict:
        """
        Process user message with full conversational intelligence
        
        This is the MAIN ENTRY POINT - the brain of the system
        
        FLOW:
        ┌─────────────────────────────────────────┐
        │ 1. Detect language (code-switching)     │
        │ 2. Analyze intent (semantic matching)   │
        │ 3. Check conversational patterns        │
        │ 4. Fetch live data (if needed)          │
        │ 5. Generate context-aware response      │
        │ 6. Update conversation state            │
        │ 7. Return rich response                 │
        └─────────────────────────────────────────┘
        
        Args:
            user_message: User's input text
        
        Returns:
            dict: Complete response with metadata
                {
                    'response': str,              # The actual response
                    'detected_language': str,     # 'english', 'swahili', 'code_switched'
                    'confidence': float,          # CS detection confidence
                    'swahili_ratio': float,       # 0-1 ratio of Swahili
                    'knowledge_match': str,       # Matched KB question
                    'match_score': float,         # KB match score
                    'used_live_data': bool,       # Whether live data was used
                    'intent': str,                # Detected intent
                    'user_preferences': str,      # User preference summary
                    'conversation_state': str,    # Current state
                    'semantic_matches': list      # Semantic intent matches
                }
        """
        
        logger.info("")
        logger.info("="*80)
        logger.info(f"💬 USER: {user_message}")
        logger.info("="*80)
        
        # ====================================================================
        # STEP 1: CODE-SWITCHING DETECTION
        # ====================================================================
        cs_result = self.cs_detector.detect(user_message)
        swahili_ratio = self.cs_detector.get_language_ratio(user_message)
        
        language_pattern = {
            'label': cs_result['label'],
            'swahili_ratio': swahili_ratio,
            'confidence': cs_result['confidence']
        }
        
        logger.info(f"🌐 Language: {cs_result['label']}")
        logger.info(f"   Swahili: {swahili_ratio:.0%} | English: {(1-swahili_ratio):.0%}")
        logger.info(f"   Confidence: {cs_result['confidence']:.1%}")
        
        # ====================================================================
        # STEP 2: SEMANTIC INTENT ANALYSIS
        # ====================================================================
        analysis = self.intent_analyzer.analyze(user_message, self.context)
        
        logger.info(f"🎯 Intent: {analysis['intent']}")
        logger.info(f"   Confidence: {analysis['confidence']:.0%}")
        
        if analysis['amount']:
            logger.info(f"💰 Amount: KSh {analysis['amount']:,}")
        if analysis['goal']:
            logger.info(f"🎨 Goal: {analysis['goal']}")
        if analysis['is_follow_up']:
            logger.info(f"🔗 Follow-up: YES")
        
        # Get semantic matches for debugging
        semantic_matches = self.semantic_matcher.get_all_matches(user_message, threshold=0.6)
        if semantic_matches:
            logger.info(f"🧠 Semantic Matches:")
            for intent, score in semantic_matches[:3]:
                logger.info(f"   • {intent}: {score:.3f}")
        
        # ====================================================================
        # STEP 3: FETCH LIVE DATA (if needed)
        # ====================================================================
        live_data = None
        
        if self.use_live_data and self._needs_live_data(analysis['intent']):
            logger.info("📊 Fetching live market data...")
            live_data = self._fetch_relevant_live_data(analysis['intent'], analysis['amount'])
            
            if live_data:
                logger.info("   ✓ Live data fetched successfully")
                if live_data.get('market_summary'):
                    summary = live_data['market_summary']
                    logger.info(f"   NSE: {summary['sentiment']} ({summary['avg_change']:+.1f}%)")
            else:
                logger.warning("   ⚠ Live data fetch failed")
        
        # ====================================================================
        # STEP 4: CONVERSATIONAL PATTERN DETECTION (Priority)
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
            logger.info("💬 Route: CONVERSATIONAL (context-aware)")
            response_text = conversational_response
            best_match = None
            match_score = 0.0
            used_live = live_data is not None
        
        # ====================================================================
        # STEP 5: AMOUNT-BASED ROUTING (Investment/Stock Advice)
        # ====================================================================
        elif analysis['amount'] is not None:
            logger.info(f"💵 Route: AMOUNT-BASED (KSh {analysis['amount']:,})")
            
            # Determine market type
            if analysis['intent'] in ['stock_query', 'stock_recommendation', 'global_stocks_query']:
                logger.info("   → Stock advisor")
                market = 'international' if analysis['intent'] == 'global_stocks_query' else 'nse'
                
                response_text = self.response_generator.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market=market,
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
            else:
                logger.info("   → Investment advisor")
                
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
            logger.info("📚 Route: KNOWLEDGE BASE")
            
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
                    logger.info(f"   ✓ Match: {best_match['question'][:50]}...")
                    logger.info(f"   Score: {best_match['score']:.3f}")
                else:
                    logger.info(f"   ⚠ Low score ({top_result['score']:.3f}), using fallback")
            else:
                logger.info("   ⚠ No KB matches found")
            
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
            'live_data_used': used_live,
            'semantic_matches': semantic_matches
        }
        
        self.context.add_exchange(
            user_message,
            response_text,
            analysis['intent'],
            metadata
        )
        
        logger.info(f"   State: {self.context.state}")
        logger.info(f"   Preferences: {self.context.get_user_preference_summary()}")
        
        # ====================================================================
        # STEP 9: SAVE TO HISTORY
        # ====================================================================
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'bot': response_text,
            'language': cs_result['label'],
            'confidence': cs_result['confidence'],
            'used_live_data': used_live,
            'intent': analysis['intent'],
            'amount': analysis['amount'],
            'semantic_matches': semantic_matches
        })
        
        logger.info(f"✓ Response generated ({len(response_text)} chars)")
        logger.info("="*80)
        
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
            'conversation_state': self.context.state,
            'semantic_matches': [
                {'intent': intent, 'score': score}
                for intent, score in semantic_matches[:3]
            ] if semantic_matches else []
        }
    
    def _needs_live_data(self, intent: str) -> bool:
        """Determine if intent requires live data"""
        
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
    
    def _fetch_relevant_live_data(self, intent: str, amount: int = None) -> Optional[Dict]:
        """
        Smart data fetching - only gets what's needed
        
        Reduces API calls and improves performance
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
                
                logger.info(f"  ✓ NSE: {len(nse_stocks)} stocks analyzed")
            
            # Investment data for MMF/Treasury queries
            if intent in ['investment_advice', 'mmf_query', 'treasury_query']:
                logger.info("  → Fetching investment data...")
                
                # MMF rates
                mmf_rates = self.market_fetcher.get_mmf_rates()
                live_data['mmf_analysis'] = self.market_analyzer.compare_mmfs(mmf_rates)
                live_data['mmf_rates'] = mmf_rates
                
                # Treasury rates
                treasury = self.market_fetcher.get_treasury_rates()
                live_data['treasury_rates'] = treasury
                
                logger.info("  ✓ Investment data fetched")
            
            # Forex for global queries
            if intent in ['global_stocks_query', 'etf_query']:
                logger.info("  → Fetching forex...")
                live_data['forex_rate'] = self.market_fetcher.get_forex_rate('USD/KES')
                logger.info("  ✓ Forex rates fetched")
            
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
    
    def _generate_market_update(self, live_data: Dict) -> str:
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
    
    def get_welcome_message(self) -> str:
        """Get welcome message"""
        return self.response_generator.generate_welcome_message()
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.history
    
    def clear_history(self):
        """Clear conversation history and reset context"""
        self.history = []
        self.context.clear_context()
        logger.info("🗑️ History cleared and context reset")
    
    def get_market_status(self) -> str:
        """Get current market status summary"""
        
        if not self.use_live_data:
            return "📚 Static Mode"
        
        try:
            summary = self.market_fetcher.get_market_summary()
            return f"{summary['emoji']} {summary['sentiment']} - Gainers: {summary['gainers']}, Losers: {summary['losers']}"
        except:
            return "Market data unavailable"
    
    def get_conversation_context(self) -> Dict:
        """Get current conversation context (for debugging)"""
        
        return {
            'user_preferences': self.context.user_preferences,
            'last_topic': self.context.last_topic,
            'conversation_length': len(self.context.conversation_history),
            'last_amount': self.context.last_amount,
            'state': self.context.state,
            'preference_summary': self.context.get_user_preference_summary(),
            'last_5_exchanges': [
                {
                    'user': ex['user'],
                    'intent': ex['intent'],
                    'timestamp': ex['timestamp'].isoformat()
                }
                for ex in self.context.get_last_n_exchanges(5)
            ]
        }
    
    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        
        session_duration = datetime.now() - self.session_start
        
        intents = [ex['intent'] for ex in self.history]
        intent_counts = {}
        for intent in intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            'session_id': self.session_start.strftime('%Y%m%d-%H%M%S'),
            'duration_seconds': int(session_duration.total_seconds()),
            'total_messages': len(self.history),
            'intents': intent_counts,
            'live_data_used': sum(1 for ex in self.history if ex.get('used_live_data')),
            'current_state': self.context.state
        }
    
    def close(self):
        """Clean up resources"""
        
        logger.info("🔄 Closing chatbot session...")
        
        if self.use_live_data:
            try:
                self.market_fetcher.close()
                logger.info("   ✓ Market fetcher closed")
            except:
                pass
        
        # Log session stats
        stats = self.get_session_stats()
        logger.info(f"   Session duration: {stats['duration_seconds']}s")
        logger.info(f"   Total messages: {stats['total_messages']}")
        logger.info(f"   Live data calls: {stats['live_data_used']}")
        
        logger.info("✓ Chatbot closed successfully")

# ============================================================================
# COMPREHENSIVE TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print(" 🤖 PRODUCTION KENYAN FINANCIAL CHATBOT - COMPREHENSIVE TEST")
    print("="*80)
    
    # Initialize
    chatbot = KenyanFinancialChatbot(use_live_data=True)
    
    # Welcome
    print(f"\n{chatbot.get_welcome_message()}")
    print(f"\n📊 Market Status: {chatbot.get_market_status()}")
    
    # Test conversations
    test_conversations = [
        {
            'name': 'Investment Flow with Single Place Preference',
            'description': 'User wants to invest 100k in one place, selects T-Bills',
            'messages': [
                "niko na 100k, nataka kuweka place moja. niadvise",
                "option 1 inabamba",
                "yes niambie",
                "hapana, sina bank account"
            ]
        },
        
        {
            'name': 'Bank Comparison with Real Data',
            'description': 'User asks for bank recommendations',
            'messages': [
                "bank gani mzuri kuweka pesa?",
                "yes niambie",
                "equity ama kcb?"
            ]
        },
        
        {
            'name': 'MMF Query with Follow-up',
            'description': 'User asks about MMFs and provides amount',
            'messages': [
                "which money market fund is best?",
                "I have 50k",
                "how much will I get after 1 year?"
            ]
        },
        
        {
            'name': 'Stock Recommendations',
            'description': 'User asks which stocks to buy today',
            'messages': [
                "Which stocks should I buy today?",
                "I have 200k",
                "tell me more about option 1"
            ]
        },
        
        {
            'name': 'Short Follow-ups',
            'description': 'Testing short query handling',
            'messages': [
                "niko na pesa, invest wapi?",
                "75k",
                "just one place",
                "option 2",
                "yes"
            ]
        }
    ]
    
    print("\n" + "="*80)
    print(" 💬 TESTING CONVERSATIONS")
    print("="*80)
    
    for conv_num, conversation in enumerate(test_conversations, 1):
        print(f"\n{'='*80}")
        print(f" CONVERSATION {conv_num}: {conversation['name']}")
        print(f" Description: {conversation['description']}")
        print(f"{'='*80}")
        
        for msg_num, msg in enumerate(conversation['messages'], 1):
            print(f"\n👤 You ({msg_num}): {msg}")
            print(f"{'-'*80}")
            
            result = chatbot.chat(msg)
            
            print(f"🤖 Bot: {result['response']}")
            
            # Show metadata
            print(f"\n📊 Metadata:")
            print(f"   Language: {result['detected_language']} (Swahili: {result['swahili_ratio']:.0%})")
            print(f"   Intent: {result['intent']}")
            print(f"   Live Data: {'✓' if result['used_live_data'] else '✗'}")
            print(f"   State: {result['conversation_state']}")
            print(f"   Preferences: {result['user_preferences']}")
            
            if result['semantic_matches']:
                print(f"   Semantic Matches:")
                for match in result['semantic_matches']:
                    print(f"      • {match['intent']}: {match['score']:.3f}")
        
        # Show conversation context
        print(f"\n🔍 Conversation Context:")
        ctx = chatbot.get_conversation_context()
        print(f"   Last Amount: KSh {ctx['last_amount']:,}" if ctx['last_amount'] else "   Last Amount: None")
        print(f"   Exchanges: {ctx['conversation_length']}")
        
        # Clear between conversations
        chatbot.clear_history()
        print(f"\n{'='*80}")
        print(" [History cleared for next conversation]")
        print()
    
    # Final stats
    print("\n" + "="*80)
    print(" 📈 SESSION STATISTICS")
    print("="*80)
    
    stats = chatbot.get_session_stats()
    print(f"\nSession ID: {stats['session_id']}")
    print(f"Duration: {stats['duration_seconds']} seconds")
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Live Data Calls: {stats['live_data_used']}")
    
    if stats['intents']:
        print(f"\nIntent Distribution:")
        for intent, count in sorted(stats['intents'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {intent}: {count}")
    
    print("\n" + "="*80)
    
    chatbot.close()
    
    print("\n✅ ALL TESTS COMPLETE!")
    print("="*80)