"""
Kenyan proverbs and code-switching phrases
"""

import random

class KenyanPhrases:
    """Collection of Kenyan proverbs and phrases"""
    
    def __init__(self):
        # Kenyan/Swahili proverbs about money
        self.proverbs = [
            {
                'swahili': 'Akiba haiozi',
                'english': 'Savings never rot',
                'meaning': 'Money saved is never wasted'
            },
            {
                'swahili': 'Haraka haraka haina baraka',
                'english': 'Hurry hurry has no blessings',
                'meaning': 'Take your time with financial decisions'
            },
            {
                'swahili': 'Asiyefunzwa na mamaye hufunzwa na ulimwengu',
                'english': 'He who is not taught by his mother will be taught by the world',
                'meaning': 'Learn to save early or life will teach you the hard way'
            },
            {
                'swahili': 'Kidogo kidogo hujaza kibaba',
                'english': 'Little by little fills the pot',
                'meaning': 'Small savings add up over time'
            },
            {
                'swahili': 'Haba na haba hujaza kibaba',
                'english': 'Little by little fills the measure',
                'meaning': 'Consistent small savings lead to wealth'
            },
            {
                'swahili': 'Mchuma janga hula na wenziwe',
                'english': 'He who saves for a rainy day eats with friends',
                'meaning': 'Savings help you and your community in tough times'
            }
        ]
        
        # Common code-switching phrases
        self.greetings = [
            'Habari!', 'Vipi!', 'Sasa!', 'Hi!', 'Hello!'
        ]
        
        self.encouragements = [
            'Poa sana!', 'Very good!', 'Vizuri!', 'Nice!',
            'You\'re doing great!', 'Umefanya vizuri!',
            'Keep it up!', 'Endelea hivyo!', 'Great job!', 'Poa kabisa!'
        ]
        
        self.transitions = [
            'Sawa,', 'Okay,', 'Vizuri,', 'Poa,', 'Sawa sawa,',
            'Got it,', 'Nimeelewa,', 'Alright,', 'Sure,'
        ]
    
    def get_random_proverb(self, topic='savings'):
        """Get random proverb"""
        return random.choice(self.proverbs)
    
    def get_greeting(self):
        """Get random greeting"""
        return random.choice(self.greetings)
    
    def get_encouragement(self):
        """Get random encouragement"""
        return random.choice(self.encouragements)
    
    def get_transition(self):
        """Get random transition phrase"""
        return random.choice(self.transitions)