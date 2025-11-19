"""
Generate dynamic financial advice based on context
"""

class DynamicFinancialAdvisor:
    """Generate personalized advice based on amount and context"""
    
    def generate_investment_advice(self, amount, goal=None, urgency='flexible', language_mix=0.5):
        """
        Generate dynamic investment advice
        
        Args:
            amount: Amount in KES
            goal: Purpose (emergency, business, etc)
            urgency: How soon (immediate, short_term, long_term)
            language_mix: 0=English, 1=Swahili, 0.5=Mixed
        """
        
        if not amount:
            return self._generic_investment_advice(language_mix)
        
        # Generate advice based on amount
        if amount < 10000:
            advice = self._advice_under_10k(amount, goal, urgency)
        elif amount < 50000:
            advice = self._advice_10k_to_50k(amount, goal, urgency)
        elif amount < 100000:
            advice = self._advice_50k_to_100k(amount, goal, urgency)
        elif amount < 500000:
            advice = self._advice_100k_to_500k(amount, goal, urgency)
        else:
            advice = self._advice_over_500k(amount, goal, urgency)
        
        # Adapt language
        if language_mix > 0.6:
            advice = self._add_swahili_flavor(advice)
        
        return advice
    
    def _advice_under_10k(self, amount, goal, urgency):
        base = f"With KSh {amount:,}, here are smart options:\n\n"
        
        if urgency == 'immediate' or goal == 'emergency':
            return base + "Keep it in M-Pesa or bank savings for easy access. Don't lock it in investments - you need it available!"
        
        return base + "1. **Chama** - Join a group contributing weekly/monthly\n2. **M-Shwari** - Save via M-Pesa, earn small interest\n3. **Bank savings** - Keep it safe and accessible\n\nStart building your emergency fund first!"
    
    def _advice_10k_to_50k(self, amount, goal, urgency):
        base = f"Great! With KSh {amount:,}, you have good options:\n\n"
        
        if goal == 'business':
            return base + "1. **Start small business** - Use capital wisely\n2. **Keep 30% in savings** - Business emergency fund\n3. **Join chama** - Build network and backup funds\n\nDon't invest all in business - keep buffer!"
        
        if urgency == 'immediate':
            return base + "Keep in accessible accounts:\n- Bank savings (instant access)\n- MMF (withdraw in 1-2 days)\n- M-Shwari (via M-Pesa)\n\nAvoid locked investments if you need money soon!"
        
        return base + "1. **SACCO** - Deposit KSh 30k, qualify for loans later\n2. **MMF** - Put KSh 15k in Sanlam/CIC (10% returns)\n3. **Emergency fund** - Keep KSh 5k in bank\n\nSACCOs give best returns at this level!"
    
    def _advice_50k_to_100k(self, amount, goal, urgency):
        base = f"Excellent! With KSh {amount:,}, diversify:\n\n"
        
        if goal == 'property':
            return base + "**Saving for land/house?**\n1. SACCO - KSh 40k (earn dividends + qualify for land loans)\n2. MMF - KSh 30k (grows while you save more)\n3. Keep KSh 20k accessible\n\nLand takes time - put money where it grows!"
        
        if urgency == 'long_term':
            return base + "**Long-term growth strategy:**\n1. SACCO - KSh 40k (8-12% returns + loans)\n2. MMF - KSh 30k (10-12%, flexible)\n3. Emergency - KSh 20k in bank\n\nRe-invest dividends for compound growth!"
        
        return base + "**Balanced approach:**\n1. SACCO - KSh 40k (good returns + loan access)\n2. MMF - KSh 30k (Sanlam/CIC, 10% returns)\n3. Bank savings - KSh 20k (emergencies)\n\nStart building wealth foundation!"
    
    def _advice_100k_to_500k(self, amount, goal, urgency):
        base = f"Great position! With KSh {amount:,}, go strategic:\n\n"
        
        if urgency == 'immediate':
            return base + "**Need money accessible?**\n1. MMF - 70% (good returns, withdraw in 1-2 days)\n2. Bank savings - 20% (instant access)\n3. Keep 10% as cash\n\nAvoid T-Bills (locked for months)!"
        
        if goal == 'business':
            split_business = int(amount * 0.6)
            split_save = int(amount * 0.3)
            split_emergency = int(amount * 0.1)
            return base + f"**Starting business?**\n1. Business capital - KSh {split_business:,} (60%)\n2. Safety net - KSh {split_save:,} in SACCO (30%)\n3. Emergency - KSh {split_emergency:,} accessible (10%)\n\nNever invest 100% in business!"
        
        split_tbill = int(amount * 0.5)
        split_sacco = int(amount * 0.3)
        split_mmf = int(amount * 0.2)
        
        return base + f"**Diversified strategy:**\n1. Treasury Bills - KSh {split_tbill:,} (15-17% returns, lock 3-12 months)\n2. SACCO - KSh {split_sacco:,} (dividends + loans)\n3. MMF - KSh {split_mmf:,} (flexible access)\n\nThis balances growth with accessibility!"
    
    def _advice_over_500k(self, amount, goal, urgency):
        base = f"Excellent! With KSh {amount:,}, think long-term:\n\n"
        
        if goal == 'retirement':
            return base + "**Retirement planning:**\n1. Treasury Bonds - 50% (12-15% for 5-20 years)\n2. SACCO - 20% (dividends + security)\n3. NSE Stocks - 15% (growth potential)\n4. MMF - 10% (flexibility)\n5. Emergency - 5% accessible\n\nDiversification is key!"
        
        split_bonds = int(amount * 0.4)
        split_sacco = int(amount * 0.25)
        split_mmf = int(amount * 0.20)
        split_property = int(amount * 0.10)
        split_emergency = int(amount * 0.05)
        
        return base + f"**Wealth building strategy:**\n1. T-Bills/Bonds - KSh {split_bonds:,} (12-17%)\n2. SACCO - KSh {split_sacco:,} (steady returns)\n3. MMF - KSh {split_mmf:,} (liquid funds)\n4. Consider land - KSh {split_property:,} (down payment)\n5. Emergency fund - KSh {split_emergency:,}\n\nConsider financial advisor for advanced strategies!"
    
    def _generic_investment_advice(self, language_mix):
        if language_mix > 0.6:
            return "Nikuambie! Investment options depend on how much you have:\n- KSh 1k-10k: Chama or M-Shwari\n- KSh 10k-50k: SACCO\n- KSh 50k-100k: SACCO + MMF\n- KSh 100k+: Treasury Bills, SACCO, MMF\n\nHow much are you working with?"
        else:
            return "Investment options depend on your amount:\n- KSh 1k-10k: Start with chama or M-Shwari\n- KSh 10k-50k: Join a SACCO\n- KSh 50k-100k: SACCO + Money Market Fund\n- KSh 100k+: Treasury Bills, SACCO, MMF mix\n\nHow much do you have to invest?"
    
    def generate_stock_advice(self, amount, experience='beginner', market='nse', language_mix=0.5):
        """Generate stock investment advice"""
        
        if not amount:
            return self._generic_stock_advice(experience, market, language_mix)
        
        if amount < 10000:
            advice = self._stock_advice_under_10k(amount, experience, market)
        elif amount < 50000:
            advice = self._stock_advice_10k_to_50k(amount, experience, market)
        elif amount < 100000:
            advice = self._stock_advice_50k_to_100k(amount, experience, market)
        elif amount < 500000:
            advice = self._stock_advice_100k_to_500k(amount, experience, market)
        else:
            advice = self._stock_advice_over_500k(amount, experience, market)
        
        # Add risk warning
        advice += "\n\n⚠️ **Remember**: Stocks are risky! Only invest money you can afford to lose. Diversify across multiple stocks."
        
        if language_mix > 0.6:
            advice = self._add_swahili_flavor(advice)
        
        return advice
    
    def _stock_advice_under_10k(self, amount, experience, market):
        base = f"Starting with KSh {amount:,} for stocks:\n\n"
        
        return base + "**Perfect amount to learn!**\n\n" + \
               "1. **Use Hisa app** - Buy NSE stocks with as little as KSh 100\n" + \
               "2. **Start with Safaricom** - Most stable, beginner-friendly\n" + \
               "3. **Buy fractional shares** - Own pieces of multiple companies\n\n" + \
               f"Strategy: Split KSh {amount:,} into 3-4 different stocks (Safaricom, Equity, KCB). Learn by doing!"
    
    def _stock_advice_10k_to_50k(self, amount, experience, market):
        base = f"With KSh {amount:,} for stocks:\n\n"
        
        if market == 'international':
            return base + "**Too small for international stocks** (wire fees alone are KSh 3,000-5,000).\n\n" + \
                   "Better: Focus on NSE first - build to KSh 100k+, or use crypto exchanges that offer US stocks (like Exness)."
        
        return base + "**Good starting capital!**\n\n" + \
               "1. **NSE Blue-chips only** - Safaricom (40%), Equity Bank (30%), KCB (30%)\n" + \
               "2. **Open CDS account** - Through any broker or use Hisa app\n" + \
               "3. **Long-term mindset** - Hold 2+ years\n\n" + \
               f"Expect: ~15-25% annual returns if held long-term. Budget KSh {int(amount * 0.013):,} for fees (1.3%)."
    
    def _stock_advice_50k_to_100k(self, amount, experience, market):
        base = f"Strong position with KSh {amount:,}:\n\n"
        
        split_stocks = int(amount * 0.5)
        split_tbill = int(amount * 0.3)
        split_mmf = int(amount * 0.2)
        
        return base + "**Balanced approach:**\n\n" + \
               f"1. NSE Stocks - KSh {split_stocks:,} (50%)\n" + \
               f"   - Safaricom: {int(split_stocks*0.4):,}\n" + \
               f"   - Equity Bank: {int(split_stocks*0.3):,}\n" + \
               f"   - KCB/EABL: {int(split_stocks*0.3):,}\n" + \
               f"2. T-Bills - KSh {split_tbill:,} (30%) - safe anchor\n" + \
               f"3. MMF - KSh {split_mmf:,} (20%) - liquidity\n\n" + \
               "This limits stock risk while you learn."
    
    def _stock_advice_100k_to_500k(self, amount, experience, market):
        base = f"Excellent! With KSh {amount:,}:\n\n"
        
        if market == 'international':
            split_nse = int(amount * 0.5)
            split_us = int(amount * 0.3)
            split_safe = int(amount * 0.2)
            
            return base + "**Diversified global portfolio:**\n\n" + \
                   f"1. **NSE Stocks** - KSh {split_nse:,} (50%)\n" + \
                   f"2. **US Market** - KSh {split_us:,} (30%)\n" + \
                   f"   - S&P 500 ETF (VOO/SPY) or Apple, Microsoft\n" + \
                   f"   - Use: Interactive Brokers\n" + \
                   f"3. **Safe Anchor** - KSh {split_safe:,} (20%)\n" + \
                   f"   - T-Bills or MMF\n\n" + \
                   "Setup costs: CDS (KSh 1,100), wire (KSh 5,000). Forex risk applies!"
        
        split_growth = int(amount * 0.6)
        split_dividend = int(amount * 0.25)
        split_cash = int(amount * 0.15)
        
        return base + "**Focused growth strategy:**\n\n" + \
               f"1. **Growth stocks** - KSh {split_growth:,} (Banking, Tech)\n" + \
               f"2. **Dividend stocks** - KSh {split_dividend:,} (passive income)\n" + \
               f"3. **Cash reserve** - KSh {split_cash:,} (buy opportunities)\n\n" + \
               "Track quarterly earnings. Rebalance bi-annually."
    
    def _stock_advice_over_500k(self, amount, experience, market):
        base = f"Substantial capital! KSh {amount:,} portfolio:\n\n"
        
        split_nse = int(amount * 0.35)
        split_intl = int(amount * 0.30)
        split_bonds = int(amount * 0.20)
        split_alternative = int(amount * 0.10)
        split_cash = int(amount * 0.05)
        
        return base + "**Sophisticated diversification:**\n\n" + \
               f"1. **NSE Stocks** - KSh {split_nse:,} (35%) - 10-15 companies\n" + \
               f"2. **International** - KSh {split_intl:,} (30%) - S&P 500 ETF + US stocks\n" + \
               f"3. **Bonds/Fixed Income** - KSh {split_bonds:,} (20%) - T-Bills, T-Bonds\n" + \
               f"4. **Alternatives** - KSh {split_alternative:,} (10%) - REITs, gold ETF\n" + \
               f"5. **Cash** - KSh {split_cash:,} (5%) - opportunities\n\n" + \
               "**Strongly consider:** Financial advisor for tax optimization!"
    
    def _generic_stock_advice(self, experience, market, language_mix):
        if market == 'international':
            return "For international stocks: Need minimum KSh 100k (wire fees). Options: Interactive Brokers, TD Ameritrade. Buy: S&P 500 ETFs (VOO, SPY) or blue chips (Apple, Microsoft). Start with NSE first if you're new!"
        
        if experience == 'beginner':
            return "Starting with stocks? Use Hisa app (start with KSh 100!). Buy: Safaricom, Equity Bank, KCB. Blue-chip stocks are safest for learning. How much are you thinking of starting with?"
        
        return "Stock investment depends on amount. KSh 1k-10k: Use Hisa app. KSh 10k-100k: Build NSE portfolio. KSh 100k+: Add international exposure. What's your budget?"
    
    def _add_swahili_flavor(self, text):
        """Add Swahili terms to make it more natural"""
        replacements = {
            'Great!': 'Poa!',
            'Excellent!': 'Vizuri sana!',
            'savings': 'akiba',
            'emergency': 'dharura',
            'returns': 'faida',
            'Here are': 'Hizi ndio',
            'Good!': 'Sawa!'
        }
        
        for eng, swa in replacements.items():
            if eng in text:
                text = text.replace(eng, swa, 1)
                break
        
        return text

if __name__ == "__main__":
    # Test the advisor
    advisor = DynamicFinancialAdvisor()
    
    print("\n" + "=" * 60)
    print("TESTING DYNAMIC ADVISOR")
    print("=" * 60)
    
    test_cases = [
        (100000, None, 'flexible', 0.5, 'investment'),
        (50000, 'business', 'short_term', 0.3, 'investment'),
        (75000, None, 'flexible', 0.5, 'stocks')
    ]
    
    for amount, goal, urgency, lang_mix, advice_type in test_cases:
        print(f"\n{'='*60}")
        print(f"Amount: KSh {amount:,}, Goal: {goal}, Type: {advice_type}")
        print(f"{'='*60}")
        
        if advice_type == 'investment':
            advice = advisor.generate_investment_advice(amount, goal, urgency, lang_mix)
        else:
            advice = advisor.generate_stock_advice(amount, 'beginner', 'nse', lang_mix)
        
        print(advice)