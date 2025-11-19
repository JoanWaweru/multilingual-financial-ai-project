"""
Analyze market data and generate intelligent recommendations
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Fix import path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Analyze market data and generate actionable recommendations"""
    
    def analyze_nse_stocks(self, stocks: Dict, amount: int = None) -> Dict:
        """
        Analyze NSE stocks and generate recommendations
        
        Returns comprehensive analysis with buy/sell signals
        """
        
        if not stocks:
            return {'error': 'No stock data available'}
        
        # Categorize by signal
        strong_buy = []
        buy = []
        hold = []
        sell = []
        
        for symbol, data in stocks.items():
            stock_info = {
                'symbol': symbol,
                'name': data['name'],
                'price': data['price'],
                'change_percent': data['change_percent'],
                'dividend_yield': data.get('dividend_yield', 0),
                'signal': data['signal'],
                'score': self._calculate_stock_score(data)
            }
            
            if data['signal'] == 'STRONG BUY':
                strong_buy.append(stock_info)
            elif data['signal'] == 'BUY':
                buy.append(stock_info)
            elif data['signal'] == 'HOLD':
                hold.append(stock_info)
            else:
                sell.append(stock_info)
        
        # Sort by score
        strong_buy.sort(key=lambda x: x['score'], reverse=True)
        buy.sort(key=lambda x: x['score'], reverse=True)
        
        # Combine buy signals
        all_buy_signals = strong_buy + buy
        
        # Generate portfolio if amount provided
        allocation = None
        if amount and all_buy_signals:
            allocation = self._generate_smart_portfolio(all_buy_signals, amount)
        
        return {
            'strong_buy': strong_buy,
            'buy': buy,
            'hold': hold,
            'sell': sell,
            'top_pick': all_buy_signals[0] if all_buy_signals else None,
            'allocation': allocation,
            'market_sentiment': self._calculate_sentiment(stocks),
            'total_analyzed': len(stocks)
        }
    
    def _calculate_stock_score(self, stock_data: Dict) -> float:
        """Calculate composite score for stock"""
        
        # Factors: momentum + dividend yield + value (low PE)
        momentum_score = stock_data['change_percent'] * 2  # Weight momentum heavily
        dividend_score = stock_data.get('dividend_yield', 0)
        
        # Lower PE is better (defensive)
        pe = stock_data.get('pe_ratio', 10)
        value_score = max(0, 15 - pe)  # Reward low PE
        
        total_score = momentum_score + dividend_score + value_score
        return round(total_score, 2)
    
    def _generate_smart_portfolio(self, buy_signals: List[Dict], amount: int) -> Dict:
        """Generate optimized portfolio allocation"""
        
        if not buy_signals:
            return None
        
        # Take top 4 stocks
        top_stocks = buy_signals[:4]
        
        # Calculate weights based on scores
        total_score = sum(s['score'] for s in top_stocks)
        
        if total_score <= 0:
            # Equal weight fallback
            weight_per_stock = 1.0 / len(top_stocks)
            weights = [weight_per_stock] * len(top_stocks)
        else:
            weights = [s['score'] / total_score for s in top_stocks]
        
        allocation = {}
        remaining = amount
        
        for i, stock in enumerate(top_stocks):
            if i == len(top_stocks) - 1:
                # Last stock gets remaining amount
                amount_allocated = remaining
            else:
                amount_allocated = int(weights[i] * amount)
                remaining -= amount_allocated
            
            shares = int(amount_allocated / stock['price'])
            actual_cost = shares * stock['price']
            
            allocation[stock['symbol']] = {
                'name': stock['name'],
                'percentage': round(weights[i] * 100, 1),
                'amount': int(actual_cost),
                'shares': shares,
                'price': stock['price'],
                'signal': stock['signal']
            }
        
        return allocation
    
    def _calculate_sentiment(self, stocks: Dict) -> str:
        """Calculate overall market sentiment"""
        
        if not stocks:
            return 'UNKNOWN'
        
        # Count positive vs negative movers
        positive = sum(1 for s in stocks.values() if s['change'] > 0)
        total = len(stocks)
        
        # Calculate average change
        avg_change = sum(s['change_percent'] for s in stocks.values()) / total
        
        # Determine sentiment
        if avg_change > 1 and positive/total > 0.6:
            return 'BULLISH'
        elif avg_change < -1 or positive/total < 0.4:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def compare_mmfs(self, mmfs: Dict) -> Dict:
        """Compare and rank Money Market Funds"""
        
        if not mmfs:
            return {'error': 'No MMF data available'}
        
        ranked = []
        
        for name, data in mmfs.items():
            ranked.append({
                'name': name,
                'rate': data['current_rate'],
                'change': data.get('change', 0),
                'minimum': data['minimum'],
                'liquidity': data['liquidity'],
                'recommendation': data['recommendation'],
                'score': data['current_rate'] + (data.get('change', 0) * 10)  # Bonus for improving rates
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'best': ranked[0] if ranked else None,
            'top_3': ranked[:3],
            'all': ranked
        }
    
    def analyze_global_stock(self, stock_data: Dict) -> Dict:
        """Analyze individual global stock"""
        
        if not stock_data:
            return {'error': 'No stock data'}
        
        change_pct = stock_data.get('change_percent', 0)
        
        # Generate detailed analysis
        analysis = {
            'symbol': stock_data['symbol'],
            'name': stock_data['name'],
            'price': stock_data['price'],
            'signal': stock_data['signal'],
            'change_percent': change_pct,
            'recommendation': self._generate_recommendation(change_pct),
            'risk_level': self._assess_risk(change_pct)
        }
        
        return analysis
    
    def _generate_recommendation(self, change_pct: float) -> str:
        """Generate text recommendation"""
        
        if change_pct > 3:
            return "Strong momentum - good entry point for long-term"
        elif change_pct > 1:
            return "Positive momentum - consider buying"
        elif change_pct > -1:
            return "Stable - good for holding"
        elif change_pct > -3:
            return "Declining - wait for better entry"
        else:
            return "Sharp decline - high risk, avoid for now"
    
    def _assess_risk(self, change_pct: float) -> str:
        """Assess risk level based on volatility"""
        
        abs_change = abs(change_pct)
        
        if abs_change < 1:
            return 'LOW'
        elif abs_change < 3:
            return 'MODERATE'
        else:
            return 'HIGH'
    
    def generate_summary(self, nse_analysis: Dict, mmf_analysis: Dict) -> str:
        """Generate human-readable market summary"""
        
        sentiment = nse_analysis.get('market_sentiment', 'NEUTRAL')
        top_pick = nse_analysis.get('top_pick')
        best_mmf = mmf_analysis.get('best')
        
        summary = f"Market Sentiment: {sentiment}\n"
        
        if top_pick:
            summary += f"Top NSE Pick: {top_pick['name']} (KSh {top_pick['price']}, {top_pick['change_percent']:+.2f}%)\n"
        
        if best_mmf:
            summary += f"Best MMF: {best_mmf['name']} ({best_mmf['rate']}%)"
        
        return summary

if __name__ == "__main__":
    # Test analyzer
    from chatbot.utils.market_data import MarketDataFetcher
    
    print("\n" + "=" * 70)
    print("📊 TESTING MARKET ANALYZER")
    print("=" * 70)
    
    fetcher = MarketDataFetcher()
    analyzer = MarketAnalyzer()
    
    # Analyze NSE
    nse_stocks = fetcher.get_nse_stocks()
    analysis = analyzer.analyze_nse_stocks(nse_stocks, amount=100000)
    
    print(f"\n📈 Market Sentiment: {analysis['market_sentiment']}")
    print(f"Stocks Analyzed: {analysis['total_analyzed']}")
    
    if analysis['top_pick']:
        top = analysis['top_pick']
        print(f"\n🏆 TOP PICK: {top['name']}")
        print(f"   Price: KSh {top['price']} ({top['change_percent']:+.2f}%)")
        print(f"   Score: {top['score']}")
        print(f"   Signal: {top['signal']}")
    
    if analysis['allocation']:
        print(f"\n💼 PORTFOLIO FOR KSh 100,000:")
        for symbol, data in analysis['allocation'].items():
            print(f"   {data['name']}: {data['percentage']}% (KSh {data['amount']:,}, {data['shares']} shares)")
    
    # Analyze MMFs
    mmfs = fetcher.get_mmf_rates()
    mmf_analysis = analyzer.compare_mmfs(mmfs)
    
    if mmf_analysis['best']:
        best = mmf_analysis['best']
        print(f"\n💰 BEST MMF: {best['name']}")
        print(f"   Rate: {best['rate']}%")
        print(f"   Rating: {best['recommendation']}")
    
    print("\n✓ Market analyzer working!")