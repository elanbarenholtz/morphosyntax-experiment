"""
Comprehensive verification of tokenization matching across full dataset.

Sanity checks:
1. Match rate: % of sentences with exact full-token-count match
2. Position-by-position verification: histogram of token counts per position
"""

import json
import numpy as np
from transformers import AutoTokenizer
from collections import defaultdict, Counter

def verify_full_dataset(stimuli_file='stimuli_context_matched.json', tokenizer_name='gpt2'):
    """
    Verify tokenization matching across entire dataset.
    """
    print("=" * 80)
    print("FULL DATASET TOKENIZATION VERIFICATION")
    print("=" * 80)

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"\nLoaded {len(stimuli)} stimulus sets")
    print(f"Tokenizer: {tokenizer_name}\n")

    # ========================================================================
    # SANITY CHECK 1: Match rate across entire dataset
    # ========================================================================
    print("=" * 80)
    print("SANITY CHECK 1: Full-Text Token Count Matching")
    print("=" * 80)

    conditions_to_check = [
        ('sentence', 'jabberwocky_matched', 'Sentence vs Jabberwocky'),
        ('sentence', 'word_list_real', 'Sentence vs Word List (Real)'),
        ('sentence', 'skeleton_function_words', 'Sentence vs Skeleton'),
        ('word_list_nonce_1tok', 'word_list_nonce_2tok', '1-tok vs 2-tok Nonces'),
    ]

    for cond1, cond2, label in conditions_to_check:
        exact_matches = 0
        mismatches = []

        for item in stimuli:
            if cond1 in item and cond2 in item:
                text1 = item[cond1]
                text2 = item[cond2]

                toks1 = len(tokenizer.encode(text1, add_special_tokens=False))
                toks2 = len(tokenizer.encode(text2, add_special_tokens=False))

                if toks1 == toks2:
                    exact_matches += 1
                else:
                    mismatches.append(abs(toks1 - toks2))

        total = len([s for s in stimuli if cond1 in s and cond2 in s])
        match_rate = 100 * exact_matches / total if total > 0 else 0

        print(f"\n{label}:")
        print(f"  Exact matches: {exact_matches}/{total} ({match_rate:.1f}%)")

        if mismatches:
            print(f"  Mismatches: {len(mismatches)}")
            print(f"  Mismatch distribution: {Counter(mismatches)}")
            print(f"  Max mismatch: {max(mismatches)} tokens")
            print(f"  Mean mismatch: {np.mean(mismatches):.2f} tokens")
        else:
            print(f"  ✓ PERFECT: All stimuli match!")

    # ========================================================================
    # SANITY CHECK 2: Position-by-position token count verification
    # ========================================================================
    print("\n" + "=" * 80)
    print("SANITY CHECK 2: Position-by-Position Token Count Verification")
    print("=" * 80)

    print("\nComparing: Sentence vs Jabberwocky")
    print("-" * 80)

    # Collect token counts by position
    position_data = defaultdict(lambda: {'sentence': [], 'jabberwocky': []})
    max_positions = 0

    for item in stimuli:
        if 'sentence' in item and 'jabberwocky_matched' in item:
            sent_words = item['sentence'].split()
            jab_words = item['jabberwocky_matched'].split()

            max_positions = max(max_positions, len(sent_words), len(jab_words))

            # Count tokens per position (in context)
            for i, word in enumerate(sent_words):
                if i == 0:
                    n_toks = len(tokenizer.encode(word, add_special_tokens=False))
                else:
                    n_toks = len(tokenizer.encode(' ' + word, add_special_tokens=False))
                position_data[i]['sentence'].append(n_toks)

            for i, word in enumerate(jab_words):
                if i == 0:
                    n_toks = len(tokenizer.encode(word, add_special_tokens=False))
                else:
                    n_toks = len(tokenizer.encode(' ' + word, add_special_tokens=False))
                position_data[i]['jabberwocky'].append(n_toks)

    # Analyze each position
    print(f"\n{'Pos':>3} | {'N':>3} | {'Sent Tok Dist':20s} | {'Jab Tok Dist':20s} | {'Match?':7s}")
    print("-" * 80)

    all_positions_match = True

    for pos in range(max_positions):
        if pos in position_data:
            sent_counts = position_data[pos]['sentence']
            jab_counts = position_data[pos]['jabberwocky']

            if sent_counts and jab_counts:
                n_samples = min(len(sent_counts), len(jab_counts))

                # Get distribution
                sent_dist = Counter(sent_counts)
                jab_dist = Counter(jab_counts)

                # Format distributions
                sent_str = ', '.join(f"{k}:{v}" for k, v in sorted(sent_dist.items()))
                jab_str = ', '.join(f"{k}:{v}" for k, v in sorted(jab_dist.items()))

                # Check if distributions match
                match = (sent_dist == jab_dist)
                match_str = '✓' if match else '✗'

                if not match:
                    all_positions_match = False

                print(f"{pos:3d} | {n_samples:3d} | {sent_str:20s} | {jab_str:20s} | {match_str:7s}")

    if all_positions_match:
        print("\n✓ PERFECT: All positions have matching token count distributions!")
    else:
        print("\n⚠️  Some positions have mismatched distributions")

    # ========================================================================
    # DETAILED ANALYSIS: Show examples of mismatches if any
    # ========================================================================
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS: Examples of Any Mismatches")
    print("=" * 80)

    mismatch_examples = []

    for item in stimuli:
        if 'sentence' in item and 'jabberwocky_matched' in item:
            sent = item['sentence']
            jab = item['jabberwocky_matched']

            sent_toks = len(tokenizer.encode(sent, add_special_tokens=False))
            jab_toks = len(tokenizer.encode(jab, add_special_tokens=False))

            if sent_toks != jab_toks:
                mismatch_examples.append({
                    'set_id': item['set_id'],
                    'sentence': sent,
                    'jabberwocky': jab,
                    'sent_toks': sent_toks,
                    'jab_toks': jab_toks,
                    'diff': abs(sent_toks - jab_toks)
                })

    if mismatch_examples:
        print(f"\nFound {len(mismatch_examples)} mismatched stimulus sets:\n")
        for ex in mismatch_examples[:5]:  # Show first 5
            print(f"Set {ex['set_id']}:")
            print(f"  Sentence:     \"{ex['sentence']}\"")
            print(f"  Jabberwocky:  \"{ex['jabberwocky']}\"")
            print(f"  Tokens: {ex['sent_toks']} vs {ex['jab_toks']} (diff: {ex['diff']})")
            print()

        if len(mismatch_examples) > 5:
            print(f"... and {len(mismatch_examples) - 5} more")
    else:
        print("\n✓ NO MISMATCHES FOUND - All stimuli have perfect token count matching!")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    # Check sentence vs jabberwocky
    sent_jab_matches = sum(1 for item in stimuli
                           if 'sentence' in item and 'jabberwocky_matched' in item
                           and len(tokenizer.encode(item['sentence'], add_special_tokens=False))
                           == len(tokenizer.encode(item['jabberwocky_matched'], add_special_tokens=False)))
    sent_jab_total = sum(1 for item in stimuli if 'sentence' in item and 'jabberwocky_matched' in item)

    print(f"\nKey Finding: Sentence vs Jabberwocky Matching")
    print(f"  {sent_jab_matches}/{sent_jab_total} exact matches ({100*sent_jab_matches/sent_jab_total:.1f}%)")

    if sent_jab_matches == sent_jab_total:
        print(f"  ✓✓✓ EXCELLENT: Perfect matching across entire dataset!")
    elif sent_jab_matches / sent_jab_total >= 0.95:
        print(f"  ✓ GOOD: >95% match rate")
    else:
        print(f"  ⚠️  WARNING: Substantial mismatches remain")

    print("\n" + "=" * 80)

    return {
        'match_rate': sent_jab_matches / sent_jab_total if sent_jab_total > 0 else 0,
        'mismatches': len(mismatch_examples),
        'position_match': all_positions_match
    }

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Verify tokenization matching across full dataset')
    parser.add_argument('--stimuli', type=str, default='stimuli_context_matched.json',
                       help='Stimuli file to verify')
    parser.add_argument('--tokenizer', type=str, default='gpt2',
                       help='Tokenizer to use (gpt2 or EleutherAI/pythia-410m)')

    args = parser.parse_args()

    results = verify_full_dataset(args.stimuli, args.tokenizer)
