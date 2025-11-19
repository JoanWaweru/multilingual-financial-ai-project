"""
Enhanced Response Generator with Conversational Intelligence
Handles code-switching, context awareness, and natural dialogue
"""

import sys
from pathlib import Path
import random

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

class ResponseGenerator:
    """
    Generate responses with:
    - Adaptive code-switching
    - Conversational context awareness
    - Option selection handling
    - Follow-up question support
    - Live data integration
    """
    
    def __init__(self):
        self.phrases = KenyanPhrases()
        self.intent_analyzer = IntentAnalyzer()
        self.advisor = DynamicFinancialAdvisor()
        
        # Swahili financial terms for code-switching
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
            'interest': 'riba',
            'profit': 'faida',
            'returns': 'mapato'
        }
    
    def generate_conversational_response(self, user_query, analysis, context, live_data, language_pattern):
        """
        Generate conversational response that adapts to dialogue flow
        
        This is the KEY method that makes the chatbot feel conversational!
        
        Args:
            user_query: User's message
            analysis: Intent analysis result
            context: Conversation context
            live_data: Live market data
            language_pattern: Detected language pattern
        
        Returns:
            str: Conversational response or None (fall through)
        """
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        
        # Priority 1: Check if user is selecting an option
        if self._is_option_selection(user_query):
            return self._handle_option_selection(user_query, context, swahili_ratio)
        
        # Priority 2: Check if user is disagreeing/rejecting advice
        if context.detect_disagreement(user_query):
            # Learn what they prefer
            context.detect_investment_style_preference(user_query)
            
            # Generate alternative based on their preference
            if context.user_preferences['investment_style'] == 'single':
                # User wants ONE place for ALL money
                return self._generate_single_investment_advice(
                    analysis['amount'],
                    context,
                    live_data,
                    swahili_ratio
                )
        
        # Priority 3: Check for return calculation questions (follow-up)
        return_keywords = [
            'how much', 'nitapata', 'return', 'profit', 'expect', 
            'after', 'year', 'get back', 'returns', 'faida',
            'mapato', 'calculate', 'total'
        ]
        if any(keyword in user_query.lower() for keyword in return_keywords):
            if context.has_context() and context.last_amount:
                return self._generate_return_calculation(context, swahili_ratio)
        
        # No conversational context detected - return None to use normal flow
        return None
    
    def _is_option_selection(self, user_query: str) -> bool:
        """
        Check if user is selecting an option from previous suggestions
        
        Detects patterns like:
        - "option 1", "option 2", "option 3"
        - "1", "2", "3"
        - "first option", "second option"
        - "the first one"
        """
        
        query_lower = user_query.lower().strip()
        
        # Check for option patterns
        option_patterns = [
            'option 1', 'option 2', 'option 3',
            'option one', 'option two', 'option three',
            'first option', 'second option', 'third option',
            'the first', 'the second', 'the third',
            'number 1', 'number 2', 'number 3',
            'choice 1', 'choice 2', 'choice 3'
        ]
        
        # Short queries that are likely option selections
        if len(query_lower.split()) <= 3:
            # Check if it's just a number
            if query_lower in ['1', '2', '3', 'one', 'two', 'three']:
                return True
            
            # Check option patterns
            return any(pattern in query_lower for pattern in option_patterns)
        
        return False
    
    def _handle_option_selection(self, user_query: str, context, swahili_ratio: float) -> str:
        """
        Handle when user selects an option
        
        Provides detailed information about the selected option
        """
        
        greeting = "Poa!" if swahili_ratio > 0.5 else "Great choice!"
        
        query_lower = user_query.lower()
        
        # Determine which option
        if '1' in query_lower or 'first' in query_lower or 'one' in query_lower:
            option_num = 1
        elif '2' in query_lower or 'second' in query_lower or 'two' in query_lower:
            option_num = 2
        elif '3' in query_lower or 'third' in query_lower or 'three' in query_lower:
            option_num = 3
        else:
            option_num = 1  # Default to first
        
        # Check if we were discussing investments
        if context.last_amount:
            amount = context.last_amount
            
            if option_num == 1:
                # Treasury Bills
                response = f"{greeting} Treasury Bills are an excellent choice! Here's what you need to know:\n\n"
                response += f"**💰 Investment**: KSh {amount:,}\n"
                response += f"**📈 Expected Return**: 17.5% per year\n"
                response += f"**💵 Profit**: KSh {int(amount * 0.175):,}\n"
                response += f"**🏦 Total after 1 year**: KSh {int(amount * 1.175):,}\n\n"
                
                response += "**How to invest:**\n"
                response += "1. Open a CDS account at your bank or CBK\n"
                response += "2. Fund your account (minimum KSh 100,000)\n"
                response += "3. Buy 364-day T-Bills during weekly auction (Tuesdays)\n"
                response += "4. Money is locked for 1 year\n"
                response += "5. Get principal + interest at maturity\n\n"
                
                response += "**✅ Benefits:**\n"
                response += "• Government-backed (100% safe)\n"
                response += "• Highest guaranteed returns\n"
                response += "• Interest is taxable at 15%\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Ungependa kusaidia na CDS account process? 😊"
                else:
                    response += "Would you like help with the CDS account process? 😊"
            
            elif option_num == 2:
                # Money Market Fund
                response = f"{greeting} Money Market Funds are perfect for flexibility! Here's the breakdown:\n\n"
                response += f"**💰 Investment**: KSh {amount:,}\n"
                response += f"**📈 Expected Return**: ~11% per year\n"
                response += f"**💵 Profit**: KSh {int(amount * 0.11):,}\n"
                response += f"**🏦 Total after 1 year**: KSh {int(amount * 1.11):,}\n\n"
                
                response += "**Top MMFs to consider:**\n"
                response += "1. **Sanlam MMF** - 11.2% (Min: KSh 1,000)\n"
                response += "   Website: sanlaminvestments.com\n"
                response += "2. **CIC MMF** - 10.8% (Min: KSh 5,000)\n"
                response += "   Website: cicgroup.co.ke\n"
                response += "3. **Britam MMF** - 10.5% (Min: KSh 1,000)\n"
                response += "   Website: britam.com\n\n"
                
                response += "**How to invest:**\n"
                response += "1. Visit fund website (e.g., sanlaminvestments.com)\n"
                response += "2. Fill registration form online\n"
                response += "3. Upload ID and KRA PIN\n"
                response += "4. Deposit via M-Pesa or bank transfer\n"
                response += "5. Can withdraw to M-Pesa in 1-2 days!\n\n"
                
                response += "**✅ Benefits:**\n"
                response += "• Withdraw anytime (very liquid)\n"
                response += "• Better than bank savings\n"
                response += "• Low minimum investment\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Ungependa link ya kufungua account? 😊"
                else:
                    response += "Would you like me to guide you through opening an account? 😊"
            
            elif option_num == 3:
                # SACCO
                response = f"{greeting} SACCOs are smart for getting loans later! Here's the plan:\n\n"
                response += f"**💰 Investment**: KSh {amount:,}\n"
                response += f"**📈 Expected Return**: ~10% dividends\n"
                response += f"**💵 Profit**: KSh {int(amount * 0.10):,}\n"
                response += f"**🏦 Total after 1 year**: KSh {int(amount * 1.10):,}\n\n"
                
                response += f"**🎁 BONUS**: After 6 months, qualify for loans up to KSh {int(amount * 3):,} (3x your deposit)!\n\n"
                
                response += "**Popular SACCOs:**\n"
                response += "1. **Stima SACCO** - Good returns, reliable\n"
                response += "2. **Mwalimu SACCO** - For teachers, open to public\n"
                response += "3. **Kenya Police SACCO** - Excellent rates\n"
                response += "4. **Harambee SACCO** - Accessible to anyone\n\n"
                
                response += "**How to join:**\n"
                response += "1. Choose a SACCO (check if employer has one)\n"
                response += "2. Visit branch with ID\n"
                response += "3. Pay registration fee (KSh 500-1,000)\n"
                response += "4. Buy shares (your deposit becomes shares)\n"
                response += "5. Start earning dividends quarterly\n\n"
                
                if swahili_ratio > 0.5:
                    response += "Nataka kukuonesha nearest SACCO? 😊"
                else:
                    response += "Need help finding a SACCO near you? 😊"
            
            return response
        
        # Generic option selection (no context)
        if swahili_ratio > 0.5:
            return f"{greeting} Nikusaidie vizuri, remind me - tulikuwa tunaongea kuhusu nini? 😊"
        else:
            return f"{greeting} Could you remind me which options we were discussing? I want to give you the best details! 😊"
    
    def _generate_single_investment_advice(self, amount, context, live_data, swahili_ratio):
        """
        Generate advice for putting ALL money in ONE place
        
        User explicitly rejected diversification
        """
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Got it,"
        
        # If no amount, use context or ask
        if not amount:
            if context.last_amount:
                amount = context.last_amount
            else:
                if swahili_ratio > 0.5:
                    return f"{greeting} unataka kuweka pesa yote mahali pamoja. Ni kiasi gani? Nitakusaidia kuchagua best option! 😊"
                else:
                    return f"{greeting} you want to put everything in one place. How much are you investing? That will help me recommend the BEST single option for you! 😊"
        
        response = f"{greeting} you want to invest ALL KSh {amount:,} in ONE place. Here are your best single-investment options:\n\n"
        
        # Get current rates from live data
        treasury_rates = live_data.get('treasury_rates', {}) if live_data else {}
        tbills = treasury_rates.get('treasury_bills', {})
        tbill_364 = tbills.get('364_day', {}).get('rate', 17.5)
        
        mmf_analysis = live_data.get('mmf_analysis', {}) if live_data else {}
        best_mmf = mmf_analysis.get('best')
        
        # Option 1: Treasury Bills
        response += f"**OPTION 1: Treasury Bills (364-day)** ⭐ RECOMMENDED\n"
        response += f"   📍 Put ALL KSh {amount:,} here\n"
        response += f"   💰 Current rate: **{tbill_364:.1f}%** per year\n"
        expected_tbill = int(amount * (tbill_364 / 100))
        response += f"   📈 After 1 year: KSh {amount + expected_tbill:,}\n"
        response += f"   💵 Profit: KSh {expected_tbill:,}\n"
        response += f"   ✅ Government-backed (safest option)\n"
        response += f"   ⚠️ Locked for 1 year (can't withdraw early)\n\n"
        
        # Option 2: Money Market Fund
        if best_mmf:
            response += f"**OPTION 2: {best_mmf['name']}**\n"
            response += f"   📍 Put ALL KSh {amount:,} here\n"
            response += f"   💰 Current rate: **{best_mmf['rate']}%** per year\n"
            expected_mmf = int(amount * (best_mmf['rate'] / 100))
            response += f"   📈 After 1 year: KSh {amount + expected_mmf:,}\n"
            response += f"   💵 Profit: KSh {expected_mmf:,}\n"
            response += f"   ✅ Can withdraw anytime (flexible!)\n"
            response += f"   ⚠️ Slightly lower return than T-Bills\n\n"
        else:
            response += f"**OPTION 2: Money Market Fund**\n"
            response += f"   📍 Put ALL KSh {amount:,} here\n"
            response += f"   💰 Rate: ~11% per year\n"
            expected_mmf = int(amount * 0.11)
            response += f"   📈 After 1 year: KSh {amount + expected_mmf:,}\n"
            response += f"   💵 Profit: KSh {expected_mmf:,}\n"
            response += f"   ✅ Can withdraw anytime!\n\n"
        
        # Option 3: SACCO (if amount is reasonable)
        if amount >= 20000:
            response += f"**OPTION 3: SACCO Deposit**\n"
            response += f"   📍 Put ALL KSh {amount:,} here\n"
            response += f"   💰 Returns: ~10% dividends per year\n"
            expected_sacco = int(amount * 0.10)
            response += f"   📈 After 1 year: KSh {amount + expected_sacco:,}\n"
            response += f"   💵 Profit: KSh {expected_sacco:,}\n"
            response += f"   ✅ BONUS: Qualify for loans (3x your deposit!)\n"
            response += f"   ⚠️ Less liquid than MMF\n\n"
        
        # My recommendation
        response += f"💡 **My Recommendation**: "
        
        if amount >= 100000:
            response += f"Treasury Bills (364-day) - highest guaranteed return at {tbill_364:.1f}%"
        elif amount >= 50000:
            response += f"SACCO - good returns PLUS you qualify for loans"
        else:
            if best_mmf:
                response += f"{best_mmf['name']} - flexible access with {best_mmf['rate']}% returns"
            else:
                response += "Money Market Fund - flexible with good returns"
        
        if swahili_ratio > 0.5:
            response += f"\n\nOption gani inakupendeza? 😊"
        else:
            response += f"\n\nWhich option interests you most? 😊"
        
        return response
    
    def _generate_return_calculation(self, context, swahili_ratio):
        """Calculate and explain returns from previous advice"""
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Good question!"
        
        returns = context.calculate_expected_returns()
        
        if not returns:
            # No previous context - ask for specifics
            if swahili_ratio > 0.5:
                return f"{greeting} nisaidie na details - unataka invest kiasi gani na wapi? Nitakucalculate returns! 😊"
            else:
                return f"{greeting} let me know how much you're investing and where, and I'll calculate your expected returns! 😊"
        
        response = f"{greeting} based on the KSh {returns['initial_amount']:,} we discussed:\n\n"
        
        if returns['breakdown']:
            response += "**Expected Returns After 1 Year:**\n\n"
            
            for name, data in returns['breakdown'].items():
                response += f"• **{name}**:\n"
                response += f"  Invested: KSh {data['invested']:,}\n"
                response += f"  Return: KSh {data['return']:,} ({data['rate']*100:.1f}%)\n"
                response += f"  Total: KSh {data['total']:,}\n\n"
        
        response += f"**💰 TOTAL EXPECTED:**\n"
        response += f"   Start with: KSh {returns['initial_amount']:,}\n"
        response += f"   Profit: KSh {returns['total_return']:,}\n"
        response += f"   End with: KSh {returns['final_amount']:,}\n"
        response += f"   Overall return: {returns['overall_rate']:.1f}%\n\n"
        
        if swahili_ratio > 0.5:
            response += f"💡 Hizi ni estimated returns. Actual returns inategemea market conditions!"
        else:
            response += f"💡 These are estimated returns. Actual may vary slightly based on market conditions."
        
        return response
    
    def _generate_mmf_comparison(self, live_data, swahili_ratio: float) -> str:
        """Generate MMF comparison with live rates"""
        
        greeting = "Sawa," if swahili_ratio > 0.5 else "Here are"
        
        response = f"{greeting} the current Money Market Fund rates:\n\n"
        
        # Try to get live MMF data
        if live_data and live_data.get('mmf_rates'):
            mmf_rates = live_data['mmf_rates']
            
            # Sort by rate
            sorted_mmfs = sorted(
                mmf_rates.items(),
                key=lambda x: x[1]['current_rate'],
                reverse=True
            )
            
            response += "**📊 LIVE RATES** (updated today):\n\n"
            
            for i, (name, data) in enumerate(sorted_mmfs, 1):
                emoji = "⭐" if i == 1 else "✅" if i <= 3 else "📊"
                
                response += f"{i}. {emoji} **{name}**\n"
                response += f"   Rate: **{data['current_rate']}%** per year\n"
                response += f"   Minimum: KSh {data['minimum']:,}\n"
                response += f"   Liquidity: {data['liquidity']}\n"
                response += f"   Rating: {data['recommendation']}\n\n"
            
            # Add recommendation
            best = sorted_mmfs[0]
            response += f"💡 **Best Option**: {best[0]} at {best[1]['current_rate']}%\n\n"
            
            # Compare to alternatives
            response += f"**📈 Comparison**:\n"
            response += f"• Bank savings: 2-5% (much lower!)\n"
            response += f"• Treasury Bills: 17.5% (but locked 1 year)\n"
            response += f"• MMF: {best[1]['current_rate']}% (withdraw anytime!)\n"
        
        else:
            # Fallback to typical rates
            response += "**Top MMFs** (current market rates):\n\n"
            response += "1. ⭐ **Sanlam Money Market Fund**\n"
            response += "   Rate: 11.2% | Min: KSh 1,000 | Liquidity: 1-2 days\n\n"
            response += "2. ✅ **CIC Money Market Fund**\n"
            response += "   Rate: 10.8% | Min: KSh 5,000 | Liquidity: 1-2 days\n\n"
            response += "3. ✅ **Britam Money Market Fund**\n"
            response += "   Rate: 10.5% | Min: KSh 1,000 | Liquidity: 2-3 days\n\n"
            response += "4. 📊 **Old Mutual Money Market**\n"
            response += "   Rate: 10.3% | Min: KSh 5,000 | Liquidity: 1-2 days\n\n"
            
            response += "💡 **Best**: Sanlam at 11.2% - highest rate + lowest minimum!\n"
        
        if swahili_ratio > 0.5:
            response += "\nUngependa kuweka pesa ngapi? Nitakuguide! 😊"
        else:
            response += "\nHow much are you looking to invest? I can give you specific advice! 😊"
        
        return response
    
    def generate_response(self, knowledge_result, user_language_pattern, 
                         include_proverb=False, user_query=None, live_data=None, context=None):
        """
        Generate response matching user's language pattern
        
        Main response generation for knowledge base matches
        """
        
        if not knowledge_result:
            return self._generate_fallback_response(user_language_pattern, user_query, live_data, context)
        
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
            response += f"\n\n💡 Remember: \"{proverb['swahili']}\" ({proverb['english']}) - {proverb['meaning']}"
        
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
        """Adapt response to match user's language pattern"""
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
        """Add live market data snippet to answer"""
        enhancement = ""
        
        if live_data.get('market_summary'):
            summary = live_data['market_summary']
            enhancement += f"\n\n📊 **Live Update**: NSE is {summary['emoji']} {summary['sentiment']} today (Avg: {summary['avg_change']:+.1f}%)"
        
        if live_data.get('mmf_analysis', {}).get('best'):
            best_mmf = live_data['mmf_analysis']['best']
            enhancement += f"\n💰 Top MMF now: {best_mmf['name']} ({best_mmf['rate']}%)"
        
        return answer + enhancement
    
    def _generate_fallback_response(self, language_pattern, user_query=None, live_data=None, context=None):
        """Generate intelligent fallback response"""
        
        swahili_ratio = language_pattern.get('swahili_ratio', 0.5)
        greeting = self.phrases.get_transition() if swahili_ratio > 0.5 else "Alright,"
        
        if user_query:
            analysis = self.intent_analyzer.analyze(user_query)
            
            # Handle MMF queries
            if analysis['intent'] == 'mmf_query':
                return self._generate_mmf_comparison(live_data, swahili_ratio)
            
            # Handle investment advice
            if analysis['intent'] == 'investment_advice':
                advice = self.advisor.generate_investment_advice(
                    amount=analysis['amount'],
                    goal=analysis['goal'],
                    urgency=analysis['urgency'],
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
                return f"{greeting} {advice}"
            
            # Handle stock queries
            elif analysis['intent'] in ['stock_query', 'stock_recommendation']:
                advice = self.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market='nse',
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
                return f"{greeting} {advice}"
            
            # Handle global stocks
            elif analysis['intent'] == 'global_stocks_query':
                advice = self.advisor.generate_stock_advice(
                    amount=analysis['amount'],
                    experience='beginner',
                    market='international',
                    language_mix=swahili_ratio,
                    live_data=live_data
                )
                return f"{greeting} {advice}"
        
        # Generic fallback
        if swahili_ratio > 0.6:
            return "Pole, nisaidie na details zaidi. Unataka kujua kuhusu nini? Stocks? Akiba? M-Pesa? Una pesa ngapi? 😊"
        elif swahili_ratio < 0.3:
            return "I'd love to help! What specifically would you like to know? Stocks, savings, M-Pesa, loans? How much money are you working with? 😊"
        else:
            return "Pole, nisaidie with more details. What do you want to know? Stocks, savings, loans? How much pesa una? 😊"
    
    def generate_welcome_message(self):
        """Generate welcome message"""
        return """Habari! Welcome to the Kenyan Financial Advisor chatbot. 🇰🇪

I can help you with:
💰 Savings and investment advice (with real-time data!)
📱 M-Pesa and mobile money
🏦 Banking and SACCOs
💵 Loans and credit
👥 Chamas and savings groups
📈 NSE stocks and global markets
📊 Treasury Bills and Money Market Funds

Feel free to ask in English, Swahili, or mix them (code-switching)! 

What would you like to know? 😊"""

# ============================================================================
# TEST CODE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 💬 TESTING RESPONSE GENERATOR")
    print("="*70)
    
    generator = ResponseGenerator()
    
    print("\n" + generator.generate_welcome_message())
    
    print("\n✓ Response Generator ready!")