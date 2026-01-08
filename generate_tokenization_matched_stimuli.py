"""
Generate tokenization-matched morphosyntax stimuli with normalization.

Uses the nonce lexicon to create conditions with controlled subtoken distributions.
ALL TEXT IS NORMALIZED (lowercase, consistent punctuation) to eliminate
capitalization-based tokenization confounds.
"""

import json
import random
import spacy
from transformers import AutoTokenizer
from collections import Counter
from normalization import normalize_text

# Load spaCy for POS tagging
nlp = spacy.load("en_core_web_sm")

# Function word categories (for skeleton condition)
FUNCTION_WORDS = {
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    'is', 'was', 'are', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'can', 'may', 'might', 'must',
    'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'from', 'about',
    'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'and', 'or', 'but', 'if', 'than', 'when', 'where', 'while', 'who', 'which',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'not', 'no', 'yes', 'very', 'too', 'so', 'just', 'now', 'then'
}

def load_lexicon(lexicon_file='nonce_lexicon.json'):
    """Load the nonce lexicon."""
    with open(lexicon_file, 'r') as f:
        return json.load(f)

def count_subtokens(word, tokenizer, with_leading_space=False):
    """
    Count subtokens for a word in context.

    Args:
        word: The word to tokenize
        tokenizer: The tokenizer
        with_leading_space: If True, prepend a space (for non-initial positions)

    Returns:
        Number of subtokens
    """
    text = " " + word if with_leading_space else word
    tokens = tokenizer.encode(text, add_special_tokens=False)
    return len(tokens)

def sample_nonce_by_subtokens(lexicon, tokenizer_name, n_subtokens, exclude=None):
    """Sample a nonce word with specific subtoken count."""
    exclude = exclude or set()
    bucket = lexicon[tokenizer_name].get(str(n_subtokens), [])

    # Filter out already used words
    available = [w for w in bucket if w not in exclude]

    if not available:
        # Fallback to nearby bucket if exact match exhausted
        for nearby in [n_subtokens-1, n_subtokens+1, n_subtokens-2, n_subtokens+2]:
            bucket = lexicon[tokenizer_name].get(str(nearby), [])
            available = [w for w in bucket if w not in exclude]
            if available:
                break

    if not available:
        raise ValueError(f"No available nonces with ~{n_subtokens} subtokens")

    return random.choice(available)

def get_subtoken_distribution(words, tokenizer):
    """Get the subtoken count distribution for a list of words."""
    counts = [count_subtokens(w, tokenizer) for w in words]
    return counts

def generate_jabberwocky_matched(sentence, lexicon, tokenizer, tokenizer_name, used_nonces):
    """
    Generate jabberwocky with matched tokenization.

    Real function words + nonce content words matched to real content word tokenization.
    Uses normalized (lowercase) form for tokenization matching.

    IMPORTANT: Matches in-context tokenization:
    - Position 0: match word without leading space
    - Position i>0: match " " + word (with leading space)
    """
    # Normalize input first
    sentence = normalize_text(sentence, strip_punctuation=True)

    doc = nlp(sentence)
    new_words = []

    for i, token in enumerate(doc):
        word = token.text
        word_lower = word.lower()

        if word_lower in FUNCTION_WORDS or token.pos_ in ['DET', 'AUX', 'ADP', 'CONJ', 'SCONJ']:
            # Keep function word (already lowercase)
            new_words.append(word)
        else:
            # Replace with tokenization-matched nonce
            # Match in-context tokenization: with leading space for i>0
            with_leading_space = (i > 0)
            n_subtokens = count_subtokens(word, tokenizer, with_leading_space=with_leading_space)
            nonce = sample_nonce_by_subtokens(lexicon, tokenizer_name, n_subtokens, used_nonces)
            used_nonces.add(nonce)
            new_words.append(nonce)

    return ' '.join(new_words)

def generate_word_list_real(sentence):
    """Generate word list by scrambling real words."""
    words = sentence.split()
    scrambled = words.copy()
    random.shuffle(scrambled)
    return ' '.join(scrambled)

def generate_word_list_nonce(sentence, lexicon, tokenizer, tokenizer_name, target_n_subtokens, used_nonces):
    """
    Generate word list of nonces matched to target subtoken count.

    Args:
        target_n_subtokens: 1 for sentence regime, 2 for jabberwocky regime
    """
    words = sentence.split()
    n_words = len(words)

    nonces = []
    for _ in range(n_words):
        nonce = sample_nonce_by_subtokens(lexicon, tokenizer_name, target_n_subtokens, used_nonces)
        used_nonces.add(nonce)
        nonces.append(nonce)

    # Capitalize first word
    if nonces:
        nonces[0] = nonces[0].capitalize()

    return ' '.join(nonces)

def generate_skeleton_function_words(sentence):
    """Generate skeleton with only function words, rest replaced with '___'."""
    doc = nlp(sentence.lower())
    new_words = []

    for token in doc:
        word = token.text
        word_lower = word.lower()

        if word_lower in FUNCTION_WORDS or token.pos_ in ['DET', 'AUX', 'ADP', 'CONJ', 'SCONJ']:
            new_words.append(word)
        else:
            # Replace content word with placeholder (for visualization)
            # In practice, we'll use nonces of same length
            new_words.append('___')

    return ' '.join(new_words)

