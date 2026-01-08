"""
Verify that key qualitative orderings hold under both aggregation methods.

Tests:
1. Word-mean (average of mean entropy per word)
2. Word-sum (average of summed entropy per word)

Key comparisons to verify:
- Jabberwocky vs Scrambled Jabberwocky
- Sentence vs Swapped Function Words
- Overall structural hierarchy

If both methods produce the same qualitative ordering, this demonstrates
robustness to aggregation methodology.
"""

import torch
import numpy as np
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from word_aligned_metrics import process_text_with_word_metrics
from collections import defaultdict

def run_verification_experiment(stimuli_file='stimuli_tokenization_matched_normalized.json',
                                model_name='gpt2',
                                n_items=5):
    """
    Run experiment on subset of stimuli and verify aggregation robustness.
    """
    print("=" * 80)
    print("AGGREGATION ROBUSTNESS VERIFICATION")
    print("=" * 80)
    print(f"\nModel: {model_name}")
    print(f"Testing on first {n_items} stimulus sets\n")

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Loading model... (device: {device})")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    # Use subset for quick verification
    stimuli = stimuli[:n_items]

    # Storage for results
    results = {
        'word_mean': defaultdict(list),
        'word_sum': defaultdict(list)
    }

    # Process each stimulus set
    print("\nProcessing stimulus sets...")
    for item in stimuli:
        set_id = item['set_id']
        print(f"  Set {set_id}...", end='\r')

        for condition in ['sentence', 'jabberwocky_matched',
                         'word_list_real', 'skeleton_function_words',
                         'scrambled_jabberwocky', 'swapped_function_words']:
            if condition not in item:
                continue

            text = item[condition]
            metrics = process_text_with_word_metrics(model, tokenizer, text, device)

            # Store both aggregation methods
            results['word_mean'][condition].append(metrics['mean_word_entropy'])
            results['word_sum'][condition].append(metrics['mean_word_entropy_sum'])

    print("\nProcessing complete!\n")

    # Compute means for each condition under both methods
    print("=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)

    condition_order = ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky',
                      'swapped_function_words', 'skeleton_function_words', 'word_list_real']

    print(f"\n{'Condition':30s} | {'Word-Mean':>12s} | {'Word-Sum':>12s} | {'Rank-Mean':>10s} | {'Rank-Sum':>10s}")
    print("-" * 85)

    means_word_mean = {}
    means_word_sum = {}

    for cond in condition_order:
        if cond in results['word_mean'] and results['word_mean'][cond]:
            mean_wm = np.mean(results['word_mean'][cond])
            mean_ws = np.mean(results['word_sum'][cond])
            means_word_mean[cond] = mean_wm
            means_word_sum[cond] = mean_ws

    # Compute ranks
    sorted_wm = sorted(means_word_mean.items(), key=lambda x: x[1])
    sorted_ws = sorted(means_word_sum.items(), key=lambda x: x[1])

    ranks_wm = {cond: i+1 for i, (cond, _) in enumerate(sorted_wm)}
    ranks_ws = {cond: i+1 for i, (cond, _) in enumerate(sorted_ws)}

    for cond in condition_order:
        if cond in means_word_mean:
            print(f"{cond:30s} | {means_word_mean[cond]:12.4f} | {means_word_sum[cond]:12.4f} | "
                  f"{ranks_wm[cond]:10d} | {ranks_ws[cond]:10d}")

    # Key comparisons
    print("\n" + "=" * 80)
    print("KEY QUALITATIVE COMPARISONS")
    print("=" * 80)

    comparisons = [
        ('sentence', 'swapped_function_words',
         'Sentence < Swapped Function Words',
         'Tests: Does removing proper function words increase entropy?'),
        ('jabberwocky_matched', 'scrambled_jabberwocky',
         'Jabberwocky < Scrambled Jabberwocky',
         'Tests: Does syntactic structure reduce entropy in nonsense?'),
        ('sentence', 'jabberwocky_matched',
         'Sentence < Jabberwocky',
         'Tests: Does semantics reduce entropy beyond syntax?'),
    ]

    all_pass = True

    for cond1, cond2, expected, description in comparisons:
        if cond1 in means_word_mean and cond2 in means_word_mean:
            # Test word-mean
            wm_holds = means_word_mean[cond1] < means_word_mean[cond2]
            wm_diff = means_word_mean[cond2] - means_word_mean[cond1]

            # Test word-sum
            ws_holds = means_word_sum[cond1] < means_word_sum[cond2]
            ws_diff = means_word_sum[cond2] - means_word_sum[cond1]

            # Both should agree
            agreement = wm_holds == ws_holds

            print(f"\n{description}")
            print(f"Expected: {expected}")
            print(f"  Word-Mean: {cond1} = {means_word_mean[cond1]:.4f}, "
                  f"{cond2} = {means_word_mean[cond2]:.4f}")
            print(f"             Difference = {wm_diff:+.4f} | Holds: {wm_holds}")
            print(f"  Word-Sum:  {cond1} = {means_word_sum[cond1]:.4f}, "
                  f"{cond2} = {means_word_sum[cond2]:.4f}")
            print(f"             Difference = {ws_diff:+.4f} | Holds: {ws_holds}")
            print(f"  Agreement: {'✓ YES' if agreement else '✗ NO'}")

            if not agreement:
                all_pass = False

    # Overall verdict
    print("\n" + "=" * 80)
    if all_pass:
        print("✓ ROBUSTNESS VERIFIED: Key orderings hold under both methods")
    else:
        print("⚠ WARNING: Some orderings differ between aggregation methods")
    print("=" * 80)

    return results, means_word_mean, means_word_sum

def analyze_full_results(results_file):
    """
    Analyze full experimental results for aggregation robustness.
    """
    print("=" * 80)
    print("FULL RESULTS AGGREGATION ANALYSIS")
    print("=" * 80)

    with open(results_file, 'r') as f:
        results = json.load(f)

    # Collect data
    data_wm = defaultdict(list)
    data_ws = defaultdict(list)

    for item in results:
        for condition, metrics in item['conditions'].items():
            data_wm[condition].append(metrics['mean_word_entropy'])
            data_ws[condition].append(metrics['mean_word_entropy_sum'])

    # Compute means and report
    print(f"\n{'Condition':30s} | {'Word-Mean':>12s} | {'Word-Sum':>12s}")
    print("-" * 60)

    for condition in sorted(data_wm.keys()):
        mean_wm = np.mean(data_wm[condition])
        mean_ws = np.mean(data_ws[condition])
        print(f"{condition:30s} | {mean_wm:12.4f} | {mean_ws:12.4f}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Verify aggregation robustness')
    parser.add_argument('--model', type=str, default='gpt2',
                       help='Model to test (gpt2, gpt2-medium, etc.)')
    parser.add_argument('--n-items', type=int, default=5,
                       help='Number of stimulus sets to test (default: 5 for quick check)')
    parser.add_argument('--stimuli', type=str, default='stimuli_tokenization_matched_normalized.json',
                       help='Stimuli file to use')
    parser.add_argument('--analyze-results', type=str,
                       help='Analyze existing results file instead of running new experiment')

    args = parser.parse_args()

    if args.analyze_results:
        analyze_full_results(args.analyze_results)
    else:
        run_verification_experiment(
            stimuli_file=args.stimuli,
            model_name=args.model,
            n_items=args.n_items
        )
