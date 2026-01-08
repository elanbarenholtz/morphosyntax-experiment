#!/usr/bin/env python3
"""
Word-Level Analysis Infrastructure for Morphosyntax Audit

Handles BPE tokenization issues by:
1. Identifying word-start tokens (space-prefixed in GPT-2/Pythia)
2. Mapping tokens to words using lexicon lookup
3. Computing class-level probability mass at word boundaries

This avoids artifacts from multi-token nonce words in Jabberwocky conditions.
"""

import torch
import numpy as np
from typing import Dict, Set, List, Tuple, Optional


class WordLevelAnalyzer:
    """
    Analyzes model predictions at word level (not token level).

    Key features:
    - Only considers word-start tokens (space-prefixed)
    - Maps tokens to words via lexicon lookup
    - Aggregates probability mass by word class
    """

    def __init__(self, tokenizer, cue_families: Dict):
        """
        Initialize analyzer.

        Args:
            tokenizer: HuggingFace tokenizer (GPT-2, Pythia, etc.)
            cue_families: Dictionary of cue family definitions from cue_families.py
        """
        self.tokenizer = tokenizer
        self.cue_families = cue_families

        # Cache for token → word mappings
        self._token_to_word_cache = {}

        # Cache for word → class memberships
        self._word_class_cache = {}

    def is_word_start_token(self, token_id: int) -> bool:
        """
        Check if token represents start of a word.

        In GPT-2/Pythia BPE, word-start tokens begin with space (e.g., " the", " cat").
        Mid-word tokens do not (e.g., "ing", "ed").

        Args:
            token_id: Token ID

        Returns:
            Boolean indicating if token is word-start
        """
        token_str = self.tokenizer.decode([token_id])

        # Special case: single-token special tokens
        if token_str in ['<|endoftext|>', '<unk>', '<pad>']:
            return False

        # Word-start tokens begin with space in GPT-2/Pythia
        return token_str.startswith(' ') or token_str.startswith('\n')

    def get_word_from_token(self, token_id: int) -> Optional[str]:
        """
        Extract word from token (lowercase, stripped).

        Args:
            token_id: Token ID

        Returns:
            Word string (lowercase) or None if not a word-start token
        """
        if token_id in self._token_to_word_cache:
            return self._token_to_word_cache[token_id]

        if not self.is_word_start_token(token_id):
            self._token_to_word_cache[token_id] = None
            return None

        token_str = self.tokenizer.decode([token_id])
        # Remove leading space/newline, lowercase, strip punctuation
        word = token_str.strip().lower().strip('.,!?;:"\'-')

        self._token_to_word_cache[token_id] = word
        return word

    def get_word_classes(self, word: str, family_name: str) -> Set[str]:
        """
        Get word classes for a word in a cue family.

        Args:
            word: Word string (lowercase)
            family_name: Cue family name

        Returns:
            Set of class names this word belongs to (e.g., {'VERB'})
        """
        cache_key = (word, family_name)
        if cache_key in self._word_class_cache:
            return self._word_class_cache[cache_key]

        family = self.cue_families[family_name]
        classes = set()

        for class_name, word_set in family['expected_classes'].items():
            if word in word_set:
                classes.add(class_name)

        self._word_class_cache[cache_key] = classes
        return classes

    def compute_class_mass(
        self,
        probs: torch.Tensor,
        family_name: str,
        top_k: int = 1000
    ) -> Dict[str, float]:
        """
        Compute probability mass for each word class in a cue family.

        Only considers word-start tokens (space-prefixed).

        Args:
            probs: Probability distribution over vocabulary (shape: [vocab_size])
            family_name: Cue family name
            top_k: Number of top tokens to consider (default: 1000)

        Returns:
            Dictionary mapping class names to probability mass
            Example: {'VERB': 0.42, 'NOUN': 0.18}
        """
        # Get top-k predictions
        top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

        # Initialize class mass
        family = self.cue_families[family_name]
        class_mass = {class_name: 0.0 for class_name in family['expected_classes'].keys()}

        # Aggregate probability by word class
        for prob, token_id in zip(top_k_probs, top_k_ids):
            word = self.get_word_from_token(token_id.item())

            if word is None:
                continue  # Skip non-word-start tokens

            # Check which classes this word belongs to
            word_classes = self.get_word_classes(word, family_name)

            # Add probability to each class
            for class_name in word_classes:
                class_mass[class_name] += prob.item()

        return class_mass

    def find_cue_positions(
        self,
        text: str,
        family_name: str
    ) -> List[Tuple[int, str, str]]:
        """
        Find positions of cue words in text.

        Args:
            text: Sentence text
            family_name: Cue family name

        Returns:
            List of (word_index, cue_word, context_up_to_cue) tuples
        """
        family = self.cue_families[family_name]
        cue_words = family['cue_words']

        words = text.split()
        cue_positions = []

        for i, word in enumerate(words):
            word_clean = word.lower().strip('.,!?;:"\'-')

            if word_clean in cue_words:
                context = ' '.join(words[:i+1])
                cue_positions.append((i, word_clean, context))

        return cue_positions

    def analyze_cue_predictions(
        self,
        text: str,
        family_name: str,
        model,
        top_k: int = 1000
    ) -> List[Dict]:
        """
        Analyze model predictions after each cue word in text.

        Args:
            text: Sentence text
            family_name: Cue family name
            model: Language model (HuggingFace)
            top_k: Number of top tokens to consider

        Returns:
            List of dictionaries, one per cue occurrence:
            [
                {
                    'cue_word': 'to',
                    'word_index': 3,
                    'context': 'the prell decided to',
                    'class_mass': {'VERB': 0.42},
                    'num_tokens': 5,
                },
                ...
            ]
        """
        # Find cue positions
        cue_positions = self.find_cue_positions(text, family_name)

        if not cue_positions:
            return []

        results = []

        for word_idx, cue_word, context in cue_positions:
            # Tokenize context
            inputs = self.tokenizer(context, return_tensors='pt')

            # Move inputs to same device as model
            device = next(model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            # Get model predictions
            with torch.no_grad():
                outputs = model(**inputs)

            logits = outputs.logits[0, -1, :]  # Last token position
            probs = torch.softmax(logits, dim=-1)

            # Compute class mass
            class_mass = self.compute_class_mass(probs, family_name, top_k=top_k)

            results.append({
                'cue_word': cue_word,
                'word_index': word_idx,
                'context': context,
                'class_mass': class_mass,
                'num_tokens': len(inputs['input_ids'][0]),
            })

        return results


# ============================================================================
# METHOD 2: POS-Tagger Based Classification
# ============================================================================

class POSTaggerAnalyzer:
    """
    Uses spaCy POS tagger to classify predicted words.

    More flexible than lexicon-based, but requires valid English words.
    """

    def __init__(self, tokenizer, nlp, cue_families: Dict):
        """
        Initialize analyzer.

        Args:
            tokenizer: HuggingFace tokenizer
            nlp: spaCy NLP pipeline (e.g., en_core_web_sm)
            cue_families: Cue family definitions
        """
        self.tokenizer = tokenizer
        self.nlp = nlp
        self.cue_families = cue_families

        # Mapping from spaCy POS tags to our word classes
        self.pos_to_class = {
            'VERB': 'VERB',
            'NOUN': 'NOUN',
            'PROPN': 'NOUN',  # Proper nouns count as nouns
            'ADJ': 'ADJECTIVE',
            'ADP': 'NP_START',  # Prepositions (shouldn't appear after cues, but include for completeness)
            'DET': 'NP_START',
            'PRON': 'CLAUSE_START',
        }

    def is_word_start_token(self, token_id: int) -> bool:
        """Check if token is word-start."""
        token_str = self.tokenizer.decode([token_id])
        if token_str in ['<|endoftext|>', '<unk>', '<pad>']:
            return False
        return token_str.startswith(' ') or token_str.startswith('\n')

    def get_word_from_token(self, token_id: int) -> Optional[str]:
        """Extract word from token."""
        if not self.is_word_start_token(token_id):
            return None
        token_str = self.tokenizer.decode([token_id])
        return token_str.strip().lower().strip('.,!?;:"\'-')

    def classify_word(self, word: str, family_name: str) -> Set[str]:
        """
        Classify word using POS tagger.

        Args:
            word: Word string
            family_name: Cue family (to determine relevant classes)

        Returns:
            Set of class names
        """
        doc = self.nlp(word)

        if len(doc) == 0:
            return set()

        pos = doc[0].pos_

        # Map spaCy POS to our class taxonomy
        classes = set()

        family = self.cue_families[family_name]
        expected_classes = set(family['expected_classes'].keys())

        if pos in self.pos_to_class:
            class_name = self.pos_to_class[pos]
            if class_name in expected_classes:
                classes.add(class_name)

        # Special handling for participles (VERB + participle tags)
        if pos == 'VERB' and 'PARTICIPLE' in expected_classes:
            # Check if it's a participle form
            tag = doc[0].tag_  # Fine-grained POS tag
            if tag in ['VBG', 'VBN', 'VBD']:  # -ing, -ed, past
                classes.add('PARTICIPLE')

        return classes

    def compute_class_mass(
        self,
        probs: torch.Tensor,
        family_name: str,
        top_k: int = 1000
    ) -> Dict[str, float]:
        """Compute class mass using POS tagger."""
        top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

        family = self.cue_families[family_name]
        class_mass = {class_name: 0.0 for class_name in family['expected_classes'].keys()}

        for prob, token_id in zip(top_k_probs, top_k_ids):
            word = self.get_word_from_token(token_id.item())

            if word is None:
                continue

            word_classes = self.classify_word(word, family_name)

            for class_name in word_classes:
                class_mass[class_name] += prob.item()

        return class_mass


# ============================================================================
# METHOD 3: Classifier-Based (Placeholder for existing classifier)
# ============================================================================

class ClassifierBasedAnalyzer:
    """
    Uses an existing morphosyntactic classifier to categorize words.

    This is a placeholder - would integrate with your existing classifier
    from morphosyntax_audit_refined.py if available.
    """

    def __init__(self, tokenizer, classifier_model, cue_families: Dict):
        """
        Initialize analyzer.

        Args:
            tokenizer: HuggingFace tokenizer
            classifier_model: Pre-trained word classifier (e.g., BERT-based)
            cue_families: Cue family definitions
        """
        self.tokenizer = tokenizer
        self.classifier = classifier_model
        self.cue_families = cue_families

    def compute_class_mass(
        self,
        probs: torch.Tensor,
        family_name: str,
        top_k: int = 1000
    ) -> Dict[str, float]:
        """
        Compute class mass using external classifier.

        NOTE: This is a placeholder. Actual implementation would depend on
        the specific classifier architecture.
        """
        # TODO: Implement when classifier is available
        raise NotImplementedError("Classifier-based analysis not yet implemented")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_analyzer(
    method: str,
    tokenizer,
    cue_families: Dict,
    nlp=None,
    classifier=None
):
    """
    Factory function to create appropriate analyzer.

    Args:
        method: One of ['lexicon', 'pos', 'classifier']
        tokenizer: HuggingFace tokenizer
        cue_families: Cue family definitions
        nlp: spaCy NLP (required for 'pos' method)
        classifier: Classifier model (required for 'classifier' method)

    Returns:
        Analyzer instance
    """
    if method == 'lexicon':
        return WordLevelAnalyzer(tokenizer, cue_families)

    elif method == 'pos':
        if nlp is None:
            raise ValueError("POS method requires nlp parameter (spaCy model)")
        return POSTaggerAnalyzer(tokenizer, nlp, cue_families)

    elif method == 'classifier':
        if classifier is None:
            raise ValueError("Classifier method requires classifier parameter")
        return ClassifierBasedAnalyzer(tokenizer, classifier, cue_families)

    else:
        raise ValueError(f"Unknown method: {method}. Choose from ['lexicon', 'pos', 'classifier']")


# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("WORD-LEVEL ANALYSIS INFRASTRUCTURE")
    print("=" * 80)
    print()

    # Test with GPT-2
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    from cue_families import CUE_FAMILIES

    print("Loading GPT-2...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    model.eval()
    print("✓ Loaded")
    print()

    # Create analyzer
    analyzer = WordLevelAnalyzer(tokenizer, CUE_FAMILIES)

    # Test on example sentence
    text = "the scientist decided to study the ancient artifacts"
    family_name = 'infinitival_to'

    print(f"Test sentence: {text}")
    print(f"Cue family: {family_name}")
    print()

    # Analyze
    results = analyzer.analyze_cue_predictions(text, family_name, model)

    print(f"Found {len(results)} cue instance(s):")
    print()

    for r in results:
        print(f"  Cue: '{r['cue_word']}' at word position {r['word_index']}")
        print(f"  Context: ...{r['context'][-40:]}")
        print(f"  Class mass:")
        for class_name, mass in r['class_mass'].items():
            print(f"    {class_name}: {mass:.4f}")
        print()

    print("=" * 80)
    print("WORD-START TOKEN DETECTION")
    print("=" * 80)
    print()

    # Test word-start detection
    test_tokens = [
        ' the',    # Word-start
        ' cat',    # Word-start
        'ing',     # Mid-word
        'ed',      # Mid-word
        ' study',  # Word-start
    ]

    for tok_str in test_tokens:
        # Encode to get token ID
        tok_id = tokenizer.encode(tok_str, add_special_tokens=False)[0]
        is_word_start = analyzer.is_word_start_token(tok_id)
        word = analyzer.get_word_from_token(tok_id)
        print(f"'{tok_str}' (ID={tok_id}): word_start={is_word_start}, word={word}")

    print()
    print("✓ Word-level analysis infrastructure verified")
