#!/usr/bin/env python3
"""
Generate comprehensive stimulus set with all 6 conditions:
1. SENTENCE (real English)
2. JABBERWOCKY (content→nonce, scaffold preserved)
3. FULL_SCRAMBLED (shuffle all words)
4. CONTENT_SCRAMBLED (shuffle content, preserve function)
5. FUNCTION_SCRAMBLED (shuffle function, preserve content) - NEW
6. CUE_DELETION (remove/replace critical cues) - NEW

This makes the analysis airtight by controlling for:
- Content ordering effects (via CONTENT_SCRAMBLED)
- Function skeleton necessity (via FUNCTION_SCRAMBLED)
- Specific cue necessity (via CUE_DELETION)
"""

import json
import random
import hashlib

# Load existing stimuli (base sentences + jabberwocky)
with open('stimuli_infinitival_to.json', 'r') as f:
    base_stimuli = json.load(f)

# Function words (never treated as content)
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
    # Control verbs (these act as function words in our stimuli)
    'decided', 'wanted', 'began', 'tried', 'planned', 'continued',
}

def identify_slots(words):
    """
    Identify function vs content word positions.

    Returns:
        function_slots: list of (index, word) for function words
        content_slots: list of (index, word) for content words
    """
    function_slots = []
    content_slots = []

    for i, word in enumerate(words):
        word_clean = word.lower().strip('.,!?;:')
        if word_clean in FUNCTION_WORDS:
            function_slots.append((i, word))
        else:
            content_slots.append((i, word))

    return function_slots, content_slots

def full_scramble(sentence, seed):
    """Shuffle all words."""
    words = sentence.split()
    random.seed(seed)
    shuffled = words.copy()
    random.shuffle(shuffled)

    # Ensure different from original
    attempts = 0
    while shuffled == words and len(words) > 1 and attempts < 10:
        random.shuffle(shuffled)
        attempts += 1

    return ' '.join(shuffled)

def content_scramble(sentence, seed):
    """Shuffle only content words, preserve function skeleton."""
    words = sentence.split()
    function_slots, content_slots = identify_slots(words)

    # Extract content words
    content_words = [word for idx, word in content_slots]

    # Shuffle content
    random.seed(seed)
    shuffled_content = content_words.copy()
    random.shuffle(shuffled_content)

    # Ensure different
    attempts = 0
    while shuffled_content == content_words and len(content_words) > 1 and attempts < 10:
        random.shuffle(shuffled_content)
        attempts += 1

    # Reconstruct sentence
    result = words.copy()
    content_idx = 0
    for idx, word in content_slots:
        result[idx] = shuffled_content[content_idx]
        content_idx += 1

    return ' '.join(result)

def function_scramble(sentence, seed):
    """
    Shuffle only function words among function positions, preserve content.

    This is the "dual" of content scramble and directly tests skeleton necessity.
    """
    words = sentence.split()
    function_slots, content_slots = identify_slots(words)

    # Extract function words
    function_words_list = [word for idx, word in function_slots]

    # Shuffle function words
    random.seed(seed)
    shuffled_function = function_words_list.copy()
    random.shuffle(shuffled_function)

    # Ensure different
    attempts = 0
    while shuffled_function == function_words_list and len(function_words_list) > 1 and attempts < 10:
        random.shuffle(shuffled_function)
        attempts += 1

    # Reconstruct sentence
    result = words.copy()
    function_idx = 0
    for idx, word in function_slots:
        result[idx] = shuffled_function[function_idx]
        function_idx += 1

    return ' '.join(result)

def cue_deletion(sentence, cue_word='to', replacement='ke'):
    """
    Replace critical cue with a nonce function word.

    This tests cue necessity: does removing/replacing 'to' eliminate the effect?
    """
    words = sentence.split()
    result = []

    for word in words:
        word_clean = word.lower().strip('.,!?;:')
        if word_clean == cue_word:
            result.append(replacement)
        else:
            result.append(word)

    return ' '.join(result)

