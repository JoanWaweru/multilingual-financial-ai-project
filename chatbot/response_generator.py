"""
Production-Grade Response Generator
Handles ALL conversation scenarios with context awareness
"""

import sys
from pathlib import Path
import random
import logging

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Complete response generation system
    
    Handles:
    - Conversational context
    - Follow-up questions
    - Option selections
    - Affirmations (yes/no)
    - Return calculations
    - Short queries
    - Code-switching
    - Live data integration
    """
    
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
            'profit': 'faida',
            'returns': 'mapato',
            'interest': 'riba'
        }
    
    def generate_conversational_response(self, user_query, analysis, context, live_data, language_pattern):
        """
        MAIN CONVERSATIONAL ROUTING
        
        This is the BRAIN of conversational flow
        Handles ALL context-aware responses
        
        Priority Order:
        1. Affirmations (yes/no)
        2. Option selections (1, 2, 3)
        3. Return calculations (follow-up)
        4. Disagreements (no, but, instead)
        5. Short follow-ups (context-dependent)
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        # ================================================================
        # PRIORITY 1: AFFIRMATIONS (YES/NO)
        # ================================================================
        affirmation = context.detect_affirmation(user_query)
        if affirmation:
            return self._handle_affirmation(affirmation, context, swahili_ratio)
        
        # ================================================================
        # PRIORITY 2: OPTION SELECTION
        # ================================================================
        option_num = context.detect_option_selection(user_query)
        if option_num:
            return self._handle_option_selection(option_num, context, swahili_ratio, live_data)
        
        # ================================================================
        # PRIORITY 3: RETURN CALCULATION (FOLLOW-UP)
        # ================================================================
        if self._is_asking_about_returns(user_query):
            if context.has_context() and context.last_amount:
                return self._generate_return_calculation(context, swahili_ratio)
        
        # ================================================================
        # PRIORITY 4: DISAGREEMENT/PREFERENCE CHANGE
        # ================================================================
        if context.detect_disagreement(user_query):
            context.detect_investment_style_preference(user_query)
            
            if context.user_preferences['investment_style'] == 'single':
                return self._generate_single_investment_advice(
                    analysis['amount'] or context.last_amount,
                    context,
                    live_data,
                    swahili_ratio
                )
        
        # ================================================================
        # PRIORITY 5: SHORT FOLLOW-UP (USING CONTEXT)
        # ================================================================
        if analysis['is_short'] and context.has_context():
            # Just a number - user answering "how much?"
            if analysis['amount'] and len(user_query.split()) <= 2:
                return self._handle_amount_follow_up(
                    analysis['amount'],
                    context,
                    live_data,
                    swahili_ratio
                )
        
        # No conversational context matched - use normal flow
        return None
    
    def _is_asking_about_returns(self, user_query: str) -> bool:
        """Check if asking about returns/profits"""
        return_keywords = [
            'how much', 'nitapata', 'return', 'profit', 'expect',
            'after', 'year', 'get back', 'mapato', 'faida',
            'calculate', 'total', 'itakuwa', 'will be'
        ]
        query_lower = user_query.lower()
        return any(keyword in query_lower for keyword in return_keywords)
    
    def _handle_affirmation(self, affirmation: str, context, swahili_ratio: float) -> str:
        """
        Handle YES/NO based on what we last discussed
        
        Looks at conversation history to understand context
        """
        
        logger.info(f"Handling affirmation: {affirmation}")
        
        is_yes = (affirmation == 'yes')
        
        # Get last exchange
        last_exchange = context.get_last_exchange()
        if not last_exchange:
            return self._generic_affirmation_response(is_yes, swahili_ratio)
        
        last_bot = last_exchange['bot'].lower()
        
        # ============================================================
        # CONTEXT 1: CDS Account Help
        # ============================================================
        if 'cds' in last_bot and 'help' in last_bot:
            if is_yes:
                response = "Poa! " if swahili_ratio > 0.5 else "Great! "
                response += "Here's how to open a CDS account:\n\n"
                
                response += "**OPTION A: Through Your Bank** (Easiest)\n"
                response += "1. Visit any bank where you have account (Equity, KCB, Co-op)\n"
                response += "2. Ask: \"I want to open a CDS account\"\n"
                response += "3. Bring: ID, KRA PIN\n"
                response += "4. Pay: ~KSh 1,100 registration\n"
                response += "5. Wait: 1-2 days activation\n\n"
                
                response += "**OPTION B: Direct with CBK**\n"
                response += "1. Go to: centralbank.go.ke\n"
                response += "2. Download CDS form\n"
                response += "3. Submit online or visit CBK office\n\n"
                
                response += "**💡 Recommendation**: Use your bank - much faster!\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Una account ya bank? 😊"
                else:
                    response += "Do you have a bank account? 😊"
                
                return response
            else:
                if swahili_ratio > 0.5:
                    return "Sawa, hakuna shida! Kuna kitu kingine ninaweza kukusaidia? 😊"
                else:
                    return "No problem! Is there anything else I can help you with? 😊"
        
        # ============================================================
        # CONTEXT 2: MMF Account Help
        # ============================================================
        if any(word in last_bot for word in ['mmf', 'money market', 'sanlam', 'cic', 'britam']):
            if 'link' in last_bot or 'account' in last_bot:
                if is_yes:
                    response = "Poa! " if swahili_ratio > 0.5 else "Great! "
                    response += "Here are the direct links:\n\n"
                    
                    response += "**1. Sanlam MMF** (11.2% - Highest rate!)\n"
                    response += "   🔗 https://sanlaminvestments.com\n"
                    response += "   📱 Min: KSh 1,000\n"
                    response += "   ⏱️ Process: 100% online, 24hrs\n\n"
                    
                    response += "**2. CIC MMF** (10.8%)\n"
                    response += "   🔗 https://cicgroup.co.ke/investments\n"
                    response += "   📱 Min: KSh 5,000\n"
                    response += "   ⏱️ Process: Online + ID upload\n\n"
                    
                    response += "**3. Britam MMF** (10.5%)\n"
                    response += "   🔗 https://britam.com/investments\n"
                    response += "   📱 Min: KSh 1,000\n\n"
                    
                    response += "**Quick Steps:**\n"
                    response += "1. Click link above\n"
                    response += "2. Find 'Register' or 'Open Account'\n"
                    response += "3. Fill form (5 mins)\n"
                    response += "4. Upload ID photo\n"
                    response += "5. Fund via M-Pesa!\n\n"
                    
                    if swahili_ratio > 0.5:
                        response += "Ungependa nisaidie na registration? 😊"
                    else:
                        response += "Need help with registration? 😊"
                    
                    return response
        
        # ============================================================
        # CONTEXT 3: Bank Account Question
        # ============================================================
        if 'bank account' in last_bot and '?' in last_bot:
            if is_yes:
                if swahili_ratio > 0.5:
                    return "Poa! Basi unaweza enda bank yako direct na kufungua CDS account. Itachukua siku 1-2 tu. Una bank gani? 😊"
                else:
                    return "Perfect! You can go directly to your bank and open a CDS account. It takes just 1-2 days. Which bank do you use? 😊"
            else:
                if swahili_ratio > 0.5:
                    return "Sawa, lazima ufungue bank account kwanza. Ungependa recommendations za banks? 😊"
                else:
                    return "Okay, you'll need to open a bank account first. Would you like bank recommendations? 😊"
        
        # ============================================================
        # CONTEXT 4: Generic follow-up
        # ============================================================
        return self._generic_affirmation_response(is_yes, swahili_ratio)
    
    def _generic_affirmation_response(self, is_yes: bool, swahili_ratio: float) -> str:
        """Generic yes/no response"""
        
        if is_yes:
            if swahili_ratio > 0.5:
                return "Sawa! Nikusaidie na nini zaidi? 😊"
            else:
                return "Great! What else can I help you with? 😊"
        else:
            if swahili_ratio > 0.5:
                return "Hakuna shida! Kuna swali lingine? 😊"
            else:
                return "No worries! Any other questions? 😊"
    
    def _handle_option_selection(self, option_num: int, context, swahili_ratio: float, live_data) -> str:
        """
        Handle when user selects option 1, 2, or 3
        
        Provides detailed breakdown and next steps
        """
        
        logger.info(f"Handling option selection: {option_num}")
        
        greeting = "Poa choice!" if swahili_ratio > 0.5 else "Great choice!"
        
        # Must have investment context
        if not context.last_amount:
            if swahili_ratio > 0.5:
                return f"{greeting} Remind me - tulikuwa tunaongea kuhusu investment ya kiasi gani? 😊"
            else:
                return f"{greeting} Could you remind me - what amount were we discussing? 😊"
        
        amount = context.last_amount
        
        # Get current rates
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        tbill_rate = tbills.get('364_day', {}).get('rate', 17.5)
        
        mmf_analysis = live_data.get('mmf_analysis', {}) if live_data else {}
        best_mmf = mmf_analysis.get('best')
        mmf_rate = best_mmf['rate'] if best_mmf else 11.0
        mmf_name = best_mmf['name'] if best_mmf else "Money Market Fund"
        
        # ============================================================
        # OPTION 1: TREASURY BILLS
        # ============================================================
        if option_num == 1:
            response = f"{greeting} Treasury Bills are excellent! Here's your complete plan:\n\n"
            
            response += f"**💰 YOUR INVESTMENT**\n"
            response += f"Amount: KSh {amount:,}\n"
            response += f"Rate: {tbill_rate:.1f}% per year\n"
            response += f"Profit: KSh {int(amount * (tbill_rate/100)):,}\n"
            response += f"Total after 1 year: KSh {int(amount * (1 + tbill_rate/100)):,}\n\n"
            
            response += f"**📋 HOW TO INVEST (Step by Step)**\n\n"
            response += f"**Step 1: Open CDS Account**\n"
            response += f"• Go to your bank (Equity, KCB, Co-op, etc.)\n"
            response += f"• Say: \"I want a CDS account for T-Bills\"\n"
            response += f"• Bring: National ID, KRA PIN\n"
            response += f"• Pay: ~KSh 1,100 registration\n"
            response += f"• Time: 1-2 days to activate\n\n"
            
            response += f"**Step 2: Fund Your CDS Account**\n"
            response += f"• Transfer KSh {amount:,} from your bank to CDS account\n"
            response += f"• Your bank will help with this\n\n"
            
            response += f"**Step 3: Buy T-Bills**\n"
            response += f"• T-Bill auctions happen every Tuesday\n"
            response += f"• Tell your bank: \"Buy 364-day T-Bills\"\n"
            response += f"• Or use CBK online portal\n"
            response += f"• Money auto-debited on auction day\n\n"
            
            response += f"**Step 4: Wait & Earn**\n"
            response += f"• Money locked for 364 days\n"
            response += f"• After 1 year: Get KSh {int(amount * (1 + tbill_rate/100)):,}\n"
            response += f"• Interest taxed at 15%\n\n"
            
            response += f"**✅ BENEFITS**\n"
            response += f"• 100% government-backed (safest investment!)\n"
            response += f"• Highest guaranteed returns in Kenya\n"
            response += f"• No fees, no hidden charges\n\n"
            
            response += f"**⚠️ IMPORTANT**\n"
            response += f"• Cannot withdraw before 364 days\n"
            response += f"• Minimum: KSh 100,000\n"
            response += f"• Interest is taxable\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa nisaidie na CDS account process? 😊"
            else:
                response += f"Would you like help with opening the CDS account? 😊"
            
            return response
        
        # ============================================================
        # OPTION 2: MONEY MARKET FUND
        # ============================================================
        elif option_num == 2:
            response = f"{greeting} {mmf_name} is perfect for flexibility! Here's your plan:\n\n"
            
            response += f"**💰 YOUR INVESTMENT**\n"
            response += f"Amount: KSh {amount:,}\n"
            response += f"Rate: {mmf_rate:.1f}% per year\n"
            response += f"Profit: KSh {int(amount * (mmf_rate/100)):,}\n"
            response += f"Total after 1 year: KSh {int(amount * (1 + mmf_rate/100)):,}\n\n"
            
            response += f"**🏆 TOP MMF OPTIONS**\n\n"
            response += f"**1. Sanlam MMF** (11.2%) ⭐ BEST\n"
            response += f"   Min: KSh 1,000\n"
            response += f"   Liquidity: Withdraw anytime (1-2 days)\n"
            response += f"   Website: sanlaminvestments.com\n\n"
            
            response += f"**2. CIC MMF** (10.8%)\n"
            response += f"   Min: KSh 5,000\n"
            response += f"   Liquidity: 1-2 days\n"
            response += f"   Website: cicgroup.co.ke/investments\n\n"
            
            response += f"**3. Britam MMF** (10.5%)\n"
            response += f"   Min: KSh 1,000\n"
            response += f"   Liquidity: 2-3 days\n"
            response += f"   Website: britam.com/investments\n\n"
            
            response += f"**📋 HOW TO INVEST (Step by Step)**\n\n"
            response += f"**Step 1: Choose MMF**\n"
            response += f"• Recommendation: Sanlam (highest rate + lowest min)\n\n"
            
            response += f"**Step 2: Register Online**\n"
            response += f"• Visit: sanlaminvestments.com\n"
            response += f"• Click 'Open Account' or 'Register'\n"
            response += f"• Fill form (Name, ID, Phone, Email, KRA PIN)\n"
            response += f"• Upload ID photo (clear photo)\n"
            response += f"• Time: 5-10 minutes\n\n"
            
            response += f"**Step 3: Account Verification**\n"
            response += f"• Wait for approval email/SMS (24-48 hours)\n"
            response += f"• You'll get account number\n\n"
            
            response += f"**Step 4: Fund Your Account**\n"
            response += f"• M-Pesa: Send to MMF paybill\n"
            response += f"• Bank: Transfer to account number\n"
            response += f"• Amount: KSh {amount:,}\n\n"
            
            response += f"**Step 5: Watch It Grow**\n"
            response += f"• Interest calculated daily\n"
            response += f"• Can withdraw anytime to M-Pesa!\n"
            response += f"• No lock-in period\n\n"
            
            response += f"**✅ BENEFITS**\n"
            response += f"• Withdraw anytime (super flexible!)\n"
            response += f"• Much better than bank savings (2-5%)\n"
            response += f"• Low minimum (KSh 1,000)\n"
            response += f"• Daily interest calculation\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa links za kufungua account? 😊"
            else:
                response += f"Would you like the registration links? 😊"
            
            return response
        
        # ============================================================
        # OPTION 3: SACCO
        # ============================================================
        elif option_num == 3:
            response = f"{greeting} SACCO is smart for getting loans! Here's your plan:\n\n"
            
            response += f"**💰 YOUR INVESTMENT**\n"
            response += f"Amount: KSh {amount:,}\n"
            response += f"Dividends: ~10% per year\n"
            response += f"Profit: KSh {int(amount * 0.10):,}\n"
            response += f"Total after 1 year: KSh {int(amount * 1.10):,}\n\n"
            
            response += f"**🎁 BONUS BENEFIT**\n"
            response += f"After 6 months, qualify for loans up to:\n"
            response += f"**KSh {int(amount * 3):,}** (3x your deposit!)\n"
            response += f"At low interest: 12-14% vs 15-20% at banks\n\n"
            
            response += f"**🏆 TOP SACCO OPTIONS**\n\n"
            response += f"**1. Stima SACCO**\n"
            response += f"   • Open to public\n"
            response += f"   • Good returns + reliable\n"
            response += f"   • Strong loan program\n\n"
            
            response += f"**2. Mwalimu SACCO**\n"
            response += f"   • For teachers (but open to all)\n"
            response += f"   • Excellent dividends\n"
            response += f"   • Very stable\n\n"
            
            response += f"**3. Kenya Police SACCO**\n"
            response += f"   • Open to public\n"
            response += f"   • Competitive rates\n"
            response += f"   • Good customer service\n\n"
            
            response += f"**4. Harambee SACCO**\n"
            response += f"   • Accessible to everyone\n"
            response += f"   • No restrictions\n\n"
            
            response += f"**📋 HOW TO JOIN (Step by Step)**\n\n"
            response += f"**Step 1: Choose SACCO**\n"
            response += f"• Check if your employer has one (best option)\n"
            response += f"• Or choose from list above\n\n"
            
            response += f"**Step 2: Visit Branch**\n"
            response += f"• Bring: National ID, Payslip (if employed)\n"
            response += f"• Ask: \"I want to join SACCO\"\n\n"
            
            response += f"**Step 3: Registration**\n"
            response += f"• Fill membership form\n"
            response += f"• Pay registration: KSh 500-1,000\n"
            response += f"• Buy shares: Your KSh {amount:,} becomes shares\n\n"
            
            response += f"**Step 4: Start Earning**\n"
            response += f"• Dividends paid quarterly or annually\n"
            response += f"• Attend AGM (Annual General Meeting)\n"
            response += f"• Vote on SACCO decisions\n\n"
            
            response += f"**✅ BENEFITS**\n"
            response += f"• Get dividends (10-12%)\n"
            response += f"• Qualify for cheap loans (3x deposit)\n"
            response += f"• Build credit history\n"
            response += f"• You own part of SACCO\n\n"
            
            response += f"**⚠️ NOTES**\n"
            response += f"• Less liquid than MMF\n"
            response += f"• Withdrawal may take 1-2 weeks\n"
            response += f"• But loan access makes up for it!\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa kusaidia kutafuta SACCO karibu na wewe? 😊"
            else:
                response += f"Need help finding a SACCO near you? 😊"
            
            return response
        
        # Unknown option
        return self._generic_affirmation_response(True, swahili_ratio)
    
    def _handle_amount_follow_up(self, amount: int, context, live_data, swahili_ratio: float) -> str:
        """
        Handle when user just states an amount as follow-up
        
        Example:
        Bot: "How much do you want to invest?"
        User: "50k"
        """
        
        logger.info(f"Handling amount follow-up: {amount}")
        
        # Generate investment advice with this amount
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
        Generate advice for ONE place investment
        
        User rejected diversification
        """
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Got it,"
        
        # If no amount, ask
        if not amount:
            if swahili_ratio > 0.5:
                return f"{greeting} unataka kuweka pesa yote mahali pamoja. Ni kiasi gani? 😊"
            else:
                return f"{greeting} you want to put everything in one place. How much are you investing? 😊"
        
        response = f"{greeting} you want to invest ALL KSh {amount:,} in ONE place.\n\n"
        response += f"Here are your best single-investment options:\n\n"
        
        # Get rates
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        tbill_rate = tbills.get('364_day', {}).get('rate', 17.5)
        
        mmf_analysis = live_data.get('mmf_analysis', {}) if live_data else {}
        best_mmf = mmf_analysis.get('best')
        mmf_rate = best_mmf['rate'] if best_mmf else 11.0
        mmf_name = best_mmf['name'] if best_mmf else "Money Market Fund"
        
        # Option 1: Treasury Bills
        response += f"**OPTION 1: Treasury Bills (364-day)** ⭐ RECOMMENDED\n"
        response += f"   📍 Invest: KSh {amount:,}\n"
        response += f"   💰 Rate: {tbill_rate:.1f}% per year\n"
        response += f"   📈 After 1 year: KSh {int(amount * (1 + tbill_rate/100)):,}\n"
        response += f"   💵 Profit: KSh {int(amount * (tbill_rate/100)):,}\n"
        response += f"   ✅ Government-backed (100% safe)\n"
        response += f"   ⚠️ Locked for 1 year\n\n"
        
        # Option 2: MMF
        response += f"**OPTION 2: {mmf_name}**\n"
        response += f"   📍 Invest: KSh {amount:,}\n"
        response += f"   💰 Rate: {mmf_rate:.1f}% per year\n"
        response += f"   📈 After 1 year: KSh {int(amount * (1 + mmf_rate/100)):,}\n"
        response += f"   💵 Profit: KSh {int(amount * (mmf_rate/100)):,}\n"
        response += f"   ✅ Withdraw anytime (flexible!)\n"
        response += f"   ⚠️ Lower return than T-Bills\n\n"
        
        # Option 3: SACCO (if amount >= 20k)
        if amount >= 20000:
            response += f"**OPTION 3: SACCO Deposit**\n"
            response += f"   📍 Invest: KSh {amount:,}\n"
            response += f"   💰 Rate: ~10% dividends\n"
            response += f"   📈 After 1 year: KSh {int(amount * 1.10):,}\n"
            response += f"   💵 Profit: KSh {int(amount * 0.10):,}\n"
            response += f"   🎁 BONUS: Loans up to KSh {int(amount * 3):,}!\n"
            response += f"   ⚠️ Less liquid than MMF\n\n"
        
        # Recommendation
        response += f"**💡 MY RECOMMENDATION**: "
        if amount >= 100000:
            response += f"Treasury Bills - highest guaranteed return ({tbill_rate:.1f}%)"
        elif amount >= 50000:
            response += f"SACCO - good returns PLUS loan access"
        else:
            response += f"{mmf_name} - flexible with {mmf_rate:.1f}% returns"
        
        response += f"\n\n"
        
        if swahili_ratio > 0.5:
            response += f"Option gani inakupendeza? (Andika 1, 2, au 3) 😊"
        else:
            response += f"Which option interests you? (Type 1, 2, or 3) 😊"
        
        # Save context
        context.save_investment_context(amount, {}, ['option 1', 'option 2', 'option 3'])
        
        return response
    
    def _generate_return_calculation(self, context, swahili_ratio):
        """Calculate and explain returns"""
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Good question!"
        
        returns = context.calculate_expected_returns()
        
        if not returns:
            if swahili_ratio > 0.5:
                return f"{greeting} nisaidie - unataka invest kiasi gani na wapi? Nitakucalculate returns! 😊"
            else:
                return f"{greeting} let me know how much you're investing and where, I'll calculate returns! 😊"
        
        response = f"{greeting} based on KSh {returns['initial_amount']:,}:\n\n"
        
        if returns['breakdown']:
            response += f"**Expected Returns After 1 Year:**\n\n"
            
            for name, data in returns['breakdown'].items():
                response += f"• **{name}**:\n"
                response += f"  Invested: KSh {data['invested']:,}\n"
                response += f"  Return: KSh {data['return']:,} ({data['rate']*100:.1f}%)\n"
                response += f"  Total: KSh {data['total']:,}\n\n"
        
        response += f"**💰 TOTAL EXPECTED:**\n"
        response += f"   Initial: KSh {returns['initial_amount']:,}\n"
        response += f"   Profit: KSh {returns['total_return']:,}\n"
        response += f"   Final: KSh {returns['final_amount']:,}\n"
        response += f"   Return: {returns['overall_rate']:.1f}%\n\n"
        
        if swahili_ratio > 0.5:
            response += f"💡 Hizi ni estimated returns. Actual inategemea market!"
        else:
            response += f"💡 These are estimated. Actual may vary with market conditions."
        
        return response
    
    def generate_response(self, knowledge_result, user_language_pattern, 
                         include_proverb=False, user_query=None, live_data=None, context=None):
        """
        Main response generation for knowledge base matches
        
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
        if random.random() < 0.5:
            response += f" {self.phrases.get_encouragement()}"
        
        # Add proverb
        if include_proverb and random.random() < 0.7:
            proverb = self.phrases.get_random_proverb()
            response += f"\n\n💡 \"{proverb['swahili']}\" ({proverb['english']}) - {proverb['meaning']}"
        
        return response
    
    def _add_greeting(self, language_pattern):
        """Add greeting"""
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        if swahili_ratio > 0.6:
            return self.phrases.get_transition()
        elif swahili_ratio < 0.3:
            return random.choice(['Okay,', 'Alright,', 'Sure,'])
        else:
            return self.phrases.get_transition()
    
    def _adapt_language(self, text, language_pattern):
        """Adapt to user's language mix"""
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        if swahili_ratio > 0.4:
            for eng, sw in self.swahili_terms.items():
                if random.random() < swahili_ratio and eng in text.lower():
                    text = text.replace(eng, sw, 1)
        
        return text
    
    def _is_market_related(self, category: str) -> bool:
        """Check if benefits from live data"""
        market_categories = ['stocks', 'etfs', 'investment', 'global_stocks', 'savings']
        return category in market_categories if category else False
    
    def _enhance_with_live_data(self, answer: str, live_data: dict) -> str:
        """Add live data snippet"""
        enhancement = ""
        
        if live_data.get('market_summary'):
            summary = live_data['market_summary']
            enhancement += f"\n\n📊 NSE: {summary['emoji']} {summary['sentiment']} (Avg: {summary['avg_change']:+.1f}%)"
        
        return answer + enhancement
    
    def _generate_fallback_response(self, language_pattern, user_query=None, live_data=None, context=None):
        """
        Intelligent fallback - HANDLES ALL INTENTS
        
        This is the SAFETY NET
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        greeting = self.phrases.get_transition() if swahili_ratio > 0.5 else "Alright,"
        
        if not user_query:
            return self._generic_help(swahili_ratio)
        
        # Analyze with context
        analysis = self.intent_analyzer.analyze(user_query, context)
        
        # ============================================================
        # HANDLE EACH INTENT
        # ============================================================
        
        # MMF Query
        if analysis['intent'] == 'mmf_query':
            return self._generate_mmf_comparison(live_data, swahili_ratio)
        
        # Bank Comparison
        if analysis['intent'] == 'bank_comparison':
            return self._generate_bank_comparison(swahili_ratio, analysis['amount'])
        
        # Investment Advice
        if analysis['intent'] == 'investment_advice':
            advice = self.advisor.generate_investment_advice(
                amount=analysis['amount'],
                goal=analysis['goal'],
                urgency=analysis['urgency'],
                language_mix=swahili_ratio,
                live_data=live_data
            )
            return f"{greeting} {advice}"
        
        # Stock Queries
        if analysis['intent'] in ['stock_query', 'stock_recommendation']:
            advice = self.advisor.generate_stock_advice(
                amount=analysis['amount'],
                experience='beginner',
                market='nse',
                language_mix=swahili_ratio,
                live_data=live_data
            )
            return f"{greeting} {advice}"
        
        # Global Stocks
        if analysis['intent'] == 'global_stocks_query':
            advice = self.advisor.generate_stock_advice(
                amount=analysis['amount'],
                experience='beginner',
                market='international',
                language_mix=swahili_ratio,
                live_data=live_data
            )
            return f"{greeting} {advice}"
        
        # ETF Query
        if analysis['intent'] == 'etf_query':
            if swahili_ratio > 0.5:
                return f"{greeting} ETFs ni baskets ya stocks bought as one. Kenya ina limited local ETFs, lakini unaweza access global ETFs (S&P 500, Vanguard) kupitia international brokers like Interactive Brokers. Minimum: $100-500. Alternatively, consider local unit trusts (CIC, Sanlam)! 😊"
            else:
                return f"{greeting} ETFs are baskets of stocks bought as one investment. Kenya has limited local ETFs, but you can access global ETFs through international brokers. Popular ones: S&P 500 (SPY, VOO). Consider local unit trusts as alternatives! 😊"
        
        # Treasury Query
        if analysis['intent'] == 'treasury_query':
            treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
            tbills = treasury_rates.get('treasury_bills', {})
            
            response = f"{greeting} current Treasury rates:\n\n"
            response += f"**T-Bills:**\n"
            response += f"• 91-day: {tbills.get('91_day', {}).get('rate', 16.8):.1f}%\n"
            response += f"• 182-day: {tbills.get('182_day', {}).get('rate', 17.2):.1f}%\n"
            response += f"• 364-day: {tbills.get('364_day', {}).get('rate', 17.5):.1f}% ⭐\n\n"
            response += f"Minimum: KSh 100,000\n"
            response += f"Risk: Zero (government-backed)\n\n"
            
            if swahili_ratio > 0.5:
                response += f"Ungependa kusave pesa ngapi? 😊"
            else:
                response += f"How much would you like to invest? 😊"
            
            return response
        
        # Generic fallback
        return self._generic_help(swahili_ratio)
    
    def _generate_mmf_comparison(self, live_data, swahili_ratio):
        """MMF comparison"""
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Here are"
        response = f"{greeting} the top Money Market Funds:\n\n"
        
        if live_data and live_data.get('mmf_rates'):
            mmf_rates = live_data['mmf_rates']
            sorted_mmfs = sorted(mmf_rates.items(), key=lambda x: x[1]['current_rate'], reverse=True)
            
            for i, (name, data) in enumerate(sorted_mmfs, 1):
                emoji = "⭐" if i == 1 else "✅"
                response += f"{i}. {emoji} **{name}**\n"
                response += f"   Rate: {data['current_rate']}%\n"
                response += f"   Min: KSh {data['minimum']:,}\n"
                response += f"   Liquidity: {data['liquidity']}\n\n"
        else:
            response += "1. ⭐ **Sanlam MMF** - 11.2% (Min: 1k)\n"
            response += "2. ✅ **CIC MMF** - 10.8% (Min: 5k)\n"
            response += "3. ✅ **Britam MMF** - 10.5% (Min: 1k)\n\n"
        
        if swahili_ratio > 0.5:
            response += "Una pesa ngapi unataka save? 😊"
        else:
            response += "How much do you want to invest? 😊"
        
        return response
    
    def _generate_bank_comparison(self, swahili_ratio, amount):
        """Bank comparison"""
        
        if swahili_ratio > 0.5:
            response = "Sawa, best banks in Kenya:\n\n"
        else:
            response = "Here are the best banks:\n\n"
        
        response += "1. ⭐ **Equity Bank** - Low fees, most accessible\n"
        response += "2. ✅ **KCB** - Largest, reliable\n"
        response += "3. ✅ **Co-operative Bank** - Good for chamas\n"
        response += "4. ✅ **NCBA** - Modern digital banking\n\n"
        
        response += "**💡 Recommendation**: "
        if amount and amount < 50000:
            response += "Equity Bank (lowest fees)"
        else:
            response += "KCB or Equity (both excellent)"
        
        return response
    
    def _generic_help(self, swahili_ratio):
        """Generic help message"""
        if swahili_ratio > 0.6:
            return "Pole, nisaidie zaidi. Unataka kujua kuhusu nini? Stocks, savings, M-Pesa, loans? 😊"
        else:
            return "I'd love to help! What would you like to know? Stocks, savings, M-Pesa, loans? 😊"
    
    def generate_welcome_message(self):
        """Welcome message"""
        return """Habari! Welcome to Kenyan Financial Advisor 🇰🇪

I can help you with:
💰 Investment advice (with live data!)
📈 NSE stocks & global markets
📊 Treasury Bills & Money Market Funds
💵 Loans & M-Pesa
🏦 Banks & SACCOs

Ask in English, Swahili, or mix! 😊"""