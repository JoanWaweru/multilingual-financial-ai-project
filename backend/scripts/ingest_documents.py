"""
Script to ingest sample Kenyan financial documents
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.vector_store import vector_store
from app.utils.document_processor import DocumentProcessor

async def ingest_sample_documents():
    """Ingest sample documents from data directory"""
    data_dir = Path(__file__).parent.parent / "data" / "sample_documents"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    processor = DocumentProcessor()
    
    # Sample Kenyan financial content (will be created as text files)
    sample_docs = [
        {
            "filename": "cbk_guidelines.txt",
            "content": """CENTRAL BANK OF KENYA (CBK) GUIDELINES FOR PERSONAL FINANCE

The Central Bank of Kenya is the primary regulator of the banking sector in Kenya. 
Key regulations affecting personal finance include:

1. BANKING SERVICES
- All commercial banks in Kenya are licensed and regulated by CBK
- Deposit Protection Fund (DPF) insures deposits up to KES 500,000 per depositor per bank
- Interest rates on loans are regulated, with banks required to disclose Annual Percentage Rate (APR)
- Mobile banking services (M-Pesa, Airtel Money) are regulated by CBK

2. SAVINGS AND INVESTMENTS
- Commercial banks offer savings accounts with interest rates typically ranging from 3-7% per annum
- Fixed deposit accounts offer higher rates for longer terms (1-5 years)
- Money Market Funds (MMFs) are regulated by the Capital Markets Authority (CMA)
- Treasury Bills and Bonds are issued by the Government of Kenya through CBK

3. LOANS AND CREDIT
- CBK maintains a Credit Reference Bureau (CRB) system
- All loans must be registered with CRB
- Maximum interest rates are capped by law
- Borrowers should check their credit scores before applying for loans

4. CONSUMER PROTECTION
- CBK requires banks to provide clear information about fees and charges
- Customers have the right to file complaints with CBK
- Banks must provide statements and account information upon request"""
        },
        {
            "filename": "sacco_guide.txt",
            "content": """SACCO (SAVINGS AND CREDIT COOPERATIVE ORGANIZATIONS) GUIDE FOR KENYANS

SACCOs are member-owned financial cooperatives regulated by the Sacco Societies Regulatory Authority (SASRA).

1. TYPES OF SACCOs
- Deposit-taking SACCOs (DT-SACCOs): Licensed by SASRA, can accept deposits from members
- Non-withdrawable deposit SACCOs: Members can only withdraw upon exit
- Front Office Service Activity (FOSA): Banking services provided by SACCOs

2. MEMBERSHIP BENEFITS
- Higher interest rates on savings compared to commercial banks (typically 6-12% per annum)
- Lower interest rates on loans (typically 12-18% per annum)
- Dividends paid to members based on SACCO performance
- Member ownership and democratic governance

3. LOAN PRODUCTS
- Development loans: For business or investment purposes
- Emergency loans: Quick access to funds for urgent needs
- School fees loans: Specifically for education expenses
- Asset financing: For purchasing assets like vehicles or property

4. RISKS AND CONSIDERATIONS
- SACCOs are not covered by Deposit Protection Fund (only banks are)
- Members should verify SASRA licensing before joining
- Check SACCO financial health and track record
- Understand withdrawal terms and conditions

5. REGULATORY COMPLIANCE
- All DT-SACCOs must be licensed by SASRA
- SACCOs must submit regular financial reports
- Members have rights to information and participation in governance"""
        },
        {
            "filename": "nse_investing.txt",
            "content": """INVESTING IN NAIROBI SECURITIES EXCHANGE (NSE) FOR KENYANS

The Nairobi Securities Exchange is the principal stock exchange in Kenya, regulated by the Capital Markets Authority (CMA).

1. GETTING STARTED
- Open a CDS (Central Depository System) account through a licensed stockbroker
- Minimum investment amounts vary by broker (typically KES 5,000-10,000)
- Choose between full-service or online brokers
- Complete KYC (Know Your Customer) requirements

2. INVESTMENT OPTIONS
- Equities: Shares in listed companies (e.g., Safaricom, Equity Bank, KCB)
- Bonds: Government and corporate bonds traded on NSE
- REITs: Real Estate Investment Trusts for property exposure
- ETFs: Exchange Traded Funds for diversified exposure

3. COSTS AND FEES
- Brokerage fees: Typically 1.5-2.5% of transaction value
- CDS account maintenance: Annual fees (KES 500-1,000)
- Stamp duty: 0.1% on share purchases
- Capital gains tax: 5% on profits from share sales

4. RISK MANAGEMENT
- Diversify across sectors and companies
- Understand company fundamentals before investing
- Consider your risk tolerance and investment horizon
- Monitor market conditions and company performance

5. REGULATORY PROTECTION
- CMA regulates all market participants
- Investor Compensation Fund protects investors up to KES 50,000
- All brokers must be licensed by CMA
- Market manipulation and insider trading are illegal"""
        },
        {
            "filename": "treasury_bills_bonds.txt",
            "content": """TREASURY BILLS AND BONDS IN KENYA

Government securities issued by the Central Bank of Kenya on behalf of the Government of Kenya.