def generate_comprehensive_stimuli():
    """Generate all 6 conditions for each base stimulus."""

    comprehensive_stimuli = []

    print("=" * 80)
    print("GENERATING COMPREHENSIVE STIMULUS SET")
    print("=" * 80)
    print()

    for stim in base_stimuli:
        set_id = stim['set_id']
        sentence = stim['sentence']
        jabberwocky = stim['jabberwocky_matched']

        # Create seeds for reproducibility
        seed_full = int(hashlib.md5(f"full_{set_id}".encode()).hexdigest()[:8], 16)
        seed_content = int(hashlib.md5(f"content_{set_id}".encode()).hexdigest()[:8], 16)
        seed_function = int(hashlib.md5(f"function_{set_id}".encode()).hexdigest()[:8], 16)

        # Generate all conditions
        full_scrambled = full_scramble(jabberwocky, seed_full)
        content_scrambled = content_scramble(jabberwocky, seed_content)
        function_scrambled = function_scramble(jabberwocky, seed_function)
        cue_deleted = cue_deletion(jabberwocky, cue_word='to', replacement='ke')

        # Store comprehensive stimulus set
        comprehensive_stim = {
            'set_id': set_id,
            'template_type': stim['template_type'],
            'content_words_replaced': stim['content_words_replaced'],

            # All 6 conditions
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'full_scrambled': full_scrambled,
            'content_scrambled': content_scrambled,
            'function_scrambled': function_scrambled,
            'cue_deleted': cue_deleted,

            # Metadata
            'seeds': {
                'full_scramble': seed_full,
                'content_scramble': seed_content,
                'function_scramble': seed_function
            }
        }

        comprehensive_stimuli.append(comprehensive_stim)

        # Show examples
        if set_id <= 3 or set_id % 10 == 0:
            print(f"Set {set_id}:")
            print(f"  Sentence:          {sentence}")
            print(f"  Jabberwocky:       {jabberwocky}")
            print(f"  Full-scrambled:    {full_scrambled}")
            print(f"  Content-scrambled: {content_scrambled}")
            print(f"  Function-scrambled: {function_scrambled}")
            print(f"  Cue-deleted:       {cue_deleted}")
            print()

    return comprehensive_stimuli

def verify_conditions(stimuli):
    """Sanity checks on all conditions."""
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print()

    # Count 'to' instances in each condition
    to_counts = {
        'sentence': 0,
        'jabberwocky': 0,
        'full_scrambled': 0,
        'content_scrambled': 0,
        'function_scrambled': 0,
        'cue_deleted': 0
    }

    ke_count = 0  # Replacement cue

    for stim in stimuli:
        for cond_name in to_counts.keys():
            text = stim[cond_name]
            words = text.split()
            to_counts[cond_name] += sum(1 for w in words if w.lower() == 'to')

        # Count 'ke' in cue_deleted
        ke_count += sum(1 for w in stim['cue_deleted'].split() if w.lower() == 'ke')

    print("'to' counts per condition:")
    for cond_name, count in to_counts.items():
        print(f"  {cond_name:20s}: {count}")
    print()
    print(f"'ke' (replacement) count in cue_deleted: {ke_count}")
    print()

    # Check: function_scrambled should have different function order but same content
    print("Checking FUNCTION_SCRAMBLED integrity (first 3 examples):")
    for i in range(min(3, len(stimuli))):
        jab_words = stimuli[i]['jabberwocky'].split()
        func_scram_words = stimuli[i]['function_scrambled'].split()

        # Extract content words from both
        _, jab_content = identify_slots(jab_words)
        _, func_content = identify_slots(func_scram_words)

        jab_content_set = [word for idx, word in sorted(jab_content)]
        func_content_set = [word for idx, word in sorted(func_content)]

        match = jab_content_set == func_content_set
        print(f"  Set {stimuli[i]['set_id']}: Content preserved: {match}")
        if not match:
            print(f"    Jab content:  {jab_content_set}")
            print(f"    Func content: {func_content_set}")

    print()
    print("✓ Verification complete")

def main():
    # Generate stimuli
    comprehensive_stimuli = generate_comprehensive_stimuli()

    # Verify
    verify_conditions(comprehensive_stimuli)

    # Save
    output_file = 'stimuli_comprehensive.json'
    with open(output_file, 'w') as f:
        json.dump(comprehensive_stimuli, f, indent=2)

    print()
    print("=" * 80)
    print("SAVED")
    print("=" * 80)
    print(f"✓ Saved {len(comprehensive_stimuli)} stimulus sets to: {output_file}")
    print()
    print("Conditions included:")
    print("  1. SENTENCE (real English)")
    print("  2. JABBERWOCKY (content→nonce, scaffold preserved)")
    print("  3. FULL_SCRAMBLED (all words shuffled)")
    print("  4. CONTENT_SCRAMBLED (content shuffled, function preserved)")
    print("  5. FUNCTION_SCRAMBLED (function shuffled, content preserved)")
    print("  6. CUE_DELETED (critical cue 'to' → 'ke')")
    print()
    print("Ready for comprehensive morphosyntax audit!")

if __name__ == '__main__':
    main()
