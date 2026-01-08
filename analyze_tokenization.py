"""
Comprehensive tokenization analysis across all conditions.
Checks for tokenization confounds that could affect entropy measurements.
"""

import json
import numpy as np
import pandas as pd
from transformers import AutoTokenizer
from collections import defaultdict

def analyze_tokenization_per_text(tokenizer, text):
    """
    Analyze tokenization for a single text string.

    Returns dict with:
    - n_tokens_total: total BPE tokens
    - n_words_whitespace: number of whitespace-delimited words
    - tokens_per_word: n_tokens_total / n_words_whitespace
    - subtokens_per_word_list: list of subtoken counts for each word
    """
    # Tokenize the full text
    tokens = tokenizer.encode(text, add_special_tokens=False)
    n_tokens_total = len(tokens)

    # Count whitespace words
    words = text.split()
    n_words_whitespace = len(words)

    # Analyze subtokens per word
    subtokens_per_word = []
    for word in words:
        word_tokens = tokenizer.encode(word, add_special_tokens=False)
        subtokens_per_word.append(len(word_tokens))

    return {
        'n_tokens_total': n_tokens_total,
        'n_words_whitespace': n_words_whitespace,
        'tokens_per_word': n_tokens_total / n_words_whitespace if n_words_whitespace > 0 else 0,
        'subtokens_per_word_list': subtokens_per_word,
        'subtokens_min': min(subtokens_per_word) if subtokens_per_word else 0,
        'subtokens_max': max(subtokens_per_word) if subtokens_per_word else 0,
        'subtokens_mean': np.mean(subtokens_per_word) if subtokens_per_word else 0
    }

def analyze_condition(tokenizer, tokenizer_name, stimuli, condition):
    """Analyze all texts in a single condition."""
    results = []

    for stim in stimuli:
        if condition not in stim:
            continue
        text = stim[condition]
        analysis = analyze_tokenization_per_text(tokenizer, text)
        analysis['set_id'] = stim['set_id']
        results.append(analysis)

    return results

def print_condition_summary(condition, results):
    """Print summary statistics for a condition."""
    n_tokens = [r['n_tokens_total'] for r in results]
    n_words = [r['n_words_whitespace'] for r in results]
    tpw = [r['tokens_per_word'] for r in results]
    subtoken_means = [r['subtokens_mean'] for r in results]
    subtoken_maxs = [r['subtokens_max'] for r in results]

    print(f"\n{condition.upper()}")
    print(f"  n_tokens_total:        {np.mean(n_tokens):.2f} ± {np.std(n_tokens):.2f} (range: {min(n_tokens)}-{max(n_tokens)})")
    print(f"  n_words_whitespace:    {np.mean(n_words):.2f} ± {np.std(n_words):.2f} (range: {min(n_words)}-{max(n_words)})")
    print(f"  tokens_per_word:       {np.mean(tpw):.2f} ± {np.std(tpw):.2f}")
    print(f"  subtokens_per_word (mean): {np.mean(subtoken_means):.2f} ± {np.std(subtoken_means):.2f}")
    print(f"  subtokens_per_word (max):  {np.mean(subtoken_maxs):.2f} ± {np.std(subtoken_maxs):.2f}")

def main(stimuli_file='stimuli_6conditions.json'):
    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print("="*80)
    print("TOKENIZATION ANALYSIS ACROSS CONDITIONS")
    print("="*80)

    # Analyze with both tokenizers
    tokenizers = {
        'gpt2': AutoTokenizer.from_pretrained('gpt2'),
        'pythia': AutoTokenizer.from_pretrained('EleutherAI/pythia-410m')
    }

    conditions = ['sentence', 'jabberwocky', 'stripped', 'nonwords',
                  'scrambled_jabberwocky', 'swapped_function_words']

    all_summaries = {}

    for tok_name, tokenizer in tokenizers.items():
        print(f"\n{'='*80}")
        print(f"TOKENIZER: {tok_name.upper()}")
        print(f"{'='*80}")

        condition_summaries = {}

        for condition in conditions:
            results = analyze_condition(tokenizer, tok_name, stimuli, condition)
            condition_summaries[condition] = results
            print_condition_summary(condition, results)

        all_summaries[tok_name] = condition_summaries

        # Create comparison table
        print(f"\n{'-'*80}")
        print(f"SUMMARY TABLE ({tok_name})")
        print(f"{'-'*80}")
        print(f"{'Condition':<25} | {'Tokens':>8} | {'Words':>7} | {'Tok/Word':>8} | {'Subtok/Word':>12}")
        print(f"{'-'*80}")

        for condition in conditions:
            results = condition_summaries[condition]
            n_tokens = np.mean([r['n_tokens_total'] for r in results])
            n_words = np.mean([r['n_words_whitespace'] for r in results])
            tpw = np.mean([r['tokens_per_word'] for r in results])
            stpw = np.mean([r['subtokens_mean'] for r in results])
            print(f"{condition:<25} | {n_tokens:8.2f} | {n_words:7.2f} | {tpw:8.2f} | {stpw:12.2f}")

    # Compare across conditions
    print(f"\n{'='*80}")
    print("CROSS-CONDITION COMPARISON")
    print(f"{'='*80}")

    for tok_name in ['gpt2', 'pythia']:
        print(f"\n{tok_name.upper()} - Pairwise differences in tokens_per_word:")

        summaries = all_summaries[tok_name]
        tpw_by_condition = {
            cond: np.mean([r['tokens_per_word'] for r in summaries[cond]])
            for cond in conditions
        }

        # Sort by tokens_per_word
        sorted_conds = sorted(tpw_by_condition.items(), key=lambda x: x[1])

        print(f"\nOrdered by tokens_per_word:")
        for cond, tpw in sorted_conds:
            print(f"  {cond:<25}: {tpw:.3f}")

        # Flag potential confounds
        max_tpw = max(tpw_by_condition.values())
        min_tpw = min(tpw_by_condition.values())
        difference = max_tpw - min_tpw

        print(f"\nMax - Min difference: {difference:.3f} tokens/word")
        if difference > 0.3:
            print("⚠️  WARNING: Substantial tokenization difference across conditions!")
            print("   This could confound entropy measurements.")
        else:
            print("✅ Tokenization relatively balanced across conditions")

    # Save detailed results
    print(f"\n{'='*80}")
    print("Saving detailed results...")

    for tok_name, summaries in all_summaries.items():
        # Flatten to DataFrame
        rows = []
        for condition, results in summaries.items():
            for r in results:
                rows.append({
                    'tokenizer': tok_name,
                    'condition': condition,
                    'set_id': r['set_id'],
                    'n_tokens_total': r['n_tokens_total'],
                    'n_words_whitespace': r['n_words_whitespace'],
                    'tokens_per_word': r['tokens_per_word'],
                    'subtokens_mean': r['subtokens_mean'],
                    'subtokens_min': r['subtokens_min'],
                    'subtokens_max': r['subtokens_max']
                })

        df = pd.DataFrame(rows)
        df.to_csv(f'tokenization_analysis_{tok_name}.csv', index=False)
        print(f"  Saved: tokenization_analysis_{tok_name}.csv")

    print(f"\n{'='*80}")
    print("Analysis complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Analyze tokenization across conditions')
    parser.add_argument('--input', type=str, default='stimuli_6conditions.json',
                       help='Input stimuli file (default: stimuli_6conditions.json)')
    args = parser.parse_args()
    main(stimuli_file=args.input)
