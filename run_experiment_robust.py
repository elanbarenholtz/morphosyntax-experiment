"""
ROBUST version with fixed entropy calculation.
"""

import torch
import numpy as np
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def calculate_entropy_robust(logits):
    """
    Calculate Shannon entropy with numerical stability.
    """
    # Convert logits to probabilities with numerical stability
    logits_max = logits.max()
    exp_logits = torch.exp(logits - logits_max)  # Subtract max for stability
    probs = exp_logits / exp_logits.sum()

    # Calculate entropy in bits with epsilon to avoid log(0)
    epsilon = 1e-10
    log_probs = torch.log2(probs + epsilon)
    entropy = -(probs * log_probs).sum().item()

    # Sanity check
    if np.isnan(entropy) or np.isinf(entropy):
        return 0.0

    return entropy

def get_token_probabilities(model, tokenizer, text, device='cpu'):
    """Get token-by-token probabilities."""
    # Tokenize
    inputs = tokenizer(text, return_tensors="pt").to(device)
    input_ids = inputs['input_ids']

    # Get model outputs
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits

    token_data = []

    for i in range(input_ids.shape[1]):
        token_id = input_ids[0, i].item()
        token_str = tokenizer.decode([token_id])

        # Get logits for next token
        if i < input_ids.shape[1] - 1:
            next_token_logits = logits[0, i, :]

            # Calculate entropy with robust function
            entropy = calculate_entropy_robust(next_token_logits)

            # Get top predictions
            probs = torch.softmax(next_token_logits, dim=-1)
            top_k_probs, top_k_indices = torch.topk(probs, k=20)

            top_predictions = []
            for prob, idx in zip(top_k_probs, top_k_indices):
                pred_token = tokenizer.decode([idx.item()])
                top_predictions.append({
                    'token': pred_token,
                    'prob': prob.item(),
                    'logprob': torch.log(prob).item() if prob > 0 else -100
                })

            # Get actual next token
            next_token_id = input_ids[0, i + 1].item()
            next_token_prob = probs[next_token_id].item()
            next_token_rank = (probs > next_token_prob).sum().item() + 1

            token_data.append({
                'position': i,
                'token': token_str,
                'token_id': token_id,
                'next_token': tokenizer.decode([next_token_id]),
                'next_token_prob': next_token_prob,
                'next_token_rank': next_token_rank,
                'entropy': entropy,
                'top_predictions': top_predictions
            })

    return {
        'text': text,
        'tokens': [tokenizer.decode([id]) for id in input_ids[0]],
        'token_ids': input_ids[0].tolist(),
        'num_tokens': input_ids.shape[1],
        'token_data': token_data,
        'mean_entropy': np.mean([t['entropy'] for t in token_data]) if token_data else 0,
        'mean_next_token_prob': np.mean([t['next_token_prob'] for t in token_data]) if token_data else 0
    }

def run_experiment(stimuli_file='stimuli_controlled.json',
                   output_file='experiment_results.json',
                   model_name='gpt2'):
    """Run experiment."""
    print("=" * 80)
    print("MORPHOSYNTAX EXPERIMENT - ROBUST VERSION")
    print("=" * 80)
    print(f"\nLoading model: {model_name}")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    print(f"Model loaded successfully!\n")

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets\n")

    results = []

    for stim_set in tqdm(stimuli, desc="Processing"):
        set_results = {
            'set_id': stim_set['set_id'],
            'conditions': {}
        }

        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
            text = stim_set[condition]

            prob_data = get_token_probabilities(model, tokenizer, text, device)

            set_results['conditions'][condition] = {
                'text': text,
                'tokens': prob_data['tokens'],
                'num_tokens': prob_data['num_tokens'],
                'mean_entropy': prob_data['mean_entropy'],
                'mean_next_token_prob': prob_data['mean_next_token_prob'],
                'token_entropies': [t['entropy'] for t in prob_data['token_data']],
                'token_probs': [t['next_token_prob'] for t in prob_data['token_data']]
            }

        results.append(set_results)

        if stim_set['set_id'] % 5 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

    # Final save
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {output_file}\n")

    # Summary
    print("=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    condition_entropies = {'sentence': [], 'jabberwocky': [], 'stripped': [], 'nonwords': []}

    for result in results:
        for condition in condition_entropies.keys():
            if condition in result['conditions']:
                mean_ent = result['conditions'][condition]['mean_entropy']
                condition_entropies[condition].append(mean_ent)

    for condition, entropies in condition_entropies.items():
        if entropies:
            mean = np.mean(entropies)
            std = np.std(entropies)
            print(f"{condition:15s}: {mean:.3f} ± {std:.3f} bits")

    return results

if __name__ == "__main__":
    import sys
    model_name = sys.argv[1] if len(sys.argv) > 1 else 'gpt2'
    output_file = f'experiment_results_{model_name.replace("-", "_")}_robust.json'

    run_experiment(
        stimuli_file='stimuli_controlled.json',
        output_file=output_file,
        model_name=model_name
    )
