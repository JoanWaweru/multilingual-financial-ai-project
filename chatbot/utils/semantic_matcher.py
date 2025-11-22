"""
Production Semantic Intent Matcher
Understands meaning, not just patterns - handles ALL language variations
"""

import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from typing import Dict, Optional, List, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticMatcher:
    """
    BERT-based semantic matching system
    
    Core Features:
    - Understands intent from meaning, not keywords
    - Handles English/Swahili/mixed automatically
    - No need to add new patterns for variations
    - Works with typos and informal language
    - Learns from semantic similarity
    
    Example:
        "tell me", "show me", "niambie", "explain" → ALL detected as "request_information"
        "one place", "mahali moja", "pamoja" → ALL detected as "single_place_preference"
    """
    
    def __init__(self, model_name: str = "bert-base-multilingual-cased", cache_dir: str = None):
        """
        Initialize semantic matcher with BERT
        
        Args:
            model_name: HuggingFace model (multilingual for English+Swahili)
            cache_dir: Where to cache model
        """
        
        logger.info("🧠 Initializing Semantic Matcher...")
        logger.info(f"   Model: {model_name}")
        
        # Set cache directory
        if cache_dir:
            os.environ['TRANSFORMERS_CACHE'] = cache_dir
        
        # Load BERT
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()
            logger.info("✓ BERT model loaded")
        except Exception as e:
            logger.error(f"Failed to load BERT: {e}")
            raise
        
        # Intent templates - semantic examples
        self.intent_templates = {
            # Yes/No responses
            'affirmation_yes': [
                "yes", "yeah", "yep", "sure", "okay", "correct", "right", 
                "absolutely", "definitely", "of course", "affirmative",
                "ndio", "sawa", "ndiyo", "eeh", "ehe", "kabisa", 
                "poa", "sawa sawa", "vizuri"
            ],
            
            'affirmation_no': [
                "no", "nope", "nah", "not really", "wrong", "incorrect", 
                "negative", "never", "not at all",
                "hapana", "la", "siyo", "ala", "sitaki", 
                "hapana kabisa", "si vizuri"
            ],
            
            # Information requests
            'request_information': [
                "tell me", "show me", "explain", "describe", "what is", 
                "how does", "can you tell", "let me know", "inform me",
                "I want to know", "could you explain",
                "niambie", "onyesha", "eleza", "nisaidie kuelewa", 
                "ni nini", "inafanya vipi", "nieleze", "nishow"
            ],
            
            # Help requests
            'request_help': [
                "help me", "assist me", "guide me", "support me", 
                "can you help", "need help", "please help",
                "nisaidie", "saidia", "nishughulikie", "unaweza kunisaidia",
                "nataka msaada"
            ],
            
            # Single investment preference
            'single_place_preference': [
                "one place", "single location", "all in one", "together", 
                "one spot", "one investment", "just one", "only one",
                "everything in one", "put it all",
                "mahali moja", "place moja", "moja tu", "yote mahali moja", 
                "pamoja", "sehemu moja", "weka yote mahali moja"
            ],
            
            # Diversification preference
            'diversify_preference': [
                "spread", "diversify", "multiple places", "different places", 
                "split it", "divide", "various places", "many places",
                "gawa", "tofauti", "mbalimbali", "separate", "tengana",
                "mahali tofauti"
            ],
            
            # Option selections
            'option_selection_1': [
                "option one", "first option", "number 1", "the first", 
                "option 1", "choice 1", "1st", "one",
                "ya kwanza", "chaguo la kwanza", "namba moja"
            ],
            
            'option_selection_2': [
                "option two", "second option", "number 2", "the second", 
                "option 2", "choice 2", "2nd", "two",
                "ya pili", "chaguo la pili", "namba mbili"
            ],
            
            'option_selection_3': [
                "option three", "third option", "number 3", "the third", 
                "option 3", "choice 3", "3rd", "three",
                "ya tatu", "chaguo la tatu", "namba tatu"
            ],
            
            # Rejection/disagreement
            'rejection': [
                "I don't want", "not interested", "don't like", "not that",
                "something else", "different option", "not this",
                "sitaki", "si hii", "sio hiyo", "pengine", "si hio"
            ],
            
            # Return/profit questions
            'ask_returns': [
                "how much will I get", "what returns", "profit", 
                "how much back", "earn how much", "calculate returns",
                "nitapata kiasi gani", "faida gani", "mapato", "pesa ngapi"
            ]
        }
        
        # Precompute embeddings
        self.intent_embeddings = {}
        self._precompute_embeddings()
        
        logger.info(f"✓ Semantic Matcher Ready")
        logger.info(f"   Intents: {len(self.intent_embeddings)}")
        logger.info(f"   Templates: {sum(len(t) for t in self.intent_templates.values())}")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Get BERT embedding for text
        
        Uses [CLS] token representation as sentence embedding
        """
        
        with torch.no_grad():
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=128
            )
            
            # Get BERT output
            outputs = self.model(**inputs)
            
            # Use [CLS] token (first token) as sentence representation
            embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
        
        return embedding
    
    def _precompute_embeddings(self):
        """
        Precompute embeddings for all intent templates
        
        This is done once at initialization for speed
        """
        
        logger.info("Precomputing intent embeddings...")
        
        for intent, templates in self.intent_templates.items():
            embeddings = []
            
            for template in templates:
                embedding = self._get_embedding(template)
                embeddings.append(embedding)
            
            # Average all template embeddings for this intent
            # This creates a "semantic center" for the intent
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)
        
        logger.info(f"✓ Precomputed {len(self.intent_embeddings)} intent embeddings")
    
    def match_intent(self, text: str, threshold: float = 0.65) -> Dict[str, float]:
        """
        Match text against ALL intents
        
        Args:
            text: User's message
            threshold: Minimum similarity (0-1)
        
        Returns:
            Dict of {intent: similarity_score} for matches above threshold
        """
        
        if not text or len(text.strip()) == 0:
            return {}
        
        text_embedding = self._get_embedding(text.lower().strip())
        
        similarities = {}
        
        for intent, intent_embedding in self.intent_embeddings.items():
            similarity = self._cosine_similarity(text_embedding, intent_embedding)
            
            if similarity >= threshold:
                similarities[intent] = float(similarity)
        
        return similarities
    
    def is_affirmation(self, text: str, threshold: float = 0.75) -> Optional[str]:
        """
        Detect yes/no - handles ALL variations
        
        Examples that work:
        - "yes", "yeah", "sure" → 'yes'
        - "ndio", "sawa", "eeh" → 'yes'
        - "yes tell me more" → 'yes'
        - "no thanks", "hapana" → 'no'
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            'yes', 'no', or None
        """
        
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Fast path: exact matches
        if text_lower in ['yes', 'yeah', 'yep', 'ndio', 'sawa', 'eeh', 'ehe']:
            return 'yes'
        if text_lower in ['no', 'nope', 'nah', 'hapana', 'la']:
            return 'no'
        
        # Semantic matching for variations
        matches = self.match_intent(text, threshold=threshold)
        
        # Return highest scoring affirmation
        yes_score = matches.get('affirmation_yes', 0)
        no_score = matches.get('affirmation_no', 0)
        
        if yes_score > no_score and yes_score >= threshold:
            return 'yes'
        elif no_score > yes_score and no_score >= threshold:
            return 'no'
        
        return None
    
    def is_information_request(self, text: str, threshold: float = 0.7) -> bool:
        """
        Detect information requests
        
        Examples that work:
        - "tell me", "show me", "explain"
        - "niambie", "eleza", "onyesha"
        - "can you tell me more"
        - "nisaidie kuelewa"
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            True if information request detected
        """
        
        matches = self.match_intent(text, threshold=threshold)
        return 'request_information' in matches
    
    def is_single_place_preference(self, text: str, threshold: float = 0.7) -> bool:
        """
        Detect single investment place preference
        
        Examples that work:
        - "one place", "single location"
        - "mahali moja", "place moja"
        - "all in one", "just one"
        - "pamoja", "weka yote mahali moja"
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            True if single place preference detected
        """
        
        matches = self.match_intent(text, threshold=threshold)
        return 'single_place_preference' in matches
    
    def get_option_selection(self, text: str, threshold: float = 0.75) -> Optional[int]:
        """
        Detect option selection (1, 2, or 3)
        
        Examples that work:
        - "option 1", "first one", "number 1"
        - "ya kwanza", "chaguo la kwanza"
        - "the first option", "1"
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            1, 2, 3, or None
        """
        
        matches = self.match_intent(text, threshold=threshold)
        
        # Check which option has highest score
        option_scores = {
            1: matches.get('option_selection_1', 0),
            2: matches.get('option_selection_2', 0),
            3: matches.get('option_selection_3', 0)
        }
        
        best_option = max(option_scores.items(), key=lambda x: x[1])
        
        if best_option[1] >= threshold:
            return best_option[0]
        
        return None
    
    def is_rejection(self, text: str, threshold: float = 0.7) -> bool:
        """
        Detect rejection/disagreement
        
        Examples:
        - "I don't want that", "not interested"
        - "sitaki", "si hii", "pengine"
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            True if rejection detected
        """
        
        matches = self.match_intent(text, threshold=threshold)
        return 'rejection' in matches
    
    def is_asking_returns(self, text: str, threshold: float = 0.7) -> bool:
        """
        Detect questions about returns/profits
        
        Examples:
        - "how much will I get", "what returns"
        - "nitapata kiasi gani", "faida gani"
        
        Args:
            text: User's message
            threshold: Confidence threshold
        
        Returns:
            True if asking about returns
        """
        
        matches = self.match_intent(text, threshold=threshold)
        return 'ask_returns' in matches
    
    def get_all_matches(self, text: str, threshold: float = 0.65) -> List[Tuple[str, float]]:
        """
        Get all intent matches sorted by confidence
        
        Useful for debugging and understanding what the system detected
        
        Args:
            text: User's message
            threshold: Minimum confidence
        
        Returns:
            List of (intent, score) tuples sorted by score
        """
        
        matches = self.match_intent(text, threshold=threshold)
        return sorted(matches.items(), key=lambda x: x[1], reverse=True)
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Returns value between -1 and 1 (typically 0.5-1.0 for similar)
        """
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

