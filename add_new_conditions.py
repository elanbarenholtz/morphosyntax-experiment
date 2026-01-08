"""
Add two new experimental conditions to existing stimuli:
1. Scrambled Jabberwocky - randomize word order of jabberwocky sentences
2. Swapped Function Words - replace function words with nonsense, keep content words
"""

import json
import random
import spacy

# Load spacy for POS tagging
nlp = spacy.load('en_core_web_sm')

# Function words to replace (articles, prepositions, auxiliaries, pronouns)
FUNCTION_WORD_MAP = {
    'the': 'ke',
    'a': 'na',
    'an': 'nar',
    'to': 'po',
    'of': 'gef',
    'in': 'lin',
    'on': 'pon',
    'at': 'lat',
    'by': 'bly',
    'for': 'gor',
    'with': 'vith',
    'from': 'prom',
    'was': 'nar',
    'is': 'lis',
    'are': 'nar',
    'were': 'ner',
    'been': 'neen',
    'be': 'ne',
    'being': 'ning',
    'have': 'lev',
    'has': 'las',
    'had': 'lad',
    'will': 'nil',
    'would': 'nould',
    'can': 'gan',
    'could': 'gould',
    'should': 'thould',
    'may': 'nay',
    'might': 'nite',
    'must': 'nust',
    'he': 'ke',
    'she': 'the',
    'it': 'lit',
    'they': 'blay',
    'i': 'li',
    'you': 'pou',
    'we': 'ne',
    'his': 'lis',
    'her': 'ler',
    'their': 'bleir',
    'my': 'ny',
    'your': 'pour',
    'our': 'nour',
    'this': 'blis',
    'that': 'blat',
    'these': 'blese',
    'those': 'blose',
}

def scramble_jabberwocky(jabberwocky_text):
    """Scramble word order of jabberwocky sentence."""
    words = jabberwocky_text.split()
    random.shuffle(words)
    return ' '.join(words)

def swap_function_words(sentence):
    """Replace function words with nonsense, preserving content words and morphology."""
    doc = nlp(sentence)

    new_words = []
    for token in doc:
        word_lower = token.text.lower()

        # Check if it's a function word in our map
        if word_lower in FUNCTION_WORD_MAP:
            replacement = FUNCTION_WORD_MAP[word_lower]

            # Preserve capitalization
            if token.text[0].isupper():
                replacement = replacement.capitalize()

            new_words.append(replacement)
        else:
            # Keep the original word (content word or morphology)
            new_words.append(token.text)

    return ' '.join(new_words)

def add_new_conditions(input_file='stimuli_controlled.json',
                       output_file='stimuli_6conditions.json'):
    """Add scrambled jabberwocky and swapped function words to existing stimuli."""

    print("=" * 80)
    print("ADDING NEW EXPERIMENTAL CONDITIONS")
    print("=" * 80)

    # Load existing stimuli
    with open(input_file, 'r') as f:
        stimuli = json.load(f)

    print(f"\nLoaded {len(stimuli)} stimulus sets from {input_file}")

    # Set random seed for reproducibility
    random.seed(42)

    # Add new conditions to each stimulus set
    for i, stim_set in enumerate(stimuli):
        # Condition 5: Scrambled Jabberwocky
        scrambled = scramble_jabberwocky(stim_set['jabberwocky'])
        stim_set['scrambled_jabberwocky'] = scrambled

        # Condition 6: Swapped Function Words
        swapped = swap_function_words(stim_set['sentence'])
        stim_set['swapped_function_words'] = swapped

        # Show examples for first few sets
        if i < 3:
            print(f"\n{'*' * 80}")
            print(f"SET {stim_set['set_id']}:")
            print(f"{'*' * 80}")
            print(f"\nOriginal Sentence:")
            print(f"  {stim_set['sentence']}")
            print(f"\nJabberwocky:")
            print(f"  {stim_set['jabberwocky']}")
            print(f"\nScrambled Jabberwocky:")
            print(f"  {scrambled}")
            print(f"\nSwapped Function Words:")
            print(f"  {swapped}")

    # Save extended stimuli
    with open(output_file, 'w') as f:
        json.dump(stimuli, f, indent=2)

    print(f"\n{'=' * 80}")
    print(f"COMPLETE")
    print(f"{'=' * 80}")
    print(f"\nSaved {len(stimuli)} stimulus sets with 6 conditions to: {output_file}")
    print(f"\nConditions:")
    print(f"  1. sentence")
    print(f"  2. jabberwocky")
    print(f"  3. stripped")
    print(f"  4. nonwords")
    print(f"  5. scrambled_jabberwocky (NEW)")
    print(f"  6. swapped_function_words (NEW)")

    return stimuli

if __name__ == "__main__":
    add_new_conditions()
