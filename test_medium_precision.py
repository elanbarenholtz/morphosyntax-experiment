"""
Test different precision settings for GPT-2-medium to fix NaN logits.
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_precision_mode(model_name, text, dtype=None, device='cpu'):
    """Test model with specific precision settings."""
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    if dtype:
        print(f"dtype: {dtype}")
    print(f"device: {device}")
    print(f"{'='*80}")

    # Load model with explicit dtype
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if dtype:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            low_cpu_mem_usage=True
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    model = model.to(device)
    model.eval()

    # Tokenize
    encoding = tokenizer(text, return_tensors="pt", add_special_tokens=False)
    input_ids = encoding['input_ids'].to(device)

    print(f"\nText: {text}")
    print(f"Tokens: {tokenizer.convert_ids_to_tokens(input_ids[0])}")

    # Get logits
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits

    # Check first token
    first_token_logits = logits[0, 0, :]

    print(f"\nFirst token logits stats:")
    print(f"  dtype: {first_token_logits.dtype}")
    print(f"  Min: {first_token_logits.min().item():.4f}")
    print(f"  Max: {first_token_logits.max().item():.4f}")
    print(f"  Mean: {first_token_logits.mean().item():.4f}")
    print(f"  Has inf: {torch.isinf(first_token_logits).any().item()}")
    print(f"  Has nan: {torch.isnan(first_token_logits).any().item()}")

    # Try softmax
    probs = torch.softmax(first_token_logits, dim=-1)
    print(f"\nProbabilities:")
    print(f"  Has inf: {torch.isinf(probs).any().item()}")
    print(f"  Has nan: {torch.isnan(probs).any().item()}")

    return not torch.isnan(first_token_logits).any().item()


if __name__ == "__main__":
    test_text = "The snirpy fleem gorped the blonk."

    # Test 1: Default loading
    print("\n" + "="*80)
    print("TEST 1: Default loading (no dtype specified)")
    print("="*80)
    success1 = test_precision_mode('gpt2-medium', test_text)

    # Test 2: Explicit float32
    print("\n" + "="*80)
    print("TEST 2: Explicit float32")
    print("="*80)
    success2 = test_precision_mode('gpt2-medium', test_text, dtype=torch.float32)

    # Test 3: Float16 (if that's what was causing issues)
    print("\n" + "="*80)
    print("TEST 3: Float16 (to see if this causes the issue)")
    print("="*80)
    success3 = test_precision_mode('gpt2-medium', test_text, dtype=torch.float16)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Default loading:    {'✓ WORKS' if success1 else '✗ NaN'}")
    print(f"Explicit float32:   {'✓ WORKS' if success2 else '✗ NaN'}")
    print(f"Float16:            {'✓ WORKS' if success3 else '✗ NaN'}")
