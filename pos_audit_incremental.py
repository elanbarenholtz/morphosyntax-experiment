"""
Incremental POS Audit - Building on working minimal test
"""
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Simple POS tagger
def simple_pos_tag(word):
    word_lower = word.lower().strip()
    if word_lower in ['the', 'a', 'an']:
        return 'DET'
    if word_lower in ['in', 'on', 'at', 'to', 'for', 'with', 'from', 'by']:
        return 'PREP'
    if word_lower in ['i', 'you', 'he', 'she', 'it', 'we', 'they']:
        return 'PRON'
    if word_lower in ['is', 'are', 'was', 'were', 'has', 'have', 'had']:
        return 'AUX'
    if word_lower.endswith('ly'):
        return 'ADV'
    if word_lower.endswith('ing') or word_lower.endswith('ed'):
        return 'VERB'
    return 'NOUN'

print("="*80)
print("POS AUDIT - Incremental Build")
print("="*80)
print()

# Load model (using proven pattern from ultraminimal test)
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained('gpt2')
print("Tokenizer loaded.")

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained('gpt2')
model.eval()
print("Model loaded.")
print()

# Load stimuli
print("Loading stimuli...")
with open('stimuli_with_scrambled.json') as f:
    stimuli = json.load(f)
print(f"Loaded {len(stimuli)} stimulus sets.")
print()

# Test with first stimulus
stim = stimuli[0]
print("TEST: Predictions after 'the' (determiner)")
print("-" * 80)
print()

for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
    text = stim[condition]
    print(f"{condition.upper()}:")
    print(f"  Text: {text[:60]}...")

    # Find 'the'
    words = text.split()
    the_position = None
    for i, word in enumerate(words[:-1]):
        if word.lower().strip('.,!?;:') == 'the':
            the_position = i
            break

    if the_position is None:
        print("  (No 'the' found)")
        print()
        continue

    # Get predictions after 'the'
    context = ' '.join(words[:the_position+1])
    inputs = tokenizer(context, return_tensors='pt')

    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]
        probs = torch.softmax(next_token_logits, dim=-1)
        top_k_probs, top_k_ids = torch.topk(probs, 50)

    # Decode and tag
    candidates = []
    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id], skip_special_tokens=True).strip()
        if token_str:
            candidates.append({
                'token': token_str,
                'prob': prob.item(),
                'pos': simple_pos_tag(token_str)
            })

    # Compute % going to NOUN/ADJ
    total_prob = sum(c['prob'] for c in candidates)
    expected_prob = sum(c['prob'] for c in candidates if c['pos'] in ['NOUN', 'ADJ'])
    expected_pct = (expected_prob / total_prob * 100) if total_prob > 0 else 0

    print(f"  Expected categories (NOUN/ADJ): {expected_pct:.1f}%")
    print(f"  Top-5 predictions:")
    for c in candidates[:5]:
        print(f"    - {c['token']:15s} [{c['pos']:6s}] {c['prob']*100:.1f}%")

    print()

print("="*80)
print("INTERPRETATION:")
print()
print("If syntax constrains predictions:")
print("  - Sentence & Jabberwocky should show HIGH % for expected categories")
print("  - Scrambled should show LOWER % (structure disrupted)")
print("="*80)
print()
print("SUCCESS!")
