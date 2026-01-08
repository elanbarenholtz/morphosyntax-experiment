"""
Fix for GPT-2-medium NaN issue - explicitly use float32.
"""

import torch
import numpy as np
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def calculate_entropy(logits):
    """Calculate Shannon entropy from logits."""
    probs = torch.softmax(logits, dim=-1)
    log_probs = torch.log2(probs + 1e-10)
    entropy = -(probs * log_probs).sum().item()
    return entropy

def get_token_probabilities(model, tokenizer, text, device='cpu'):
    """Get token-by-token probabilities."""
    inputs = tokenizer(text, return_tensors="pt").to(device)
    input_ids = inputs['input_ids']

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits

    token_data = []

    for i in range(input_ids.shape[1]):
        token_id = input_ids[0, i].item()
        token_str = tokenizer.decode([token_id])

        if i < input_ids.shape[1] - 1:
            next_token_logits = logits[0, i, :]

            entropy = calculate_entropy(next_token_logits)

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
                   model_name='gpt2-medium'):
    """Run experiment with explicit float32 dtype."""
    print("="*80)
    print("MORPHOSYNTAX EXPERIMENT - GPT-2-MEDIUM FIX")
    print("="*80)
    print(f"\nLoading model: {model_name}")

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load with explicit dtype and low_cpu_mem_usage
    print("Loading model with torch_dtype=torch.float32...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True
    ).to(device)
    model.eval()

    print(f"Model loaded successfully!\\n")

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets")
    print(f"Total items: {len(stimuli) * 4}\\n")

    results = []

    for stim_set in tqdm(stimuli, desc="Processing stimulus sets"):
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

        # Save progress every 5 sets
        if stim_set['set_id'] % 5 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

    # Final save
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\\n\\nExperiment complete!")
    print(f"Results saved to: {output_file}\\n")

    # Summary
    print("="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

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
    run_experiment(
        stimuli_file='stimuli_controlled.json',
        output_file='experiment_results_gpt2_medium_fixed.json',
        model_name='gpt2-medium'
    )
