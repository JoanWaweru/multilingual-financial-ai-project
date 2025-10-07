"""
Generate synthetic code-switching data for Kenyan financial context
Based on authentic linguistic patterns and financial terminology
"""

import pandas as pd
import random
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyntheticCSGenerator:
    """Generate realistic Kenyan English-Swahili code-switching"""
    
    def __init__(self):
        # Financial templates with natural CS insertion points
        self.templates = [
            # Savings
            "{greeting}, I want to {action} some {money} in my {account}.",
            "How can I {action} {money} for {purpose}?",
            "Ninataka ku{action} {money} but I don't know where to start.",
            "The best way to {action} is to {advice} {frequency}.",
            "{money} yangu is not enough, I need to {action} more.",
            
            # M-Pesa
            "How do I send {money} through {service}?",
            "{service} charges are too high for {transaction}.",
            "Nilituma {money} using {service} but hakufika.",
            "Is {service} safe for {transaction}?",
            "{service} ni rahisi sana for {transaction}.",
            
            # Banking
            "Which {bank} has the best {product}?",
            "I opened an {account} at {bank} last {time}.",
            "{bank} wanauza {product} na interest ni nzuri.",
            "How do I apply for a {product} from {bank}?",
            "Nataka ku{action} {product} but the process is complicated.",
            
            # Investment
            "Where can I {action} my {money}?",
            "{investment} ni better than {alternative}.",
            "Nilitry {investment} but sikufanya profit.",
            "How much {money} do I need to start {investment}?",
            "{investment} requires {amount} to start.",
            
            # Loans
            "I need a {loan} of {amount} for {purpose}.",
            "{loan} yangu from {bank} ni {amount}.",
            "How do I qualify for a {loan}?",
            "{loan} interest rates are too high.",
            "Nimeomba {loan} lakini nilikuwa denied.",
            
            # Chamas/SACCOs
            "Our {group} collects {amount} every {time}.",
            "How do {groups} work in Kenya?",
            "{group} yangu ina members {number}.",
            "I want to join a {group} for {purpose}.",
            "{group} ni better than {alternative} for savings.",
            
            # Budget
            "How do I create a {budget}?",
            "My {budget} for {category} is {amount}.",
            "Ninaspend too much on {category}.",
            "{budget} ni muhimu for {purpose}.",
            "I need to reduce my {spending} on {category}.",
            
            # General advice
            "{advice} is the best way to {action} {money}.",
            "Start by {advice} then {action} slowly.",
            "You should {advice} before you {action}.",
            "{action} {money} ni better than {alternative}.",
            "Kama unataka ku{action}, lazima {advice}."
        ]
        
        # Vocabulary by category
        self.vocab = {
            'greeting': ['Hi', 'Hello', 'Habari', 'Sasa', 'Vipi'],
            
            'money': ['pesa', 'money', 'savings', 'akiba', 'fedha', 'cash'],
            
            'action': ['save', 'hifadhi', 'invest', 'weka', 'grow', 'ongeza',
                      'transfer', 'tuma', 'send', 'withdraw', 'toa'],
            
            'account': ['account', 'akaunti', 'savings account', 'akiba account',
                       'bank account', 'mobile account'],
            
            'service': ['M-Pesa', 'Mpesa', 'Airtel Money', 'mobile money',
                       'Equitel', 'T-Kash'],
            
            'transaction': ['sending money', 'kutuma pesa', 'withdrawal', 'kutoa pesa',
                          'deposit', 'kuweka', 'payment', 'malipo'],
            
            'bank': ['Equity Bank', 'KCB', 'Co-op Bank', 'Equity', 'Cooperative Bank',
                    'NCBA', 'Absa', 'Stanbic', 'benki'],
            
            'product': ['loan', 'mkopo', 'savings account', 'fixed deposit',
                       'insurance', 'bima', 'investment', 'uwekezaji'],
            
            'investment': ['shares', 'hisa', 'real estate', 'mali', 'business',
                          'biashara', 'stocks', 'bonds', 'treasury bills'],
            
            'loan': ['loan', 'mkopo', 'personal loan', 'mkopo wa kibinafsi',
                    'logbook loan', 'salary advance'],
            
            'group': ['chama', 'SACCO', 'merry-go-round', 'table banking',
                     'investment group', 'savings group'],
            
            'groups': ['chamas', 'SACCOs', 'investment groups', 'vikundi',
                      'savings groups'],
            
            'budget': ['budget', 'bajeti', 'financial plan', 'mpango wa pesa',
                      'spending plan'],
            
            'category': ['food', 'chakula', 'rent', 'kodi', 'transport', 'usafiri',
                        'entertainment', 'burudani', 'utilities', 'bills'],
            
            'spending': ['spending', 'matumizi', 'expenses', 'gharama'],
            
            'advice': ['save regularly', 'weka kila mwezi', 'start small',
                      'anza kidogo', 'track your spending', 'fuatilia matumizi',
                      'set goals', 'weka malengo', 'automate savings'],
            
            'purpose': ['emergency fund', 'pesa ya dharura', 'buying land',
                       'nunua shamba', 'school fees', 'ada za shule',
                       'starting business', 'kuanza biashara'],
            
            'alternative': ['keeping cash', 'kuweka cash', 'borrowing',
                           'kukopa', 'spending', 'kutumia', 'saving only'],
            
            'time': ['month', 'mwezi', 'week', 'wiki', 'year', 'mwaka'],
            
            'frequency': ['monthly', 'kila mwezi', 'weekly', 'kila wiki',
                         'daily', 'kila siku'],
            
            'amount': ['Ksh 1000', 'Ksh 5000', 'Ksh 10,000', 'Ksh 50,000',
                      'elfu tano', 'elfu kumi', 'laki moja'],
            
            'number': ['10', 'kumi', '20', 'ishirini', '30', 'thelathini',
                      '50', 'hamsini']
        }
        
        # Natural Swahili sentences (for pure Swahili samples)
        self.swahili_financial = [
            "Ninahitaji kuweka akiba kwa sababu ya dharura.",
            "Chama yetu inakusanya pesa kila mwezi elfu tano.",
            "Mkopo wa benki una riba ya asilimia ishirini.",
            "M-Pesa ni njia rahisi ya kutuma pesa.",
            "Uwekezaji wa hisa ni hatari lakini una faida kubwa.",
            "SACCO yangu inatoa mikopo na riba nafuu.",
            "Bajeti ni muhimu kwa maisha ya kifedha.",
            "Nataka kununua shamba lakini sina pesa ya kutosha.",
            "Equity Bank ina akaunti nzuri za akiba.",
            "Nilipata mkopo wa biashara kutoka KCB."
        ]
        
        # Pure English sentences
        self.english_financial = [
            "I need to save money for emergencies.",
            "Our savings group collects money every month.",
            "Bank loans have high interest rates.",
            "Mobile money makes transfers easy.",
            "Stock investment is risky but profitable.",
            "My SACCO offers affordable loans.",
            "Budgeting is essential for financial health.",
            "I want to buy land but don't have enough money.",
            "Equity Bank has good savings accounts.",
            "I got a business loan from KCB."
        ]
    
    def generate_cs_sentence(self):
        """Generate one code-switched sentence"""
        
        template = random.choice(self.templates)
        
        # Fill template with vocabulary
        sentence = template
        for placeholder, options in self.vocab.items():
            if '{' + placeholder + '}' in sentence:
                sentence = sentence.replace('{' + placeholder + '}', random.choice(options))
        
        return sentence
    
    def generate_dataset(self, n_samples=5000):
        """Generate complete dataset"""
        
        logger.info(f"Generating {n_samples} synthetic samples...")
        
        data = []
        
        # Mix of code-switched, Swahili, and English
        cs_ratio = 0.60  # 60% code-switched
        sw_ratio = 0.20  # 20% Swahili
        en_ratio = 0.20  # 20% English
        
        n_cs = int(n_samples * cs_ratio)
        n_sw = int(n_samples * sw_ratio)
        n_en = n_samples - n_cs - n_sw
        
        # Generate code-switched samples
        for i in range(n_cs):
            sentence = self.generate_cs_sentence()
            data.append({
                'text': sentence,
                'language': 'code_switched',
                'has_code_switching': True,
                'is_financial': True,
                'source': 'synthetic',
                'sample_id': f'cs_{i}'
            })
        
        # Add Swahili samples
        for i in range(n_sw):
            sentence = random.choice(self.swahili_financial)
            # Add variation
            sentence = sentence + " " + random.choice(['Asante.', 'Nakushukuru.', ''])
            data.append({
                'text': sentence,
                'language': 'swahili',
                'has_code_switching': False,
                'is_financial': True,
                'source': 'synthetic',
                'sample_id': f'sw_{i}'
            })
        
        # Add English samples
        for i in range(n_en):
            sentence = random.choice(self.english_financial)
            # Add variation
            sentence = sentence + " " + random.choice(['Thank you.', 'Thanks.', ''])
            data.append({
                'text': sentence,
                'language': 'english',
                'has_code_switching': False,
                'is_financial': True,
                'source': 'synthetic',
                'sample_id': f'en_{i}'
            })
        
        df = pd.DataFrame(data)
        
        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        logger.info(f"✓ Generated {len(df)} samples")
        logger.info(f"  - Code-switched: {n_cs}")
        logger.info(f"  - Swahili: {n_sw}")
        logger.info(f"  - English: {n_en}")
        
        return df
    
    def save_dataset(self, df, filename="synthetic_cs_financial.csv"):
        """Save generated dataset"""
        
        output_path = Path("data/processed")
        output_path.mkdir(exist_ok=True, parents=True)
        
        output_file = output_path / filename
        df.to_csv(output_file, index=False)
        
        logger.info(f"✓ Saved to: {output_file}")
        
        # Show samples
        logger.info("\nSample entries:")
        for i in range(5):
            logger.info(f"{i+1}. {df.iloc[i]['text']}")
        
        return output_file

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SYNTHETIC CODE-SWITCHING DATA GENERATION")
    logger.info("=" * 60)
    
    generator = SyntheticCSGenerator()
    df = generator.generate_dataset(n_samples=5000)
    generator.save_dataset(df)
    
    logger.info("\n✓ GENERATION COMPLETE!")