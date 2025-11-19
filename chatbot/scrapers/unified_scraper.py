"""
Unified Kenyan Market Data
Combines NSE, CBK, and MMF data
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from chatbot.scrapers.nse_scraper import NSEScraper
from chatbot.scrapers.cbk_scraper import CBKScraper
from chatbot.scrapers.mmf_scraper import MMFScraper
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedKenyanMarketData:
    """
    ONE CLASS TO RULE THEM ALL
    
    Combines:
    - NSE stocks
    - CBK T-Bills and Bonds  
    - MMF rates
    """
    
    def __init__(self, use_selenium=False):
        """
        Initialize all scrapers
        
        Args:
            use_selenium: Enable NSE web scraping (requires ChromeDriver)
        """
        
        logger.info("🚀 Initializing Unified Kenyan Market Data...")
        
        # Initialize scrapers
        self.nse_scraper = NSEScraper(headless=True, use_fallback=True)
        self.cbk_scraper = CBKScraper()
        self.mmf_scraper = MMFScraper()
        
        self.cache = {}
        self.last_update = None
        
        logger.info("✓ All scrapers initialized")
    
    def get_complete_market_data(self):
        """
        Fetch EVERYTHING
        
        Returns:
            {
                'nse_stocks': {...},
                'treasury_bills': {...},
                'treasury_bonds': {...},
                'mmf_rates': {...},
                'market_summary': {...},
                'last_updated': '...'
            }
        """
        
        logger.info("\n" + "="*60)
        logger.info("FETCHING COMPLETE KENYAN MARKET DATA")
        logger.info("="*60)
        
        # 1. NSE Stocks
        logger.info("\n1️⃣ NSE Stocks...")
        nse_stocks = self.nse_scraper.scrape_nse_stocks()
        
        # 2. Government Securities
        logger.info("\n2️⃣ CBK Government Securities...")
        gov_securities = self.cbk_scraper.get_all_government_securities()
        
        # 3. MMF Rates
        logger.info("\n3️⃣ Money Market Funds...")
        mmf_rates = self.mmf_scraper.scrape_all_mmfs()
        
        # 4. Market Summary
        market_summary = self._generate_market_summary(nse_stocks)
        
        data = {
            'nse_stocks': nse_stocks,
            'treasury_bills': gov_securities['treasury_bills'],
            'treasury_bonds': gov_securities['treasury_bonds'],
            'mmf_rates': mmf_rates,
            'market_summary': market_summary,
            'last_updated': datetime.now().isoformat(),
            'data_sources': {
                'nse': 'NSE Website / Simulated',
                'cbk': 'Current Market Rates',
                'mmf': 'Current Market Rates'
            }
        }
        
        # Cache it
        self.cache = data
        self.last_update = datetime.now()
        
        logger.info("\n✓ Complete market data fetched successfully!")
        logger.info(f"   NSE: {len(nse_stocks)} stocks")
        logger.info(f"   T-Bills: {len(gov_securities['treasury_bills'])} tenors")
        logger.info(f"   Bonds: {len(gov_securities['treasury_bonds'])} maturities")
        logger.info(f"   MMFs: {len(mmf_rates)} funds")
        
        return data
    
    def _generate_market_summary(self, nse_stocks):
        """Generate market overview"""
        
        if not nse_stocks:
            return {
                'sentiment': 'UNKNOWN',
                'gainers': 0,
                'losers': 0,
                'total_stocks': 0
            }
        
        gainers = sum(1 for s in nse_stocks.values() if s['change'] > 0)
        losers = sum(1 for s in nse_stocks.values() if s['change'] < 0)
        
        avg_change = sum(s['change_percent'] for s in nse_stocks.values()) / len(nse_stocks)
        
        if avg_change > 1:
            sentiment = 'BULLISH'
            emoji = '🟢'
        elif avg_change < -1:
            sentiment = 'BEARISH'
            emoji = '🔴'
        else:
            sentiment = 'NEUTRAL'
            emoji = '🟡'
        
        return {
            'sentiment': sentiment,
            'emoji': emoji,
            'gainers': gainers,
            'losers': losers,
            'total_stocks': len(nse_stocks),
            'avg_change': round(avg_change, 2)
        }
    
    def close(self):
        """Clean up"""
        self.nse_scraper.close()
        logger.info("✓ All scrapers closed")

# Test
if __name__ == "__main__":
    fetcher = UnifiedKenyanMarketData()
    
    try:
        data = fetcher.get_complete_market_data()
        
        print("\n" + "="*60)
        print("COMPLETE MARKET DATA SUMMARY")
        print("="*60)
        
        print(f"\n📊 Market Sentiment: {data['market_summary']['emoji']} {data['market_summary']['sentiment']}")
        print(f"   Gainers: {data['market_summary']['gainers']} | Losers: {data['market_summary']['losers']}")
        
        print(f"\n💰 Top T-Bill Rate: {max(data['treasury_bills'].values(), key=lambda x: x['rate'])['rate']}%")
        print(f"💵 Top MMF: {max(data['mmf_rates'].items(), key=lambda x: x[1]['current_rate'])}")
        
    finally:
        fetcher.close()