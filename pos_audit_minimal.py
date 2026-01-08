"""
Minimal POS Audit - Proof of Concept
Tests the core idea with one stimulus triplet
"""

import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Simple POS tagger using common word patterns
def simple_pos_tag(word):
    """Basic POS tagging using word patterns"""
    word_lower = word.lower().strip()

    # Determiners
    if word_lower in ['the', 'a', 'an']:
        return 'DET'
    # Prepositions
    if word_lower in ['in', 'on', 'at', 'to', 'for', 'with', 'from', 'by']:
        return 'PREP'
    # Pronouns
    if word_lower in ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']:
        return 'PRON'
    # Auxiliaries
    if word_lower in ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 'should']:
        return 'AUX'
    # Common adjectives (simplified)
    if word_lower.endswith('ly'):
        return 'ADV'
    if word_lower.endswith('ing'):
        return 'VERB'
    if word_lower.endswith('ed'):
        return 'VERB'

    # Default: assume noun
    return 'NOUN'

def get_top_k_at_position(model, tokenizer, text, word_position, k=50):
    """Get top-k predictions after a specific word"""
    words = text.split()
    context = ' '.join(words[:word_position+1])

    inputs = tokenizer(context, return_tensors='pt')

    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]

    probs = torch.softmax(next_token_logits, dim=-1)
    top_k_probs, top_k_ids = torch.topk(probs, k)

    candidates = []
    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id], skip_special_tokens=True).strip()
        if token_str:
            candidates.append({
                'token': token_str,
                'prob': prob.item(),
                'pos': simple_pos_tag(token_str)
            })

    return candidates

def analyze_cue(model, tokenizer, text, cue_word, expected_pos):
    """Analyze predictions after a diagnostic cue"""
    words = text.split()

    # Find cue word
    cue_position = None
    for i, word in enumerate(words[:-1]):
        if word.lower().strip('.,!?;:') == cue_word.lower():
            cue_position = i
            break

    if cue_position is None:
        return None

    # Get top-50 predictions
    candidates = get_top_k_at_position(model, tokenizer, text, cue_position, k=50)

    # Compute % in expected category
    total_prob = sum(c['prob'] for c in candidates)
    expected_prob = sum(c['prob'] for c in candidates if c['pos'] in expected_pos)
    expected_pct = (expected_prob / total_prob * 100) if total_prob > 0 else 0

    return {
        'cue_position': cue_position,
        'cue_word': words[cue_position],
        'expected_categories': expected_pos,
        'expected_pct': expected_pct,
        'top_5': [(c['token'], c['pos'], f"{c['prob']*100:.1f}%") for c in candidates[:5]]
    }

def main():
    print("="*80)
    print("POS AUDIT - Minimal Proof of Concept")
    print("="*80)
    print()

    # Load model
    print("Loading GPT-2...")
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    model.eval()
    print("Model loaded.\n")

    # Load one stimulus triplet
    with open('stimuli_with_scrambled.json') as f:
        stimuli = json.load(f)

    stim = stimuli[0]

    # Test: "the" → should predict NOUN/ADJ
    print("TEST CASE: Predictions after 'the' (determiner)")
    print("-" * 80)
    print()

    for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
        text = stim[condition]
        print(f"{condition.upper()}:")
        print(f"  Text: {text[:60]}...")

        result = analyze_cue(model, tokenizer, text, 'the', {'NOUN', 'ADJ'})

        if result:
            print(f"  Expected categories (NOUN/ADJ): {result['expected_pct']:.1f}%")
            print(f"  Top-5 predictions:")
            for token, pos, prob in result['top_5']:
                print(f"    - {token:15s} [{pos:6s}] {prob}")
        else:
            print("  (No 'the' found in this text)")

        print()

    print("="*80)
    print("INTERPRETATION:")
    print()
    print("If syntax constrains predictions:")
    print("  - Sentence & Jabberwocky should show HIGH % for expected categories")
    print("  - Scrambled should show LOWER % (structure disrupted)")
    print()
    print("This demonstrates category-level constraint beyond specific lexical items.")
    print("="*80)

if __name__ == "__main__":
    main()
