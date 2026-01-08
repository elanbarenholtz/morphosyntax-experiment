"""
Add scrambled_jabberwocky condition to stimuli.

Takes the existing jabberwocky_matched condition and creates a scrambled version
with the same words in random order. This provides the cleanest test of
syntactic structure contribution:

- jabberwocky_matched: "the lift was bud the rays to the mask rug"
- scrambled_jabberwocky: "rays bud mask the to the rug was lift the"

Controls:
✓ Identical lexical items
✓ Identical tokenization (same words → same tokens)
✓ Only difference is syntactic ordering
"""

import json
import random
from copy import deepcopy

def scramble_text(text, seed=None):
    """
    Scramble words in text while preserving word boundaries.

    Args:
        text: Space-delimited text to scramble
        seed: Random seed for reproducibility

    Returns:
        Scrambled text with same words in random order
    """
    if seed is not None:
        random.seed(seed)

    words = text.split()
    scrambled_words = words.copy()
    random.shuffle(scrambled_words)

    # Ensure it's actually different from original
    # (in rare cases shuffle might return same order)
    max_attempts = 10
    attempts = 0
    while scrambled_words == words and attempts < max_attempts:
        random.shuffle(scrambled_words)
        attempts += 1

    return ' '.join(scrambled_words)

def add_scrambled_jabberwocky(input_file='stimuli_context_matched.json',
                               output_file='stimuli_with_scrambled.json'):
    """
    Add scrambled_jabberwocky condition to existing stimuli.
    """
    print("=" * 80)
    print("ADDING SCRAMBLED JABBERWOCKY CONDITION")
    print("=" * 80)

    # Load existing stimuli
    with open(input_file, 'r') as f:
        stimuli = json.load(f)

    print(f"\nLoaded {len(stimuli)} stimulus sets from {input_file}")

    # Add scrambled_jabberwocky to each set
    for item in stimuli:
        if 'jabberwocky_matched' in item:
            # Use set_id as seed for reproducibility
            scrambled = scramble_text(item['jabberwocky_matched'], seed=item['set_id'])
            item['scrambled_jabberwocky'] = scrambled

    # Save updated stimuli
    with open(output_file, 'w') as f:
        json.dump(stimuli, f, indent=2)

    print(f"\nAdded scrambled_jabberwocky to all {len(stimuli)} sets")
    print(f"Saved to: {output_file}")

    # Show examples
    print("\n" + "=" * 80)
    print("EXAMPLES (first 5 sets)")
    print("=" * 80)

    for item in stimuli[:5]:
        print(f"\nSet {item['set_id']}:")
        print(f"  Original:  \"{item['jabberwocky_matched']}\"")
        print(f"  Scrambled: \"{item['scrambled_jabberwocky']}\"")

        # Verify same words
        orig_words = sorted(item['jabberwocky_matched'].split())
        scram_words = sorted(item['scrambled_jabberwocky'].split())
        if orig_words == scram_words:
            print(f"  ✓ Same words, different order")
        else:
            print(f"  ✗ ERROR: Words don't match!")

    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Verify all sets have same words
    all_match = True
    for item in stimuli:
        orig_words = sorted(item['jabberwocky_matched'].split())
        scram_words = sorted(item['scrambled_jabberwocky'].split())
        if orig_words != scram_words:
            print(f"ERROR in set {item['set_id']}: Words don't match!")
            all_match = False

    if all_match:
        print(f"✓ All {len(stimuli)} sets verified: scrambled uses same words")

    print("\n" + "=" * 80)
    print(f"Complete! Updated stimuli saved to: {output_file}")
    print("=" * 80)

    return stimuli

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Add scrambled_jabberwocky condition')
    parser.add_argument('--input', type=str, default='stimuli_context_matched.json',
                       help='Input stimuli file')
    parser.add_argument('--output', type=str, default='stimuli_with_scrambled.json',
                       help='Output stimuli file')

    args = parser.parse_args()

    add_scrambled_jabberwocky(args.input, args.output)
