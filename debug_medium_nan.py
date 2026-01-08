"""
Minimal test script to isolate GPT-2-medium NaN bug.
Compares gpt2-medium vs gpt2-large on identical input.
"""

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForCausalLM

def test_model_entropy(model_name, text):
    """Test entropy calculation for a specific model."""
    print(f"\n{'='*80}")
    print(f"Testing: {model_name}")
    print(f"{'='*80}")

    # Load model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    # Tokenize
    encoding = tokenizer(text, return_tensors="pt", add_special_tokens=False)
    input_ids = encoding['input_ids']

    print(f"\nText: {text}")
    print(f"Tokens: {tokenizer.convert_ids_to_tokens(input_ids[0])}")
    print(f"Token IDs: {input_ids[0].tolist()}")

    # Get logits
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits

    print(f"\nLogits shape: {logits.shape}")

    # Test first token prediction
    first_token_logits = logits[0, 0, :]
    actual_next_token = input_ids[0, 1].item()

    print(f"\nFirst token logits stats:")
    print(f"  Min: {first_token_logits.min().item():.4f}")
    print(f"  Max: {first_token_logits.max().item():.4f}")
    print(f"  Mean: {first_token_logits.mean().item():.4f}")
    print(f"  Has inf: {torch.isinf(first_token_logits).any().item()}")
    print(f"  Has nan: {torch.isnan(first_token_logits).any().item()}")

    # Softmax
    probs = torch.softmax(first_token_logits, dim=-1)
    print(f"\nProbabilities stats:")
    print(f"  Min: {probs.min().item():.10f}")
    print(f"  Max: {probs.max().item():.10f}")
    print(f"  Sum: {probs.sum().item():.10f}")
    print(f"  Has inf: {torch.isinf(probs).any().item()}")
    print(f"  Has nan: {torch.isnan(probs).any().item()}")

    # Entropy calculation
    log_probs = torch.log2(probs + 1e-10)
    print(f"\nLog probabilities stats:")
    print(f"  Min: {log_probs.min().item():.4f}")
    print(f"  Max: {log_probs.max().item():.4f}")
    print(f"  Has inf: {torch.isinf(log_probs).any().item()}")
    print(f"  Has nan: {torch.isnan(log_probs).any().item()}")

    entropy_tensor = -(probs * log_probs).sum()
    entropy = entropy_tensor.item()

    print(f"\nEntropy calculation:")
    print(f"  Entropy tensor: {entropy_tensor}")
    print(f"  Entropy value: {entropy}")
    print(f"  Is nan: {np.isnan(entropy)}")

    # Surprisal
    actual_prob = probs[actual_next_token].item()
    surprisal = -np.log2(actual_prob + 1e-10)

    print(f"\nSurprisal calculation:")
    print(f"  Actual next token: {actual_next_token}")
    print(f"  Actual token prob: {actual_prob:.10f}")
    print(f"  Surprisal: {surprisal:.4f}")

    return entropy, surprisal


if __name__ == "__main__":
    # Use a simple test text from jabberwocky condition
    test_text = "The snirpy fleem gorped the blonk."

    # Test both models
    entropy_large, surprisal_large = test_model_entropy('gpt2-large', test_text)
    entropy_medium, surprisal_medium = test_model_entropy('gpt2-medium', test_text)

    print(f"\n{'='*80}")
    print("COMPARISON")
    print(f"{'='*80}")
    print(f"\nGPT-2-large:  Entropy={entropy_large:.4f}, Surprisal={surprisal_large:.4f}")
    print(f"GPT-2-medium: Entropy={entropy_medium:.4f}, Surprisal={surprisal_medium:.4f}")
