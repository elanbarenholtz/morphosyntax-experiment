"""
Analyze the constructed stimuli for potential confounds.
Check vocabulary size, repetition, token counts, etc.
"""

import json
import numpy as np
from collections import Counter
import re

def load_stimuli(filename='stimuli.json'):
    """Load stimuli."""
    with open(filename, 'r') as f:
        return json.load(f)

def extract_words(text):
    """Extract words from text."""
    # Split on whitespace and remove punctuation
    words = re.findall(r'\b\w+\b', text.lower())
    return words

def analyze_vocabulary(stimuli):
    """Analyze vocabulary size and repetition in each condition."""

    print("\n" + "=" * 80)
    print("VOCABULARY ANALYSIS")
    print("=" * 80)

    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        print(f"\n{'*' * 80}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'*' * 80}\n")

        all_words = []
        word_counts_per_stim = []

        # Collect all words from this condition
        for stim in stimuli:
            words = extract_words(stim[condition])
            all_words.extend(words)
            word_counts_per_stim.append(len(words))

        # Count occurrences
        word_counts = Counter(all_words)

        # Statistics
        total_tokens = len(all_words)
        unique_words = len(word_counts)
        type_token_ratio = unique_words / total_tokens if total_tokens > 0 else 0

        print(f"Total tokens: {total_tokens}")
        print(f"Unique words (types): {unique_words}")
        print(f"Type-token ratio: {type_token_ratio:.3f}")
        print(f"Mean words per stimulus: {np.mean(word_counts_per_stim):.2f} ± {np.std(word_counts_per_stim):.2f}")

        # Most common words
        print(f"\nTop 20 most frequent words:")
        print(f"{'Rank':>4} | {'Word':20} | {'Count':>6} | {'Freq':>7}")
        print("-" * 50)
        for rank, (word, count) in enumerate(word_counts.most_common(20), 1):
            freq = count / total_tokens
            print(f"{rank:4} | {word:20} | {count:6} | {freq:7.3f}")

        # Check for extreme repetition
        max_count = max(word_counts.values())
        max_freq = max_count / total_tokens
        most_repeated = [w for w, c in word_counts.items() if c == max_count]

        print(f"\nMost repeated word(s): {most_repeated}")
        print(f"Appears {max_count} times ({max_freq:.1%} of all tokens)")

def compare_content_words(stimuli):
    """Compare content words vs function words in each condition."""

    print("\n\n" + "=" * 80)
    print("CONTENT vs FUNCTION WORD ANALYSIS")
    print("=" * 80)

    # Common function words
    function_words = {
        'the', 'a', 'an', 'is', 'was', 'are', 'were', 'to', 'of', 'in', 'on', 'at',
        'by', 'for', 'with', 'from', 'through', 'that', 'this', 'and', 'but', 'or',
        'if', 'when', 'while', 'as', 'very', 'so', 'too', 'not', 'have', 'has', 'had',
        'will', 'would', 'could', 'should', 'can', 'may', 'might', 'their', 'her', 'his'
    }

    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        print(f"\n{condition.upper()}:")

        all_words = []
        for stim in stimuli:
            words = extract_words(stim[condition])
            all_words.extend(words)

        # Separate function and content words
        func_words = [w for w in all_words if w in function_words]
        content_words = [w for w in all_words if w not in function_words]

        # Count unique
        unique_func = len(set(func_words))
        unique_content = len(set(content_words))

        print(f"  Function word tokens: {len(func_words)} ({len(func_words)/len(all_words):.1%})")
        print(f"  Content word tokens: {len(content_words)} ({len(content_words)/len(all_words):.1%})")
        print(f"  Unique function words: {unique_func}")
        print(f"  Unique content words: {unique_content}")

        if content_words:
            content_counter = Counter(content_words)
            print(f"  Content word type-token ratio: {unique_content / len(content_words):.3f}")
            print(f"  Most common content words: {content_counter.most_common(5)}")

