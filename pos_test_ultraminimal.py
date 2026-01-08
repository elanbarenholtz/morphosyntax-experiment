"""
Ultra-minimal test - just load model and get predictions
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

print("Starting...")
print(f"PyTorch version: {torch.__version__}")

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained('gpt2')
print("Tokenizer loaded.")

print("Loading model...")
model = AutoModelForCausalLM.from_pretrained('gpt2')
model.eval()
print("Model loaded.")

print("Testing prediction...")
text = "The cat"
inputs = tokenizer(text, return_tensors='pt')
with torch.no_grad():
    outputs = model(**inputs)
    next_token_logits = outputs.logits[0, -1, :]
    probs = torch.softmax(next_token_logits, dim=-1)
    top_5_probs, top_5_ids = torch.topk(probs, 5)

print("\nTop 5 predictions after 'The cat':")
for prob, token_id in zip(top_5_probs, top_5_ids):
    token_str = tokenizer.decode([token_id])
    print(f"  {token_str:15s} {prob.item()*100:.1f}%")

print("\nSUCCESS!")
