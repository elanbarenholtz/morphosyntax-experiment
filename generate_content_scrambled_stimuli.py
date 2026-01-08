#!/usr/bin/env python3
"""
Generate CONTENT-SCRAMBLED JABBERWOCKY stimuli.

Preserves function-word skeleton (including "to" position) while
shuffling only content words. This ensures:
- Matched n (30/30 "to" instances)
- Comparable cue contexts
- Clean test of content sequencing vs syntactic skeleton
"""

import json
import random
import hashlib

# Load existing stimuli
with open('stimuli_infinitival_to.json', 'r') as f:
    stimuli = json.load(f)

# Function words to preserve (never shuffle these)
FUNCTION_WORDS = {
    # Determiners
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    # Prepositions
    'to', 'at', 'in', 'on', 'with', 'from', 'of', 'for', 'by',
    # Conjunctions
    'and', 'or', 'but', 'so', 'if', 'because',
    # Auxiliaries/modals
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had',
    'do', 'does', 'did',
    'will', 'would', 'can', 'could', 'shall', 'should', 'may', 'might', 'must',
    # Common verbs that are function-like in these stimuli
    'decided', 'wanted', 'began', 'tried', 'planned', 'continued',
}

def identify_content_positions(words):
    """
    Identify which word positions are content (to be scrambled)
    vs function (to be preserved).

    Returns:
        content_positions: list of (index, word) tuples for content words
        function_template: list of (index, word) for function words or None for content slots
    """
    content_positions = []
    function_template = []

    for i, word in enumerate(words):
        word_clean = word.lower().strip('.,!?;:')

        if word_clean in FUNCTION_WORDS:
            # Function word - preserve position
            function_template.append((i, word))
        else:
            # Content word - will be scrambled
            content_positions.append((i, word))
            function_template.append((i, None))  # Placeholder for content

    return content_positions, function_template

def content_scramble(sentence, seed):
    """
    Scramble only content words, preserving function word skeleton.

    Args:
        sentence: input sentence string
        seed: deterministic seed for reproducibility

    Returns:
        scrambled: sentence with content words shuffled
        permutation: list showing how content words were reordered
    """
    words = sentence.split()

    # Identify content vs function positions
    content_positions, function_template = identify_content_positions(words)

    # Extract content words
    content_words = [word for idx, word in content_positions]

    # Shuffle content words (deterministically using seed)
    random.seed(seed)
    shuffled_content = content_words.copy()
    random.shuffle(shuffled_content)

    # Ensure actually different from original
    attempts = 0
    while shuffled_content == content_words and len(content_words) > 1 and attempts < 10:
        random.shuffle(shuffled_content)
        attempts += 1

    # Create permutation record
    permutation = []
    for orig, shuffled in zip(content_words, shuffled_content):
        permutation.append(f"{orig}→{shuffled}")

    # Reconstruct sentence with shuffled content
    result_words = []
    content_idx = 0

    for i, (pos, func_word) in enumerate(function_template):
        if func_word is None:
            # Content position - insert shuffled content word
            result_words.append(shuffled_content[content_idx])
            content_idx += 1
        else:
            # Function position - keep original
            result_words.append(func_word)

    return ' '.join(result_words), permutation

def generate_content_scrambled_stimuli():
    """Generate content-scrambled versions of all Jabberwocky stimuli."""

    output_stimuli = []

    print("=" * 80)
    print("GENERATING CONTENT-SCRAMBLED JABBERWOCKY STIMULI")
    print("=" * 80)
    print("\nPreserving function-word skeleton, shuffling only content words...")
    print()

    for stim in stimuli:
        set_id = stim['set_id']
        jabberwocky = stim['jabberwocky_matched']

        # Create deterministic seed from set_id
        seed_string = f"content_scramble_{set_id}"
        seed = int(hashlib.md5(seed_string.encode()).hexdigest()[:8], 16)

        # Generate content-scrambled version
        content_scrambled, permutation = content_scramble(jabberwocky, seed)

        # Sanity checks
        jab_words = jabberwocky.split()
        scram_words = content_scrambled.split()

        assert len(jab_words) == len(scram_words), \
            f"Set {set_id}: Word count mismatch!"

        # Check "to" position preserved
        jab_to_positions = [i for i, w in enumerate(jab_words) if w.lower() == 'to']
        scram_to_positions = [i for i, w in enumerate(scram_words) if w.lower() == 'to']

        assert jab_to_positions == scram_to_positions, \
            f"Set {set_id}: 'to' position changed! {jab_to_positions} vs {scram_to_positions}"

        # Create output record
        output_stim = {
            'set_id': set_id,
            'sentence': stim['sentence'],
            'jabberwocky_matched': jabberwocky,
            'content_scrambled_jabberwocky': content_scrambled,
            'scramble_seed': seed,
            'content_permutation': permutation,
            'template_type': stim['template_type'],
            'content_words_replaced': stim['content_words_replaced']
        }

        output_stimuli.append(output_stim)

        # Show examples
        if set_id <= 3 or set_id % 10 == 0:
            print(f"Set {set_id}:")
            print(f"  Jabberwocky:     {jabberwocky}")
            print(f"  Content-scrambled: {content_scrambled}")
            print(f"  Permutation:     {', '.join(permutation)}")
            print()

    return output_stimuli

def main():
    # Generate stimuli
    output_stimuli = generate_content_scrambled_stimuli()

    # Save to JSON
    output_file = 'stimuli_content_scrambled.json'
    with open(output_file, 'w') as f:
        json.dump(output_stimuli, f, indent=2)

    print("=" * 80)
    print("SANITY CHECKS")
    print("=" * 80)
    print()

    # Count "to" instances in each condition
    to_count_jab = 0
    to_count_scram = 0

    for stim in output_stimuli:
        jab_words = stim['jabberwocky_matched'].split()
        scram_words = stim['content_scrambled_jabberwocky'].split()

        to_count_jab += sum(1 for w in jab_words if w.lower() == 'to')
        to_count_scram += sum(1 for w in scram_words if w.lower() == 'to')

    print(f"✓ Generated {len(output_stimuli)} stimulus sets")
    print(f"✓ Jabberwocky 'to' instances: {to_count_jab}")
    print(f"✓ Content-scrambled 'to' instances: {to_count_scram}")

    assert to_count_jab == to_count_scram, "'to' counts don't match!"
    assert to_count_jab == 30, f"Expected 30 'to' instances, got {to_count_jab}"

    print(f"✓ MATCHED n=30 in both conditions!")
    print()
    print(f"✓ Saved to: {output_file}")
    print()
    print("=" * 80)
    print("READY FOR MORPHOSYNTAX AUDIT")
    print("=" * 80)
    print()
    print("Next step: Run audit comparing:")
    print("  1. SENTENCE")
    print("  2. JABBERWOCKY_MATCHED")
    print("  3. CONTENT_SCRAMBLED_JABBERWOCKY")
    print()
    print("Expected result:")
    print("  - JABBERWOCKY > CONTENT_SCRAMBLED (if sequencing matters)")
    print("  - OR ~equal (if only function skeleton matters)")

if __name__ == '__main__':
    main()
