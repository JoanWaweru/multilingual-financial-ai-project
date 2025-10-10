"""
Code-switching detector with improved heuristic correction
"""

import torch
from transformers import BertTokenizer
from pathlib import Path
import logging
import re

# Import your trained model
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from training.model import BERTCodeSwitchingModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeSwitchingDetector:
    """Hybrid code-switching detector (Model + Heuristics)"""
    
    def __init__(self, model_path="saved_models/best_model.pt"):
        """Initialize detector"""
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Loading CS detector on device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
        
        # Load model
        self.model = BERTCodeSwitchingModel(num_labels=3)
        
        model_path = Path(model_path)
        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        # Label mapping
        self.id2label = {
            0: 'english',
            1: 'swahili',
            2: 'code_switched'
        }
        
        # EXPANDED Swahili word markers
        self.swahili_markers = {
            # Common words
            'ni', 'na', 'ya', 'wa', 'kwa', 'lakini', 'sana', 'tu',
            'nina', 'wewe', 'mimi', 'yake', 'yangu', 'wangu', 'wake',
            'nini', 'kitu', 'watu', 'sasa', 'leo', 'kesho', 'jana',
            'hapa', 'pale', 'kule', 'ndio', 'hapana',
            
            # Verbs
            'kusema', 'kufanya', 'kuweka', 'kuwa', 'kutoka', 'kwenda',
            'nataka', 'ninataka', 'unataka', 'anataka', 'tunataka',
            'naweza', 'unaweza', 'anaweza', 'tunaweza',
            'najua', 'unajua', 'anajua', 'tunajua',
            'sijui', 'hujui', 'hajui', 'hatujui',
            'kuona', 'kusoma', 'kula', 'kunywa', 'kulala',
            
            # Greetings/Polite
            'habari', 'vipi', 'vizuri', 'nzuri', 'mbaya', 'pole',
            'asante', 'karibu', 'tafadhali', 'samahani',
            
            # Financial terms (Swahili)
            'pesa', 'benki', 'akiba', 'mkopo', 'akaunti',
            'uwekezaji', 'bajeti', 'malipo', 'riba',
            'chama', 'sacco', 'mpesa', 'shilling',
            
            # Time/Place
            'wakati', 'mahali', 'nyumbani', 'kazini', 'sokoni',
            'wiki', 'mwezi', 'mwaka', 'siku', 'usiku', 'asubuhi',
            
            # Numbers
            'moja', 'mbili', 'tatu', 'nne', 'tano', 'sita',
            'elfu', 'laki', 'milioni'
        }
        
        # EXPANDED English markers
        self.english_markers = {
            # Common function words
            'the', 'is', 'are', 'was', 'were', 'and', 'or', 'to', 'for',
            'a', 'an', 'in', 'on', 'at', 'by', 'of', 'with', 'from',
            'but', 'if', 'then', 'so', 'as', 'than',
            
            # Pronouns
            'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'this', 'that', 'these', 'those',
            
            # Verbs
            'can', 'will', 'would', 'should', 'could', 'may', 'might',
            'must', 'have', 'has', 'had', 'do', 'does', 'did',
            'get', 'make', 'go', 'come', 'want', 'need', 'know',
            'think', 'see', 'tell', 'say', 'give', 'take',
            'open', 'close', 'send', 'receive', 'pay', 'buy',
            
            # Questions
            'how', 'what', 'where', 'when', 'why', 'which', 'who',
            
            # Financial terms (English)
            'bank', 'money', 'save', 'saving', 'savings', 'loan',
            'account', 'balance', 'deposit', 'withdraw', 'transfer',
            'payment', 'interest', 'credit', 'debit', 'card',
            'investment', 'invest', 'budget', 'spend', 'cost',
            
            # Common adjectives
            'good', 'bad', 'big', 'small', 'new', 'old', 'much', 'many'
        }
        
        logger.info("✓ CS detector loaded successfully")
    
    def detect(self, text):
        """
        Detect language/code-switching in text with heuristic correction
        
        Returns:
            dict with 'label', 'confidence', 'probabilities', 'method'
        """
        
        # Step 1: Get model prediction
        model_result = self._model_predict(text)
        
        # Step 2: Apply heuristic correction
        corrected_result = self._heuristic_correction(text, model_result)
        
        return corrected_result
    
    def _model_predict(self, text):
        """Get raw model prediction"""
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            max_length=128,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.model(input_ids, attention_mask)
            probabilities = torch.softmax(logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1)
        
        pred_id = prediction.item()
        confidence = probabilities[0][pred_id].item()
        
        return {
            'label': self.id2label[pred_id],
            'confidence': confidence,
            'probabilities': {
                'english': probabilities[0][0].item(),
                'swahili': probabilities[0][1].item(),
                'code_switched': probabilities[0][2].item()
            },
            'method': 'model_only'
        }
    
    def _heuristic_correction(self, text, model_result):
        """
        Apply rule-based correction with improved logic
        """
        
        # Analyze text composition
        words = self._extract_words(text)
        
        if len(words) == 0:
            return model_result
        
        # Count language markers
        swahili_words = [w for w in words if w in self.swahili_markers]
        english_words = [w for w in words if w in self.english_markers]
        
        swahili_count = len(swahili_words)
        english_count = len(english_words)
        
        total_identified = swahili_count + english_count
        total_words = len(words)
        
        # Calculate ratios
        if total_identified > 0:
            swahili_ratio = swahili_count / total_identified
            english_ratio = english_count / total_identified
        else:
            # No clear markers, trust model
            return model_result
        
        # IMPROVED DECISION LOGIC
        corrected_label = model_result['label']
        method = 'model_only'
        confidence = model_result['confidence']
        
        # Case 1: BOTH languages present → Code-switched
        if swahili_count >= 1 and english_count >= 1:
            corrected_label = 'code_switched'
            method = 'heuristic_both_languages'
            confidence = 0.90
        
        # Case 2: ONLY Swahili (no English markers)
        elif swahili_count >= 2 and english_count == 0:
            corrected_label = 'swahili'
            method = 'heuristic_swahili_only'
            confidence = 0.95
        
        # Case 3: ONLY English (no Swahili markers)
        elif english_count >= 2 and swahili_count == 0:
            corrected_label = 'english'
            method = 'heuristic_english_only'
            confidence = 0.95
        
        # Case 4: Very short text with single marker
        elif total_words <= 3:
            if swahili_count > 0 and english_count == 0:
                corrected_label = 'swahili'
                method = 'heuristic_short_swahili'
                confidence = 0.85
            elif english_count > 0 and swahili_count == 0:
                corrected_label = 'english'
                method = 'heuristic_short_english'
                confidence = 0.85
        
        # Case 5: Dominant language (>80% of identified words)
        elif swahili_ratio > 0.8 and swahili_count >= 3:
            corrected_label = 'swahili'
            method = 'heuristic_dominant_swahili'
            confidence = 0.90
        elif english_ratio > 0.8 and english_count >= 3:
            corrected_label = 'english'
            method = 'heuristic_dominant_english'
            confidence = 0.90
        
        # Otherwise trust model
        else:
            method = 'model_trusted'
        
        # Update result
        result = model_result.copy()
        result['label'] = corrected_label
        result['confidence'] = confidence
        result['method'] = method
        result['analysis'] = {
            'swahili_words': swahili_count,
            'english_words': english_count,
            'total_words': total_words,
            'identified_words': total_identified,
            'swahili_ratio': swahili_ratio if total_identified > 0 else 0.0,
            'english_ratio': english_ratio if total_identified > 0 else 0.0,
            'swahili_found': swahili_words[:5],  # Show first 5
            'english_found': english_words[:5]   # Show first 5
        }
        
        return result
    
    def _extract_words(self, text):
        """Extract words from text (lowercase, alphanumeric only)"""
        
        # Convert to lowercase
        text = text.lower()
        
        # Extract words (alphanumeric sequences)
        words = re.findall(r'\b[a-z]+\b', text)
        
        return words
    
    def get_language_ratio(self, text):
        """
        Estimate Swahili-English ratio in text
        Returns: float between 0.0 (all English) and 1.0 (all Swahili)
        """
        
        words = self._extract_words(text)
        
        if len(words) == 0:
            return 0.5  # Default to balanced
        
        swahili_count = sum(1 for word in words if word in self.swahili_markers)
        english_count = sum(1 for word in words if word in self.english_markers)
        
        total = swahili_count + english_count
        
        if total == 0:
            return 0.5  # No clear markers, assume balanced
        
        return swahili_count / total

