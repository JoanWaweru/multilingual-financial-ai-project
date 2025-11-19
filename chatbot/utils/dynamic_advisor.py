"""
Enhanced dynamic advisor with real-time market data integration
"""

import sys
from pathlib import Path

# Fix import path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DynamicFinancialAdvisor:
    """Generate personalized advice with real-time data"""
    
    def generate_investment_advice(self, amount, goal=None, urgency='flexible', 
                                   language_mix=0.5, live_data=None):
        """
        Generate dynamic investment advice with optional real-time data
        
        Args:
            amount: Investment amount in KES
            goal: Purpose (emergency, business, etc)
            urgency: Timeline (immediate, short_term, long_term)
            language_mix: 0=English, 1=Swahili, 0.5=Mixed
            live_data: Optional dict with real-time market data
        """
        
        if not amount:
            return self._generic_investment_advice(language_mix)
        
        # Use live data if available
        if live_data and live_data.get('mmf_rates'):
            advice = self._generate_live_investment_advice(amount, goal, urgency, live_data)
        else:
            # Fallback to static advice
            advice = self._generate_static_investment_advice(amount, goal, urgency)
        
        # Adapt language
        if language_mix > 0.6:
            advice = self._add_swahili_flavor(advice)
        
        return advice
    
    def _generate_live_investment_advice(self, amount, goal, urgency, live_data):
        """Generate advice using real-time data"""
        
        mmf_analysis = live_data.get('mmf_analysis', {})
        best_mmf = mmf_analysis.get('best')
        treasury_rates = live_data.get('treasury_rates', {})
        
        if amount < 10000:
            advice = f"With KSh {amount:,}, smart options:\n\n"
            advice += "1. **M-Shwari** - Save via M-Pesa, accessible\n"
            advice += "2. **Chama** - Join group savings\n"
            
            if best_mmf:
                advice += f"3. **{best_mmf['name']}** - Currently at {best_mmf['rate']}% (top performer!)\n"
            
            advice += "\nStart building emergency fund!"
        
        elif amount < 50000:
            advice = f"Great! With KSh {amount:,}:\n\n"
            
            if best_mmf:
                advice += f"1. **MMF ({best_mmf['name']})** - KSh 30k → {best_mmf['rate']}% return (beating savings accounts!)\n"
            else:
                advice += "1. **MMF** - KSh 30k → 10-12% returns\n"
            
            advice += "2. **SACCO** - KSh 15k → Qualify for loans\n"
            advice += "3. **Emergency fund** - KSh 5k accessible\n"
        
        elif amount < 100000:
            advice = f"Excellent! With KSh {amount:,}:\n\n"
            
            if goal == 'property':
                advice += "**Saving for land/house?**\n"
                advice += "1. SACCO - KSh 40k (qualify for land loans)\n"
                
                if best_mmf:
                    advice += f"2. {best_mmf['name']} - KSh 30k ({best_mmf['rate']}%)\n"
                else:
                    advice += "2. MMF - KSh 30k (grows while saving)\n"
                
                advice += "3. Keep KSh 20k accessible\n"
            else:
                advice += "**Balanced approach:**\n"
                advice += "1. SACCO - KSh 40k (8-12% + loans)\n"
                
                if best_mmf:
                    advice += f"2. {best_mmf['name']} - KSh 30k ({best_mmf['rate']}% - TOP RATED)\n"
                else:
                    advice += "2. MMF - KSh 30k (10-12%)\n"
                
                advice += "3. Bank savings - KSh 20k (emergencies)\n"
        
        elif amount < 500000:
            advice = f"Strategic position! With KSh {amount:,}:\n\n"
            
            split_tbill = int(amount * 0.5)
            split_sacco = int(amount * 0.3)
            split_mmf = int(amount * 0.2)
            
            # Get current T-Bill rate
            tbill_rate = 17.5  # default
            if treasury_rates and '364_day' in treasury_rates:
                tbill_rate = treasury_rates['364_day'].get('rate', 17.5)
            
            advice += "**Diversified strategy:**\n"
            advice += f"1. **Treasury Bills** - KSh {split_tbill:,} → {tbill_rate:.1f}% (government-backed!)\n"
            advice += f"2. **SACCO** - KSh {split_sacco:,} → dividends + loans\n"
            
            if best_mmf:
                advice += f"3. **{best_mmf['name']}** - KSh {split_mmf:,} → {best_mmf['rate']}% (flexible access)\n"
            else:
                advice += f"3. **MMF** - KSh {split_mmf:,} → flexible access\n"
            
            advice += "\n💡 Balances growth with accessibility!"
        
        else:
            advice = self._advice_over_500k_live(amount, goal, live_data)
        
        return advice
    
    def _advice_over_500k_live(self, amount, goal, live_data):
        """Advice for amounts over 500k with live data"""
        
        split_bonds = int(amount * 0.4)
        split_sacco = int(amount * 0.25)
        split_mmf = int(amount * 0.20)
        split_stocks = int(amount * 0.10)
        split_emergency = int(amount * 0.05)
        
        advice = f"Wealth building! With KSh {amount:,}:\n\n"
        
        treasury_rates = live_data.get('treasury_rates', {})
        bond_rate = 17.8 if treasury_rates and '2_year_bond' in treasury_rates else 17.5
        
        advice += f"1. **T-Bills/Bonds** - KSh {split_bonds:,} → {bond_rate:.1f}% (safe anchor)\n"
        advice += f"2. **SACCO** - KSh {split_sacco:,} → steady dividends\n"
        
        best_mmf = live_data.get('mmf_analysis', {}).get('best')
        if best_mmf:
            advice += f"3. **{best_mmf['name']}** - KSh {split_mmf:,} → {best_mmf['rate']}%\n"
        else:
            advice += f"3. **MMF** - KSh {split_mmf:,} → liquid funds\n"
        
        advice += f"4. **NSE Stocks** - KSh {split_stocks:,} → growth potential\n"
        advice += f"5. **Emergency** - KSh {split_emergency:,} → accessible\n"
        
        advice += "\n💼 Consider financial advisor for advanced strategies!"
        
        return advice
    
    def _generate_static_investment_advice(self, amount, goal, urgency):
        """Static fallback advice (your original code)"""
        
        if amount < 10000:
            return self._advice_under_10k_static(amount, goal, urgency)
        elif amount < 50000:
            return self._advice_10k_to_50k_static(amount, goal, urgency)
        elif amount < 100000:
            return self._advice_50k_to_100k_static(amount, goal, urgency)
        elif amount < 500000:
            return self._advice_100k_to_500k_static(amount, goal, urgency)
        else:
            return self._advice_over_500k_static(amount, goal, urgency)
    
    def _advice_under_10k_static(self, amount, goal, urgency):
        base = f"With KSh {amount:,}, here are smart options:\n\n"
        if urgency == 'immediate' or goal == 'emergency':
            return base + "Keep it in M-Pesa or bank savings for easy access. Don't lock it in investments!"
        return base + "1. **Chama** - Join group savings\n2. **M-Shwari** - Save via M-Pesa\n3. **Bank savings** - Safe and accessible\n\nStart building emergency fund!"
    
    def _advice_10k_to_50k_static(self, amount, goal, urgency):
        base = f"Great! With KSh {amount:,}:\n\n"
        if goal == 'business':
            return base + "1. **Business capital** - Use wisely\n2. **Keep 30% in savings** - Safety net\n3. **Join chama** - Backup funds"
        return base + "1. **SACCO** - KSh 30k (qualify for loans)\n2. **MMF** - KSh 15k (10% returns)\n3. **Emergency** - KSh 5k in bank"
    
    def _advice_50k_to_100k_static(self, amount, goal, urgency):
        base = f"Excellent! With KSh {amount:,}:\n\n"
        if goal == 'property':
            return base + "**Saving for land?**\n1. SACCO - KSh 40k\n2. MMF - KSh 30k\n3. Keep KSh 20k accessible"
        return base + "1. SACCO - KSh 40k (8-12% + loans)\n2. MMF - KSh 30k (flexible)\n3. Bank - KSh 20k (emergencies)"
    
    def _advice_100k_to_500k_static(self, amount, goal, urgency):
        split_tbill = int(amount * 0.5)
        split_sacco = int(amount * 0.3)
        split_mmf = int(amount * 0.2)
        
        base = f"Strategic! With KSh {amount:,}:\n\n"
        return base + f"1. T-Bills - KSh {split_tbill:,} (15-17%)\n2. SACCO - KSh {split_sacco:,}\n3. MMF - KSh {split_mmf:,}\n\nBalances growth with access!"
    
    def _advice_over_500k_static(self, amount, goal, urgency):
        split_bonds = int(amount * 0.4)
        split_sacco = int(amount * 0.25)
        split_mmf = int(amount * 0.20)
        split_property = int(amount * 0.10)
        split_emergency = int(amount * 0.05)
        
        return f"Wealth building! KSh {amount:,}:\n\n1. T-Bills/Bonds - KSh {split_bonds:,}\n2. SACCO - KSh {split_sacco:,}\n3. MMF - KSh {split_mmf:,}\n4. Land down payment - KSh {split_property:,}\n5. Emergency - KSh {split_emergency:,}\n\nConsider financial advisor!"
    
    def generate_stock_advice(self, amount, experience='beginner', market='nse', 
                             language_mix=0.5, live_data=None):
        """Generate stock advice with optional real-time data"""
        
        if not amount:
            return self._generic_stock_advice(experience, market, language_mix)
        
        # Use live data if available
        if live_data and live_data.get('nse_analysis'):
            advice = self._generate_live_stock_advice(amount, market, live_data)
        else:
            advice = self._generate_static_stock_advice(amount, experience, market)
        
        # Add risk warning
        advice += "\n\n⚠️ **Remember**: Stocks are risky! Only invest money you can afford to lose."
        
        if language_mix > 0.6:
            advice = self._add_swahili_flavor(advice)
        
        return advice
    
    def _generate_live_stock_advice(self, amount, market, live_data):
        """Generate stock advice using real-time data"""
        
        nse_analysis = live_data.get('nse_analysis', {})
        market_sentiment = nse_analysis.get('market_sentiment', 'NEUTRAL')
        top_pick = nse_analysis.get('top_pick')
        allocation = nse_analysis.get('allocation')
        
        sentiment_emoji = {'BULLISH': '📈', 'NEUTRAL': '➡️', 'BEARISH': '📉'}.get(market_sentiment, '➡️')
        
        advice = f"**📊 Current Market: {sentiment_emoji} {market_sentiment}**\n\n"
        advice += f"With KSh {amount:,} for NSE stocks:\n\n"
        
        if top_pick:
            advice += f"🏆 **TOP PICK RIGHT NOW**: {top_pick['name']}\n"
            advice += f"   Price: KSh {top_pick['price']} ({top_pick['change_percent']:+.2f}% today)\n"
            advice += f"   Signal: {top_pick['signal']}\n\n"
        
        if allocation:
            advice += "**💼 RECOMMENDED PORTFOLIO** (based on today's performance):\n"
            for symbol, data in allocation.items():
                advice += f"   • {data['name']}: {data['percentage']}% (KSh {data['amount']:,}, {data['shares']} shares @ KSh {data['price']})\n"
        else:
            # Fallback portfolio
            if amount < 10000:
                advice += "**Strategy**: Use Hisa app, start with KSh 100 per stock\n"
                advice += "Split across 3-4 blue-chips"
            elif amount < 50000:
                advice += "**Beginner portfolio**:\n"
                if top_pick:
                    advice += f"   • {top_pick['name']}: 40%\n"
                advice += "   • Equity Bank: 30%\n   • KCB: 30%"
        
        return advice
    
    def _generate_static_stock_advice(self, amount, experience, market):
        """Static stock advice fallback"""
        
        base = f"With KSh {amount:,} for stocks:\n\n"
        
        if amount < 10000:
            return base + "**Use Hisa app** (start with KSh 100!)\n1. Safaricom - 40%\n2. Equity - 30%\n3. KCB - 30%\n\nLearn by doing!"
        elif amount < 50000:
            return base + "**Blue-chips only**:\n1. Safaricom - 40%\n2. Equity Bank - 30%\n3. KCB - 30%\n\nExpect 15-25% annual returns if held 2+ years"
        elif amount < 100000:
            split_stocks = int(amount * 0.5)
            split_safe = int(amount * 0.5)
            return base + f"**Balanced**:\n1. NSE Stocks - KSh {split_stocks:,}\n2. T-Bills/MMF - KSh {split_safe:,} (safety net)"
        else:
            return base + "**Diversified**: 50% NSE, 30% international (if KSh 100k+), 20% T-Bills"
    
    def _generic_investment_advice(self, language_mix):
        if language_mix > 0.6:
            return "Investment options depend on amount:\n- KSh 1k-10k: Chama/M-Shwari\n- KSh 10k-50k: SACCO\n- KSh 50k-100k: SACCO + MMF\n- KSh 100k+: T-Bills, SACCO, MMF\n\nHow much una?"
        return "Investment options by amount:\n- KSh 1k-10k: Chama/M-Shwari\n- KSh 10k-50k: SACCO\n- KSh 50k-100k: SACCO + MMF\n- KSh 100k+: T-Bills mix\n\nHow much do you have?"
    
    def _generic_stock_advice(self, experience, market, language_mix):
        if market == 'international':
            return "International stocks need KSh 100k+ (wire fees). Use Interactive Brokers. Buy: S&P 500 ETFs or Apple, Microsoft. Start with NSE first!"
        return "Use Hisa app (KSh 100 minimum!). Buy: Safaricom, Equity, KCB. Blue-chips safest for beginners. How much are you starting with?"
    
    def _add_swahili_flavor(self, text):
        """Add Swahili terms naturally"""
        replacements = {
            'Great!': 'Poa!',
            'Excellent!': 'Vizuri sana!',
            'Strategic': 'Smart',
            'With': 'Na'
        }
        for eng, swa in replacements.items():
            if eng in text:
                text = text.replace(eng, swa, 1)
                break
        return text