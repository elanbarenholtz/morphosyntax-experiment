"""
Morphosyntactic Constraint Audit (REFINED)

Refinements:
1. Disambiguate "to" (PART vs ADP) using spaCy POS tagging
2. Tighter mass accounting (top_k=10000, residual target <0.01)
3. Filter punctuation-heavy positions (skip if punct >30%)
"""

import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from collections import defaultdict
import spacy

# Load spaCy for "to" disambiguation only
print("Loading spaCy for 'to' disambiguation...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy loaded")
except:
    print("⚠ spaCy not found. Installing...")
    import subprocess
    subprocess.run(["python3", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy installed and loaded")

# ============================================================================
# LEXICON DEFINITIONS
# ============================================================================

FUNCTION_SET = {
    # Determiners
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his',
    'her', 'its', 'our', 'their', 'some', 'any', 'no', 'every', 'each', 'either',
    'neither', 'much', 'many', 'more', 'most', 'few', 'several', 'all', 'both',
    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
    'who', 'whom', 'whose', 'what', 'which', 'whoever', 'whomever', 'whatever',
    # Auxiliaries
    'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing',
    'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would',
    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'with', 'from', 'by', 'about', 'as', 'of',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
    'among', 'under', 'over', 'against', 'within', 'without', 'throughout',
    # Conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet',
    'because', 'since', 'unless', 'until', 'while', 'although', 'though',
    'if', 'when', 'where', 'whether', 'than',
    # Negation & other
    'not', "n't", 'there', 'here', 'then', 'now', 'very', 'too', 'also', 'just', 'only',
}

VERB_SET = {
    'be', 'have', 'do', 'say', 'get', 'make', 'go', 'know', 'take', 'see',
    'come', 'think', 'look', 'want', 'give', 'use', 'find', 'tell', 'ask',
    'work', 'seem', 'feel', 'try', 'leave', 'call', 'become', 'run', 'move',
    'live', 'believe', 'bring', 'happen', 'write', 'sit', 'stand', 'lose',
    'pay', 'meet', 'include', 'continue', 'set', 'learn', 'change', 'lead',
    'understand', 'watch', 'follow', 'stop', 'create', 'speak', 'read', 'allow',
    'add', 'spend', 'grow', 'open', 'walk', 'win', 'offer', 'remember', 'love',
    'consider', 'appear', 'buy', 'wait', 'serve', 'die', 'send', 'expect',
    'build', 'stay', 'fall', 'cut', 'reach', 'kill', 'raise', 'pass', 'sell',
    # -ing/-ed forms
    'going', 'making', 'doing', 'saying', 'getting', 'taking', 'seeing', 'coming',
    'looking', 'working', 'trying', 'running', 'playing', 'showing', 'talking',
    'went', 'made', 'said', 'got', 'took', 'saw', 'came', 'looked', 'worked',
}

NOUN_SET = {
    'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life',
    'hand', 'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case',
    'point', 'government', 'company', 'number', 'group', 'problem', 'fact',
    'people', 'water', 'room', 'mother', 'area', 'money', 'story', 'family',
    'student', 'word', 'business', 'country', 'question', 'school', 'state',
    'night', 'head', 'home', 'office', 'power', 'hour', 'game', 'line', 'end',
    'dog', 'house', 'president', 'book', 'community', 'computer',
}

# ============================================================================
# CUE DEFINITIONS
# ============================================================================

CUE_SPECS = {
    'infinitival_to': {
        'cues': ['to'],
        'expected_class': 'verb',
        'description': 'Infinitival "to" (PART) expects VERB',
        'requires_pos_check': True  # Need to verify it's PART not ADP
    },
    'modal': {
        'cues': ['can', 'will', 'would', 'could', 'should', 'must', 'may', 'might'],
        'expected_class': 'verb',
        'description': 'Modals expect VERB',
        'requires_pos_check': False
    },
    'aux_copula': {
        'cues': ['is', 'are', 'was', 'were'],
        'expected_class': 'open_class',
        'description': 'Aux/copula expects open-class',
        'requires_pos_check': False
    },
    'preposition': {
        'cues': ['in', 'on', 'at', 'with', 'from', 'for'],
        'expected_class': 'function_or_noun',
        'description': 'Prepositions expect DET/NOUN',
        'requires_pos_check': False
    },
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_infinitival_to(text, word_position):
    """
    Check if "to" at word_position is infinitival (PART) or prepositional (ADP).
    Returns True only if:
    - POS tag is PART
    - NOT at position 0 (sentence-initial)
    """
    if word_position == 0:
        return False  # Exclude sentence-initial

    # Parse with spaCy
    doc = nlp(text)

    # Find the token at word_position
    words = text.split()
    target_word_idx = 0
    for token in doc:
        if not token.is_space and not token.is_punct:
            if target_word_idx == word_position:
                # Check if it's "to" with tag PART
                return token.text.lower() == 'to' and token.pos_ == 'PART'
            target_word_idx += 1

    return False

def is_word_start_token(token_str):
    """Check if BPE token starts a new word (space + letter)."""
    if not token_str:
        return False
    if token_str[0] == ' ' and len(token_str) > 1 and token_str[1].isalpha():
        return True
    return False

def decode_to_word(token_str):
    """Strip leading space and trailing punctuation to get base word."""
    word = token_str.strip()

    # If it's pure punctuation, preserve it (don't strip to empty string)
    if word and all(not c.isalnum() for c in word):
        return word  # Return punctuation as-is for classification

    # Otherwise strip trailing punctuation from words
    while word and not word[-1].isalnum():
        word = word[:-1]
    return word.lower()

def classify_candidate(word):
    """
    Classify word into lexical class.
    Priority: FUNCTION > VERB > NOUN > OTHER
    """
    if not word:
        return 'other'
    if all(not c.isalnum() for c in word):
        return 'punct'

    word_lower = word.lower()
    if word_lower in FUNCTION_SET:
        return 'function'
    if word_lower in VERB_SET:
        return 'verb'
    if word_lower in NOUN_SET:
        return 'noun'
    return 'other_open'

# ============================================================================
# CORE ANALYSIS
# ============================================================================

def analyze_cue_position(model, tokenizer, text, cue_word, cue_type, top_k=10000, debug=False):
    """
    Analyze predictions after a diagnostic cue.

    Refinements:
    - Increased top_k to 10000 for tighter mass accounting
    - Filter positions with high punctuation mass (>30%)
    - For "to", verify it's infinitival (PART) not prepositional (ADP)

    Returns None if:
    - Cue not found
    - For "to": not infinitival or sentence-initial
    - Punctuation mass > 30% (filtered out)
    """
    words = text.split()

    # Find cue position
    cue_position = None
    for i, word in enumerate(words[:-1]):
        if word.lower().strip('.,!?;:') == cue_word.lower():
            cue_position = i
            break

    if cue_position is None:
        return None

    # REFINEMENT 1: For "to", verify it's infinitival (PART) and not sentence-initial
    if cue_word.lower() == 'to' and cue_type == 'infinitival_to':
        if not is_infinitival_to(text, cue_position):
            return None  # Skip prepositional "to" or sentence-initial

    # Get context (prefix ending after cue)
    context = ' '.join(words[:cue_position+1])
    inputs = tokenizer(context, return_tensors='pt')

    # Get next-token predictions
    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]
        probs = torch.softmax(next_token_logits, dim=-1)

        # REFINEMENT 2: Increased top_k for tighter mass accounting
        top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

    # Classify candidates and accumulate mass
    mass = {
        'verb': 0.0,
        'noun': 0.0,
        'function': 0.0,
        'other_open': 0.0,
        'punct': 0.0,
        'non_wordstart': 0.0,
    }

    word_start_candidates = []

    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id])

        if is_word_start_token(token_str):
            word = decode_to_word(token_str)
            word_class = classify_candidate(word)
            mass[word_class] += prob.item()

            if debug and len(word_start_candidates) < 20:
                word_start_candidates.append({
                    'token': repr(token_str),
                    'word': word,
                    'class': word_class,
                    'prob': prob.item()
                })
        else:
            mass['non_wordstart'] += prob.item()

    # Compute residual
    mass['residual'] = 1.0 - sum(mass.values())

    # REFINEMENT 3: Filter punctuation-heavy positions
    if mass['punct'] > 0.30:  # >30% punctuation
        return None  # Skip this position

    # ENHANCED LOGGING: Always include full context metadata
    result = {
        'cue_word_index': cue_position,
        'mass': mass,
        # Context logging (Point 1 from requirements)
        'full_text': text,
        'cue_word': cue_word,
        'context_prefix': context,  # Exact string fed to model
        'context_tokens': len(inputs['input_ids'][0]),  # Number of BPE tokens
    }

    if debug:
        result['context_display'] = context[-60:] if len(context) > 60 else context
        result['top_candidates'] = word_start_candidates

    return result

