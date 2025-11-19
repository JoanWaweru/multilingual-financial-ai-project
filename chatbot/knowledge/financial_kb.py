"""
Financial Knowledge Base with comprehensive Kenyan and global financial Q&As
"""

import pandas as pd
from pathlib import Path
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialKnowledgeBase:
    """Knowledge base for financial Q&A"""
    
    def __init__(self, use_bitext=True):
        """Initialize knowledge base"""
        
        if use_bitext:
            # Try to load Bitext-based KB
            bitext_kb_path = Path("data/processed/chatbot_knowledge_base.csv")
            
            if bitext_kb_path.exists():
                self.qa_df = pd.read_csv(bitext_kb_path)
                logger.info(f"✓ Loaded {len(self.qa_df)} Q&A pairs from Bitext KB")
                
                # Add Kenyan-specific Q&As to supplement Bitext
                kenyan_qa = self._create_kenyan_qa()
                self.qa_df = pd.concat([self.qa_df, kenyan_qa], ignore_index=True)
                logger.info(f"✓ Added {len(kenyan_qa)} Kenyan-specific Q&As")
                logger.info(f"✓ Total: {len(self.qa_df)} Q&A pairs")
            else:
                logger.warning(f"Bitext KB not found at {bitext_kb_path}")
                logger.info("Creating default KB with Kenyan Q&As...")
                self.qa_df = self._create_kenyan_qa()
        else:
            # Use default Kenyan-only KB
            self.qa_df = self._create_kenyan_qa()
        
        # Create TF-IDF vectorizer for question matching
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.95
        )
        
        # Fit on questions
        questions = self.qa_df['question'].fillna('').values
        self.question_vectors = self.vectorizer.fit_transform(questions)
        
        logger.info("✓ Knowledge base initialized")
    
    def _create_kenyan_qa(self):
        """Create comprehensive Kenyan-specific Q&As"""
        
        kenyan_qa = [
            # ==================== M-PESA ====================
            {
                'question': 'What is M-Pesa?',
                'answer': 'M-Pesa is Kenya\'s mobile money service by Safaricom. You can send money, pay bills, buy airtime, save, and borrow - all from your phone. To use: Dial *334#, no bank account needed. It\'s the most popular way Kenyans handle money! Over 30 million users.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I send money via M-Pesa?',
                'answer': 'To send money: 1) Dial *334#, 2) Select "Send Money", 3) Enter phone number, 4) Enter amount, 5) Enter your PIN. Charges: KSh 11 for KSh 100-500, KSh 22 for KSh 501-1,000. Money arrives instantly!',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I check M-Pesa balance?',
                'answer': 'To check balance: Dial *334#, select "My Account", then "Show Balance", enter PIN. Or send empty SMS to 234. Your balance will be shown immediately.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'Can I borrow money from M-Pesa?',
                'answer': 'Yes! M-Shwari and Fuliza offer M-Pesa loans. M-Shwari: Save first, then borrow up to 3x your savings. Fuliza: Overdraft when you have insufficient balance. Also try: KCB M-Pesa (higher limits, lower rates).',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'What are M-Pesa charges?',
                'answer': 'M-Pesa sending charges: KSh 0-100 (Free), KSh 101-500 (KSh 11), KSh 501-1,000 (KSh 22), KSh 1,001-1,500 (KSh 33), KSh 1,501-2,500 (KSh 54). Withdrawal charges similar. Sending to bank free! Check full tariff at Safaricom website.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            
            # ==================== CHAMAS ====================
            {
                'question': 'What is a chama?',
                'answer': 'A chama is a Kenyan savings group where friends/family contribute monthly (e.g. KSh 5,000 each). Members take turns receiving the pooled money. Great for: buying land, starting business, emergency funds. Very popular in Kenya - over 300,000 chamas nationwide!',
                'category': 'chama',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I start a chama?',
                'answer': 'To start: 1) Gather 5-15 trusted people, 2) Agree on monthly contribution (e.g. KSh 2,000-10,000), 3) Choose leaders (chair, treasurer, secretary), 4) Write simple rules, 5) Open group bank account (optional), 6) Start contributing! Meet monthly to distribute funds.',
                'category': 'chama',
                'is_kenyan_specific': True
            },
            {
                'question': 'How much should I contribute to my chama?',
                'answer': 'Contribute 10-20% of monthly income. Example: Earning KSh 50,000? Contribute KSh 5,000-10,000. Start small if needed - even KSh 1,000/month builds savings. Make sure amount is comfortable for all members.',
                'category': 'chama',
                'is_kenyan_specific': True
            },
            
            # ==================== SACCOs ====================
            {
                'question': 'What is a SACCO?',
                'answer': 'SACCO = Savings and Credit Cooperative. Member-owned institution offering: savings accounts (8-12% interest), cheap loans (10-12% interest), shares/dividends. Better rates than banks! Popular SACCOs: Stima, Mwalimu, Kenya Police, Harambee.',
                'category': 'sacco',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I join a SACCO?',
                'answer': 'To join: 1) Choose SACCO (check if your employer/profession has one), 2) Pay registration fee (KSh 500-1,000), 3) Buy shares (minimum KSh 5,000-10,000), 4) Start saving monthly. After 6 months, you qualify for loans up to 3x your savings!',
                'category': 'sacco',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is the difference between a SACCO and a bank?',
                'answer': 'SACCO: Member-owned, higher interest on savings (8-12%), cheaper loans (10-12%), share dividends, less accessible. BANK: Investor-owned, lower interest (2-5%), higher loan rates (13-18%), many branches, more accessible. Best: Keep emergency fund in bank, long-term savings in SACCO.',
                'category': 'sacco',
                'is_kenyan_specific': True
            },
            
            # ==================== BANKING ====================
            {
                'question': 'Which bank is best in Kenya?',
                'answer': 'Top banks: 1) Equity Bank - low fees, many branches, good mobile app, 2) KCB - largest, everywhere in Kenya, 3) Co-operative Bank - SACCO-friendly, 4) NCBA - good digital banking. Choose based on: branch location, fees, mobile app quality.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I open a bank account in Kenya?',
                'answer': 'To open account: 1) Go to any bank with National ID, 2) Fill form, 3) Deposit minimum (KSh 100-1,000 depending on bank), 4) Get account number + ATM card. Some banks (Equity, KCB) let you open via mobile app!',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            {
                'question': 'What documents do I need to open a bank account?',
                'answer': 'Required: 1) National ID or Passport, 2) KRA PIN certificate (some banks), 3) Passport photo, 4) Proof of residence (utility bill or tenancy agreement). Some banks need employment letter if opening salary account.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            
            # ==================== SAVINGS & INVESTMENT AMOUNTS ====================
            {
                'question': 'I have 100k KES where should I invest?',
                'answer': 'Great! With KSh 100,000, here are smart options: 1) Open MMF account (Sanlam/CIC) - earn 10-12% annually, withdraw anytime, 2) Buy Treasury Bills through your bank - 15-17% returns, lock for 91-364 days, very safe, 3) Join a SACCO - deposit and qualify for loans, 4) Split: 50k in MMF (emergency), 30k in T-Bill (high return), 20k in SACCO (loans access). Start with what feels safe!',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'I have 50k KES where should I save it?',
                'answer': 'With KSh 50,000, smart options: 1) Join a SACCO - deposit KSh 30k, earn dividends + qualify for loans, 2) MMF like Sanlam - KSh 20k, earn 10% annually, withdraw anytime, 3) M-Shwari savings - easy access via M-Pesa. Don\'t keep it all at home! Even a simple bank savings account is better than nothing.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            {
                'question': 'I have 200k KES what should I do with it?',
                'answer': 'Excellent! With KSh 200,000: 1) Emergency fund: Keep KSh 50k in MMF (easy access), 2) T-Bills: Invest KSh 100k (15-17% returns), 3) SACCO: Deposit KSh 30k (qualify for bigger loans), 4) Chama: Join with KSh 20k. Or consider: 50% safe (MMF/T-Bills), 30% growth (SACCO/NSE stocks if experienced), 20% emergency fund.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'Where should I invest my money in Kenya?',
                'answer': 'Best places to invest in Kenya: 1) SACCOs - safest, 8-12% returns + loans, 2) Money Market Funds - flexible, 10-12% returns, 3) Treasury Bills/Bonds - government-backed, 12-17% returns, 4) Real estate - long-term, but needs large capital, 5) NSE stocks - higher risk/reward. For beginners: Start with SACCOs or MMFs. They are safe and teach you about investing.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'Where should I put my savings?',
                'answer': 'Best savings options: 1) SACCO account - highest interest (8-12%), get dividends, qualify for cheap loans, 2) MMF (Money Market Fund) - 10-12% returns, withdraw anytime, 3) Bank savings account - safe, accessible, but low interest (2-5%), 4) Chama - forced savings, community support. Avoid: Keeping cash at home (no growth, theft risk). Mix them: emergency money in bank, long-term in SACCO/MMF.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            {
                'question': 'How much should I save each month?',
                'answer': 'Save 20-30% of income. Example: Earning KSh 50,000? Save KSh 10,000-15,000. Split it: Emergency fund (50%), Long-term goals (30%), Investments (20%). Start with even KSh 1,000/month - consistency matters more than amount!',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            
            # ==================== TREASURY BILLS & BONDS ====================
            {
                'question': 'What is the difference between MMFs and government bonds?',
                'answer': 'MMFs (Money Market Funds): Short-term, withdraw anytime, 8-12% returns, low risk, start with KSh 1,000. Examples: Sanlam, CIC, Britam. Government Bonds: Long-term (2-30 years), locked, 12-15% returns, minimum KSh 50,000. MMFs = flexibility, Bonds = higher returns but locked.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I invest in treasury bills in Kenya?',
                'answer': 'To invest in T-Bills: 1) Open CDS account (Central Depository System) at CBK or your bank, 2) Have KSh 100,000 minimum, 3) Buy via bank or CBK mobile app, 4) Choose: 91, 182, or 364 days, 5) Earn 15-17% interest at maturity. Very safe, government-backed.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'What are MMFs?',
                'answer': 'Money Market Funds (MMFs) are low-risk investments where you pool money with others to invest in short-term securities. In Kenya, popular MMFs include Sanlam, CIC, and Britam. Benefits: Higher returns than savings accounts (8-12%), withdraw anytime, minimum investment as low as KSh 1,000. Good for: Emergency funds, short-term savings, beginners.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'What are government bonds?',
                'answer': 'Government bonds are loans you give to the Kenyan government, and they pay you interest. Types: Infrastructure Bonds (build roads, etc.), Treasury Bonds (general government funding). Returns: 12-15% per year. Minimum: KSh 50,000. Lock-in period: 2-30 years. Very safe but your money is locked. Good for: Long-term savings, retirement planning.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            
            # ==================== LOANS ====================
            {
                'question': 'How do I get a loan?',
                'answer': 'In Kenya, you can get loans from: 1) Banks (requires good credit history), 2) SACCOs (for members), 3) Mobile lending apps (Tala, Branch, M-Shwari), 4) Your chama. Requirements and interest rates vary.',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is mobile lending?',
                'answer': 'Mobile lending apps like Tala, Branch, M-Shwari, and KCB M-Pesa offer instant loans on your phone. They assess your credit using phone data and offer loans within minutes, but interest rates are higher than banks (7-15% per month).',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            {
                'question': 'Which mobile loan apps are best in Kenya?',
                'answer': 'Popular loan apps: 1) M-Shwari - integrated with M-Pesa, 2) KCB M-Pesa - lower interest, 3) Tala - fast approval, 4) Branch - good for regulars, 5) Fuliza - M-Pesa overdraft. Warning: High interest! Use only for emergencies. Repay on time to avoid CRB listing.',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            
            # ==================== NSE STOCKS ====================
            {
                'question': 'How do I buy stocks in Kenya?',
                'answer': 'To buy NSE stocks: 1) Open CDS account (Central Depository System) at any stockbroker or bank with brokerage, 2) Deposit money (minimum varies), 3) Tell broker which stocks to buy (like Safaricom, Equity, KCB), 4) Pay fees (1.3% + other charges). Popular brokers: Genghis Capital, Sterling Capital, Old Mutual. Or use apps: Hisa (minimum KSh 100!), or bank platforms.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is NSE?',
                'answer': 'NSE (Nairobi Securities Exchange) is Kenya\'s stock market where companies list their shares for public trading. Popular stocks: Safaricom (telecom), Equity Bank, KCB, East African Breweries, Bamburi Cement. You can buy shares and earn from: dividends (company profits shared) and capital gains (selling higher than buying price). Higher risk than bonds but potential for better returns.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'Which stocks should I buy in Kenya?',
                'answer': 'Popular NSE stocks for beginners: 1) Safaricom - largest, stable, regular dividends, 2) Equity Bank - banking sector, good dividends, 3) KCB - stable bank, 4) EABL (East African Breweries) - consumer goods. Blue-chip stocks (large, stable companies) are safer for beginners. WARNING: Stock prices fluctuate! Only invest money you can afford to lose. Diversify - don\'t put all in one stock.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'How much money do I need to buy stocks?',
                'answer': 'Minimum for NSE stocks varies: Traditional brokers: KSh 10,000-50,000 minimum. Mobile apps like Hisa: Start with KSh 100-1,000! Costs involved: Brokerage fee (1.3%), CDS fee (0.06%), CDSC fee (0.14%), capital gains tax (5% on profits). Example: To buy KSh 10,000 Safaricom shares, you\'ll pay about KSh 150-200 in fees. Start small to learn!',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is Hisa app?',
                'answer': 'Hisa is a Kenyan investment app that makes buying NSE stocks super easy! Features: Start with just KSh 100 (yes, 100 bob!), buy fractional shares (own piece of expensive stocks), user-friendly app, no broker needed, auto-invest options. You can buy: Safaricom, Equity, KCB, etc. Perfect for beginners! Download from Play Store/App Store.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'What are dividends?',
                'answer': 'Dividends are profits companies share with shareholders. Example: You own 1,000 Safaricom shares. Safaricom announces KSh 1.50 dividend per share. You get: 1,000 × 1.50 = KSh 1,500 (paid to your account!). Frequency: Usually 1-2 times per year. Good dividend stocks in NSE: Safaricom, Equity Bank, KCB, EABL. Tax: 5% dividend tax (deducted automatically).',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'Are stocks risky?',
                'answer': 'YES, stocks are risky! Reality: You can LOSE money. NSE examples: Some stocks have dropped 50-80%. But also: Safaricom investors made 10x+ over years. RISKS: Company goes bankrupt, market crashes, bad management, economic downturn. REDUCE RISK: 1) Only invest money you can lose, 2) Diversify (buy 5-10 different stocks), 3) Long-term view (5+ years), 4) Start small, 5) Never borrow to invest! Stocks should be 20-30% of portfolio, not 100%.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'Should beginners invest in stocks?',
                'answer': 'Yes, BUT start smart! Beginner strategy: 1) Build emergency fund FIRST (3-6 months expenses), 2) Start with bonds/SACCOs (learn basics), 3) Then add stocks with small amount (10-20% of savings), 4) Use apps like Hisa (start with KSh 1,000-5,000), 5) Buy blue-chip stocks (Safaricom, Equity), 6) DON\'T check prices daily (causes panic). Invest for 5+ years minimum.',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is the difference between stocks and bonds?',
                'answer': 'Stocks vs Bonds: STOCKS - You own part of a company, higher risk, potential for high returns OR losses, earn from dividends + price increases, prices fluctuate daily. BONDS - You lend to government, lower risk, fixed returns (12-15%), very safe, locked for set period. Example: KSh 100k in NSE stocks might become KSh 80k or KSh 150k. Same in bonds becomes KSh 115k (predictable).',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            
            # ==================== ETFs ====================
            {
                'question': 'What are ETFs?',
                'answer': 'ETFs (Exchange Traded Funds) are baskets of stocks/bonds you buy as one investment. Instead of buying individual stocks, you buy a piece of many companies at once. Benefits: Instant diversification (spread risk), lower fees than mutual funds, trade like stocks. Kenya has few ETFs, but you can access global ones through international brokers. Example: S&P 500 ETF = owning 500 US companies with one purchase!',
                'category': 'etfs',
                'is_kenyan_specific': False
            },
            {
                'question': 'Can I buy ETFs in Kenya?',
                'answer': 'Kenya has limited local ETFs, but you can access global ETFs: 1) NSE has NewGold ETF (tracks gold prices), 2) For US/global ETFs (like S&P 500, Vanguard): Use international brokers like Interactive Brokers, TD Ameritrade (accept Kenyans), 3) Requirements: Passport, proof of address, minimum $100-500. Costs: International wire fees, forex charges. Easier: Start with NSE stocks or local unit trusts first!',
                'category': 'etfs',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I invest in ETFs?',
                'answer': 'To invest in ETFs: For LOCAL (NewGold ETF): Buy through NSE like regular stocks via broker. For INTERNATIONAL ETFs: 1) Open account with international broker (Interactive Brokers, etc.), 2) Fund account (wire transfer), 3) Buy ETFs (S&P 500, emerging markets, etc.). Popular ETFs: SPY (S&P 500), VOO (Vanguard S&P), VTI (total US market). Minimum: $100-1,000.',
                'category': 'etfs',
                'is_kenyan_specific': False
            },
            
            # ==================== GLOBAL STOCKS ====================
            {
                'question': 'Can I buy international stocks from Kenya?',
                'answer': 'Yes! You can buy US/global stocks: 1) International brokers: Interactive Brokers, TD Ameritrade, Exness (popular with Kenyans), 2) Requirements: Passport, proof of address, bank account, 3) Minimum: $100-500, 4) Process: Open online account, fund via wire transfer, start trading. Popular stocks: Apple, Tesla, Microsoft, Amazon. WARNING: Consider forex risk (USD/KES changes), wire transfer fees (KSh 3,000-5,000).',
                'category': 'global_stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'Should I invest in Kenya or international stocks?',
                'answer': 'Both have benefits! NSE (Kenya) stocks: Understand local economy, easier access, trade in KES, dividends paid in KES, cheaper fees. International stocks: Access to giants (Apple, Tesla), more diversified markets, stronger currencies (USD), BUT forex risk, higher fees, complex tax. BEST STRATEGY: Start with NSE (70%), add international (30%) as you learn.',
                'category': 'global_stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'Which international broker is best for Kenyans?',
                'answer': 'Top international brokers for Kenyans: 1) Interactive Brokers - most popular, low fees, access to US/global markets, minimum $100, 2) Exness - crypto-friendly, easy deposits, 3) TD Ameritrade - user-friendly, good research tools. Challenges: Funding (wire fees KSh 3k-5k), verification (need passport + proof of address). TIP: Join Kenyan investor groups on Telegram for guidance!',
                'category': 'global_stocks',
                'is_kenyan_specific': True
            },
            
            # ==================== UNIT TRUSTS ====================
            {
                'question': 'What are unit trusts?',
                'answer': 'Unit trusts are professionally managed investment funds - like ETFs but managed by experts. How it works: You pool money with others, fund manager invests in stocks/bonds/properties, you earn based on performance. In Kenya: CIC, Sanlam, Britam, Old Mutual offer unit trusts. Types: Equity funds (stocks, higher risk), balanced funds (mix), money market funds (safest). Minimum: KSh 5,000-10,000.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            
            # ==================== COMPARISONS ====================
            {
                'question': 'Stocks vs MMFs vs Treasury Bills comparison',
                'answer': 'Investment comparison: STOCKS (NSE): Returns: -50% to +100% (varies!), Risk: HIGH, Liquidity: Sell anytime but prices fluctuate, Minimum: KSh 100 (Hisa). MMFs: Returns: 10-12% annually, Risk: LOW, Liquidity: Withdraw in 1-2 days, Minimum: KSh 1,000. T-BILLS: Returns: 15-17% annually, Risk: VERY LOW (government), Liquidity: Locked 91-364 days, Minimum: KSh 100,000.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'Should I save in a bank or SACCO?',
                'answer': 'Both have benefits! SACCO: Higher interest (8-12%), dividends, cheap loans, BUT less accessible. Bank: Safe, accessible anytime, many branches, BUT low interest (2-5%). Best strategy: Keep emergency fund in BANK (easy access), Keep long-term savings in SACCO (better returns + loans). Or split 50-50.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            
            # ==================== BEGINNER GUIDANCE ====================
            {
                'question': 'I am a beginner in investing, where should I start?',
                'answer': 'Great that you\'re starting! Step 1: Build emergency fund (3 months expenses) in savings account. Step 2: Join a SACCO or chama (safe, good returns). Step 3: Try Money Market Funds like Sanlam or CIC (KSh 1,000 minimum). Step 4: Learn about Treasury Bills and Bonds. Step 5: When comfortable, try NSE stocks. Start small, learn as you grow!',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is an emergency fund?',
                'answer': 'An emergency fund is money saved for unexpected expenses like: job loss, medical bills, car breakdown, urgent house repairs. How much: Save 3-6 months of living expenses. Example: If you spend KSh 30,000/month, save KSh 90,000-180,000. Where: Keep in accessible place like savings account or MMF, NOT locked investments.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I learn about stock investing?',
                'answer': 'Learn stock investing (Kenyan context): FREE resources: 1) NSE website (free courses on NSE Academy), 2) YouTube: "The Money Doctor KE", "WillieTheInvestor", 3) Twitter/X: Follow #KOTFinance, 4) Books: "Intelligent Investor" (Benjamin Graham). PRACTICE: Use NSE demo accounts. COMMUNITIES: Telegram/WhatsApp groups. START: Open CDS + buy KSh 1,000 of Safaricom on Hisa!',
                'category': 'stocks',
                'is_kenyan_specific': True
            },
            {
                'question': 'ETFs ni nini?',  
                'answer': 'ETFs (Exchange Traded Funds) ni baskets za stocks unazinunua kama investment moja. Instead of buying individual stocks, unabuy piece of companies nyingi at once. Benefits: Diversification (spread risk), lower fees, trade like stocks. Kenya has limited local ETFs, lakini you can access global ones (S&P 500, Vanguard) through international brokers like Interactive Brokers. Example: S&P 500 ETF = owning 500 US companies!',
                'category': 'etfs',
                'is_kenyan_specific': False
            }
        ]
        
        return pd.DataFrame(kenyan_qa)
    
    def search(self, query, top_k=3, threshold=0.15):
        """
        Search knowledge base for relevant Q&A
        
        Args:
            query: User query
            top_k: Number of results to return
            threshold: Minimum similarity threshold
        
        Returns:
            List of relevant Q&A pairs with scores
        """
        
        # Vectorize query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.question_vectors)[0]
        
        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = similarities[idx]
            if score >= threshold:
                results.append({
                    'question': self.qa_df.iloc[idx]['question'],
                    'answer': self.qa_df.iloc[idx]['answer'],
                    'category': self.qa_df.iloc[idx].get('category', 'general'),
                    'score': float(score),
                    'is_kenyan': self.qa_df.iloc[idx].get('is_kenyan_specific', False)
                })
        
        return results
    
    def get_by_category(self, category):
        """Get Q&As by category"""
        
        if 'category' not in self.qa_df.columns:
            return []
        
        matches = self.qa_df[self.qa_df['category'] == category]
        
        return [
            {
                'question': row['question'],
                'answer': row['answer'],
                'category': row['category']
            }
            for _, row in matches.iterrows()
        ]

if __name__ == "__main__":
    # Test the knowledge base
    kb = FinancialKnowledgeBase()
    
    print("\n" + "=" * 60)
    print("TESTING KNOWLEDGE BASE")
    print("=" * 60)
    print(f"Total Q&As: {len(kb.qa_df)}")
    
    test_queries = [
        'Which bank is good in Kenya?',
        'What is the difference between MMFs and bonds?',
        'How do I send money via M-Pesa?',
        'What is a chama?',
        'How do I buy stocks?',
        'Can I buy Apple stock from Kenya?'
    ]
    
    for query in test_queries:
        results = kb.search(query, top_k=2)
        
        print(f"\n📝 Query: {query}")
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. Score: {result['score']:.3f}")
                print(f"      Q: {result['question'][:80]}...")
                print(f"      A: {result['answer'][:120]}...")
        else:
            print('   ✗ No good match found')