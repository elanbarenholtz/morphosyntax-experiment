"""
Morphosyntactic Constraint Audit

Tests whether syntactic structure shifts probability mass toward grammatically-
appropriate lexical classes (VERB/NOUN/FUNCTION) at diagnostic cue positions.

Key improvement over POS audit: Uses lexicon-based classification on word-start
candidates only, avoiding BPE fragment issues.
"""

import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from collections import defaultdict

# ============================================================================
# LEXICON DEFINITIONS
# ============================================================================

# Function words (closed-class, ~200 items)
FUNCTION_SET = {
    # Determiners
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his',
    'her', 'its', 'our', 'their', 'some', 'any', 'no', 'every', 'each', 'either',
    'neither', 'much', 'many', 'more', 'most', 'few', 'several', 'all', 'both',

    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 'themselves',
    'who', 'whom', 'whose', 'what', 'which', 'whoever', 'whomever', 'whatever',
    'whichever', 'that', 'this', 'these', 'those',

    # Auxiliaries
    'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing',
    'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would',

    # Prepositions
    'in', 'on', 'at', 'to', 'for', 'with', 'from', 'by', 'about', 'as', 'of',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
    'among', 'under', 'over', 'against', 'within', 'without', 'throughout',
    'toward', 'towards', 'upon', 'off', 'out', 'up', 'down', 'around', 'across',
    'along', 'behind', 'beside', 'besides', 'beyond', 'near', 'past',

    # Conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'for',
    'because', 'since', 'unless', 'until', 'while', 'although', 'though',
    'if', 'when', 'where', 'whether', 'than',

    # Negation
    'not', 'no', "n't",

    # Other closed-class
    'there', 'here', 'then', 'now', 'very', 'too', 'also', 'just', 'only',
}

# Common verbs (lemmatized forms)
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
    'require', 'report', 'decide', 'pull', 'explain', 'hope', 'develop', 'carry',
    'break', 'receive', 'agree', 'support', 'hit', 'produce', 'eat', 'cover',
    'catch', 'draw', 'choose', 'cause', 'point', 'prove', 'listen', 'occur',
    'prepare', 'wear', 'accept', 'enter', 'save', 'place', 'fill', 'obtain',
    'plan', 'manage', 'express', 'answer', 'identify', 'claim', 'join', 'share',
    'avoid', 'reduce', 'lie', 'seek', 'throw', 'miss', 'indicate', 'assume',
    'sing', 'suffer', 'mention', 'represent', 'forget', 'ensure', 'describe',
    'admit', 'apply', 'argue', 'emerge', 'provide', 'establish', 'affect',
    # Common -ing/-ed forms
    'going', 'making', 'doing', 'saying', 'getting', 'taking', 'seeing', 'coming',
    'looking', 'working', 'trying', 'running', 'playing', 'showing', 'talking',
    'went', 'made', 'said', 'got', 'took', 'saw', 'came', 'looked', 'worked',
    'tried', 'ran', 'played', 'showed', 'talked', 'used', 'found', 'gave',
}

# Common nouns
NOUN_SET = {
    'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life',
    'hand', 'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case',
    'point', 'government', 'company', 'number', 'group', 'problem', 'fact',
    'people', 'water', 'room', 'mother', 'area', 'money', 'story', 'family',
    'student', 'word', 'business', 'country', 'question', 'school', 'state',
    'night', 'head', 'home', 'office', 'power', 'hour', 'game', 'line', 'end',
    'member', 'law', 'car', 'city', 'name', 'team', 'minute', 'idea', 'body',
    'information', 'back', 'parent', 'face', 'level', 'door', 'health', 'art',
    'war', 'history', 'party', 'result', 'change', 'morning', 'reason', 'girl',
    'guy', 'moment', 'air', 'teacher', 'force', 'education', 'foot', 'boy',
    'age', 'policy', 'process', 'music', 'market', 'sense', 'nation', 'plan',
    'college', 'interest', 'death', 'experience', 'effect', 'use', 'class',
    'control', 'care', 'field', 'development', 'role', 'effort', 'rate', 'heart',
    'drug', 'show', 'leader', 'light', 'voice', 'wife', 'production', 'player',
    'economic', 'action', 'price', 'society', 'activity', 'cost', 'industry',
    'bank', 'century', 'member', 'value', 'book', 'structure', 'hour', 'black',
    'dog', 'house', 'president', 'sea', 'resource', 'community', 'computer',
}

# ============================================================================
# CUE DEFINITIONS
# ============================================================================

