"""Debug why GPT-2-medium produces NaN entropies."""

import torch
import numpy as np
from transformers import AutoModelForCausalLM, AutoTokenizer

def test_model(model_name):
    print(f"\n{'='*60}")
    print(f"Testing: {model_name}")
    print('='*60)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    text = "The cat sat on the mat"
    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        outputs = model(inputs['input_ids'], labels=inputs['input_ids'])
        logits = outputs.logits

    print(f"Input shape: {inputs['input_ids'].shape}")
    print(f"Logits shape: {logits.shape}")

    # Check first position logits
    first_logits = logits[0, 0, :]
    print(f"\nFirst position logits stats:")
    print(f"  Min: {first_logits.min().item()}")
    print(f"  Max: {first_logits.max().item()}")
    print(f"  Mean: {first_logits.mean().item()}")
    print(f"  Has NaN: {torch.isnan(first_logits).any().item()}")
    print(f"  Has Inf: {torch.isinf(first_logits).any().item()}")

    # Try softmax
    probs = torch.softmax(first_logits, dim=-1)
    print(f"\nProbabilities stats:")
    print(f"  Min: {probs.min().item()}")
    print(f"  Max: {probs.max().item()}")
    print(f"  Sum: {probs.sum().item()}")
    print(f"  Has NaN: {torch.isnan(probs).any().item()}")
    print(f"  Has Inf: {torch.isinf(probs).any().item()}")

    # Try entropy calculation
    log_probs = torch.log2(probs + 1e-10)
    entropy = -(probs * log_probs).sum().item()
    print(f"\nEntropy calculation:")
    print(f"  log_probs has NaN: {torch.isnan(log_probs).any().item()}")
    print(f"  product has NaN: {torch.isnan(probs * log_probs).any().item()}")
    print(f"  Entropy: {entropy}")

    # Alternative entropy calculation
    print(f"\nAlternative calculation:")
    mask = probs > 0
    safe_log_probs = torch.zeros_like(probs)
    safe_log_probs[mask] = torch.log2(probs[mask])
    alt_entropy = -(probs * safe_log_probs).sum().item()
    print(f"  Alternative entropy: {alt_entropy}")

if __name__ == "__main__":
    for model_name in ['gpt2', 'gpt2-medium', 'gpt2-large']:
        try:
            test_model(model_name)
        except Exception as e:
            print(f"Error with {model_name}: {e}")
