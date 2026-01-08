#!/usr/bin/env python3
"""
Stress test to trigger SIGBUS crash.
Processes multiple stimuli to test memory accumulation.
"""

import sys
import json
import torch
import spacy
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def main():
    print("="*80)
    print("SIGBUS STRESS TEST - Processing Multiple Stimuli")
    print("="*80)

    # Load models
    print("\nLoading models...")
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    model.eval()
    print("✓ GPT-2 loaded")

    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy loaded")

    # Load stimuli
    with open('stimuli_with_scrambled.json', 'r') as f:
        stimuli = json.load(f)
    print(f"✓ Loaded {len(stimuli)} stimulus sets")

    # Process each stimulus set
    print("\nProcessing stimuli (watching for crash)...")
    print("-"*80)

    total_processed = 0

    for set_idx, stim_set in enumerate(stimuli):
        print(f"\n[{set_idx + 1}/30] Processing set {stim_set['set_id']}...")

        for condition_name in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            if condition_name not in stim_set:
                continue

            text = stim_set[condition_name]
            print(f"  {condition_name}: '{text[:40]}...'")

            # Find "to" occurrences
            doc = nlp(text)
            to_count = 0

            for token in doc:
                if token.text.lower() == 'to':
                    to_count += 1

                    # Build context up to and including "to"
                    context_tokens = list(doc)[:token.i + 1]
                    context = ' '.join([t.text for t in context_tokens])

                    # Get next-token predictions
                    inputs = tokenizer(context, return_tensors='pt')

                    with torch.no_grad():
                        outputs = model(**inputs)

                    logits = outputs.logits[0, -1, :]
                    probs = torch.softmax(logits, dim=-1)

                    # Get top-k
                    top_k_probs, top_k_ids = torch.topk(probs, 100)

                    total_processed += 1

            if to_count > 0:
                print(f"    → Processed {to_count} 'to' occurrence(s)")

        # Progress update
        if (set_idx + 1) % 5 == 0:
            print(f"\n✓ Completed {set_idx + 1}/30 sets ({total_processed} contexts processed)")

    # If we get here, no crash!
    print("\n" + "="*80)
    print("✓ STRESS TEST PASSED - NO CRASH!")
    print("="*80)
    print(f"\nProcessed {total_processed} contexts across all 30 stimulus sets.")
    print("\nConclusion:")
    print("  - Basic pipeline works fine")
    print("  - No SIGBUS on multiple stimuli processing")
    print("  - Crash may be specific to:")
    print("    • The exact iteration pattern in morphosyntax_audit_refined.py")
    print("    • Specific classification/lexicon loading")
    print("    • File I/O during processing")
    print("    • Specific debugging/logging code")
    print("\nNext: Try running with reduced features to isolate.")

if __name__ == '__main__':
    main()