# ============================================================================
# SANITY CHECKS
# ============================================================================

def run_sanity_checks():
    """Test classification on known cases."""
    print("=" * 80)
    print("SANITY CHECKS: Classification")
    print("=" * 80)
    print()

    test_cases = [
        (' the', 'function', 'Determiner → FUNCTION'),
        (' and', 'function', 'Conjunction → FUNCTION'),
        (' is', 'function', 'Auxiliary → FUNCTION'),
        (' run', 'verb', 'Common verb → VERB'),
        (' running', 'verb', 'Verb -ing → VERB'),
        (' time', 'noun', 'Common noun → NOUN'),
        (' people', 'noun', 'Common noun → NOUN'),
        (',', 'punct', 'Comma → PUNCT'),
        ('.', 'punct', 'Period → PUNCT'),
    ]

    all_passed = True
    for token, expected, desc in test_cases:
        word = decode_to_word(token)
        result = classify_candidate(word)
        status = "✓" if result == expected else "✗ FAIL"
        if result != expected:
            all_passed = False
        print(f"{status}  {repr(token):15s} → {word:12s} → {result:12s}  ({desc})")

    print()
    if all_passed:
        print("✓ All sanity checks passed!")
    else:
        print("✗ Some tests FAILED - check classification logic")
        print("STOPPING - fix classification before proceeding")
        exit(1)
    print()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 80)
    print("MORPHOSYNTACTIC CONSTRAINT AUDIT (REFINED)")
    print("=" * 80)
    print()
    print("Refinements:")
    print("  1. Disambiguate 'to' (PART vs ADP) + exclude sentence-initial")
    print("  2. Tighter mass accounting (top_k=10000, target residual <0.01)")
    print("  3. Filter punctuation-heavy positions (skip if punct >30%)")
    print()
    print("=" * 80)
    print()

    # Load model
    print("Loading GPT-2...")
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    model.eval()
    print("✓ Model loaded\n")

    # Run sanity checks
    run_sanity_checks()

    # Load stimuli
    print("Loading stimuli...")
    with open('stimuli_with_scrambled.json') as f:
        stimuli = json.load(f)
    print(f"✓ Loaded {len(stimuli)} stimulus sets\n")

    # Collect results
    all_results = []
    filtered_counts = defaultdict(int)  # Track how many filtered per reason

    # For each cue type
    for cue_type, spec in CUE_SPECS.items():
        print("=" * 80)
        print(f"ANALYZING: {spec['description']}")
        print("=" * 80)
        print()

        cue_results = defaultdict(list)
        debug_samples = defaultdict(list)

        # Process each stimulus
        for stim_idx, stim in enumerate(stimuli):
            for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
                text = stim[condition]

                for cue_word in spec['cues']:
                    debug = len(debug_samples[condition]) < 3

                    result = analyze_cue_position(
                        model, tokenizer, text, cue_word, cue_type,
                        top_k=10000, debug=debug
                    )

                    if result is not None:
                        # Check residual
                        if result['mass']['residual'] > 0.02:
                            print(f"⚠ High residual ({result['mass']['residual']:.3f}) for {condition} stim {stim_idx}")

                        result_record = {
                            'model': 'gpt2',
                            'cue_type': cue_type,
                            'condition': condition,
                            'stimulus_id': stim_idx,
                            'cue_word': cue_word,
                            **result
                        }

                        all_results.append(result_record)
                        cue_results[condition].append(result['mass'])

                        if debug:
                            debug_samples[condition].append(result_record)
                    else:
                        # Track filtering
                        filtered_counts[f"{cue_type}_{condition}"] += 1

        # Show debug samples
        print("\nDEBUG SAMPLES (first 3 per condition):")
        print("-" * 80)
        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            print(f"\n{condition.upper()}:")
            for sample in debug_samples[condition]:
                print(f"\n  Context: ...{sample.get('context_display', sample.get('context_prefix', ''))}")
                print(f"  Cue: '{sample['cue_word']}' at index {sample['cue_word_index']}")
                print(f"  Mass distribution:")
                for class_name, mass_val in sample['mass'].items():
                    print(f"    {class_name:15s}: {mass_val*100:5.1f}%")
                print(f"  Top-10 word-start candidates:")
                for cand in sample.get('top_candidates', [])[:10]:
                    print(f"    {cand['token']:20s} [{cand['class']:12s}] {cand['prob']*100:5.1f}%")

        # Summary statistics
        print("\n" + "=" * 80)
        print(f"SUMMARY: {spec['description']}")
        print("=" * 80)
        print()

        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            if cue_results[condition]:
                masses = cue_results[condition]
                n = len(masses)

                mean_mass = {
                    class_name: np.mean([m[class_name] for m in masses])
                    for class_name in ['verb', 'noun', 'function', 'other_open', 'punct', 'residual']
                }

                print(f"{condition:30s} (n={n}):")
                for class_name in ['verb', 'noun', 'function', 'other_open', 'punct', 'residual']:
                    print(f"  {class_name:15s}: {mean_mass[class_name]*100:5.2f}%")
                print()

    # Report filtering
    print("\n" + "=" * 80)
    print("FILTERING REPORT")
    print("=" * 80)
    print()
    for key, count in filtered_counts.items():
        print(f"  {key:40s}: {count} positions filtered")
    print()

    # Save results
    print("=" * 80)
    print("Saving results...")
    with open('morphosyntax_audit_refined_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("✓ Results saved to: morphosyntax_audit_refined_results.json")
    print(f"✓ Total records: {len(all_results)}")
    print("=" * 80)

if __name__ == '__main__':
    main()
