"""
POS Audit - Using proven working model loading pattern
"""

import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM
from collections import defaultdict

# Simple POS tagging
def simple_pos_tag(word):
    word_lower = word.lower().strip()
    if word_lower in ['the', 'a', 'an']:
        return 'DET'
    if word_lower in ['in', 'on', 'at', 'to', 'for', 'with', 'from', 'by']:
        return 'PREP'
    if word_lower in ['i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']:
        return 'PRON'
    if word_lower in ['is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'would', 'should']:
        return 'AUX'
    if word_lower.endswith('ly'):
        return 'ADV'
    if word_lower.endswith('ing') or word_lower.endswith('ed'):
        return 'VERB'
    return 'NOUN'

def get_top_k_at_position(model, tokenizer, text, word_position, device, k=50):
    words = text.split()
    context = ' '.join(words[:word_position+1])

    inputs = tokenizer(context, return_tensors='pt').to(device)

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

def analyze_cue(model, tokenizer, text, cue_word, expected_pos, device):
    words = text.split()

    cue_position = None
    for i, word in enumerate(words[:-1]):
        if word.lower().strip('.,!?;:') == cue_word.lower():
            cue_position = i
            break

    if cue_position is None:
        return None

    candidates = get_top_k_at_position(model, tokenizer, text, cue_position, device, k=50)

    total_prob = sum(c['prob'] for c in candidates)
    expected_prob = sum(c['prob'] for c in candidates if c['pos'] in expected_pos)
    expected_pct = (expected_prob / total_prob * 100) if total_prob > 0 else 0

    return {
        'cue_position': cue_position,
        'cue_word': words[cue_position],
        'expected_categories': list(expected_pos),
        'expected_pct': expected_pct,
        'top_5': [(c['token'], c['pos'], f"{c['prob']*100:.1f}%") for c in candidates[:5]]
    }

def main():
    print("="*80)
    print("POS AUDIT - Working Version")
    print("="*80)
    print()

    # Use same device selection as working scripts
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model (device: {device})...")

    # Load model using exact same pattern as working experiments
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2').to(device)
    model.eval()
    print("Model loaded successfully\n")

    # Load stimuli
    with open('stimuli_with_scrambled.json') as f:
        stimuli = json.load(f)

    stim = stimuli[0]

    print("TEST CASE: Predictions after 'the' (determiner)")
    print("-" * 80)
    print()

    for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
        text = stim[condition]
        print(f"{condition.upper()}:")
        print(f"  Text: {text[:60]}...")

        result = analyze_cue(model, tokenizer, text, 'the', {'NOUN', 'ADJ'}, device)

        if result:
            print(f"  Expected categories (NOUN/ADJ): {result['expected_pct']:.1f}%")
            print(f"  Top-5 predictions:")
            for token, pos, prob in result['top_5']:
                print(f"    - {token:15s} [{pos:6s}] {prob}")
        else:
            print("  (No 'the' found)")

        print()

    print("="*80)
    print("INTERPRETATION:")
    print()
    print("If syntax constrains predictions:")
    print("  - Sentence & Jabberwocky should show HIGH % for expected categories")
    print("  - Scrambled should show LOWER % (structure disrupted)")
    print("="*80)

if __name__ == "__main__":
    main()
