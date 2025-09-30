from typing import Dict, List, Optional
import random

class CulturalKnowledgeBase:
    """Cultural context and traditional financial knowledge for East Africa"""
    
    def __init__(self):
        # Swahili proverbs about money and finance
        self.proverbs = {
            "savings": [
                "Akiba haiozi - Savings never rot",
                "Haba na haba hujaza kibaba - Little by little fills the measure",
                "Maji yakimwagika hayazoleki - Spilled water cannot be collected (save before spending)",
                "Asiye na akiba hufa maskini - One without savings dies poor",
                "Akili ni mali - Wisdom is wealth"
            ],
            "investment": [
                "Usifte mayai yako kwenye kikapu kimoja - Don't put all your eggs in one basket",
                "Mti ukigwa hukuwa ule ule - A fallen tree remains itself (choose investments wisely)",
                "Usipoziba ufa utajenga ukuta - If you don't fix the crack, you'll rebuild the wall (prevent losses)",
                "Haraka haraka haina baraka - Hurry has no blessing (patience in investment)"
            ],
            "planning": [
                "Asiyepanga ni kujiandaa kushindwa - Not planning is preparing to fail",
                "Mwenye kujipanga hachoki - One who plans doesn't get tired",
                "Baada ya dhiki faraja - After hardship comes relief (save for tough times)",
                "Subira huvuta heri - Patience brings good fortune"
            ],
            "business": [
                "Mchagua jembe si mkulima - A choosy farmer is not a real farmer (take action)",
                "Ukiona vyaelea vimeundwa - If you see something floating, it was made (success requires work)",
                "Kidole kimoja hakivunji chawa - One finger cannot kill a louse (collaboration is key)"
            ],
            "wisdom": [
                "Penye nia pana njia - Where there's a will, there's a way",
                "Mgeni siku ya kwanza, siku ya pili mpe jembe - A guest on day one, give them a hoe on day two (don't depend on handouts)",
                "Asiyekubali kushindwa si mshindani - One who doesn't accept defeat is not a true competitor"
            ]
        }
        
        # Traditional financial concepts
        self.traditional_concepts = {
            "chama": {
                "definition": "A traditional rotating savings and credit association where members contribute regularly",
                "how_it_works": "Members meet regularly (weekly/monthly), contribute equal amounts, and take turns receiving the lump sum",
                "benefits": "Builds discipline, provides access to larger sums, creates accountability, and fosters community",
                "modern_equivalent": "Similar to a mutual fund or investment club, but with stronger social bonds"
            },
            "harambee": {
                "definition": "Community fundraising tradition for collective goals like building schools, helping families",
                "how_it_works": "Community members contribute money or labor towards a common cause",
                "benefits": "Solves problems collectively, builds community solidarity, helps those in need",
                "modern_equivalent": "Like crowdfunding platforms (GoFundMe, Kickstarter) but based on community trust"
            },
            "merry-go-round": {
                "definition": "Informal savings arrangement where group members take turns receiving contributions",
                "how_it_works": "Similar to chama but more flexible and based on close relationships",
                "benefits": "Quick access to funds, no interest charges, based on trust",
                "modern_equivalent": "Peer-to-peer lending circles"
            },
            "table banking": {
                "definition": "Community-based microfinance where members save together and borrow from the pool",
                "how_it_works": "Members save regularly, borrow at low interest, and share profits",
                "benefits": "Access to credit without banks, lower interest rates, community controlled",
                "modern_equivalent": "Credit union or SACCO model"
            },
            "stokvels": {
                "definition": "Savings clubs where members contribute to a common pool (popular in South Africa but known in East Africa)",
                "how_it_works": "Regular contributions, payouts for specific purposes (Christmas, school fees)",
                "benefits": "Disciplined saving, social support, financial buffer",
                "modern_equivalent": "Automated savings apps with social features"
            }
        }
        
        # Financial tips by experience level
        self.financial_tips = {
            "beginner": [
                "Start with small amounts - even 100 KES per week adds up to 5,200 KES yearly",
                "Anza na kidogo - hata shilingi mia moja kila wiki inasaidia",
                "Track every expense for one month to understand your spending patterns",
                "Open a savings account separate from your spending account",
                "Weka pesa mbali - akaunti ya akiba separate from matumizi",
                "Pay yourself first - save before you spend on wants",
                "Use the envelope method - cash for different budget categories"
            ],
            "intermediate": [
                "Build 3-6 months emergency fund before aggressive investing",
                "Jenga emergency fund ya miezi 3-6 kabla ya aggressive investment",
                "Diversify investments: 60% stocks/equity, 30% bonds, 10% cash",
                "Join a chama or investment club to learn from others",
                "Jiunga na chama ya uwekezaji - ujifunze from experienced members",
                "Consider SACCOs for affordable credit and forced savings",
                "Review and rebalance your portfolio quarterly",
                "Invest in yourself - skills and education have highest ROI"
            ],
            "advanced": [
                "Explore EAC regional investment opportunities for diversification",
                "Use tax-efficient vehicles like pension schemes (15% tax relief)",
                "Consider real estate investment trusts (REITs) for property exposure without large capital",
                "Wekeza kwa REITs - mali bila kulazimika kununa nyumba",
                "Balance growth assets (stocks) with stable income (bonds, deposits)",
                "Set up automatic investment plans (SIPs) for consistent wealth building",
                "Review tax optimization strategies - pension, life insurance",
                "Consider impact investing - financial returns with social benefit"
            ]
        }
        
        # Country-specific financial info
        self.country_info = {
            "Kenya": {
                "currency": "KES (Kenya Shilling)",
                "mobile_money": "M-Pesa (most popular), Airtel Money",
                "stock_exchange": "NSE (Nairobi Securities Exchange)",
                "popular_banks": "Equity Bank, KCB, Cooperative Bank",
                "savings_options": "SACCOs, Chamas, Money Market Funds",
                "investment_tip": "NSE has good companies - Safaricom, Equity Bank, EABL"
            },
            "Uganda": {
                "currency": "UGX (Uganda Shilling)",
                "mobile_money": "MTN Mobile Money, Airtel Money",
                "stock_exchange": "USE (Uganda Securities Exchange)",
                "popular_banks": "Centenary Bank, Stanbic, dfcu",
                "savings_options": "SACCOs, VSLAs (Village Savings and Loans)",
                "investment_tip": "Consider government bonds - they're stable and accessible"
            },
            "Tanzania": {
                "currency": "TZS (Tanzania Shilling)",
                "mobile_money": "M-Pesa, Tigo Pesa, Airtel Money",
                "stock_exchange": "DSE (Dar es Salaam Stock Exchange)",
                "popular_banks": "CRDB, NMB Bank, Stanbic",
                "savings_options": "VICOBA (Village Community Banks), SACCOs",
                "investment_tip": "DSE offers good opportunities in banking and telecom sectors"
            },
            "Rwanda": {
                "currency": "RWF (Rwanda Franc)",
                "mobile_money": "MTN MoMo, Airtel Money",
                "stock_exchange": "RSE (Rwanda Stock Exchange)",
                "popular_banks": "Bank of Kigali, I&M Bank, Equity Bank",
                "savings_options": "Umurenge SACCOs, cooperatives",
                "investment_tip": "Rwanda has attractive investment climate - consider REITs"
            }
        }
    
    def get_proverb(self, topic: str = None) -> str:
        """Get a random proverb, optionally filtered by topic"""
        if topic and topic in self.proverbs:
            return random.choice(self.proverbs[topic])
        
        # Random from all proverbs
        all_proverbs = [p for proverbs in self.proverbs.values() for p in proverbs]
        return random.choice(all_proverbs)
    
    def explain_traditional_concept(self, concept: str) -> str:
        """Get detailed explanation of traditional financial concept"""
        concept_lower = concept.lower().strip()
        
        if concept_lower in self.traditional_concepts:
            info = self.traditional_concepts[concept_lower]
            explanation = f"**{concept.capitalize()}**: {info['definition']}\n\n"
            explanation += f"**How it works**: {info['how_it_works']}\n\n"
            explanation += f"**Benefits**: {info['benefits']}\n\n"
            explanation += f"**Modern equivalent**: {info['modern_equivalent']}"
            return explanation
        
        return f"Samahani, I don't have detailed information about '{concept}'. Could you ask about chama, harambee, or table banking?"
    
    def get_financial_tip(self, level: str = "beginner") -> str:
        """Get financial tip appropriate for experience level"""
        level_lower = level.lower()
        
        if level_lower in self.financial_tips:
            return random.choice(self.financial_tips[level_lower])
        
        return random.choice(self.financial_tips["beginner"])
    
    def get_country_info(self, country: str) -> Dict:
        """Get financial information for specific country"""
        return self.country_info.get(country, {})
    
    def enhance_response_with_culture(self, response: str, topic: str = None, 
                                     add_proverb: bool = True) -> str:
        """Add cultural elements to response"""
        enhanced = response
        
        # Add proverb if requested and topic matches
        if add_proverb and topic and topic in self.proverbs:
            proverb = self.get_proverb(topic)
            enhanced = f"{enhanced}\n\n💡 Kama wahenga walivyosema: *'{proverb}'*"
        
        return enhanced
    
    def get_contextual_greeting(self) -> str:
        """Get culturally appropriate greeting"""
        greetings = [
            "Habari! How can I help you with pesa matters today?",
            "Mambo! Ready to talk about savings na investment?",
            "Karibu! Let's discuss your financial goals.",
            "Sasa! What financial questions do you have?",
            "Hello! Niaje? How can I assist with your finances?"
        ]
        return random.choice(greetings)
    
    def get_encouragement(self) -> str:
        """Get encouraging message about financial journey"""
        encouragements = [
            "You're taking great steps towards financial freedom! Endelea!",
            "Small steps lead to big changes. Keep going!",
            "Financial discipline ni journey, not a sprint. Pole pole!",
            "Every shilling saved today is an investment in tomorrow. Hongera!",
            "You're building a strong financial foundation. Songa mbele!"
        ]
        return random.choice(encouragements)

if __name__ == "__main__":
    # Test the knowledge base
    kb = CulturalKnowledgeBase()
    
    print("\n" + "="*70)
    print("TESTING CULTURAL KNOWLEDGE BASE")
    print("="*70)
    
    print("\n--- Random Proverb ---")
    print(kb.get_proverb())
    
    print("\n--- Savings Proverb ---")
    print(kb.get_proverb("savings"))
    
    print("\n--- Explain Chama ---")
    print(kb.explain_traditional_concept("chama"))
    
    print("\n--- Financial Tip (Beginner) ---")
    print(kb.get_financial_tip("beginner"))
    
    print("\n--- Financial Tip (Advanced) ---")
    print(kb.get_financial_tip("advanced"))
    
    print("\n--- Kenya Info ---")
    kenya_info = kb.get_country_info("Kenya")
    for key, value in kenya_info.items():
        print(f"{key}: {value}")