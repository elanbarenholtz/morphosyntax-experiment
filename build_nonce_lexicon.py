"""
Build a tokenization-matched nonce lexicon.

Generates 50k nonce words and organizes them by subtoken count
for both GPT-2 and Pythia tokenizers.
"""

import json
import random
import string
from collections import defaultdict
from transformers import AutoTokenizer
from tqdm import tqdm

# Phonotactic patterns for English-like nonce words
ONSETS = ['', 'b', 'p', 't', 'd', 'k', 'g', 'f', 'v', 's', 'z', 'sh', 'ch', 'j',
          'th', 'm', 'n', 'l', 'r', 'w', 'y', 'h',
          'bl', 'br', 'pl', 'pr', 'tr', 'dr', 'kr', 'gr', 'fl', 'fr', 'sl', 'sm',
          'sn', 'sp', 'st', 'sk', 'sw', 'kw', 'skr', 'spr', 'str', 'thr', 'shr']

NUCLEI = ['a', 'e', 'i', 'o', 'u', 'ee', 'oo', 'ai', 'ay', 'ey', 'oi', 'oy',
          'ou', 'ow', 'ie', 'ea', 'oa']

CODAS = ['', 'p', 't', 'k', 'b', 'd', 'g', 'f', 'v', 's', 'z', 'sh', 'ch', 'j',
         'm', 'n', 'ng', 'l', 'r',
         'mp', 'nt', 'nk', 'nd', 'ng', 'st', 'sk', 'sp', 'ft', 'pt', 'kt',
         'lp', 'lt', 'lk', 'rp', 'rt', 'rk', 'lm', 'rm', 'ln', 'rn']

def generate_syllable():
    """Generate a single syllable."""
    onset = random.choice(ONSETS)
    nucleus = random.choice(NUCLEI)
    coda = random.choice(CODAS)
    return onset + nucleus + coda

def generate_nonce_word(min_syllables=1, max_syllables=3):
    """Generate a phonotactically plausible nonce word."""
    n_syllables = random.randint(min_syllables, max_syllables)
    syllables = [generate_syllable() for _ in range(n_syllables)]
    word = ''.join(syllables)

    # Simplify some clusters
    word = word.replace('shsh', 'sh')
    word = word.replace('chch', 'ch')
    word = word.replace('thth', 'th')
    word = word.replace('ngng', 'ng')

    return word

def count_subtokens(word, tokenizer):
    """Count how many subtokens a word produces."""
    tokens = tokenizer.encode(word, add_special_tokens=False)
    return len(tokens)

def build_lexicon(n_candidates=50000, output_file='nonce_lexicon.json'):
    """
    Build a large nonce lexicon organized by subtoken count.

    Returns dict with structure:
    {
        'gpt2': {
            '1': ['word1', 'word2', ...],
            '2': ['word3', 'word4', ...],
            ...
        },
        'pythia': {
            '1': [...],
            '2': [...],
            ...
        },
        'metadata': {
            'n_candidates': 50000,
            'distribution_gpt2': {1: 1234, 2: 5678, ...},
            'distribution_pythia': {1: 1245, 2: 5621, ...}
        }
    }
    """
    print("=" * 80)
    print("BUILDING TOKENIZATION-MATCHED NONCE LEXICON")
    print("=" * 80)
    print(f"\nGenerating {n_candidates:,} nonce candidates...")

    # Load tokenizers
    print("\nLoading tokenizers...")
    tokenizers = {
        'gpt2': AutoTokenizer.from_pretrained('gpt2'),
        'pythia': AutoTokenizer.from_pretrained('EleutherAI/pythia-410m')
    }

    # Generate candidates (all lowercase for normalization)
    print("\nGenerating nonce words...")
    candidates = set()

    pbar = tqdm(total=n_candidates, desc="Generating unique nonces")
    while len(candidates) < n_candidates:
        word = generate_nonce_word(min_syllables=1, max_syllables=3)
        word = word.lower()  # Normalize to lowercase
        if word and len(word) >= 3:  # Minimum length requirement
            candidates.add(word)
            pbar.update(1)
    pbar.close()

    candidates = list(candidates)

    # Organize by subtoken count for each tokenizer
    # IMPORTANT: Use in-context tokenization (with leading space) for non-initial positions
    lexicon = {
        'gpt2': defaultdict(list),
        'pythia': defaultdict(list),
        'metadata': {
            'n_candidates': len(candidates),
            'distribution_gpt2': defaultdict(int),
            'distribution_pythia': defaultdict(int),
            'note': 'Subtoken counts are for in-context tokenization (with leading space)'
        }
    }

    print("\nComputing in-context subtoken counts (with leading space)...")
    for word in tqdm(candidates, desc="Tokenizing"):
        for tok_name, tokenizer in tokenizers.items():
            # Count subtokens with leading space (for non-initial positions)
            n_subtokens = count_subtokens(" " + word, tokenizer)
            lexicon[tok_name][str(n_subtokens)].append(word)
            lexicon['metadata'][f'distribution_{tok_name}'][n_subtokens] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    lexicon['gpt2'] = dict(lexicon['gpt2'])
    lexicon['pythia'] = dict(lexicon['pythia'])
    lexicon['metadata']['distribution_gpt2'] = dict(lexicon['metadata']['distribution_gpt2'])
    lexicon['metadata']['distribution_pythia'] = dict(lexicon['metadata']['distribution_pythia'])

    # Save lexicon
    print(f"\nSaving lexicon to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(lexicon, f, indent=2)

    # Print statistics
    print("\n" + "=" * 80)
    print("LEXICON STATISTICS")
    print("=" * 80)

    for tok_name in ['gpt2', 'pythia']:
        print(f"\n{tok_name.upper()}:")
        print(f"{'Subtokens':>12} | {'Count':>10} | {'Percentage':>10}")
        print("-" * 40)

        dist = lexicon['metadata'][f'distribution_{tok_name}']
        total = sum(dist.values())

        for n_subtokens in sorted(dist.keys()):
            count = dist[n_subtokens]
            pct = 100 * count / total
            print(f"{n_subtokens:12} | {count:10,} | {pct:9.2f}%")

        print(f"{'Total':>12} | {total:10,} | {100.0:9.2f}%")

    print("\n" + "=" * 80)
    print("SAMPLE WORDS BY SUBTOKEN COUNT (GPT-2)")
    print("=" * 80)

    for n in sorted([int(k) for k in lexicon['gpt2'].keys()])[:5]:
        words = lexicon['gpt2'][str(n)]
        sample = random.sample(words, min(10, len(words)))
        print(f"\n{n} subtoken(s): {', '.join(sample)}")

    print("\n" + "=" * 80)
    print("Lexicon building complete!")
    print("=" * 80)

    return lexicon

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build tokenization-matched nonce lexicon')
    parser.add_argument('--n-candidates', type=int, default=50000,
                       help='Number of nonce words to generate (default: 50000)')
    parser.add_argument('--output', type=str, default='nonce_lexicon.json',
                       help='Output file path (default: nonce_lexicon.json)')

    args = parser.parse_args()

    build_lexicon(n_candidates=args.n_candidates, output_file=args.output)