CUE_SPECS = {
    'infinitival_to': {
        'cues': ['to'],
        'expected_class': 'verb',
        'description': 'Infinitival "to" expects VERB'
    },
    'modal': {
        'cues': ['can', 'will', 'would', 'could', 'should', 'must', 'may', 'might'],
        'expected_class': 'verb',
        'description': 'Modals expect VERB'
    },
    'aux_copula': {
        'cues': ['is', 'are', 'was', 'were'],
        'expected_class': 'open_class',  # ADJ/NOUN/DET - we'll track function vs open
        'description': 'Aux/copula expects open-class'
    },
    'preposition': {
        'cues': ['in', 'on', 'at', 'with', 'from', 'for'],
        'expected_class': 'function_or_noun',  # DET/NOUN (NP start)
        'description': 'Prepositions expect DET/NOUN'
    },
}

# ============================================================================
# CLASSIFICATION FUNCTIONS
# ============================================================================

def is_word_start_token(token_str):
    """Check if BPE token starts a new word (space + letter)."""
    if not token_str:
        return False
    # GPT-2 BPE: word-start has leading space + letter
    if token_str[0] == ' ' and len(token_str) > 1 and token_str[1].isalpha():
        return True
    return False

def decode_to_word(token_str):
    """Strip leading space and trailing punctuation to get base word."""
    word = token_str.strip()
    # Strip trailing punctuation
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

    # Check if punctuation only
    if all(not c.isalnum() for c in word):
        return 'punct'

    word_lower = word.lower()

    # Priority order
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

def analyze_cue_position(model, tokenizer, text, cue_word, top_k=5000, debug=False):
    """
    Analyze predictions after a diagnostic cue.

    Returns:
        dict with:
        - mass: probability mass by class
        - top_candidates: top-20 word-start candidates (if debug=True)
    """
    words = text.split()

    # Find cue position
    cue_position = None
    for i, word in enumerate(words[:-1]):  # Don't check last word
        if word.lower().strip('.,!?;:') == cue_word.lower():
            cue_position = i
            break

    if cue_position is None:
        return None

    # Get context (prefix ending after cue)
    context = ' '.join(words[:cue_position+1])
    inputs = tokenizer(context, return_tensors='pt')

    # Get next-token predictions
    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]
        probs = torch.softmax(next_token_logits, dim=-1)
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

        # Check if word-start
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

    # Compute residual (mass not in top-k)
    mass['residual'] = 1.0 - sum(mass.values())

    result = {
        'cue_word_index': cue_position,
        'mass': mass,
    }

    if debug:
        result['context'] = context[-60:] if len(context) > 60 else context
        result['top_candidates'] = word_start_candidates

    return result

# ============================================================================
# SANITY CHECKS
# ============================================================================

def run_sanity_checks(tokenizer):
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
        (',', 'punct', 'Comma → PUNCT (after decode)'),
        ('.', 'punct', 'Period → PUNCT (after decode)'),
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
    print()

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 80)
    print("MORPHOSYNTACTIC CONSTRAINT AUDIT")
    print("=" * 80)
    print()
    print("Tests: Does syntactic structure shift probability mass toward")
    print("       grammatically-appropriate lexical classes at diagnostic cues?")
    print()
    print("Cue types:")
    for cue_type, spec in CUE_SPECS.items():
        print(f"  - {cue_type:20s}: {spec['description']}")
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
    run_sanity_checks(tokenizer)

    # Load stimuli
    print("Loading stimuli...")
    with open('stimuli_with_scrambled.json') as f:
        stimuli = json.load(f)
    print(f"✓ Loaded {len(stimuli)} stimulus sets\n")

    # Collect results
    all_results = []

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

                # Try each cue in this spec
                for cue_word in spec['cues']:
                    # Debug first 3 items
                    debug = len(debug_samples[condition]) < 3

                    result = analyze_cue_position(
                        model, tokenizer, text, cue_word,
                        top_k=5000, debug=debug
                    )

                    if result is not None:
                        # Store result
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

        # Show debug samples
        print("\nDEBUG SAMPLES (first 3 per condition):")
        print("-" * 80)
        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            print(f"\n{condition.upper()}:")
            for sample in debug_samples[condition]:
                print(f"\n  Context: ...{sample['context']}")
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

                # Compute means
                mean_mass = {
                    class_name: np.mean([m[class_name] for m in masses])
                    for class_name in ['verb', 'noun', 'function', 'other_open', 'punct']
                }

                print(f"{condition:30s} (n={n}):")
                for class_name in ['verb', 'noun', 'function', 'other_open', 'punct']:
                    print(f"  {class_name:15s}: {mean_mass[class_name]*100:5.1f}%")
                print()

    # Save results
    print("=" * 80)
    print("Saving results...")
    with open('morphosyntax_audit_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("✓ Results saved to: morphosyntax_audit_results.json")
    print("=" * 80)

if __name__ == '__main__':
    main()
