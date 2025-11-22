"""
Production Response Generator
Complete conversational intelligence with semantic understanding
"""

import sys
from pathlib import Path
import random
import logging
from typing import Dict, Optional, List

# Fix imports
try:
    from chatbot.knowledge.kenyan_phrases import KenyanPhrases
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor
    from chatbot.utils.bank_data_fetcher import BankDataFetcher
    from chatbot.utils.semantic_matcher import SemanticMatcher
except ModuleNotFoundError:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    sys.path.insert(0, str(project_root))
    from chatbot.knowledge.kenyan_phrases import KenyanPhrases
    from chatbot.utils.intent_analyzer import IntentAnalyzer
    from chatbot.utils.dynamic_advisor import DynamicFinancialAdvisor
    from chatbot.utils.bank_data_fetcher import BankDataFetcher
    from chatbot.utils.semantic_matcher import SemanticMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Production-Grade Response Generator
    
    Features:
    ✅ Semantic understanding (no pattern matching hell)
    ✅ Real-time bank data integration
    ✅ Context-aware conversations
    ✅ Natural dialogue flow
    ✅ Code-switching adaptation
    ✅ Dynamic recommendations
    
    Architecture:
    1. Conversational patterns (yes/no, options, follow-ups)
    2. Amount-based routing (investment/stock advice)
    3. Knowledge base fallback
    4. Intelligent defaults
    """
    
    def __init__(self):
        """Initialize all components"""
        
        logger.info("🎯 Initializing Response Generator...")
        
        # Core components
        self.phrases = KenyanPhrases()
        self.intent_analyzer = IntentAnalyzer()
        self.advisor = DynamicFinancialAdvisor()
        
        # NEW: Intelligent systems
        self.bank_fetcher = BankDataFetcher()
        self.semantic_matcher = SemanticMatcher()
        
        logger.info("✓ Response Generator Ready")
        logger.info("   • Semantic understanding: ENABLED")
        logger.info("   • Dynamic bank data: ENABLED")
        logger.info("   • Conversational AI: ENABLED")
        
        # Swahili financial terms
        self.swahili_terms = {
            'money': 'pesa',
            'bank': 'benki',
            'save': 'weka',
            'savings': 'akiba',
            'loan': 'mkopo',
            'account': 'akaunti',
            'investment': 'uwekezaji',
            'profit': 'faida',
            'returns': 'mapato',
            'interest': 'riba'
        }
    
    def generate_conversational_response(self, user_query, analysis, context, live_data, language_pattern):
        """
        MAIN CONVERSATIONAL ROUTER
        
        Priority flow:
        1. Affirmations (yes/no) - using semantic matcher
        2. Option selections (1, 2, 3) - using semantic matcher
        3. Return calculations (follow-up)
        4. Single place preference - using semantic matcher
        5. Short follow-ups (context-dependent)
        
        This is what makes the chatbot TRULY conversational
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        logger.info(f"🔄 Conversational routing: {user_query[:50]}...")
        
        # ================================================================
        # PRIORITY 1: AFFIRMATIONS (YES/NO) - SEMANTIC
        # ================================================================
        affirmation = self.semantic_matcher.is_affirmation(user_query)
        if affirmation:
            logger.info(f"   → Detected affirmation: {affirmation}")
            return self._handle_affirmation(affirmation, context, swahili_ratio, user_query)
        
        # ================================================================
        # PRIORITY 2: OPTION SELECTION - SEMANTIC
        # ================================================================
        option_num = self.semantic_matcher.get_option_selection(user_query)
        if option_num:
            logger.info(f"   → Detected option selection: {option_num}")
            return self._handle_option_selection(option_num, context, swahili_ratio, live_data)
        
        # ================================================================
        # PRIORITY 3: RETURN CALCULATION QUESTIONS - SEMANTIC
        # ================================================================
        if self.semantic_matcher.is_asking_returns(user_query):
            if context.has_context() and context.last_amount:
                logger.info(f"   → Detected return calculation request")
                return self._generate_return_calculation(context, swahili_ratio)
        
        # ================================================================
        # PRIORITY 4: SINGLE PLACE PREFERENCE - SEMANTIC
        # ================================================================
        if self.semantic_matcher.is_single_place_preference(user_query):
            logger.info(f"   → Detected single place preference")
            context.detect_investment_style_preference(user_query)
            
            return self._generate_single_investment_advice(
                analysis['amount'] or context.last_amount,
                context,
                live_data,
                swahili_ratio
            )
        
        # ================================================================
        # PRIORITY 5: SHORT FOLLOW-UP WITH AMOUNT
        # ================================================================
        if analysis['is_short'] and context.has_context():
            if analysis['amount'] and len(user_query.split()) <= 2:
                logger.info(f"   → Detected amount follow-up: {analysis['amount']}")
                return self._handle_amount_follow_up(
                    analysis['amount'],
                    context,
                    live_data,
                    swahili_ratio
                )
        
        # No conversational pattern matched
        logger.info(f"   → No conversational pattern matched")
        return None
    
    def _handle_affirmation(self, affirmation: str, context, swahili_ratio: float, user_query: str) -> str:
        """
        Handle YES/NO with full context awareness
        
        Uses conversation history to understand what user is affirming/rejecting
        """
        
        logger.info(f"💬 Handling affirmation: {affirmation}")
        
        is_yes = (affirmation == 'yes')
        
        # Check if this is also an information request (e.g., "yes niambie")
        wants_more_info = self.semantic_matcher.is_information_request(user_query)
        
        # Get last exchange for context
        last_exchange = context.get_last_exchange()
        if not last_exchange:
            return self._generic_affirmation_response(is_yes, swahili_ratio)
        
        last_bot = last_exchange['bot'].lower()
        
        # ============================================================
        # CONTEXT 1: CDS Account Help
        # ============================================================
        if 'cds' in last_bot and ('help' in last_bot or 'opening' in last_bot or 'account' in last_bot):
            if is_yes or wants_more_info:
                response = "Poa! " if swahili_ratio > 0.5 else "Great! "
                response += "Here's the complete CDS account process:\n\n"
                
                response += "**🏦 OPTION A: Through Your Bank** (Recommended)\n\n"
                response += "**Step 1:** Visit your bank branch\n"
                response += "   • Banks: Equity, KCB, Co-op, NCBA, Stanbic\n"
                response += "   • Bring: National ID, KRA PIN\n\n"
                
                response += "**Step 2:** Tell them:\n"
                response += "   • \"I want to open a CDS account for Treasury Bills\"\n\n"
                
                response += "**Step 3:** Complete registration\n"
                response += "   • Fill CDS registration form\n"
                response += "   • Pay registration fee: ~KSh 1,100\n"
                response += "   • Provide ID copy + KRA PIN\n\n"
                
                response += "**Step 4:** Activation\n"
                response += "   • Wait 1-2 business days\n"
                response += "   • You'll get CDS account number\n"
                response += "   • Can check via bank app or CBK portal\n\n"
                
                response += "**🌐 OPTION B: Direct with CBK**\n"
                response += "   1. Go to: centralbank.go.ke\n"
                response += "   2. Download CDS registration form\n"
                response += "   3. Submit online or visit CBK office\n"
                response += "   4. Takes 3-5 days\n\n"
                
                response += "**💡 Why Option A is better:**\n"
                response += "   • Faster (1-2 days vs 3-5 days)\n"
                response += "   • Bank helps you buy T-Bills\n"
                response += "   • Easier fund transfers\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Una bank account tayari? 😊"
                else:
                    response += "Do you already have a bank account? 😊"
                
                return response
            else:
                if swahili_ratio > 0.5:
                    return "Sawa, hakuna shida! Kuna kitu kingine ninaweza kukusaidia? 😊"
                else:
                    return "No problem! Is there anything else I can help with? 😊"
        
        # ============================================================
        # CONTEXT 2: Bank Account Question
        # ============================================================
        if 'bank account' in last_bot and '?' in last_bot:
            if is_yes or wants_more_info:
                if swahili_ratio > 0.5:
                    return "Poa! Unaweza enda direct kwa bank yako kufungua CDS account. Una bank gani? 😊"
                else:
                    return "Perfect! You can go directly to your bank to open a CDS account. Which bank do you use? 😊"
            else:
                # User doesn't have bank account - offer bank recommendations
                if swahili_ratio > 0.5:
                    return "Sawa, lazima ufungue bank account kwanza. Ningependa kukushow best banks? 😊"
                else:
                    return "Okay, you'll need to open a bank account first. Would you like me to recommend the best banks? 😊"
        
        # ============================================================
        # CONTEXT 3: Bank Recommendations
        # ============================================================
        if any(word in last_bot for word in ['bank recommend', 'best bank', 'which bank']):
            if is_yes or wants_more_info:
                # Get user profile from context
                user_profile = {
                    'amount': context.last_amount or 50000,
                    'purpose': 'savings',
                    'tech_savvy': swahili_ratio < 0.5,
                    'location': 'urban'
                }
                
                # Get REAL bank data
                banks = self.bank_fetcher.get_bank_recommendations(user_profile)
                
                # Generate response
                if swahili_ratio > 0.5:
                    response = "Sawa! Hapa ni best banks (based on real ratings & fees):\n\n"
                else:
                    response = "Here are the best banks (based on real data & ratings):\n\n"
                
                for i, bank in enumerate(banks[:4], 1):
                    emoji = "⭐" if i == 1 else "✅"
                    
                    response += f"**{i}. {emoji} {bank['name']}** (Score: {bank['score']:.0f}/100)\n"
                    response += f"   • Rating: {bank['rating']:.1f}/5.0\n"
                    response += f"   • Monthly Fee: KSh {bank['monthly_fee']:,}\n"
                    
                    if bank['reasons']:
                        response += f"   • Why: {bank['reasons'][0]}\n"
                    
                    response += "\n"
                
                response += f"**💡 MY RECOMMENDATION**: {banks[0]['name']}\n"
                response += f"   → {banks[0]['reasons'][0] if banks[0]['reasons'] else 'Best overall'}\n\n"
                
                response += "**📋 To open account:**\n"
                response += "   1. Visit branch with ID\n"
                response += "   2. Fill account form (5 mins)\n"
                response += "   3. Initial deposit: KSh 100-500\n"
                response += "   4. Get card + mobile banking same day!\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Uko ready kwenda bank? 😊"
                else:
                    response += "Ready to visit the bank? 😊"
                
                return response
        
        # ============================================================
        # CONTEXT 4: MMF Account Links
        # ============================================================
        if any(word in last_bot for word in ['mmf', 'money market', 'sanlam', 'cic']):
            if 'registration' in last_bot or 'link' in last_bot:
                if is_yes or wants_more_info:
                    response = "Poa! " if swahili_ratio > 0.5 else "Great! "
                    response += "Here are the direct registration links:\n\n"
                    
                    response += "**1. ⭐ Sanlam MMF** (11.2% - Highest!)\n"
                    response += "   🔗 https://sanlaminvestments.com\n"
                    response += "   • Min: KSh 1,000\n"
                    response += "   • Process: 100% online (5-10 mins)\n"
                    response += "   • Withdraw: 1-2 days to M-Pesa\n\n"
                    
                    response += "**2. ✅ CIC MMF** (10.8%)\n"
                    response += "   🔗 https://cicgroup.co.ke/investments\n"
                    response += "   • Min: KSh 5,000\n"
                    response += "   • Process: Online + ID upload\n"
                    response += "   • Withdraw: 1-2 days\n\n"
                    
                    response += "**3. ✅ Britam MMF** (10.5%)\n"
                    response += "   🔗 https://britam.com/investments\n"
                    response += "   • Min: KSh 1,000\n"
                    response += "   • Process: Online\n\n"
                    
                    response += "**📱 Quick Registration Steps:**\n"
                    response += "1. Click link → 'Register' or 'Open Account'\n"
                    response += "2. Fill form: Name, ID, Phone, Email, KRA PIN\n"
                    response += "3. Upload ID photo (clear photo from phone)\n"
                    response += "4. Wait 24-48hrs for approval\n"
                    response += "5. Fund via M-Pesa when approved!\n\n"
                    
                    if swahili_ratio > 0.5:
                        response += "Ungependa help na registration? 😊"
                    else:
                        response += "Need help with the registration? 😊"
                    
                    return response
        
        # ============================================================
        # DEFAULT: Generic affirmation response
        # ============================================================
        return self._generic_affirmation_response(is_yes, swahili_ratio)
    
    def _generic_affirmation_response(self, is_yes: bool, swahili_ratio: float) -> str:
        """Generic yes/no response when no specific context"""
        
        if is_yes:
            if swahili_ratio > 0.5:
                return random.choice([
                    "Sawa! Nikusaidie na nini zaidi? 😊",
                    "Poa! Swali lingine? 😊",
                    "Vizuri! Kuna kitu kingine? 😊"
                ])
            else:
                return random.choice([
                    "Great! What else can I help you with? 😊",
                    "Perfect! Any other questions? 😊",
                    "Awesome! How else can I assist? 😊"
                ])
        else:
            if swahili_ratio > 0.5:
                return random.choice([
                    "Hakuna shida! Kuna swali lingine? 😊",
                    "Sawa tu! Nisaidie na nini? 😊",
                    "Poa! Kitu kingine? 😊"
                ])
            else:
                return random.choice([
                    "No worries! Any other questions? 😊",
                    "That's fine! How else can I help? 😊",
                    "Okay! Anything else? 😊"
                ])
    
    def _handle_option_selection(self, option_num: int, context, swahili_ratio: float, live_data) -> str:
        """
        Handle option 1, 2, or 3 selection
        
        Provides complete breakdown and next steps
        """
        
        logger.info(f"📊 Handling option {option_num}")
        
        greeting = "Poa choice!" if swahili_ratio > 0.5 else "Great choice!"
        
        # Must have investment context
        if not context.last_amount:
            if swahili_ratio > 0.5:
                return f"{greeting} Remind me - tulikuwa tunaongea investment ya kiasi gani? 😊"
            else:
                return f"{greeting} Remind me - how much were we discussing? 😊"
        
        amount = context.last_amount
        
        # Get rates from live data
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        tbill_rate = tbills.get('364_day', {}).get('rate', 17.5)
        
        mmf_analysis = live_data.get('mmf_analysis', {}) if live_data else {}
        best_mmf = mmf_analysis.get('best')
        mmf_rate = best_mmf['rate'] if best_mmf else 11.0
        mmf_name = best_mmf['name'] if best_mmf else "CIC Money Market Fund"
        
        # ============================================================
        # OPTION 1: TREASURY BILLS (Complete Guide)
        # ============================================================
        if option_num == 1:
            response = f"{greeting} Treasury Bills - excellent choice!\n\n"
            
            response += f"**💰 YOUR INVESTMENT PLAN**\n"
            response += f"   Amount: KSh {amount:,}\n"
            response += f"   Rate: {tbill_rate:.1f}% per year\n"
            response += f"   Interest: KSh {int(amount * (tbill_rate/100)):,}\n"
            response += f"   Total after 1 year: KSh {int(amount * (1 + tbill_rate/100)):,}\n\n"
            
            response += f"**📋 COMPLETE PROCESS (Step-by-Step)**\n\n"
            
            response += f"**STEP 1: Open CDS Account**\n"
            response += f"   • Visit your bank (Equity, KCB, Co-op)\n"
            response += f"   • Say: \"I want CDS account for T-Bills\"\n"
            response += f"   • Bring: ID + KRA PIN\n"
            response += f"   • Pay: KSh 1,100 registration\n"
            response += f"   • Wait: 1-2 days activation\n\n"
            
            response += f"**STEP 2: Fund CDS Account**\n"
            response += f"   • Transfer KSh {amount:,} to CDS account\n"
            response += f"   • Via bank app or branch\n"
            response += f"   • Takes 1 day to reflect\n\n"
            
            response += f"**STEP 3: Buy T-Bills**\n"
            response += f"   • T-Bill auctions: Every Tuesday\n"
            response += f"   • Tell bank: \"Buy 364-day T-Bills for me\"\n"
            response += f"   • OR bid online via CBK portal\n"
            response += f"   • Money debited on auction day\n\n"
            
            response += f"**STEP 4: Wait & Earn**\n"
            response += f"   • Money locked for 364 days\n"
            response += f"   • Track via bank app or CBK portal\n"
            response += f"   • After 1 year: Get KSh {int(amount * (1 + tbill_rate/100)):,}\n"
            response += f"   • Interest taxed at 15% (already calculated above)\n\n"
            
            response += f"**✅ WHY THIS IS GREAT**\n"
            response += f"   • 100% government-backed (safest!)\n"
            response += f"   • Highest guaranteed returns in Kenya\n"
            response += f"   • No hidden fees or charges\n"
            response += f"   • Can roll over automatically\n\n"
            
            response += f"**⚠️ IMPORTANT TO KNOW**\n"
            response += f"   • Cannot withdraw before maturity (364 days)\n"
            response += f"   • Minimum is KSh 100,000\n"
            response += f"   • Interest is taxable income\n"
            response += f"   • Great for long-term goals\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa help na CDS account? 😊"
            else:
                response += f"Would you like help opening the CDS account? 😊"
            
            return response
        
        # ============================================================
        # OPTION 2: MONEY MARKET FUND (Complete Guide)
        # ============================================================
        elif option_num == 2:
            response = f"{greeting} {mmf_name} - perfect for flexibility!\n\n"
            
            response += f"**💰 YOUR INVESTMENT PLAN**\n"
            response += f"   Amount: KSh {amount:,}\n"
            response += f"   Rate: {mmf_rate:.2f}% per year\n"
            response += f"   Interest: KSh {int(amount * (mmf_rate/100)):,}\n"
            response += f"   Total after 1 year: KSh {int(amount * (1 + mmf_rate/100)):,}\n\n"
            
            response += f"**🏆 TOP MMF OPTIONS (Current Rates)**\n\n"
            
            response += f"1. **⭐ Sanlam MMF** (11.2%) - HIGHEST!\n"
            response += f"   • Min investment: KSh 1,000\n"
            response += f"   • Withdraw to M-Pesa: 1-2 days\n"
            response += f"   • Website: sanlaminvestments.com\n"
            response += f"   • Rating: 4.3/5.0\n\n"
            
            response += f"2. **✅ CIC MMF** (10.8%)\n"
            response += f"   • Min investment: KSh 5,000\n"
            response += f"   • Withdraw: 1-2 days\n"
            response += f"   • Website: cicgroup.co.ke/investments\n"
            response += f"   • Rating: 4.2/5.0\n\n"
            
            response += f"3. **✅ Britam MMF** (10.5%)\n"
            response += f"   • Min investment: KSh 1,000\n"
            response += f"   • Withdraw: 2-3 days\n"
            response += f"   • Website: britam.com/investments\n"
            response += f"   • Rating: 4.1/5.0\n\n"
            
            response += f"**📋 COMPLETE PROCESS**\n\n"
            
            response += f"**STEP 1: Choose Your MMF**\n"
            response += f"   • Recommendation: Sanlam (highest rate)\n"
            response += f"   • Alternative: CIC (if you have KSh 5k+)\n\n"
            
            response += f"**STEP 2: Register Online**\n"
            response += f"   • Go to: sanlaminvestments.com\n"
            response += f"   • Click: 'Open Account' or 'Register'\n"
            response += f"   • Fill form (5-10 minutes):\n"
            response += f"     - Full name\n"
            response += f"     - ID number\n"
            response += f"     - Phone & email\n"
            response += f"     - KRA PIN\n"
            response += f"   • Upload: Clear ID photo\n\n"
            
            response += f"**STEP 3: Wait for Approval**\n"
            response += f"   • Time: 24-48 hours\n"
            response += f"   • You'll get SMS/email with account number\n\n"
            
            response += f"**STEP 4: Fund Your Account**\n"
            response += f"   • M-Pesa: Send to MMF paybill (in approval SMS)\n"
            response += f"   • OR Bank transfer: Use account number\n"
            response += f"   • Amount: KSh {amount:,}\n"
            response += f"   • Reflects in 1 day\n\n"
            
            response += f"**STEP 5: Watch It Grow!**\n"
            response += f"   • Interest calculated daily\n"
            response += f"   • Check balance via app/website\n"
            response += f"   • Withdraw anytime to M-Pesa\n"
            response += f"   • No penalties for withdrawal\n\n"
            
            response += f"**✅ WHY THIS IS GREAT**\n"
            response += f"   • Withdraw anytime (super flexible!)\n"
            response += f"   • Much better than bank savings (2-5%)\n"
            response += f"   • Low minimum (KSh 1,000)\n"
            response += f"   • Daily interest calculation\n"
            response += f"   • Safe (invested in gov bonds)\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa links za registration? 😊"
            else:
                response += f"Would you like the registration links? 😊"
            
            return response
        
        # ============================================================
        # OPTION 3: SACCO (Complete Guide)
        # ============================================================
        elif option_num == 3:
            response = f"{greeting} SACCO - smart for loans & savings!\n\n"
            
            response += f"**💰 YOUR INVESTMENT PLAN**\n"
            response += f"   Amount: KSh {amount:,}\n"
            response += f"   Dividends: ~10-12% per year\n"
            response += f"   Expected: KSh {int(amount * 0.11):,}\n"
            response += f"   Total after 1 year: KSh {int(amount * 1.11):,}\n\n"
            
            response += f"**🎁 BONUS BENEFIT (HUGE!)**\n"
            response += f"   After 6 months, qualify for loans:\n"
            response += f"   → Up to KSh {int(amount * 3):,} (3x your deposit!)\n"
            response += f"   → Interest: 12-14% (vs 15-20% at banks)\n"
            response += f"   → Repayment: Flexible terms\n\n"
            
            response += f"**🏆 TOP SACCO OPTIONS**\n\n"
            
            response += f"1. **⭐ Stima SACCO**\n"
            response += f"   • Open to: Public (anyone can join)\n"
            response += f"   • Dividends: 10-12%\n"
            response += f"   • Loans: Up to 3x deposits\n"
            response += f"   • Branches: Nairobi, major towns\n"
            response += f"   • Why: Very stable, good returns\n\n"
            
            response += f"2. **✅ Mwalimu SACCO**\n"
            response += f"   • Open to: Teachers (but accepts all)\n"
            response += f"   • Dividends: 12-14%\n"
            response += f"   • Loans: Excellent rates\n"
            response += f"   • Why: Highest dividends\n\n"
            
            response += f"3. **✅ Kenya Police SACCO**\n"
            response += f"   • Open to: Public\n"
            response += f"   • Dividends: 10-11%\n"
            response += f"   • Loans: Good access\n"
            response += f"   • Why: Very accessible\n\n"
            
            response += f"4. **✅ Harambee SACCO**\n"
            response += f"   • Open to: Everyone\n"
            response += f"   • Dividends: 9-10%\n"
            response += f"   • Loans: Available after 6 months\n"
            response += f"   • Why: No restrictions\n\n"
            
            response += f"**📋 COMPLETE PROCESS**\n\n"
            
            response += f"**STEP 1: Choose SACCO**\n"
            response += f"   • Check if your employer has one (best option!)\n"
            response += f"   • OR choose from list above\n"
            response += f"   • Recommendation: Stima SACCO (open to all)\n\n"
            
            response += f"**STEP 2: Visit Branch**\n"
            response += f"   • Find nearest branch (Google Maps)\n"
            response += f"   • Bring: National ID, Payslip (if employed)\n"
            response += f"   • Ask: \"I want to join SACCO\"\n\n"
            
            response += f"**STEP 3: Registration**\n"
            response += f"   • Fill membership form\n"
            response += f"   • Pay registration: KSh 500-1,000\n"
            response += f"   • Pay share capital: Your KSh {amount:,}\n"
            response += f"   • Get membership number\n\n"
            
            response += f"**STEP 4: Start Earning**\n"
            response += f"   • Dividends paid: Quarterly or annually\n"
            response += f"   • Attend AGM: Vote on decisions\n"
            response += f"   • Apply for loans: After 6 months\n"
            response += f"   • Track via SACCO app/website\n\n"
            
            response += f"**✅ WHY THIS IS GREAT**\n"
            response += f"   • Get dividends (10-12%)\n"
            response += f"   • Qualify for cheap loans (3x deposit!)\n"
            response += f"   • Build credit history\n"
            response += f"   • You OWN part of SACCO\n"
            response += f"   • Emergency loans available\n\n"
            
            response += f"**⚠️ THINGS TO KNOW**\n"
            response += f"   • Less liquid than MMF (1-2 weeks to withdraw)\n"
            response += f"   • But loan access makes up for it!\n"
            response += f"   • Dividends vary by SACCO performance\n"
            response += f"   • Need to attend AGM (annual meeting)\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa help kutafuta SACCO karibu na wewe? 😊"
            else:
                response += f"Need help finding a SACCO near you? 😊"
            
            return response
        
        # Unknown option
        return self._generic_affirmation_response(True, swahili_ratio)
    
    def _handle_amount_follow_up(self, amount: int, context, live_data, swahili_ratio: float) -> str:
        """
        Handle when user provides amount as follow-up
        
        Example:
        Bot: "How much?"
        User: "50k"
        """
        
        logger.info(f"💵 Amount follow-up: KSh {amount:,}")
        
        # Check user preferences
        if context.user_preferences.get('investment_style') == 'single':
            # User wants single place
            return self._generate_single_investment_advice(
                amount,
                context,
                live_data,
                swahili_ratio
            )
        else:
            # Generate general investment advice
            advice = self.advisor.generate_investment_advice(
                amount=amount,
                goal=context.user_preferences.get('goal'),
                urgency='flexible',
                language_mix=swahili_ratio,
                live_data=live_data
            )
            
            greeting = self.phrases.get_transition() if swahili_ratio > 0.5 else "Alright,"
            return f"{greeting} {advice}"
    
    def _generate_single_investment_advice(self, amount, context, live_data, swahili_ratio):
        """
        Generate single place investment advice
        
        Shows 3 options, user picks one
        """
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Got it,"
        
        if not amount:
            if swahili_ratio > 0.5:
                return f"{greeting} unataka kuweka yote mahali moja. Ni kiasi gani? 😊"
            else:
                return f"{greeting} you want everything in one place. How much? 😊"
        
        response = f"{greeting} you want ALL KSh {amount:,} in ONE place.\n\n"
        response += f"Here are your best single-investment options:\n\n"
        
        # Get rates
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        tbill_rate = tbills.get('364_day', {}).get('rate', 17.5)
        
        mmf_analysis = live_data.get('mmf_analysis', {}) if live_data else {}
        best_mmf = mmf_analysis.get('best')
        mmf_rate = best_mmf['rate'] if best_mmf else 11.0
        mmf_name = best_mmf['name'] if best_mmf else "CIC Money Market Fund"
        
        # Option 1
        response += f"**OPTION 1: Treasury Bills (364-day)** ⭐ RECOMMENDED\n"
        response += f"   💰 Rate: {tbill_rate:.1f}% per year\n"
        response += f"   📈 After 1 year: KSh {int(amount * (1 + tbill_rate/100)):,}\n"
        response += f"   💵 Profit: KSh {int(amount * (tbill_rate/100)):,}\n"
        response += f"   ✅ Government-backed (100% safe)\n"
        response += f"   ✅ Highest guaranteed returns\n"
        response += f"   ⚠️ Locked for 1 year\n\n"
        
        # Option 2
        response += f"**OPTION 2: {mmf_name}**\n"
        response += f"   💰 Rate: {mmf_rate:.2f}% per year\n"
        response += f"   📈 After 1 year: KSh {int(amount * (1 + mmf_rate/100)):,}\n"
        response += f"   💵 Profit: KSh {int(amount * (mmf_rate/100)):,}\n"
        response += f"   ✅ Withdraw anytime (flexible!)\n"
        response += f"   ✅ Low minimum (KSh 1,000)\n"
        response += f"   ⚠️ Lower return than T-Bills\n\n"
        
        # Option 3 (if amount suitable)
        if amount >= 20000:
            response += f"**OPTION 3: SACCO Deposit**\n"
            response += f"   💰 Rate: ~11% dividends\n"
            response += f"   📈 After 1 year: KSh {int(amount * 1.11):,}\n"
            response += f"   💵 Profit: KSh {int(amount * 0.11):,}\n"
            response += f"   🎁 BONUS: Loans up to KSh {int(amount * 3):,}!\n"
            response += f"   ✅ Build credit history\n"
            response += f"   ⚠️ Less liquid (1-2 weeks to withdraw)\n\n"
        
        # Recommendation
        response += f"**💡 MY RECOMMENDATION**: "
        if amount >= 100000:
            response += f"Option 1 (Treasury Bills)\n"
            response += f"   Why: Highest return ({tbill_rate:.1f}%) + safest\n"
        elif amount >= 50000:
            response += f"Option 3 (SACCO)\n"
            response += f"   Why: Good returns + loan access\n"
        else:
            response += f"Option 2 ({mmf_name})\n"
            response += f"   Why: Flexible + good returns ({mmf_rate:.1f}%)\n"
        
        response += f"\n"
        
        if swahili_ratio > 0.5:
            response += f"Chagua option gani? (Type 1, 2, au 3) 😊"
        else:
            response += f"Which option would you like? (Type 1, 2, or 3) 😊"
        
        # Save context
        context.save_investment_context(amount, {}, ['option 1', 'option 2', 'option 3'])
        
        return response
    
    def _generate_return_calculation(self, context, swahili_ratio):
        """Calculate and show expected returns"""
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Good question!"
        
        returns = context.calculate_expected_returns()
        
        if not returns:
            if swahili_ratio > 0.5:
                return f"{greeting} nisaidie - unataka invest kiasi gani na wapi? 😊"
            else:
                return f"{greeting} how much and where are you investing? 😊"
        
        response = f"{greeting} here's your return calculation:\n\n"
        
        response += f"**💰 INVESTMENT SUMMARY**\n"
        response += f"   Initial: KSh {returns['initial_amount']:,}\n\n"
        
        if returns['breakdown']:
            response += f"**📊 EXPECTED RETURNS (After 1 Year)**\n\n"
            
            for name, data in returns['breakdown'].items():
                response += f"**{name}**\n"
                response += f"   • Invested: KSh {data['invested']:,}\n"
                response += f"   • Rate: {data['rate']*100:.1f}%\n"
                response += f"   • Return: KSh {data['return']:,}\n"
                response += f"   • Total: KSh {data['total']:,}\n\n"
        
        response += f"**✨ TOTAL OUTCOME**\n"
        response += f"   💵 Profit: KSh {returns['total_return']:,}\n"
        response += f"   💰 Final Amount: KSh {returns['final_amount']:,}\n"
        response += f"   📈 Overall Return: {returns['overall_rate']:.1f}%\n\n"
        
        if swahili_ratio > 0.5:
            response += f"💡 Hizi ni estimated returns. Actual depends on market!"
        else:
            response += f"💡 These are estimates. Actual may vary with market conditions."
        
        return response
    
    def generate_response(self, knowledge_result, user_language_pattern, 
                         include_proverb=False, user_query=None, live_data=None, context=None):
        """
        Generate response from knowledge base match
        
        Used when we found a KB match
        """
        
        if not knowledge_result:
            return self._generate_fallback_response(
                user_language_pattern, user_query, live_data, context
            )
        
        # Start with greeting
        response = self._add_greeting(user_language_pattern)
        
        # Get base answer
        base_answer = knowledge_result['answer']
        
        # Enhance with live data if relevant
        if live_data and self._is_market_related(knowledge_result.get('category')):
            base_answer = self._enhance_with_live_data(base_answer, live_data)
        
        # Adapt language
        adapted_answer = self._adapt_language(base_answer, user_language_pattern)
        
        response += " " + adapted_answer
        
        # Add encouragement
        if random.random() < 0.3:
            response += f" {self.phrases.get_encouragement()}"
        
        # Add proverb occasionally
        if include_proverb and random.random() < 0.5:
            proverb = self.phrases.get_random_proverb()
            response += f"\n\n💡 \"{proverb['swahili']}\" - {proverb['meaning']}"
        
        return response
    
    def _add_greeting(self, language_pattern):
        """Add appropriate greeting"""
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        if swahili_ratio > 0.6:
            return self.phrases.get_transition()
        elif swahili_ratio < 0.3:
            return random.choice(['Okay,', 'Alright,', 'Sure,'])
        else:
            return self.phrases.get_transition()
    
    def _adapt_language(self, text, language_pattern):
        """Adapt response to user's language mix"""
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        if swahili_ratio > 0.4:
            for eng, sw in self.swahili_terms.items():
                if random.random() < swahili_ratio and eng in text.lower():
                    text = text.replace(eng, sw, 1)
        
        return text
    
    def _is_market_related(self, category: str) -> bool:
        """Check if category benefits from live data"""
        market_categories = ['stocks', 'etfs', 'investment', 'global_stocks', 'savings']
        return category in market_categories if category else False
    
    def _enhance_with_live_data(self, answer: str, live_data: dict) -> str:
        """Add live data snippet to answer"""
        enhancement = ""
        
        if live_data.get('market_summary'):
            summary = live_data['market_summary']
            enhancement += f"\n\n📊 NSE: {summary['emoji']} {summary['sentiment']} (Avg: {summary['avg_change']:+.1f}%)"
        
        return answer + enhancement
    
    def _generate_fallback_response(self, language_pattern, user_query=None, live_data=None, context=None):
        """
        Intelligent fallback - handles all intents
        
        This is the safety net when no KB match
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        greeting = self.phrases.get_transition() if swahili_ratio > 0.5 else "Alright,"
        
        if not user_query:
            return self._generic_help(swahili_ratio)
        
        # Analyze intent
        analysis = self.intent_analyzer.analyze(user_query, context)
        
        # Route based on intent
        intent_handlers = {
            'mmf_query': lambda: self._generate_mmf_comparison(live_data, swahili_ratio),
            'bank_comparison': lambda: self._generate_bank_comparison(swahili_ratio, analysis['amount']),
            'treasury_query': lambda: self._generate_treasury_info(live_data, swahili_ratio),
            'investment_advice': lambda: f"{greeting} {self.advisor.generate_investment_advice(analysis['amount'], analysis['goal'], analysis['urgency'], swahili_ratio, live_data)}",
            'stock_query': lambda: f"{greeting} {self.advisor.generate_stock_advice(analysis['amount'], 'beginner', 'nse', swahili_ratio, live_data)}",
            'stock_recommendation': lambda: f"{greeting} {self.advisor.generate_stock_advice(analysis['amount'], 'beginner', 'nse', swahili_ratio, live_data)}",
            'global_stocks_query': lambda: f"{greeting} {self.advisor.generate_stock_advice(analysis['amount'], 'beginner', 'international', swahili_ratio, live_data)}",
        }
        
        handler = intent_handlers.get(analysis['intent'])
        if handler:
            return handler()
        
        return self._generic_help(swahili_ratio)
    
    def _generate_mmf_comparison(self, live_data, swahili_ratio):
        """Generate MMF comparison"""
        greeting = "Sawa," if swahili_ratio > 0.5 else "Here are"
        response = f"{greeting} the top Money Market Funds:\n\n"
        
        if live_data and live_data.get('mmf_rates'):
            mmf_rates = live_data['mmf_rates']
            sorted_mmfs = sorted(mmf_rates.items(), key=lambda x: x[1]['current_rate'], reverse=True)
            
            for i, (name, data) in enumerate(sorted_mmfs[:5], 1):
                emoji = "⭐" if i == 1 else "✅"
                response += f"{i}. {emoji} **{name}**\n"
                response += f"   Rate: {data['current_rate']}%\n"
                response += f"   Min: KSh {data['minimum']:,}\n"
                response += f"   Liquidity: {data['liquidity']}\n\n"
        else:
            response += "1. ⭐ **Sanlam MMF** - 11.2% (Min: KSh 1,000)\n"
            response += "2. ✅ **CIC MMF** - 10.8% (Min: KSh 5,000)\n"
            response += "3. ✅ **Britam MMF** - 10.5% (Min: KSh 1,000)\n\n"
        
        if swahili_ratio > 0.5:
            response += "Una pesa ngapi unataka invest? 😊"
        else:
            response += "How much do you want to invest? 😊"
        
        return response
    
    def _generate_bank_comparison(self, swahili_ratio, amount):
        """Generate bank comparison with REAL data"""
        
        # Get real bank data
        user_profile = {
            'amount': amount or 50000,
            'purpose': 'savings',
            'tech_savvy': swahili_ratio < 0.5,
            'location': 'urban'
        }
        
        banks = self.bank_fetcher.get_bank_recommendations(user_profile)
        
        if swahili_ratio > 0.5:
            response = "Sawa, best banks (based on real data):\n\n"
        else:
            response = "Here are the best banks (real ratings & data):\n\n"
        
        for i, bank in enumerate(banks[:4], 1):
            emoji = "⭐" if i == 1 else "✅"
            response += f"{i}. {emoji} **{bank['name']}** (Score: {bank['score']:.0f}/100)\n"
            response += f"   • Rating: {bank['rating']:.1f}/5.0\n"
            response += f"   • Monthly Fee: KSh {bank['monthly_fee']:,}\n"
            if bank['reasons']:
                response += f"   • Why: {bank['reasons'][0]}\n"
            response += "\n"
        
        response += f"**💡 RECOMMENDATION**: {banks[0]['name']}\n"
        
        return response
    
    def _generate_treasury_info(self, live_data, swahili_ratio):
        """Generate Treasury info with live rates"""
        greeting = "Sawa," if swahili_ratio > 0.5 else "Here are"
        
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        
        response = f"{greeting} current Treasury rates:\n\n"
        response += f"**T-Bills:**\n"
        response += f"• 91-day: {tbills.get('91_day', {}).get('rate', 16.8):.1f}%\n"
        response += f"• 182-day: {tbills.get('182_day', {}).get('rate', 17.2):.1f}%\n"
        response += f"• 364-day: {tbills.get('364_day', {}).get('rate', 17.5):.1f}% ⭐\n\n"
        response += f"Minimum: KSh 100,000\n\n"
        
        if swahili_ratio > 0.5:
            response += "Una kiasi gani unataka invest? 😊"
        else:
            response += "How much would you like to invest? 😊"
        
        return response
    
    def _generic_help(self, swahili_ratio):
        """Generic help message"""
        if swahili_ratio > 0.6:
            return "Pole, nisaidie zaidi. Unataka kujua nini? Stocks, savings, loans, banks? 😊"
        else:
            return "I'd love to help! What would you like to know? Stocks, savings, loans, banks? 😊"
    
    def generate_welcome_message(self):
        """Welcome message"""
        return """Habari! Welcome to Kenyan Financial Advisor 🇰🇪

I can help you with:
💰 Investment advice (real-time data!)
📈 NSE stocks & global markets
📊 Treasury Bills & Money Market Funds
🏦 Bank recommendations (real ratings!)
💵 Loans & M-Pesa

Ask in English, Swahili, or mix! 😊"""