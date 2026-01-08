"""
Morphosyntax experiment using LOCAL MODEL (GPT-2).
This gives us actual token-by-token probabilities as the model processes input.

NOW WITH WORD-ALIGNED METRICS:
- Token-level: entropy + surprisal (secondary)
- Word-level: entropy + surprisal aggregated per word (primary)
"""

import torch
import numpy as np
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import warnings
from word_aligned_metrics import process_text_with_word_metrics
warnings.filterwarnings('ignore')

def get_text_metrics(model, tokenizer, text, device='cpu'):
    """
    Get comprehensive metrics with word-level aggregation.

    Returns both token-level (secondary) and word-level (primary) metrics,
    including entropy and surprisal.
    """
    return process_text_with_word_metrics(model, tokenizer, text, device)

def run_experiment(stimuli_file='stimuli.json', output_file='experiment_results_local.json',
                   model_name='gpt2'):
    """
    Run the morphosyntax experiment using a local model.
    """
    print("=" * 80)
    print("MORPHOSYNTAX EXPERIMENT - LOCAL MODEL")
    print("=" * 80)
    print(f"\nLoading model: {model_name}")

    # Load model and tokenizer
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    print(f"Model loaded successfully!\n")

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets")
    print(f"Total items: {len(stimuli) * 4}")
    print()

    # Results storage
    results = []

    # Process each stimulus set
    for stim_set in tqdm(stimuli, desc="Processing stimulus sets"):
        set_results = {
            'set_id': stim_set['set_id'],
            'conditions': {}
        }

        # Process each condition
        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords',
                          'scrambled_jabberwocky', 'swapped_function_words']:
            if condition not in stim_set:
                continue

            text = stim_set[condition]

            # Get comprehensive metrics
            metrics = get_text_metrics(model, tokenizer, text, device)

            # Store results with both token-level and word-level metrics
            set_results['conditions'][condition] = {
                'text': text,

                # Token-level metrics (secondary)
                'n_tokens': metrics['n_tokens'],
                'mean_token_entropy': metrics['mean_token_entropy'],
                'mean_token_surprisal': metrics['mean_token_surprisal'],

                # Word-level metrics (primary)
                'n_words': metrics['n_words'],
                'mean_word_entropy': metrics['mean_word_entropy'],
                'mean_word_surprisal': metrics['mean_word_surprisal'],
                'mean_word_entropy_sum': metrics['mean_word_entropy_sum'],
                'mean_word_surprisal_sum': metrics['mean_word_surprisal_sum'],
            }

        results.append(set_results)

        # Save intermediate results every 5 sets
        if stim_set['set_id'] % 5 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nExperiment complete!")
    print(f"Results saved to: {output_file}\n")

    # Print summary statistics (both aggregation methods for robustness)
    print("=" * 80)
    print("SUMMARY STATISTICS - WORD-LEVEL METRICS")
    print("=" * 80)

    # Collect available conditions dynamically
    all_conditions = set()
    for result in results:
        all_conditions.update(result['conditions'].keys())

    condition_entropy_mean = {c: [] for c in all_conditions}
    condition_entropy_sum = {c: [] for c in all_conditions}

    for result in results:
        for condition in all_conditions:
            if condition in result['conditions']:
                # Collect both aggregation methods
                ent_mean = result['conditions'][condition]['mean_word_entropy']
                ent_sum = result['conditions'][condition]['mean_word_entropy_sum']
                condition_entropy_mean[condition].append(ent_mean)
                condition_entropy_sum[condition].append(ent_sum)

    print(f"\n{'Condition':30s} | {'Word-Mean':>15s} | {'Word-Sum':>15s}")
    print("-" * 70)

    for condition in sorted(all_conditions):
        if condition_entropy_mean[condition]:
            mean_wm = np.mean(condition_entropy_mean[condition])
            std_wm = np.std(condition_entropy_mean[condition])
            mean_ws = np.mean(condition_entropy_sum[condition])
            std_ws = np.std(condition_entropy_sum[condition])
            print(f"{condition:30s} | {mean_wm:6.3f} ± {std_wm:5.3f} | {mean_ws:6.3f} ± {std_ws:5.3f}")

    print(f"\nNote: Both aggregation methods shown for robustness verification.")
    print(f"Word-Mean = average of mean entropy per word")
    print(f"Word-Sum  = average of summed entropy per word")

    return results

def diagnostic_single_example(stimuli_file='stimuli.json', set_id=1, model_name='gpt2'):
    """
    Run detailed diagnostic on a single stimulus set.
    """
    print("\n" + "=" * 80)
    print(f"DIAGNOSTIC ANALYSIS: STIMULUS SET {set_id}")
    print("=" * 80 + "\n")

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    stim_set = [s for s in stimuli if s['set_id'] == set_id][0]

    # Analyze each condition
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords',
                      'scrambled_jabberwocky', 'swapped_function_words']:
        text = stim_set[condition]

        print(f"\n{'*' * 80}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'*' * 80}")
        print(f"\nText: {text}\n")

        prob_data = get_token_probabilities(model, tokenizer, text, device)

        print(f"Number of tokens: {prob_data['num_tokens']}")
        print(f"Mean entropy: {prob_data['mean_entropy']:.4f} bits")
        print(f"Mean next-token probability: {prob_data['mean_next_token_prob']:.4f}\n")

        # Show tokenization
        print("Tokenization:")
        print(f"{'Pos':>4} | {'Token':20} | {'Next Token':20} | {'Prob':>8} | {'Rank':>5} | {'Entropy':>8}")
        print("-" * 90)
        for tok in prob_data['token_data'][:15]:  # Show first 15 tokens
            print(f"{tok['position']:4} | {repr(tok['token']):20} | {repr(tok['next_token']):20} | "
                  f"{tok['next_token_prob']:8.4f} | {tok['next_token_rank']:5} | {tok['entropy']:8.4f}")
        if len(prob_data['token_data']) > 15:
            print(f"... ({len(prob_data['token_data']) - 15} more tokens)")

        # Show detailed predictions at a few positions
        positions_to_show = [0, len(prob_data['token_data']) // 2, len(prob_data['token_data']) - 1]

        for pos in positions_to_show:
            if pos < len(prob_data['token_data']):
                tok = prob_data['token_data'][pos]
                print(f"\n{'-' * 80}")
                print(f"Position {pos}: After token {repr(tok['token'])}")
                print(f"Actual next token: {repr(tok['next_token'])} (prob={tok['next_token_prob']:.4f}, rank={tok['next_token_rank']})")
                print(f"Entropy: {tok['entropy']:.4f} bits")
                print(f"{'-' * 80}")
                print(f"{'Rank':>4} | {'Predicted Token':20} | {'Probability':>12}")
                print("-" * 50)
                for rank, pred in enumerate(tok['top_predictions'][:10], 1):
                    print(f"{rank:4} | {repr(pred['token']):20} | {pred['prob']:12.6f}")

        print("\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run morphosyntax experiment with local model')
    parser.add_argument('--model', type=str, default='gpt2',
                       help='Model name (gpt2, gpt2-medium, gpt2-large, gpt2-xl)')
    parser.add_argument('--diagnostic', action='store_true',
                       help='Run diagnostic analysis on first stimulus set')
    parser.add_argument('--set-id', type=int, default=1,
                       help='Stimulus set ID for diagnostic (default: 1)')

    args = parser.parse_args()

    if args.diagnostic:
        diagnostic_single_example(set_id=args.set_id, model_name=args.model)
    else:
        run_experiment(model_name=args.model)
