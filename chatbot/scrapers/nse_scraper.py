"""
NSE Stock Scraper
Scrapes live stock prices from Nairobi Securities Exchange
"""

import sys
from pathlib import Path

# Fix imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NSEScraper:
    """Scrape NSE stock data"""
    
    def __init__(self, headless=True, use_fallback=True):
        """
        Initialize NSE scraper
        
        Args:
            headless: Run browser without GUI
            use_fallback: Return demo data if scraping fails
        """
        self.driver = None
        self.use_fallback = use_fallback
        
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✓ NSE Scraper initialized (Selenium mode)")
        except Exception as e:
            logger.warning(f"Selenium not available: {e}")
            if not use_fallback:
                raise
            logger.info("✓ NSE Scraper initialized (Fallback mode)")
    
    def scrape_nse_stocks(self, symbols=None):
        """
        Scrape NSE stock prices
        
        Args:
            symbols: List of stock symbols (e.g., ['SCOM', 'EQTY'])
        
        Returns:
            Dict with stock data
        """
        
        if not self.driver:
            logger.info("Using fallback data (Selenium not available)")
            return self._get_fallback_data(symbols)
        
        try:
            logger.info("🔍 Scraping NSE website...")
            
            # Navigate to NSE
            url = "https://www.nse.co.ke/live-market-data.html"
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(5)
            
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try to find stock table
            # NOTE: You'll need to inspect NSE website to find actual selectors
            stock_table = soup.find('table', {'class': 'market-data-table'})
            
            if not stock_table:
                # Try alternate selectors
                stock_table = soup.find('table', {'id': 'live-market-table'})
            
            if not stock_table:
                logger.warning("Could not find stock table, using fallback")
                return self._get_fallback_data(symbols)
            
            # Parse table
            stocks = {}
            rows = stock_table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cols = row.find_all('td')
                
                if len(cols) >= 5:
                    try:
                        symbol = cols[0].text.strip()
                        price = float(cols[1].text.strip().replace(',', ''))
                        change = float(cols[2].text.strip().replace(',', ''))
                        volume = int(cols[4].text.strip().replace(',', ''))
                        
                        change_percent = (change / (price - change)) * 100 if price > 0 else 0
                        
                        stocks[symbol] = {
                            'name': self._get_company_name(symbol),
                            'price': round(price, 2),
                            'change': round(change, 2),
                            'change_percent': round(change_percent, 2),
                            'volume': volume,
                            'signal': self._calculate_signal(change_percent),
                            'last_updated': datetime.now().isoformat(),
                            'source': 'NSE Website (Live)'
                        }
                    except Exception as e:
                        logger.warning(f"Error parsing row: {e}")
                        continue
            
            if stocks:
                logger.info(f"✓ Scraped {len(stocks)} NSE stocks")
                
                # Filter by requested symbols
                if symbols:
                    stocks = {k: v for k, v in stocks.items() if k in symbols}
                
                return stocks
            else:
                logger.warning("No stocks parsed, using fallback")
                return self._get_fallback_data(symbols)
        
        except Exception as e:
            logger.error(f"NSE scraping failed: {e}")
            return self._get_fallback_data(symbols)
    
    def _calculate_signal(self, change_percent):
        """Generate BUY/SELL/HOLD signal"""
        if change_percent > 2:
            return 'STRONG BUY'
        elif change_percent > 0.5:
            return 'BUY'
        elif change_percent > -0.5:
            return 'HOLD'
        elif change_percent > -2:
            return 'SELL'
        else:
            return 'STRONG SELL'
    
    def _get_company_name(self, symbol):
        """Map symbol to company name"""
        names = {
            'SCOM': 'Safaricom',
            'EQTY': 'Equity Bank',
            'KCB': 'KCB Group',
            'COOP': 'Co-operative Bank',
            'NCBA': 'NCBA Group',
            'EABL': 'East African Breweries',
            'BAT': 'BAT Kenya',
            'BAMB': 'Bamburi Cement',
            'KEGN': 'KenGen',
            'SBIC': 'Stanbic Bank',
            'ABSA': 'ABSA Bank Kenya',
            'DTB': 'Diamond Trust Bank'
        }
        return names.get(symbol, symbol)
    
    def _get_fallback_data(self, symbols=None):
        """
        Return realistic simulated data
        
        This ensures chatbot works even if scraping fails
        """
        
        import random
        
        logger.info("📊 Generating realistic fallback data")
        
        # Base prices (realistic NSE prices)
        base_prices = {
            'SCOM': 18.00,
            'EQTY': 52.00,
            'KCB': 38.00,
            'COOP': 14.50,
            'NCBA': 48.00,
            'EABL': 185.00,
            'BAT': 410.00,
            'BAMB': 28.00
        }
        
        stocks = {}
        
        # Filter if symbols specified
        symbols_to_use = symbols if symbols else list(base_prices.keys())
        
        for symbol in symbols_to_use:
            if symbol not in base_prices:
                continue
            
            base_price = base_prices[symbol]
            
            # Simulate realistic daily movement (-3% to +3%)
            change_percent = random.uniform(-3, 3)
            change = base_price * (change_percent / 100)
            current_price = base_price + change
            
            # Realistic volume
            volumes = {
                'SCOM': 15000000,
                'EQTY': 3500000,
                'KCB': 2800000,
                'EABL': 450000,
                'BAT': 120000,
                'BAMB': 200000,
                'COOP': 2000000,
                'NCBA': 1500000
            }
            
            stocks[symbol] = {
                'name': self._get_company_name(symbol),
                'price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'volume': volumes.get(symbol, 1000000) + random.randint(-100000, 100000),
                'signal': self._calculate_signal(change_percent),
                'last_updated': datetime.now().isoformat(),
                'source': 'Simulated Data (NSE unavailable)'
            }
        
        return stocks
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ NSE Scraper closed")

# Test
if __name__ == "__main__":
    scraper = NSEScraper(headless=True)
    
    try:
        stocks = scraper.scrape_nse_stocks(['SCOM', 'EQTY', 'KCB'])
        
        print("\n" + "="*60)
        print("NSE STOCKS")
        print("="*60)
        
        for symbol, data in stocks.items():
            print(f"\n{symbol} - {data['name']}")
            print(f"  Price: KSh {data['price']} ({data['change_percent']:+.2f}%)")
            print(f"  Signal: {data['signal']}")
            print(f"  Source: {data['source']}")
    
    finally:
        scraper.close()