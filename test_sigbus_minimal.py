#!/usr/bin/env python3
"""
Minimal test to isolate SIGBUS crash source.
Tests each component incrementally.
"""

import sys
import json

def test_1_imports():
    """Test 1: Basic imports"""
    print("\n" + "="*80)
    print("TEST 1: Basic imports")
    print("="*80)
    try:
        import torch
        print(f"✓ torch imported (version: {torch.__version__})")

        import transformers
        print(f"✓ transformers imported (version: {transformers.__version__})")

        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_2_load_model():
    """Test 2: Load GPT-2"""
    print("\n" + "="*80)
    print("TEST 2: Load GPT-2 model")
    print("="*80)
    try:
        from transformers import GPT2LMHeadModel, GPT2Tokenizer

        print("Loading tokenizer...")
        tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        print("✓ Tokenizer loaded")

        print("Loading model...")
        model = GPT2LMHeadModel.from_pretrained('gpt2')
        print("✓ Model loaded")

        model.eval()
        print("✓ Model set to eval mode")

        return True, tokenizer, model
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return False, None, None

def test_3_simple_inference(tokenizer, model):
    """Test 3: Simple inference"""
    print("\n" + "="*80)
    print("TEST 3: Simple inference")
    print("="*80)
    try:
        import torch

        test_text = "The cat sat on"
        print(f"Input: '{test_text}'")

        inputs = tokenizer(test_text, return_tensors='pt')
        print(f"✓ Tokenized ({len(inputs['input_ids'][0])} tokens)")

        with torch.no_grad():
            outputs = model(**inputs)
        print("✓ Model forward pass completed")

        logits = outputs.logits[0, -1, :]
        print(f"✓ Got logits (shape: {logits.shape})")

        probs = torch.softmax(logits, dim=-1)
        print(f"✓ Computed probabilities (sum: {probs.sum():.4f})")

        top_k_probs, top_k_ids = torch.topk(probs, 10)
        print(f"✓ Got top-10 predictions")

        for i, (prob, token_id) in enumerate(zip(top_k_probs, top_k_ids)):
            token = tokenizer.decode([token_id])
            print(f"  {i+1}. '{token}' (p={prob:.4f})")

        return True
    except Exception as e:
        print(f"✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_spacy():
    """Test 4: spaCy POS tagging"""
    print("\n" + "="*80)
    print("TEST 4: spaCy POS tagging")
    print("="*80)
    try:
        import spacy
        print("✓ spacy imported")

        try:
            nlp = spacy.load("en_core_web_sm")
            print("✓ Model 'en_core_web_sm' loaded")
        except:
            print("Model not found, downloading...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            nlp = spacy.load("en_core_web_sm")
            print("✓ Model downloaded and loaded")

        test_sentence = "I decided to run quickly"
        doc = nlp(test_sentence)
        print(f"✓ Processed: '{test_sentence}'")

        for token in doc:
            print(f"  '{token.text}' → {token.pos_}")

        return True, nlp
    except Exception as e:
        print(f"✗ spaCy failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_5_load_stimuli():
    """Test 5: Load stimuli file"""
    print("\n" + "="*80)
    print("TEST 5: Load stimuli file")
    print("="*80)
    try:
        with open('stimuli_with_scrambled.json', 'r') as f:
            stimuli = json.load(f)

        print(f"✓ Loaded {len(stimuli)} stimulus sets")

        # Check structure
        first = stimuli[0]
        print(f"✓ First stimulus has keys: {list(first.keys())}")

        if 'sentence' in first:
            print(f"  Sample sentence: '{first['sentence'][:60]}...'")
        if 'jabberwocky_matched' in first:
            print(f"  Sample jabberwocky: '{first['jabberwocky_matched'][:60]}...'")

        return True, stimuli
    except Exception as e:
        print(f"✗ Stimuli loading failed: {e}")
        return False, None

def test_6_full_pipeline(tokenizer, model, nlp, stimuli):
    """Test 6: Full pipeline on one stimulus"""
    print("\n" + "="*80)
    print("TEST 6: Full morphosyntax audit pipeline (1 stimulus)")
    print("="*80)
    try:
        import torch

        # Get first sentence
        test_text = stimuli[0]['sentence']
        print(f"Testing: '{test_text}'")

        # Find "to" in the sentence
        words = test_text.split()
        to_index = None
        for i, word in enumerate(words):
            if word.lower().strip('.,!?;:') == 'to':
                to_index = i
                break

        if to_index is None:
            print("  (No 'to' found, skipping to-specific test)")
            return True

        print(f"✓ Found 'to' at word position {to_index}")

        # spaCy POS tagging
        doc = nlp(test_text)
        target_token = list(doc)[to_index]
        print(f"✓ spaCy tagged '{target_token.text}' as {target_token.pos_}")

        # Build context (up to and including "to")
        context = ' '.join(words[:to_index+1])
        print(f"✓ Context: '{context}'")

        # Tokenize and get predictions
        inputs = tokenizer(context, return_tensors='pt')
        print(f"✓ Tokenized to {len(inputs['input_ids'][0])} BPE tokens")

        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits[0, -1, :]
        probs = torch.softmax(logits, dim=-1)
        print(f"✓ Got next-token probabilities")

        # Get top-k
        top_k_probs, top_k_ids = torch.topk(probs, 100)
        print(f"✓ Got top-100 predictions")

        # Classify a few
        verb_mass = 0.0
        noun_mass = 0.0

        # Simple lexicon (minimal for testing)
        VERBS = {'run', 'walk', 'eat', 'sleep', 'make', 'go', 'see', 'get', 'know', 'think'}
        NOUNS = {'cat', 'dog', 'house', 'car', 'book', 'person', 'place', 'thing', 'time', 'way'}

        for prob, token_id in zip(top_k_probs[:20], top_k_ids[:20]):
            token = tokenizer.decode([token_id]).strip().lower()
            if token in VERBS:
                verb_mass += prob.item()
            elif token in NOUNS:
                noun_mass += prob.item()

        print(f"✓ Classified tokens:")
        print(f"  VERB mass (sample): {verb_mass:.4f}")
        print(f"  NOUN mass (sample): {noun_mass:.4f}")

        return True
    except Exception as e:
        print(f"✗ Full pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("SIGBUS CRASH DIAGNOSIS - Minimal Test Suite")
    print("="*80)
    print("\nThis script tests each component incrementally to isolate the crash.")
    print("Watch for where it fails (if it does).")

    # Test 1: Imports
    if not test_1_imports():
        print("\n✗ FAILED at imports")
        return

    # Test 2: Load model
    success, tokenizer, model = test_2_load_model()
    if not success:
        print("\n✗ FAILED at model loading")
        return

    # Test 3: Simple inference
    if not test_3_simple_inference(tokenizer, model):
        print("\n✗ FAILED at simple inference")
        return

    # Test 4: spaCy
    success, nlp = test_4_spacy()
    if not success:
        print("\n✗ FAILED at spaCy")
        return

    # Test 5: Load stimuli
    success, stimuli = test_5_load_stimuli()
    if not success:
        print("\n✗ FAILED at stimuli loading")
        return

    # Test 6: Full pipeline
    if not test_6_full_pipeline(tokenizer, model, nlp, stimuli):
        print("\n✗ FAILED at full pipeline")
        return

    # Success!
    print("\n" + "="*80)
    print("✓ ALL TESTS PASSED!")
    print("="*80)
    print("\nNo SIGBUS crash detected in minimal tests.")
    print("This suggests the crash may be related to:")
    print("  - Processing many stimuli in sequence (memory accumulation)")
    print("  - Specific text patterns in the full dataset")
    print("  - macOS-specific memory handling with repeated inference")
    print("\nRecommendation: Still use Colab for full audit.")

if __name__ == '__main__':
    main()