if __name__ == "__main__":
    # Test the improved detector
    detector = CodeSwitchingDetector()
    
    test_texts = [
        "I want to save money in my bank account",
        "Ninataka kuweka pesa kwa akiba yangu",
        "I want to save pesa lakini sijui how to start",
        "How do I open a bank account?",
        "Nataka kuona balance yangu",  # Should be code_switched!
        "Can you tell me about chama?",  # Should be code_switched!
        "Pesa ni muhimu sana kwa maisha",
        "What is mpesa?",  # Should be code_switched!
        "Nina account kwa Equity Bank"  # Should be code_switched!
    ]
    
    print("\n" + "=" * 70)
    print("TESTING IMPROVED CODE-SWITCHING DETECTOR (V2)")
    print("=" * 70)
    
    for text in test_texts:
        result = detector.detect(text)
        ratio = detector.get_language_ratio(text)
        
        print(f"\n📝 Text: {text}")
        print(f"   Detected: {result['label']} ({result['method']})")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   Swahili ratio: {ratio:.0%}")
        
        if 'analysis' in result:
            analysis = result['analysis']
            print(f"   Analysis: {analysis['swahili_words']} Swahili, "
                  f"{analysis['english_words']} English, "
                  f"{analysis['total_words']} total words")
            if analysis['swahili_found']:
                print(f"   Swahili words: {', '.join(analysis['swahili_found'])}")
            if analysis['english_found']:
                print(f"   English words: {', '.join(analysis['english_found'])}")