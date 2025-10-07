"""
Scrape FAQs from Kenyan Banks
Targets: Equity Bank, KCB, Co-op Bank, Safaricom M-Pesa
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KenyanBankFAQScraper:
    """Scrape FAQs from major Kenyan banks"""
    
    def __init__(self):
        self.output_path = Path("data/raw/kenyan_banks_faq")
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_equity_bank(self):
        """Scrape Equity Bank Kenya FAQs"""
        
        logger.info("\n" + "-" * 60)
        logger.info("SCRAPING EQUITY BANK KENYA")
        logger.info("-" * 60)
        
        faqs = []
        
        try:
            # Equity Bank FAQ page (adjust URL if needed)
            url = "https://equity.custhelp.com/app/answers/list"
            
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch (Status: {response.status_code})")
                return faqs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors to find FAQs
            # Approach 1: Look for accordion/FAQ structures
            faq_containers = soup.find_all(['div', 'section'], class_=lambda x: x and ('faq' in str(x).lower() or 'accordion' in str(x).lower()))
            
            logger.info(f"Found {len(faq_containers)} potential FAQ sections")
            
            for container in faq_containers:
                # Find Q&A pairs
                questions = container.find_all(['h3', 'h4', 'h5', 'strong', 'button'])
                
                for q_elem in questions:
                    q_text = q_elem.get_text(strip=True)
                    
                    # Skip if too short
                    if len(q_text) < 10:
                        continue
                    
                    # Look for answer (usually next sibling or parent's next sibling)
                    answer = None
                    
                    # Try finding answer in next sibling
                    next_elem = q_elem.find_next_sibling(['p', 'div'])
                    if next_elem:
                        answer = next_elem.get_text(strip=True)
                    
                    # Try finding in parent's next sibling
                    if not answer and q_elem.parent:
                        next_elem = q_elem.parent.find_next_sibling(['p', 'div'])
                        if next_elem:
                            answer = next_elem.get_text(strip=True)
                    
                    if answer and len(answer) > 20:
                        faqs.append({
                            'bank': 'Equity Bank Kenya',
                            'question': q_text,
                            'answer': answer,
                            'url': url
                        })
            
            logger.info(f"✓ Scraped {len(faqs)} FAQs from Equity Bank")
            
        except Exception as e:
            logger.error(f"Error scraping Equity Bank: {e}")
        
        return faqs
    
    def scrape_kcb(self):
        """Scrape KCB Bank FAQs"""
        
        logger.info("\n" + "-" * 60)
        logger.info("SCRAPING KCB BANK")
        logger.info("-" * 60)
        
        faqs = []
        
        try:
            url = "https://ke.kcbgroup.com/quick-links/faqs"
            
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch (Status: {response.status_code})")
                return faqs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for FAQ sections
            faq_items = soup.find_all(['div', 'section'], class_=lambda x: x and 'faq' in str(x).lower())
            
            for item in faq_items:
                q = item.find(['h3', 'h4', 'h5', 'dt', 'strong'])
                a = item.find(['p', 'dd', 'div'])
                
                if q and a:
                    q_text = q.get_text(strip=True)
                    a_text = a.get_text(strip=True)
                    
                    if len(q_text) > 10 and len(a_text) > 20:
                        faqs.append({
                            'bank': 'KCB Bank Kenya',
                            'question': q_text,
                            'answer': a_text,
                            'url': url
                        })
            
            logger.info(f"✓ Scraped {len(faqs)} FAQs from KCB")
            
        except Exception as e:
            logger.error(f"Error scraping KCB: {e}")
        
        return faqs
    
    def scrape_coop_bank(self):
        """Scrape Co-operative Bank FAQs"""
        
        logger.info("\n" + "-" * 60)
        logger.info("SCRAPING CO-OPERATIVE BANK")
        logger.info("-" * 60)
        
        faqs = []
        
        try:
            url = "https://www.co-opbank.co.ke/faqs/"
            
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch (Status: {response.status_code})")
                return faqs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for FAQs
            faq_sections = soup.find_all(['div', 'section'], class_=lambda x: x and 'faq' in str(x).lower())
            
            for section in faq_sections:
                questions = section.find_all(['h3', 'h4', 'strong', 'dt'])
                answers = section.find_all(['p', 'dd'])
                
                for q, a in zip(questions, answers):
                    q_text = q.get_text(strip=True)
                    a_text = a.get_text(strip=True)
                    
                    if len(q_text) > 10 and len(a_text) > 20:
                        faqs.append({
                            'bank': 'Co-operative Bank Kenya',
                            'question': q_text,
                            'answer': a_text,
                            'url': url
                        })
            
            logger.info(f"✓ Scraped {len(faqs)} FAQs from Co-op Bank")
            
        except Exception as e:
            logger.error(f"Error scraping Co-op Bank: {e}")
        
        return faqs
    
    def scrape_mpesa(self):
        """Scrape M-Pesa information"""
        
        logger.info("\n" + "-" * 60)
        logger.info("SCRAPING M-PESA (SAFARICOM)")
        logger.info("-" * 60)
        
        faqs = []
        
        try:
            url = "https://www.safaricom.co.ke/media-center-landing/frequently-asked-questions"
            
            logger.info(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch (Status: {response.status_code})")
                return faqs
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get M-Pesa content
            headings = soup.find_all(['h2', 'h3', 'h4'])
            
            for heading in headings:
                q_text = heading.get_text(strip=True)
                
                # Skip very short headings
                if len(q_text) < 5:
                    continue
                
                # Get following paragraph
                next_p = heading.find_next('p')
                if next_p:
                    a_text = next_p.get_text(strip=True)
                    
                    if len(a_text) > 20:
                        faqs.append({
                            'bank': 'Safaricom M-Pesa',
                            'question': q_text,
                            'answer': a_text,
                            'url': url
                        })
            
            logger.info(f"✓ Scraped {len(faqs)} M-Pesa FAQs")
            
        except Exception as e:
            logger.error(f"Error scraping M-Pesa: {e}")
        
        return faqs
    
    def add_manual_faqs(self):
        """Add manually curated FAQs about Kenyan banking"""
        
        logger.info("\n" + "-" * 60)
        logger.info("ADDING MANUAL KENYAN BANKING FAQs")
        logger.info("-" * 60)
        
        manual_faqs = [
            {
                'bank': 'General Kenya',
                'question': 'What is M-Pesa?',
                'answer': 'M-Pesa is a mobile money transfer service by Safaricom that allows users to deposit, withdraw, transfer money and pay for goods and services using their mobile phones.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'What is a Chama?',
                'answer': 'A Chama is a Kenyan term for an informal savings group where members contribute money regularly and take turns to receive the pooled funds.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'What is a SACCO?',
                'answer': 'SACCO stands for Savings and Credit Cooperative. It is a member-owned financial cooperative that provides savings and loan services to its members at favorable rates.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'How do I send money via M-Pesa?',
                'answer': 'Dial *334#, select Send Money, enter recipient phone number, enter amount, enter your M-Pesa PIN to confirm the transaction.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'What are M-Pesa charges?',
                'answer': 'M-Pesa charges vary based on transaction amount. For example, sending KSh 100-500 costs KSh 11, KSh 501-1000 costs KSh 22, and larger amounts have higher charges.',
                'url': 'manual'
            },
            {
                'bank': 'Equity Bank Kenya',
                'question': 'How do I open an account at Equity Bank?',
                'answer': 'Visit any Equity Bank branch with your ID card. Fill the account opening form, deposit minimum KSh 100, and receive your account details and ATM card.',
                'url': 'manual'
            },
            {
                'bank': 'KCB Bank Kenya',
                'question': 'What is KCB M-PESA?',
                'answer': 'KCB M-PESA is an account that allows you to save, borrow and earn interest on your M-Pesa wallet balance. You can access loans instantly through M-Pesa.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'How do I join a SACCO in Kenya?',
                'answer': 'Find a SACCO that matches your needs, fill membership forms, pay registration fee and opening share capital, attend induction, and start saving regularly.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'What is mobile banking in Kenya?',
                'answer': 'Mobile banking allows you to access banking services through your phone - check balance, transfer money, pay bills, and apply for loans without visiting a branch.',
                'url': 'manual'
            },
            {
                'bank': 'General Kenya',
                'question': 'How do I save money in Kenya?',
                'answer': 'You can save through: 1) Bank savings accounts 2) SACCOs 3) Chamas 4) M-Shwari or KCB M-Pesa 5) Fixed deposits 6) Investment in shares or treasury bills.',
                'url': 'manual'
            }
        ]
        
        logger.info(f"✓ Added {len(manual_faqs)} manual FAQs")
        
        return manual_faqs
    
    def scrape_all(self):
        """Scrape all banks"""
        
        logger.info("\n" + "=" * 60)
        logger.info(" 🌐 KENYAN BANK FAQ SCRAPER")
        logger.info("=" * 60)
        
        all_faqs = []
        
        # Scrape each bank (with delays to be polite)
        all_faqs.extend(self.scrape_equity_bank())
        time.sleep(3)
        
        all_faqs.extend(self.scrape_kcb())
        time.sleep(3)
        
        all_faqs.extend(self.scrape_coop_bank())
        time.sleep(3)
        
        all_faqs.extend(self.scrape_mpesa())
        time.sleep(2)
        
        # Add manual FAQs
        all_faqs.extend(self.add_manual_faqs())
        
        # Convert to DataFrame
        df = pd.DataFrame(all_faqs)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['question', 'answer'])
        
        logger.info("\n" + "=" * 60)
        logger.info(" 📊 SCRAPING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total FAQs collected: {len(df)}")
        logger.info(f"Banks covered: {df['bank'].nunique()}")
        logger.info(f"\nBreakdown by bank:")
        print(df['bank'].value_counts())
        
        # Save combined file
        output_file = self.output_path / "kenyan_banks_faqs.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"\n✓ Saved all FAQs: {output_file}")
        
        # Save by bank
        for bank in df['bank'].unique():
            bank_df = df[df['bank'] == bank]
            bank_filename = bank.replace(' ', '_').replace('-', '_').lower() + ".csv"
            bank_file = self.output_path / bank_filename
            bank_df.to_csv(bank_file, index=False)
            logger.info(f"  - {bank}: {len(bank_df)} FAQs → {bank_filename}")
        
        # Show sample
        logger.info("\n" + "=" * 60)
        logger.info(" 📝 SAMPLE FAQs")
        logger.info("=" * 60)
        for i in range(min(3, len(df))):
            logger.info(f"\n{i+1}. Bank: {df.iloc[i]['bank']}")
            logger.info(f"   Q: {df.iloc[i]['question']}")
            logger.info(f"   A: {df.iloc[i]['answer'][:100]}...")
        
        logger.info("\n" + "=" * 60)
        logger.info(" ✓ SCRAPING COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"\n📁 Files saved to: {self.output_path}/")
        
        if len(df) < 50:
            logger.warning("\n⚠️  WARNING: Less than 50 FAQs collected!")
            logger.info("Website structures may have changed.")
            logger.info("Consider:")
            logger.info("  1. Manual FAQ collection from bank websites")
            logger.info("  2. Adjusting scraper selectors")
            logger.info("  3. Using the 10 manual FAQs as a starting point")
        
        return df

if __name__ == "__main__":
    scraper = KenyanBankFAQScraper()
    df = scraper.scrape_all()