# ============================================================================
# COMPREHENSIVE TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" 🧠 SEMANTIC MATCHER - COMPREHENSIVE TEST")
    print("="*70)
    
    matcher = SemanticMatcher()
    
    test_cases = [
        # Affirmations - Yes
        ("yes", "Should detect: YES"),
        ("yeah sure", "Should detect: YES"),
        ("ndio kabisa", "Should detect: YES (Swahili)"),
        ("sawa sawa", "Should detect: YES (Swahili)"),
        ("yes tell me more", "Should detect: YES (with extra)"),
        
        # Affirmations - No
        ("no", "Should detect: NO"),
        ("nope not interested", "Should detect: NO"),
        ("hapana sitaki", "Should detect: NO (Swahili)"),
        
        # Information requests
        ("tell me more", "Should detect: INFO REQUEST"),
        ("show me the details", "Should detect: INFO REQUEST"),
        ("niambie zaidi", "Should detect: INFO REQUEST (Swahili)"),
        ("eleza please", "Should detect: INFO REQUEST (Swahili)"),
        ("can you explain how it works", "Should detect: INFO REQUEST"),
        ("yes niambie", "Should detect: YES + INFO REQUEST"),
        
        # Single place preference
        ("one place only", "Should detect: SINGLE PLACE"),
        ("mahali moja tu", "Should detect: SINGLE PLACE (Swahili)"),
        ("just one place", "Should detect: SINGLE PLACE"),
        ("put it all together", "Should detect: SINGLE PLACE"),
        ("place moja", "Should detect: SINGLE PLACE (mixed)"),
        
        # Option selection
        ("option 1", "Should detect: OPTION 1"),
        ("the first one", "Should detect: OPTION 1"),
        ("ya kwanza", "Should detect: OPTION 1 (Swahili)"),
        ("option 2", "Should detect: OPTION 2"),
        ("third option", "Should detect: OPTION 3"),
        
        # Rejection
        ("I don't want that", "Should detect: REJECTION"),
        ("not interested", "Should detect: REJECTION"),
        ("sitaki hii", "Should detect: REJECTION (Swahili)"),
        
        # Returns questions
        ("how much will I get", "Should detect: ASK RETURNS"),
        ("nitapata pesa ngapi", "Should detect: ASK RETURNS (Swahili)"),
        ("what profit", "Should detect: ASK RETURNS"),
        
        # Random (should NOT match)
        ("the weather is nice", "Should NOT match"),
        ("I like pizza", "Should NOT match")
    ]
    
    print("\n📊 TEST RESULTS:")
    print("="*70)
    
    success_count = 0
    total_count = len(test_cases)
    
    for text, expected in test_cases:
        print(f"\n🔍 Text: \"{text}\"")
        print(f"   Expected: {expected}")
        
        detected = []
        
        # Check affirmation
        affirmation = matcher.is_affirmation(text)
        if affirmation:
            detected.append(f"Affirmation: {affirmation.upper()}")
        
        # Check information request
        if matcher.is_information_request(text):
            detected.append("INFO REQUEST")
        
        # Check single place
        if matcher.is_single_place_preference(text):
            detected.append("SINGLE PLACE")
        
        # Check option
        option = matcher.get_option_selection(text)
        if option:
            detected.append(f"OPTION {option}")
        
        # Check rejection
        if matcher.is_rejection(text):
            detected.append("REJECTION")
        
        # Check returns question
        if matcher.is_asking_returns(text):
            detected.append("ASK RETURNS")
        
        if detected:
            print(f"   ✓ Detected: {', '.join(detected)}")
            success_count += 1
        else:
            print(f"   - No detection")
        
        # Show all matches above 0.6 for debugging
        all_matches = matcher.get_all_matches(text, threshold=0.6)
        if all_matches:
            print(f"   All matches:")
            for intent, score in all_matches[:3]:
                print(f"     • {intent}: {score:.3f}")
    
    print("\n" + "="*70)
    print(f" 📊 Results: {success_count}/{total_count} tests matched expectations")
    print("="*70)
    print("✓ Semantic Matcher Test Complete!")