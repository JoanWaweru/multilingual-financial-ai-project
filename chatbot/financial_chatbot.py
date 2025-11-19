"""
Main chatbot class with conversational memory and dynamic responses
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
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor
except ModuleNotFoundError:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    from chatbot.models.cs_detector import CodeSwitchingDetector
    from chatbot.knowledge.financial_kb import FinancialKnowledgeBase
    from chatbot.response_generator import ResponseGenerator
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KenyanFinancialChatbot:
    """Multilingual financial chatbot with conversational memory"""

    def __init__(self, model_path="saved_models/best_model.pt"):
        """Initialize chatbot"""

        logger.info("Initializing Kenyan Financial Chatbot...")

        # Load components
        self.cs_detector = CodeSwitchingDetector(model_path)
        self.knowledge_base = FinancialKnowledgeBase()
        self.response_generator = ResponseGenerator()
        self.intent_analyzer = IntentAnalyzer()
        self.advisor = DynamicFinancialAdvisor()

        # Conversation history with context
        self.history = []
        self.conversation_context = {
            'last_intent': None,
            'waiting_for': None,
            'partial_info': {}
        }

        logger.info("✓ Chatbot ready!")

    def chat(self, user_message):
        """
        Process user message and generate response with improved relevance checking

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

        # 2. Analyze intent and extract entities
        from chatbot.utils.intent_analyzer import IntentAnalyzer
        intent_analyzer = IntentAnalyzer()
        analysis = intent_analyzer.analyze(user_message)

        # 3. SMART DECISION: If user has specific amount + advice request
        if analysis['amount'] and analysis['intent'] in ['investment_advice', 'stock_query']:
            logger.info(f"Using dynamic advisor for amount-specific query: {analysis['amount']}")

            # Generate dynamic response directly
            if analysis['intent'] == 'stock_query':
                response_text = self.response_generator.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market='nse',
                    language_mix=swahili_ratio
                )
            else:
                response_text = self.response_generator.advisor.generate_investment_advice(
                    amount=analysis['amount'],
                    goal=analysis['goal'],
                    urgency=analysis['urgency'],
                    language_mix=swahili_ratio
                )

            # Add greeting
            greeting = self.response_generator._add_greeting(language_pattern)
            response_text = f"{greeting} {response_text}"

            best_match = None
            match_score = 0.0

        else:
            # 4. Search knowledge base for other queries
            knowledge_results = self.knowledge_base.search(user_message, top_k=3, threshold=0.25)

            # 5. FILTER: Check if result is relevant
            best_match = None
            if knowledge_results:
                top_result = knowledge_results[0]

                user_words = set(user_message.lower().split())
                answer_words = set(top_result['answer'].lower().split())
                question_words = set(top_result['question'].lower().split())

                common_with_answer = len(user_words.intersection(answer_words))
                common_with_question = len(user_words.intersection(question_words))

                if top_result['score'] > 0.30 and (common_with_answer > 2 or common_with_question > 2):
                    best_match = top_result
                    logger.info(f"Using knowledge base match: {top_result['question'][:50]}...")
                else:
                    logger.info(
                        f"KB match too low ({top_result['score']:.3f}) or not relevant — using fallback"
                    )
                    best_match = None

            match_score = best_match['score'] if best_match else 0.0

            # 6. Generate response
            response_text = self.response_generator.generate_response(
                best_match,
                language_pattern,
                include_proverb=(best_match is not None and best_match['score'] > 0.35),
                user_query=user_message
            )

        # 7. Save to history
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
            'match_score': match_score
        }

    # -------------------------------------------------------------------------
    # FOLLOW-UP & HANDLING SUB-BEHAVIORS
    # -------------------------------------------------------------------------

    def _handle_followup(self, user_message, analysis, language_pattern):
        """Handle follow-up responses in multi-turn conversation"""

        waiting_for = self.conversation_context['waiting_for']
        last_intent = self.conversation_context['last_intent']
        swahili_ratio = language_pattern['swahili_ratio']
        user_lower = user_message.lower().strip()

        # --- YES / NO confirmation ---
        if waiting_for in ['confirmation', 'choice']:
            return self._handle_confirmation(user_lower, swahili_ratio)

        # --- Amount missing ---
        if waiting_for == 'amount':
            amount = analysis['amount']

            if not amount:
                if any(word in user_lower for word in ['no', "don't have", 'sina', 'hapana']):
                    if swahili_ratio > 0.5:
                        return (
                            "Sawa, no problem! Unaweza kuanza na pesa kidogo sana — hata KSh 100. "
                            "Ukikuwa ready, niambie! Ungependa kujua nini ingine?"
                        )
                    else:
                        return (
                            "No worries! You can start very small — even KSh 100. "
                            "When you're ready, just ask! What else would you like to know?"
                        )

                if swahili_ratio > 0.5:
                    return "Samahani, sijaelewa. Tuambie amount in KES. Example: '50k' or '50,000 KES'"
                else:
                    return "Sorry, I didn't catch that. Tell me the amount in KES. Example: '50k' or '50,000 KES'"

            # Got amount
            self.conversation_context['partial_info']['amount'] = amount
            self.conversation_context['waiting_for'] = None

            if last_intent == 'stock_query':
                advice = self.advisor.generate_stock_advice(
                    amount=amount,
                    experience='beginner',
                    market='nse',
                    language_mix=swahili_ratio
                )
                greeting = "Sawa!" if swahili_ratio > 0.5 else "Great!"
                return f"{greeting} {advice}"

            if last_intent == 'investment_advice':
                advice = self.advisor.generate_investment_advice(
                    amount=amount,
                    goal=self.conversation_context['partial_info'].get('goal'),
                    urgency='flexible',
                    language_mix=swahili_ratio
                )
                greeting = "Poa!" if swahili_ratio > 0.5 else "Perfect!"
                return f"{greeting} {advice}"

        # fallback
        self.conversation_context['waiting_for'] = None
        return self._generate_dynamic_response(user_message, analysis, language_pattern)

    # -------------------------------------------------------------------------

    def _handle_confirmation(self, user_message, swahili_ratio):
        """Handle yes/no/choice responses"""

        last_question = self.conversation_context.get('last_question')

        yes_words = ['yes', 'yeah', 'yep', 'sure', 'ok', 'okay', 'ndio', 'sawa', 'ebu']
        no_words = ['no', 'nope', 'nah', 'hapana', 'siyo']

        is_yes = any(word in user_message for word in yes_words)
        is_no = any(word in user_message for word in no_words)

        # --- ETF buying question ---
        if last_question == 'etf_how_to_buy':
            if is_no:
                if swahili_ratio > 0.5:
                    return "Sawa! Ungependa kujua nini ingine? Savings? Stocks? M-Pesa?"
                else:
                    return "Alright! What else would you like to know about? Savings, stocks, M-Pesa?"

            # Wants ETF buying instructions
            if swahili_ratio > 0.5:
                response = "Poa! Hivi ndivyo kununua ETFs kutoka Kenya:\n\n"
            else:
                response = "Great! Here's how to invest in ETFs from Kenya:\n\n"

            response += (
                "**Option 1: US ETFs (via Interactive Brokers)**\n"
                "1. Open account at interactivebrokers.com\n"
                "2. Verify identity (passport + proof of address)\n"
                "3. Fund via wire transfer (KSh 3k–5k fee)\n"
                "4. Buy ETFs: SPY, VOO, VTI\n"
                "5. Minimum: $100–500\n\n"
                "**Option 2: Local Unit Trusts (Easier!)**\n"
                "1. Visit CIC, Sanlam, or Old Mutual\n"
                "2. Open unit trust account\n"
                "3. Minimum: KSh 5,000–10,000\n"
                "4. Similar to ETFs but locally managed\n\n"
            )

            response += (
                "Recommendation: Start with unit trusts — simpler & no forex risk!"
                if swahili_ratio <= 0.5
                else "Recommendation: Anza na unit trusts — easy process, hakuna forex risk!"
            )

            self.conversation_context['waiting_for'] = None
            self.conversation_context['last_question'] = None

            return response

        # --- Stock explanation continuation ---
        elif last_question == 'want_more_stock_info':
            if is_no:
                if swahili_ratio > 0.5:
                    return "Sawa! Uliza kitu ingine yoyote — savings, loans, M-Pesa, chochote!"
                else:
                    return "Alright! Ask me anything else — savings, loans, M-Pesa, anything!"

            # User wants more stock info
            if swahili_ratio > 0.5:
                return (
                    "Poa! Ungependa kujua specifically:\n"
                    "1. How to open account na buy stocks?\n"
                    "2. Beginner-friendly stocks?\n"
                    "3. How much to start with?\n\n"
                    "Just tell me the number or ask directly!"
                )
            else:
                return (
                    "Great! What would you like to know:\n"
                    "1. How to open an account & buy stocks?\n"
                    "2. Best beginner stocks?\n"
                    "3. Starting amount?\n\n"
                    "Just tell me the number or ask directly!"
                )

        # generic confirmation fallback
        self.conversation_context['waiting_for'] = None
        self.conversation_context['last_question'] = None

        return (
            "Sawa! Niambie — what exactly would you like to know more about?"
            if swahili_ratio > 0.5
            else "Sure! What exactly would you like to know more about?"
        )

    # -------------------------------------------------------------------------

    def _generate_dynamic_response(self, user_message, analysis, language_pattern):
        """Generate response dynamically based on intent"""

        intent = analysis['intent']
        amount = analysis['amount']
        swahili_ratio = language_pattern['swahili_ratio']
        greeting = "Sawa," if swahili_ratio > 0.5 else "Alright,"

        # ---- STOCKS ----
        if intent == 'stock_query':
            if amount:
                advice = self.advisor.generate_stock_advice(
                    amount=amount,
                    experience='beginner',
                    market='nse',
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"

            # Explain stocks first
            if swahili_ratio > 0.5:
                explanation = (
                    "Sawa, stocks ni pieces of companies unazobuy...\n\n"
                    "How much pesa unafikiria kuanza nayo?"
                )
            else:
                explanation = (
                    "Alright, stocks are pieces of companies you can buy...\n\n"
                    "How much would you like to invest?"
                )

            self.conversation_context['waiting_for'] = 'amount'
            self.conversation_context['last_intent'] = 'stock_query'
            return explanation

        # ---- ETFs ----
        elif intent == 'etf_query':
            if swahili_ratio > 0.5:
                response = (
                    f"{greeting} ETFs ni baskets za stocks unazinunua kama one investment...\n\n"
                    "Would you like to know how to buy ETFs or unit trusts?"
                )
            else:
                response = (
                    f"{greeting} ETFs are baskets of stocks you buy as a single investment...\n\n"
                    "Would you like to know how to buy ETFs or unit trusts?"
                )

            self.conversation_context['waiting_for'] = 'confirmation'
            self.conversation_context['last_intent'] = 'etf_query'
            self.conversation_context['last_question'] = 'etf_how_to_buy'

            return response

        # ---- Investment advice ----
        elif intent == 'investment_advice':
            if amount:
                advice = self.advisor.generate_investment_advice(
                    amount=amount,
                    goal=analysis['goal'],
                    urgency=analysis['urgency'],
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"

            if swahili_ratio > 0.5:
                response = (
                    "Poa! Ninaweza kusaidia na investment advice. "
                    "But nisaidie — how much pesa do you have? (50k, 100k...)"
                )
            else:
                response = (
                    "Great! I can help with investment advice. "
                    "First, how much money are you investing? (50k, 100k...)"
                )

            self.conversation_context['waiting_for'] = 'amount'
            self.conversation_context['last_intent'] = 'investment_advice'
            self.conversation_context['partial_info']['goal'] = analysis['goal']

            return response

        # ---- Global stocks ----
        elif intent == 'global_stocks_query':
            if amount:
                advice = self.advisor.generate_stock_advice(
                    amount=amount,
                    experience='beginner',
                    market='international',
                    language_mix=swahili_ratio
                )
                return f"{greeting} {advice}"

            if swahili_ratio > 0.5:
                return (
                    f"{greeting} Hivi ndivyo kununua international stocks...\n\n"
                    "How much unafikiria kuinvest?"
                )
            else:
                return (
                    f"{greeting} Here's how to buy international stocks...\n\n"
                    "How much are you planning to invest?"
                )

        # ---- Knowledge base for factual queries ----
        else:
            knowledge_results = self.knowledge_base.search(user_message, top_k=1, threshold=0.20)
            if knowledge_results and knowledge_results[0]['score'] > 0.25:
                return self.response_generator.generate_response(
                    knowledge_results[0],
                    language_pattern,
                    include_proverb=(knowledge_results[0]['score'] > 0.4),
                    user_query=user_message
                )

            return self.response_generator._generate_fallback_response(
                language_pattern,
                user_query=user_message
            )

    # -------------------------------------------------------------------------

    def get_welcome_message(self):
        """Get welcome message"""
        return self.response_generator.generate_welcome_message()

    def get_history(self):
        """Get conversation history"""
        return self.history

    def clear_history(self):
        """Clear conversation history and context"""
        self.history = []
        self.conversation_context = {
            'last_intent': None,
            'waiting_for': None,
            'partial_info': {}
        }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" 🤖 KENYAN FINANCIAL CHATBOT - TEST")
    print("=" * 70)

    chatbot = KenyanFinancialChatbot()
    print(chatbot.get_welcome_message())

    test_conversation = [
        "stocks ni nini?",
        "100 shillings",
        "what are ETFs?",
        "yes",
        "niko na 50k, niweke wapi?",
    ]

    print("\n" + "=" * 70)
    print(" 💬 TEST CONVERSATION WITH MEMORY")
    print("=" * 70)

    for msg in test_conversation:
        print(f"\n👤 User: {msg}")
        result = chatbot.chat(msg)
        print(f"🤖 Bot: {result['response']}")