def generate_skeleton_with_nonces(sentence, lexicon, tokenizer, tokenizer_name, used_nonces):
    """Generate skeleton: function words + random 1-tok nonces for content."""
    doc = nlp(sentence.lower())
    new_words = []

    for token in doc:
        word = token.text
        word_lower = word.lower()

        if word_lower in FUNCTION_WORDS or token.pos_ in ['DET', 'AUX', 'ADP', 'CONJ', 'SCONJ']:
            new_words.append(word)
        else:
            # Random 1-tok nonce (doesn't need to match original word's tokenization)
            nonce = sample_nonce_by_subtokens(lexicon, tokenizer_name, 1, used_nonces)
            used_nonces.add(nonce)

            # Preserve capitalization
            if word[0].isupper():
                nonce = nonce.capitalize()

            new_words.append(nonce)

    return ' '.join(new_words)

def generate_stimuli_set(sentence_id, sentence, lexicon, tokenizer_name='gpt2'):
    """Generate all conditions for a single sentence."""
    # Load tokenizer
    if tokenizer_name == 'gpt2':
        tokenizer = AutoTokenizer.from_pretrained('gpt2')
    else:
        tokenizer = AutoTokenizer.from_pretrained('EleutherAI/pythia-410m')

    # Normalize the input sentence
    sentence = normalize_text(sentence, strip_punctuation=True)

    # Track used nonces to ensure uniqueness within set
    used_nonces = set()

    # Generate all conditions
    conditions = {
        'set_id': sentence_id,
        'sentence': sentence,  # Now normalized
    }

    # JABBERWOCKY_MATCHED: Real function words + matched content nonces
    conditions['jabberwocky_matched'] = generate_jabberwocky_matched(
        sentence, lexicon, tokenizer, tokenizer_name, used_nonces
    )

    # WORD_LIST_REAL: Scrambled real words
    conditions['word_list_real'] = generate_word_list_real(sentence)

    # WORD_LIST_NONCE_1TOK: Scrambled 1-tok nonces (baseline for sentence regime)
    conditions['word_list_nonce_1tok'] = generate_word_list_nonce(
        sentence, lexicon, tokenizer, tokenizer_name, 1, used_nonces
    )

    # WORD_LIST_NONCE_2TOK: Scrambled 2-tok nonces (baseline for jabberwocky regime)
    conditions['word_list_nonce_2tok'] = generate_word_list_nonce(
        sentence, lexicon, tokenizer, tokenizer_name, 2, used_nonces
    )

    # SKELETON_FUNCTION_WORDS: Only function words with structure
    conditions['skeleton_function_words'] = generate_skeleton_with_nonces(
        sentence, lexicon, tokenizer, tokenizer_name, used_nonces
    )

    return conditions

def generate_full_stimulus_set(source_file='stimuli_controlled.json',
                                lexicon_file='nonce_lexicon.json',
                                output_file='stimuli_tokenization_matched.json',
                                tokenizer_name='gpt2'):
    """Generate complete stimulus set with all conditions."""
    print("=" * 80)
    print("GENERATING TOKENIZATION-MATCHED STIMULI")
    print("=" * 80)

    # Load lexicon
    print(f"\nLoading nonce lexicon from {lexicon_file}...")
    lexicon = load_lexicon(lexicon_file)

    # Load source sentences
    print(f"Loading source sentences from {source_file}...")
    with open(source_file, 'r') as f:
        source_stimuli = json.load(f)

    # Extract sentences
    sentences = []
    for item in source_stimuli:
        if 'sentence' in item:
            sentences.append(item['sentence'])

    print(f"Found {len(sentences)} source sentences")
    print(f"Generating stimuli for tokenizer: {tokenizer_name}")

    # Generate all conditions
    print("\nGenerating conditions for each sentence...")
    all_stimuli = []

    for i, sentence in enumerate(sentences, 1):
        print(f"  Processing sentence {i}/{len(sentences)}...", end='\r')
        try:
            stim_set = generate_stimuli_set(i, sentence, lexicon, tokenizer_name)
            all_stimuli.append(stim_set)
        except Exception as e:
            print(f"\n  Warning: Failed to generate set {i}: {e}")
            continue

    print(f"\n\nSuccessfully generated {len(all_stimuli)} stimulus sets")

    # Save stimuli
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(all_stimuli, f, indent=2)

    # Print examples
    print("\n" + "=" * 80)
    print("EXAMPLE STIMULUS SET")
    print("=" * 80)

    if all_stimuli:
        example = all_stimuli[0]
        for condition, text in example.items():
            if condition != 'set_id':
                print(f"\n{condition.upper()}:")
                print(f"  {text}")

    print("\n" + "=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)

    return all_stimuli

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Generate tokenization-matched morphosyntax stimuli')
    parser.add_argument('--source', type=str, default='stimuli_controlled.json',
                       help='Source sentence file')
    parser.add_argument('--lexicon', type=str, default='nonce_lexicon.json',
                       help='Nonce lexicon file')
    parser.add_argument('--output', type=str, default='stimuli_tokenization_matched.json',
                       help='Output file')
    parser.add_argument('--tokenizer', type=str, default='gpt2',
                       choices=['gpt2', 'pythia'],
                       help='Tokenizer to match (gpt2 or pythia)')

    args = parser.parse_args()

    generate_full_stimulus_set(
        source_file=args.source,
        lexicon_file=args.lexicon,
        output_file=args.output,
        tokenizer_name=args.tokenizer
    )
