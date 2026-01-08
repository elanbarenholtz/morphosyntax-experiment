"""Quick test of GPT-2-XL"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

print("Testing GPT-2-XL...")
tokenizer = AutoTokenizer.from_pretrained('gpt2-xl')
model = AutoModelForCausalLM.from_pretrained('gpt2-xl')
model.eval()

text = "The cat sat on the mat"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(inputs['input_ids'], labels=inputs['input_ids'])
    logits = outputs.logits

first_logits = logits[0, 0, :]
print(f"Logits stats:")
print(f"  Min: {first_logits.min().item()}")
print(f"  Max: {first_logits.max().item()}")
print(f"  Has NaN: {torch.isnan(first_logits).any().item()}")
print(f"  Has Inf: {torch.isinf(first_logits).any().item()}")

probs = torch.softmax(first_logits, dim=-1)
entropy = -(probs * torch.log2(probs + 1e-10)).sum().item()
print(f"  Entropy: {entropy:.3f}")

if not torch.isnan(first_logits).any() and not torch.isinf(first_logits).any():
    print("\n✅ GPT-2-XL works! We can use this instead of medium.")
else:
    print("\n❌ GPT-2-XL also has issues.")