def check_nonword_reuse(stimuli):
    """Check if same nonwords are reused across stimuli."""

    print("\n\n" + "=" * 80)
    print("NONWORD REUSE ANALYSIS")
    print("=" * 80)

    # Define what we know are nonwords (from the generation script)
    known_nonwords = {
        'blicket', 'wuggle', 'wuggles', 'daxen', 'plonk', 'zorf', 'mip', 'gleb',
        'snorf', 'prock', 'flib', 'blimp', 'trell', 'sprock', 'grint',
        'flurn', 'plib', 'skeff', 'trock', 'verm', 'whiff', 'yalp', 'zink',
        'florp', 'florping', 'florped', 'florps', 'tamp', 'tamped', 'tamps', 'tamping',
        'grent', 'grentily', 'borp', 'sken', 'pliff', 'dwel', 'kreb', 'sniv',
        'vork', 'whisp', 'yalm', 'zomp', 'bliv', 'kren', 'prav', 'screll', 'teff', 'vren',
        'flimp', 'grofly', 'plonken', 'bren', 'drell', 'geff', 'klim', 'plov',
        'shill', 'tren', 'veff', 'whill', 'yeff', 'zell', 'brell', 'cleff', 'driv',
        'fleff', 'grell', 'keff', 'blickets', 'daxens', 'globs'
    }

    for condition in ['jabberwocky', 'stripped', 'nonwords']:
        print(f"\n{condition.upper()}:")

        all_words = []
        for stim in stimuli:
            words = extract_words(stim[condition])
            all_words.extend(words)

        # Filter to likely nonwords (not function words)
        function_words = {'the', 'a', 'was', 'to', 'in', 'on', 'of', 'is', 'are', 'were',
                         'with', 'from', 'by', 'at', 'that', 'this', 'very', 'ke', 'na', 'nar',
                         'po', 'ko', 'ne', 'fe', 'le', 've', 'pe', 'mo', 'so', 'ze', 'zi',
                         'en', 'ba', 'ro', 'gi', 'we', 'wi', 'da', 'vo', 'tu', 'no', 'ha',
                         'wu', 'ku', 'shu', 'ka', 'ma', 'mi', 'sho', 'ho', 'qui'}

        potential_nonwords = [w for w in all_words if w not in function_words]

        nonword_counts = Counter(potential_nonwords)

        total_nonword_tokens = len(potential_nonwords)
        unique_nonwords = len(nonword_counts)

        print(f"  Total nonword tokens: {total_nonword_tokens}")
        print(f"  Unique nonwords: {unique_nonwords}")
        print(f"  Type-token ratio: {unique_nonwords / total_nonword_tokens:.3f}")

        print(f"\n  Top 15 most repeated nonwords:")
        print(f"  {'Rank':>4} | {'Nonword':15} | {'Count':>6} | {'% of tokens':>12}")
        print("  " + "-" * 50)
        for rank, (word, count) in enumerate(nonword_counts.most_common(15), 1):
            pct = count / total_nonword_tokens * 100
            print(f"  {rank:4} | {word:15} | {count:6} | {pct:11.1f}%")

def analyze_sentence_structure(stimuli):
    """Analyze if sentences have consistent structure that might affect predictability."""

    print("\n\n" + "=" * 80)
    print("SENTENCE STRUCTURE ANALYSIS")
    print("=" * 80)

    print("\nFirst 5 stimuli across conditions:")
    print("-" * 80)

    for i, stim in enumerate(stimuli[:5], 1):
        print(f"\nSet {i}:")
        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
            print(f"  {condition:12}: {stim[condition]}")

def main():
    """Run all analyses."""
    stimuli = load_stimuli()

    print("=" * 80)
    print("STIMULI ANALYSIS - CHECKING FOR CONFOUNDS")
    print("=" * 80)
    print(f"\nAnalyzing {len(stimuli)} stimulus sets\n")

    # Run analyses
    analyze_vocabulary(stimuli)
    compare_content_words(stimuli)
    check_nonword_reuse(stimuli)
    analyze_sentence_structure(stimuli)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