1. TREASURY BILLS (T-BILLS)
- Short-term securities with maturities of 91, 182, or 364 days
- Sold at a discount and redeemed at face value
- Interest is the difference between purchase price and face value
- Minimum investment: KES 50,000
- Auctioned weekly by CBK
- No secondary market trading

2. TREASURY BONDS
- Long-term securities with maturities of 2, 5, 10, 15, 20, or 25 years
- Pay semi-annual coupon payments
- Can be traded on the secondary market (NSE)
- Minimum investment: KES 100,000
- Interest rates determined by auction

3. HOW TO INVEST
- Open a CDS account (same as for stocks)
- Participate in primary auctions through your broker
- Or buy from secondary market on NSE
- Interest income is tax-exempt for individuals

4. RISKS
- Low risk: Backed by Government of Kenya
- Interest rate risk: Bond prices fall when rates rise
- Inflation risk: Returns may not keep pace with inflation
- Liquidity: T-Bills are held to maturity; Bonds can be sold on secondary market

5. RETURNS
- T-Bill rates: Typically 8-12% per annum
- Bond yields: Vary by maturity, typically 10-15% per annum
- Tax-free for individual investors
- Considered one of the safest investments in Kenya"""
        },
        {
            "filename": "pension_planning.txt",
            "content": """PENSION PLANNING FOR KENYANS

Planning for retirement is crucial for financial security in Kenya.

1. TYPES OF PENSION SCHEMES
- National Social Security Fund (NSSF): Mandatory for all employees
- Occupational Pension Schemes: Employer-sponsored plans
- Individual Retirement Benefits Schemes (RBS): Personal pension plans
- Public Service Superannuation Scheme (PSSS): For public servants

2. NSSF CONTRIBUTIONS
- Employees contribute 6% of pensionable earnings
- Employers match with 6% contribution
- Maximum contribution: KES 2,160 per month (as of 2024)
- Benefits payable at retirement age (60 years) or upon invalidity

3. RETIREMENT BENEFITS AUTHORITY (RBA)
- Regulates all pension schemes in Kenya
- Ensures compliance with Retirement Benefits Act
- Protects member interests

4. VOLUNTARY SAVINGS
- Consider additional retirement savings beyond NSSF
- Individual RBS plans offer tax benefits
- Contributions up to KES 20,000/month are tax-deductible
- Investment options include equities, bonds, and property

5. RETIREMENT PLANNING TIPS
- Start saving early to benefit from compound interest
- Diversify retirement savings across different vehicles
- Understand your NSSF benefits and contributions
- Consider inflation when planning retirement needs
- Review and adjust your plan regularly

6. WITHDRAWAL RULES
- NSSF: Withdrawable at age 60 or upon invalidity
- Occupational schemes: Rules vary by scheme
- Individual RBS: Can access 1/3 at retirement, rest as annuity
- Early withdrawal penalties may apply"""
        },
        {
            "filename": "budgeting_tips.txt",
            "content": """PERSONAL BUDGETING TIPS FOR KENYANS

Effective budgeting is the foundation of good financial management.

1. THE 50/30/20 RULE
- 50% for needs: Housing, food, utilities, transport, insurance
- 30% for wants: Entertainment, dining out, hobbies
- 20% for savings and investments: Emergency fund, retirement, investments

2. TRACKING EXPENSES
- Use mobile apps (M-Pesa statements, bank apps)
- Keep receipts and record daily expenses
- Categorize spending to identify patterns
- Review monthly to adjust budget

3. EMERGENCY FUND
- Aim for 3-6 months of expenses
- Keep in easily accessible account (savings or MMF)
- Start with small amounts and build gradually
- Only use for true emergencies

4. DEBT MANAGEMENT
- Prioritize high-interest debt (credit cards, mobile loans)
- Consider debt consolidation if you have multiple loans
- Avoid taking new debt to pay old debt
- Negotiate payment plans if struggling

5. SAVING STRATEGIES
- Pay yourself first: Automate savings
- Use SACCOs for higher interest rates
- Consider Treasury Bills for safe, tax-free returns
- Invest in NSE for long-term growth potential

6. KENYA-SPECIFIC CONSIDERATIONS
- Account for school fees (if applicable)
- Plan for medical expenses (NHIF, private insurance)
- Consider extended family obligations
- Factor in inflation (typically 5-8% annually)
- Plan for irregular income if self-employed"""
        }
    ]
    
    print("📚 Ingesting sample Kenyan financial documents...")
    
    for doc in sample_docs:
        file_path = data_dir / doc["filename"]
        file_path.write_text(doc["content"], encoding='utf-8')
        
        # Process document
        with open(file_path, 'rb') as f:
            content = f.read()
        
        texts, metadata = await processor.process_file(
            content,
            filename=doc["filename"],
            content_type="text/plain"
        )
        
        # Add to vector store
        await vector_store.add_documents(texts, metadata)
        print(f"✅ Ingested {doc['filename']}: {len(texts)} chunks")
    
    stats = vector_store.get_stats()
    print(f"\n✅ Document ingestion complete!")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Index size: {stats['index_size']}")

if __name__ == "__main__":
    asyncio.run(ingest_sample_documents())

