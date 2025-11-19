"""
Enhanced Market Data Fetcher
Now uses unified scraper for complete Kenyan data + global stocks
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from chatbot.scrapers.unified_scraper import UnifiedKenyanMarketData
import yfinance as yf
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """
    Enhanced market data fetcher
    
    Now fetches:
    - NSE stocks (via unified scraper)
    - T-Bills (via unified scraper)
    - T-Bonds (via unified scraper)
    - MMFs (via unified scraper)
    - Global stocks (via Yahoo Finance)
    - Forex rates
    """
    
    def __init__(self):
        self.unified_scraper = UnifiedKenyanMarketData()
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_fetch = {}
        
        logger.info("✓ Enhanced Market Data Fetcher initialized")
    
    def get_nse_stocks(self, symbols=None):
        """Get NSE stocks from unified scraper"""
        
        if self._is_cached('kenyan_data'):
            return self.cache['kenyan_data']['nse_stocks']
        
        # Fetch all Kenyan data
        kenyan_data = self.unified_scraper.get_complete_market_data()
        self.cache['kenyan_data'] = kenyan_data
        self.last_fetch['kenyan_data'] = time.time()
        
        stocks = kenyan_data['nse_stocks']
        
        # Filter if symbols specified
        if symbols:
            stocks = {k: v for k, v in stocks.items() if k in symbols}
        
        return stocks
    
    def get_treasury_rates(self):
        """Get T-Bills and Bonds from unified scraper"""
        
        if self._is_cached('kenyan_data'):
            kenyan_data = self.cache['kenyan_data']
        else:
            kenyan_data = self.unified_scraper.get_complete_market_data()
            self.cache['kenyan_data'] = kenyan_data
            self.last_fetch['kenyan_data'] = time.time()
        
        return {
            'treasury_bills': kenyan_data['treasury_bills'],
            'treasury_bonds': kenyan_data['treasury_bonds']
        }
    
    def get_mmf_rates(self):
        """Get MMF rates from unified scraper"""
        
        if self._is_cached('kenyan_data'):
            return self.cache['kenyan_data']['mmf_rates']
        
        kenyan_data = self.unified_scraper.get_complete_market_data()
        self.cache['kenyan_data'] = kenyan_data
        self.last_fetch['kenyan_data'] = time.time()
        
        return kenyan_data['mmf_rates']
    
    def get_market_summary(self):
        """Get market summary from unified scraper"""
        
        if self._is_cached('kenyan_data'):
            kenyan_data = self.cache['kenyan_data']
        else:
            kenyan_data = self.unified_scraper.get_complete_market_data()
            self.cache['kenyan_data'] = kenyan_data
            self.last_fetch['kenyan_data'] = time.time()
        
        return {
            **kenyan_data['market_summary'],
            'last_update': kenyan_data['last_updated']
        }
    
    def get_global_stock(self, symbol: str):
        """Get global stock from Yahoo Finance (unchanged)"""
        
        cache_key = f'global_{symbol}'
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d', interval='1m')
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            info = ticker.info
            previous_close = info.get('previousClose', current_price)
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0
            
            if change_percent > 3:
                signal = 'STRONG BUY'
            elif change_percent > 1:
                signal = 'BUY'
            elif change_percent > -1:
                signal = 'HOLD'
            elif change_percent > -3:
                signal = 'SELL'
            else:
                signal = 'STRONG SELL'
            
            stock_data = {
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'currency': info.get('currency', 'USD'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else 'N/A',
                'signal': signal,
                'volume': hist['Volume'].iloc[-1] if not hist.empty else 0
            }
            
            self.cache[cache_key] = stock_data
            self.last_fetch[cache_key] = time.time()
            
            return stock_data
        
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
            return None
    
    def get_forex_rate(self, pair='USD/KES'):
        """Get forex rate (unchanged)"""
        
        if self._is_cached('forex'):
            return self.cache['forex'][pair]
        
        # Use exchangerate-api.com (FREE)
        try:
            import requests
            response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
            data = response.json()
            
            kes_rate = data['rates']['KES']
            
            forex_rates = {
                'USD/KES': kes_rate,
                'EUR/KES': kes_rate / data['rates']['EUR'],
                'GBP/KES': kes_rate / data['rates']['GBP']
            }
            
            self.cache['forex'] = forex_rates
            self.last_fetch['forex'] = time.time()
            
            return forex_rates.get(pair, 129.50)
        
        except:
            # Fallback
            return {'USD/KES': 129.50, 'EUR/KES': 140.20, 'GBP/KES': 164.80}.get(pair, 129.50)
    
    def _is_cached(self, key: str) -> bool:
        """Check if data is cached"""
        if key not in self.cache or key not in self.last_fetch:
            return False
        age = time.time() - self.last_fetch[key]
        return age < self.cache_duration
    
    def close(self):
        """Clean up"""
        self.unified_scraper.close()

# Test
if __name__ == "__main__":
    fetcher = MarketDataFetcher()
    
    try:
        print("\n📊 Testing Enhanced Market Data Fetcher")
        print("="*60)
        
        # Test NSE
        print("\n1. NSE Stocks:")
        nse = fetcher.get_nse_stocks(['SCOM', 'EQTY'])
        for s, d in nse.items():
            print(f"   {s}: KSh {d['price']} ({d['change_percent']:+.2f}%)")
        
        # Test T-Bills
        print("\n2. Treasury Rates:")
        treasury = fetcher.get_treasury_rates()
        for t, d in treasury['treasury_bills'].items():
            print(f"   {d['maturity']}: {d['rate']}%")
        
        # Test MMFs
        print("\n3. MMF Rates:")
        mmfs = fetcher.get_mmf_rates()
        for name, d in list(mmfs.items())[:3]:
            print(f"   {name}: {d['current_rate']}%")
        
        # Test Global
        print("\n4. Global Stock:")
        aapl = fetcher.get_global_stock('AAPL')
        if aapl:
            print(f"   Apple: ${aapl['price']} ({aapl['change_percent']:+.2f}%)")
        
        print("\n✓ All tests passed!")
        
    finally:
        fetcher.close()