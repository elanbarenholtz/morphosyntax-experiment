"""
Global text normalization for morphosyntax experiment.

Ensures consistent tokenization across all conditions by normalizing:
- Capitalization (lowercase all)
- Punctuation (consistent periods)
- Whitespace

This is NOT about "fighting capitalization" - we're not studying capitalization,
we're studying structure. Normalization is a one-line preprocessing fix that
eliminates a confound.
"""

import re

def normalize_text(text, strip_punctuation=False):
    """
    Apply global normalization to text.

    Args:
        text: Input text
        strip_punctuation: If True, remove all punctuation. If False, normalize to single period.

    Returns:
        Normalized text
    """
    # Lowercase
    text = text.lower()

    # Normalize whitespace
    text = ' '.join(text.split())

    # Normalize punctuation
    if strip_punctuation:
        # Remove all punctuation
        text = re.sub(r'[^\w\s]', '', text)
    else:
        # Remove existing punctuation and add single period at end
        text = re.sub(r'[^\w\s]', '', text)
        text = text.strip() + '.'

    return text

def normalize_stimuli_file(input_file, output_file, strip_punctuation=False):
    """
    Normalize all conditions in a stimuli file.

    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        strip_punctuation: If True, remove all punctuation
    """
    import json

    with open(input_file, 'r') as f:
        stimuli = json.load(f)

    # Normalize all text fields
    for item in stimuli:
        for key, value in item.items():
            if key != 'set_id' and isinstance(value, str):
                item[key] = normalize_text(value, strip_punctuation)

    with open(output_file, 'w') as f:
        json.dump(stimuli, f, indent=2)

    print(f"Normalized {len(stimuli)} stimulus sets")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Normalize stimuli text')
    parser.add_argument('--input', type=str, required=True, help='Input stimuli file')
    parser.add_argument('--output', type=str, required=True, help='Output stimuli file')
    parser.add_argument('--strip-punctuation', action='store_true',
                       help='Remove all punctuation instead of normalizing')

    args = parser.parse_args()

    normalize_stimuli_file(args.input, args.output, args.strip_punctuation)
