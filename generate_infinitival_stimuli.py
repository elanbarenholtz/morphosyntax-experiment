#!/usr/bin/env python3
"""
Generate stimuli with infinitival 'to' for morphosyntax audit.

Creates 30 sentence sets with:
- Clear infinitival 'to' constructions (PART tag)
- Matched jabberwocky (preserve structure, replace content words)
- Scrambled jabberwocky (scramble word order)
"""

import json
import random

# Template sentences with infinitival "to"
SENTENCE_TEMPLATES = [
    # decided to [VERB]
    ("the scientist decided to study the ancient artifacts",
     ["scientist", "study", "ancient", "artifacts"]),
    ("the teacher decided to explain the difficult concept",
     ["teacher", "explain", "difficult", "concept"]),
    ("the student decided to finish the important assignment",
     ["student", "finish", "important", "assignment"]),
    ("the artist decided to paint the beautiful landscape",
     ["artist", "paint", "beautiful", "landscape"]),
    ("the doctor decided to examine the sick patient",
     ["doctor", "examine", "sick", "patient"]),

    # wanted to [VERB]
    ("the child wanted to play with the colorful toys",
     ["child", "play", "colorful", "toys"]),
    ("the musician wanted to perform at the famous venue",
     ["musician", "perform", "famous", "venue"]),
    ("the writer wanted to publish the controversial novel",
     ["writer", "publish", "controversial", "novel"]),
    ("the chef wanted to prepare the special dinner",
     ["chef", "prepare", "special", "dinner"]),
    ("the athlete wanted to win the important competition",
     ["athlete", "win", "important", "competition"]),

    # began to [VERB]
    ("the professor began to teach the advanced course",
     ["professor", "teach", "advanced", "course"]),
    ("the detective began to investigate the mysterious crime",
     ["detective", "investigate", "mysterious", "crime"]),
    ("the engineer began to design the complex system",
     ["engineer", "design", "complex", "system"]),
    ("the gardener began to plant the fresh seeds",
     ["gardener", "plant", "fresh", "seeds"]),
    ("the driver began to repair the broken vehicle",
     ["driver", "repair", "broken", "vehicle"]),

    # tried to [VERB]
    ("the researcher tried to solve the difficult problem",
     ["researcher", "solve", "difficult", "problem"]),
    ("the manager tried to improve the poor performance",
     ["manager", "improve", "poor", "performance"]),
    ("the programmer tried to debug the complex code",
     ["programmer", "debug", "complex", "code"]),
    ("the assistant tried to organize the messy files",
     ["assistant", "organize", "messy", "files"]),
    ("the lawyer tried to defend the innocent client",
     ["lawyer", "defend", "innocent", "client"]),

    # planned to [VERB]
    ("the architect planned to build the modern structure",
     ["architect", "build", "modern", "structure"]),
    ("the director planned to film the dramatic scene",
     ["director", "film", "dramatic", "scene"]),
    ("the designer planned to create the elegant product",
     ["designer", "create", "elegant", "product"]),
    ("the merchant planned to sell the expensive goods",
     ["merchant", "sell", "expensive", "goods"]),
    ("the captain planned to sail the large vessel",
     ["captain", "sail", "large", "vessel"]),

    # continued to [VERB]
    ("the speaker continued to discuss the important topic",
     ["speaker", "discuss", "important", "topic"]),
    ("the reader continued to study the ancient texts",
     ["reader", "study", "ancient", "texts"]),
    ("the worker continued to assemble the metal parts",
     ["worker", "assemble", "metal", "parts"]),
    ("the dancer continued to practice the difficult routine",
     ["dancer", "practice", "difficult", "routine"]),
    ("the painter continued to refine the delicate details",
     ["painter", "refine", "delicate", "details"]),
]

# Nonce words (pronounceable non-words)
NONCE_NOUNS = [
    "blit", "dron", "flib", "grop", "krin", "plim", "snar", "tral", "vrim", "zept",
    "glom", "prid", "skiv", "throp", "braz", "clund", "drest", "flarn", "grift", "prell",
    "snib", "trug", "vling", "wask", "yond", "zorf", "bletch", "crint", "drell", "flust"
]

NONCE_VERBS = [
    "blim", "crog", "fleb", "grib", "plek", "slib", "trop", "vreb", "zink", "gleb",
    "prib", "skeb", "thrib", "brind", "cleb", "drib", "flib", "greb", "prib", "sneb",
    "treb", "vlib", "wrib", "yeb", "zrib", "bleb", "creb", "dreb", "flub", "grub"
]

