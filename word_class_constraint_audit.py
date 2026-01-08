"""
Word-Class Constraint Audit (Reviewer-Proof Alternative to POS)

Tests whether syntactic structure narrows the continuation space by measuring
probability mass on content-word-like continuations vs. fragments/punctuation.

Key insight: After determiners/auxiliaries, structured text should put more
probability on word-initial tokens (space + letter) vs. punctuation/fragments.
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import numpy as np

def classify_token(token_str, tokenizer_vocab):
    """
    Classify token as:
    - 'word_start': Begins a new word (has leading space + letter)
    - 'punctuation': Punctuation marks
    - 'fragment': Mid-word continuation or other fragment
    """
    # Check if empty
    if not token_str:
        return 'fragment'

    # GPT-2 uses 'Ġ' to mark word boundaries (space prefix)
    # In decoded form, this becomes a leading space
    if token_str[0] == ' ' and len(token_str) > 1 and token_str[1].isalpha():
        return 'word_start'

    # Check for punctuation
    if token_str.strip() in '.,!?;:"\'-':
        return 'punctuation'

    # Everything else is a fragment
    return 'fragment'

def analyze_position(model, tokenizer, text, target_position, k=100):
    """
    Analyze predictions at a specific word position.

    Returns probability mass on:
    - word_start: Tokens that begin new words
    - punctuation: Punctuation tokens
    - fragment: Mid-word fragments
    """
    words = text.split()

    # Get context up to target position
    context = ' '.join(words[:target_position+1])
    inputs = tokenizer(context, return_tensors='pt')

    # Get top-k predictions
    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]
        probs = torch.softmax(next_token_logits, dim=-1)
        top_k_probs, top_k_ids = torch.topk(probs, k)

    # Classify and accumulate probabilities
    class_probs = {'word_start': 0.0, 'punctuation': 0.0, 'fragment': 0.0}
    candidates = []

    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id])
        token_class = classify_token(token_str, tokenizer.get_vocab())

        class_probs[token_class] += prob.item()
        candidates.append({
            'token': repr(token_str),  # Use repr to show spaces/special chars
            'class': token_class,
            'prob': prob.item()
        })

    # Normalize to percentage
    total = sum(class_probs.values())
    if total > 0:
        class_pcts = {k: (v/total)*100 for k, v in class_probs.items()}
    else:
        class_pcts = {k: 0.0 for k in class_probs}

    return {
        'class_percentages': class_pcts,
        'top_10': candidates[:10]
    }

def find_cue_position(text, cue_word):
    """Find first occurrence of cue word."""
    words = text.split()
    for i, word in enumerate(words[:-1]):
        if word.lower().strip('.,!?;:') == cue_word.lower():
            return i
    return None

print("="*80)
print("WORD-CLASS CONSTRAINT AUDIT")
print("="*80)
print()
print("Tests: Does syntactic structure shift probability mass toward")
print("       word-initial tokens (vs. fragments/punctuation)?")
print()
print("Prediction: After 'the' (determiner):")
print("  - Sentence/Jabberwocky: HIGH % word_start (structure intact)")
print("  - Scrambled: LOWER % word_start (structure disrupted)")
print()
print("="*80)
print()

# Load model
print("Loading GPT-2...")
tokenizer = AutoTokenizer.from_pretrained('gpt2')
model = AutoModelForCausalLM.from_pretrained('gpt2')
model.eval()
print("Model loaded.\n")

# Load stimuli
with open('stimuli_with_scrambled.json') as f:
    stimuli = json.load(f)

# SANITY TEST: Verify classification works
print("SANITY TEST: Token Classification")
print("-" * 80)
test_tokens = [
    (' cat', 'word_start'),
    (' dog', 'word_start'),
    (',', 'punctuation'),
    ('.', 'punctuation'),
    ('ing', 'fragment'),
    ('ed', 'fragment'),
]
for token, expected in test_tokens:
    result = classify_token(token, tokenizer.get_vocab())
    status = "✓" if result == expected else "✗ FAIL"
    print(f"  {status}  {repr(token):15s} → {result:15s} (expected: {expected})")
print()

# Run audit on first 5 stimuli
results_by_condition = {'sentence': [], 'jabberwocky_matched': [], 'scrambled_jabberwocky': []}

print("="*80)
print("ANALYSIS: Predictions after 'the' (determiner)")
print("="*80)
print()

for stim_idx in range(min(5, len(stimuli))):
    stim = stimuli[stim_idx]

    print(f"\nSTIMULUS {stim_idx + 1}:")
    print("-" * 80)

    for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
        text = stim[condition]
        cue_pos = find_cue_position(text, 'the')

        if cue_pos is None:
            print(f"\n{condition:25s}: (No 'the' found)")
            continue

        result = analyze_position(model, tokenizer, text, cue_pos, k=100)

        # Store for summary
        results_by_condition[condition].append(result['class_percentages']['word_start'])

        print(f"\n{condition.upper()}:")
        print(f"  Text: {text[:60]}...")
        print(f"  Class distribution:")
        print(f"    Word-start:    {result['class_percentages']['word_start']:5.1f}%")
        print(f"    Punctuation:   {result['class_percentages']['punctuation']:5.1f}%")
        print(f"    Fragments:     {result['class_percentages']['fragment']:5.1f}%")
        print(f"  Top-10 predictions:")
        for cand in result['top_10']:
            print(f"    {cand['token']:20s} [{cand['class']:12s}] {cand['prob']*100:5.1f}%")

# Summary statistics
print("\n" + "="*80)
print("SUMMARY: % Probability on Word-Initial Tokens (after 'the')")
print("="*80)
print()

for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
    pcts = results_by_condition[condition]
    if pcts:
        mean_pct = np.mean(pcts)
        std_pct = np.std(pcts)
        print(f"{condition:25s}: {mean_pct:5.1f}% ± {std_pct:4.1f}%  (n={len(pcts)})")

print()
print("="*80)
print("INTERPRETATION:")
print()
jab_mean = np.mean(results_by_condition['jabberwocky_matched']) if results_by_condition['jabberwocky_matched'] else 0
scr_mean = np.mean(results_by_condition['scrambled_jabberwocky']) if results_by_condition['scrambled_jabberwocky'] else 0
delta = jab_mean - scr_mean

print(f"Δ (Jabberwocky - Scrambled): {delta:+.1f}%")
print()
if delta > 5:
    print("✓ STRUCTURE HELPS: Jabberwocky shows higher word-start probability,")
    print("  indicating that syntactic structure (even with nonsense words)")
    print("  narrows the continuation space toward word-initial positions.")
else:
    print("✗ Weak effect: Similar word-start probabilities suggest structure")
    print("  may not be constraining the distribution as expected.")
print("="*80)
