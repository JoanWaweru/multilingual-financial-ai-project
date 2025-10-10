"""
Financial Knowledge Base
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
    
    def __init__(self, qa_file="data/processed/financial_qa_dataset.csv"):
        """Initialize knowledge base"""
        
        qa_path = Path(qa_file)
        
        if not qa_path.exists():
            logger.warning(f"Q&A file not found: {qa_path}")
            self.qa_df = self._create_default_kb()
        else:
            self.qa_df = pd.read_csv(qa_path)
            logger.info(f"Loaded {len(self.qa_df)} Q&A pairs")
        
        # Create TF-IDF vectorizer for question matching
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            stop_words='english'
        )
        
        # Fit on questions
        questions = self.qa_df['question'].fillna('').values
        self.question_vectors = self.vectorizer.fit_transform(questions)
        
        logger.info("✓ Knowledge base initialized")
    
    def _create_default_kb(self):
        """Create default knowledge base with essential Q&As"""
        
        default_qa = [
            
            #Savings
            {
                'question': 'How do I save money?',
                'answer': 'You can save money through: 1) Opening a savings account at a bank like Equity or KCB, 2) Joining a chama (savings group), 3) Using M-Shwari or KCB M-Pesa for mobile savings, 4) Joining a SACCO for better interest rates.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is a chama?',
                'answer': 'A chama is a Kenyan savings group where members contribute money regularly (weekly or monthly) and take turns to receive the pooled funds. It\'s a traditional form of community-based saving popular in Kenya.',
                'category': 'chama',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is a SACCO?',
                'answer': 'SACCO stands for Savings and Credit Cooperative. It\'s a member-owned financial cooperative that provides savings and loan services to its members at favorable rates, usually lower than banks.',
                'category': 'sacco',
                'is_kenyan_specific': True
            },
            
            # M-Pesa
            {
                'question': 'How do I send money via M-Pesa?',
                'answer': 'To send money via M-Pesa: 1) Go to M-Pesa menu, 2) Select Send Money, 3) Enter recipient phone number, 4) Enter amount, 5) Enter your M-Pesa PIN to confirm.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is M-Pesa?',
                'answer': 'M-Pesa is a mobile money service by Safaricom that allows you to send, receive, and store money on your phone. You can also pay bills, buy goods, and access loans through M-Pesa.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'What are M-Pesa charges?',
                'answer': 'M-Pesa charges vary by transaction amount. Sending KSh 100-500 costs about KSh 11, KSh 501-1000 costs KSh 22, and higher amounts have proportional charges. Withdrawing also has charges.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            
            # Banking
            {
                'question': 'How do I open a bank account?',
                'answer': 'To open a bank account in Kenya: 1) Visit a bank branch (Equity, KCB, Co-op, etc.) with your ID, 2) Fill the account opening form, 3) Deposit minimum amount (usually KSh 100-500), 4) Receive your account number and ATM card.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            {
                'question': 'What documents do I need to open a bank account?',
                'answer': 'You need: 1) National ID or Passport, 2) KRA PIN certificate (for some accounts), 3) Proof of residence (utility bill), 4) Passport photo. Requirements vary by bank.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            
            # Loans
            {
                'question': 'How do I get a loan?',
                'answer': 'In Kenya, you can get loans from: 1) Banks (requires good credit history), 2) SACCOs (for members), 3) Mobile lending apps (Tala, Branch, M-Shwari), 4) Your chama. Requirements and interest rates vary.',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is mobile lending?',
                'answer': 'Mobile lending apps like Tala, Branch, M-Shwari, and KCB M-Pesa offer instant loans on your phone. They assess your credit using phone data and offer loans within minutes, but interest rates are higher than banks.',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            
            # Investment
            {
                'question': 'How can I invest money?',
                'answer': 'Investment options in Kenya include: 1) Shares at Nairobi Securities Exchange, 2) Treasury bills and bonds, 3) Real estate, 4) Unit trusts, 5) SACCOs for safer returns, 6) Starting a business.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            
            # Budgeting
            {
                'question': 'How do I create a budget?',
                'answer': 'To create a budget: 1) List all income sources, 2) List all expenses (rent, food, transport, etc.), 3) Subtract expenses from income, 4) Allocate money to savings and emergencies, 5) Track spending daily.',
                'category': 'budgeting',
                'is_kenyan_specific': False
            },
            
            # More M-Pesa
            {
                'question': 'How do I check my M-Pesa balance?',
                'answer': 'To check your M-Pesa balance: 1) Go to M-Pesa menu, 2) Select "My Account", 3) Select "Show Balance", 4) Enter your PIN. Your balance will be displayed on screen.',
                'category': 'mpesa',
                'is_kenyan_specific': True
            },
            {
                'question': 'Can I borrow from M-Pesa?',
                'answer': 'Yes! M-Shwari and KCB M-Pesa offer instant loans. For M-Shwari: Go to M-Pesa menu > Loans and Savings > M-Shwari > Request Loan. You must have saved on M-Shwari first to qualify.',
                'category': 'loans',
                'is_kenyan_specific': True
            },
            
            # Chama details
            {
                'question': 'How do I start a chama?',
                'answer': 'To start a chama: 1) Gather 5-20 trusted friends/family, 2) Agree on contribution amount and frequency, 3) Choose leaders (chairperson, treasurer, secretary), 4) Write simple rules, 5) Open a group bank account (optional), 6) Start contributing!',
                'category': 'chama',
                'is_kenyan_specific': True
            },

            # Bank Selection
            {
                'question': 'Which bank is good to save money in Kenya?',
                'answer': 'Good banks for saving in Kenya include: 1) Equity Bank - low minimum balance, good mobile banking, 2) KCB - many branches, good interest rates, 3) Co-operative Bank - friendly to chamas and groups, 4) NCBA - good digital services. Choose based on: branch accessibility, mobile app quality, minimum balance requirements, and interest rates.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            {
                'question': 'Which is the best bank in Kenya?',
                'answer': 'The "best" bank depends on your needs: Equity Bank is great for accessibility and low fees, KCB offers the most branches nationwide, Co-operative Bank is excellent for SACCOs and groups, NCBA has strong digital banking. Consider: location of branches, mobile app features, account fees, and customer service.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
        
            # Investment Products
            {
                'question': 'What is the difference between MMFs and government bonds?',
                'answer': 'Money Market Funds (MMFs) and Government Bonds are both investments, but different: MMFs are short-term (less than 1 year), very liquid (can withdraw anytime), lower returns (8-12% annually), low risk. Government Bonds are long-term (2-30 years), less liquid (locked for years), higher returns (12-15% annually), very safe. MMFs are better for beginners and emergency funds. Bonds are better for long-term savings you won\'t need soon.',
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
            {
                'question': 'How do I invest in treasury bills?',
                'answer': 'To invest in Treasury Bills (T-Bills) in Kenya: 1) Open a CDS account at CBK or through your bank, 2) Have KSh 100,000 minimum (or KSh 50,000 for some banks), 3) Buy through your bank or CBK mobile app, 4) Choose duration: 91 days, 182 days, or 364 days, 5) Earn interest at maturity. Current rates: 15-17% annually. Very safe, guaranteed by government.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'Should I invest in stocks or bonds?',
                'answer': 'It depends on your goals and risk tolerance: Stocks (NSE) - Higher returns potential (can gain 20%+ or lose money), risky, good for long-term (5+ years). Bonds - Stable returns (12-15%), very safe, locked for years. For beginners: Start with MMFs or bonds. Once comfortable, add some stocks. Rule: Don\'t invest money you\'ll need within 2 years.',
                'category': 'investment',
                'is_kenyan_specific': True
            },
        
            # Mobile Banking & Digital
            {
                'question': 'Which mobile banking app is best?',
                'answer': 'Top mobile banking apps in Kenya: 1) Equity eazzy - user-friendly, many features, 2) KCB Mobile - fast, reliable, 3) Mco-opCash (Co-op Bank) - good for payments, 4) NCBA Loop - modern interface. All allow: balance checking, money transfers, bill payments, loan applications. Choose based on which bank you use.',
                'category': 'banking',
                'is_kenyan_specific': True
            },
            {
                'question': 'How do I protect my mobile money from fraud?',
                'answer': 'Protect your mobile money: 1) Never share your PIN with anyone, 2) Use strong PIN (not 1234 or birthdate), 3) Don\'t click suspicious links via SMS, 4) Always verify recipient number before sending, 5) Enable biometric login if available, 6) Check your balance regularly, 7) Report suspicious activity immediately to your bank/Safaricom.',
                'category': 'security',
                'is_kenyan_specific': True
            },
        
            # Financial Planning
            {
                'question': 'How much should I save each month?',
                'answer': 'A good rule: Save at least 20% of your income. Example: If you earn KSh 50,000, save KSh 10,000. Split savings: 50% emergency fund (3-6 months expenses), 30% long-term goals (house, business), 20% investments (MMFs, SACCOs). Start small: Even KSh 1,000 per month builds good habits. Increase as income grows.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
            {
                'question': 'What is an emergency fund?',
                'answer': 'An emergency fund is money saved for unexpected expenses like: job loss, medical bills, car breakdown, urgent house repairs. How much: Save 3-6 months of living expenses. Example: If you spend KSh 30,000/month, save KSh 90,000-180,000. Where: Keep in accessible place like savings account or MMF, NOT locked investments. Build gradually: KSh 5,000-10,000 per month.',
                'category': 'savings',
                'is_kenyan_specific': True
            },
        
            # Beginner Advice
            {
                'question': 'I am a beginner in investing, where should I start?',
                'answer': 'Great that you\'re starting! Step 1: Build emergency fund (3 months expenses) in savings account. Step 2: Join a SACCO or chama (safe, good returns). Step 3: Try Money Market Funds like Sanlam or CIC (KSh 1,000 minimum). Step 4: Learn about Treasury Bills and Bonds. Step 5: When comfortable, try NSE stocks. Start small, learn as you grow. Don\'t rush into complex investments!',
                'category': 'investment',
                'is_kenyan_specific': True
            },
            {
                'question': 'I am new to investing, what should I know?',
                'answer': 'Key things for beginners: 1) Never invest money you\'ll need within 2 years, 2) Don\'t put all money in one place (diversify), 3) Start with low-risk: MMFs, SACCOs, government bonds, 4) Avoid "get rich quick" schemes, 5) Learn before investing, 6) Higher returns = higher risk, 7) Ask questions - it\'s okay not to know! Start with KSh 1,000-5,000 to learn.',
                'category': 'investment',
                'is_kenyan_specific': True
            }
        ]
            
        
        logger.info(f"Created default KB with {len(default_qa)} entries")
        return pd.DataFrame(default_qa)
    
    def search(self, query, top_k=3, threshold=0.15):  # RAISED threshold from 0.1 to 0.15
        """
    Search knowledge base for relevant Q&A
    
    Args:
        query: User query
        top_k: Number of results to return
        threshold: Minimum similarity threshold (0.15 = stricter matching)
    
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
        if score >= threshold:  # Only return if score is decent
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
    
    test_queries = [
        "How do I save money?",
        "Nataka kutuma pesa kwa M-Pesa",
        "What is a chama?",
        "How to get a loan?"
    ]
    
    for query in test_queries:
        results = kb.search(query, top_k=2)
        
        print(f"\nQuery: {query}")
        print(f"Found {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. Score: {result['score']:.3f}")
            print(f"     Q: {result['question']}")
            print(f"     A: {result['answer'][:100]}...")