NONCE_ADJECTIVES = [
    "blip", "cral", "flom", "grel", "plon", "slib", "trop", "vrel", "zim", "glib",
    "pril", "skel", "thrim", "bril", "clom", "dril", "flim", "gril", "pril", "snel",
    "tril", "vlim", "wril", "yel", "zril", "blel", "crel", "drel", "flul", "grul"
]

def create_jabberwocky(sentence, content_words):
    """
    Create jabberwocky version by replacing content words with nonce words.
    Preserve function words and structure.
    """
    words = sentence.split()

    # Get random nonce words (without replacement within a sentence)
    available_nouns = NONCE_NOUNS.copy()
    available_verbs = NONCE_VERBS.copy()
    available_adjs = NONCE_ADJECTIVES.copy()

    random.shuffle(available_nouns)
    random.shuffle(available_verbs)
    random.shuffle(available_adjs)

    # Replace content words
    jab_words = []
    noun_idx = 0
    verb_idx = 0
    adj_idx = 0

    for word in words:
        # Check if this word is a content word to replace
        word_clean = word.strip('.,!?;:')

        if word_clean in content_words:
            # Determine word type and replace
            idx = content_words.index(word_clean)

            # First word is typically noun, second is verb, third is adj, fourth is noun
            if idx == 0:  # First noun
                replacement = available_nouns[noun_idx % len(available_nouns)]
                noun_idx += 1
            elif idx == 1:  # Verb
                replacement = available_verbs[verb_idx % len(available_verbs)]
                verb_idx += 1
            elif idx == 2:  # Adjective
                replacement = available_adjs[adj_idx % len(available_adjs)]
                adj_idx += 1
            else:  # Second noun
                replacement = available_nouns[noun_idx % len(available_nouns)]
                noun_idx += 1

            jab_words.append(replacement)
        else:
            # Keep function words
            jab_words.append(word)

    return ' '.join(jab_words)

def create_scrambled(sentence):
    """
    Scramble word order while keeping words intact.
    """
    words = sentence.split()
    scrambled = words.copy()
    random.shuffle(scrambled)

    # Ensure it's actually different from original
    attempts = 0
    while ' '.join(scrambled) == sentence and attempts < 10:
        random.shuffle(scrambled)
        attempts += 1

    return ' '.join(scrambled)

def generate_stimuli():
    """Generate 30 stimulus sets with infinitival 'to'."""
    stimuli = []

    for i, (sentence, content_words) in enumerate(SENTENCE_TEMPLATES):
        # Create jabberwocky version
        jabberwocky = create_jabberwocky(sentence, content_words)

        # Create scrambled jabberwocky
        scrambled = create_scrambled(jabberwocky)

        # Create stimulus set
        stim_set = {
            'set_id': i + 1,
            'sentence': sentence,
            'jabberwocky_matched': jabberwocky,
            'scrambled_jabberwocky': scrambled,
            'content_words_replaced': content_words,
            'template_type': sentence.split()[2]  # decided/wanted/began/etc.
        }

        stimuli.append(stim_set)

    return stimuli

def main():
    print("="*80)
    print("GENERATING INFINITIVAL 'TO' STIMULI")
    print("="*80)

    # Set random seed for reproducibility
    random.seed(42)

    # Generate stimuli
    stimuli = generate_stimuli()

    print(f"\n✓ Generated {len(stimuli)} stimulus sets")

    # Save to JSON
    output_file = 'stimuli_infinitival_to.json'
    with open(output_file, 'w') as f:
        json.dump(stimuli, f, indent=2)

    print(f"✓ Saved to: {output_file}")

    # Show examples
    print("\n" + "="*80)
    print("EXAMPLES")
    print("="*80)

    for i in [0, 5, 10]:
        stim = stimuli[i]
        print(f"\nSet {stim['set_id']} ({stim['template_type']}):")
        print(f"  Sentence:    {stim['sentence']}")
        print(f"  Jabberwocky: {stim['jabberwocky_matched']}")
        print(f"  Scrambled:   {stim['scrambled_jabberwocky']}")

    # Verify "to" positions
    print("\n" + "="*80)
    print("VERIFICATION: 'to' positions")
    print("="*80)

    for stim in stimuli[:5]:
        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            text = stim[condition]
            words = text.split()
            to_positions = [j for j, w in enumerate(words) if w.lower() == 'to']
            print(f"Set {stim['set_id']} {condition}: 'to' at positions {to_positions}")

    print("\n" + "="*80)
    print("READY FOR MORPHOSYNTAX AUDIT")
    print("="*80)
    print("\nNext steps:")
    print("1. Upload 'stimuli_infinitival_to.json' to Colab")
    print("2. Update Colab notebook to use this file")
    print("3. Run morphosyntax audit")
    print("4. Expect strong VERB mass after infinitival 'to'!")

if __name__ == '__main__':
    main()
