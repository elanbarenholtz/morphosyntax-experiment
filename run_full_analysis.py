"""
Complete analysis pipeline for morphosyntax experiment.

Computes:
1. Results table with word-mean entropy, word-mean surprisal (+ token-level)
2. Signature effect sizes: Δ(Sentence - Jabberwocky), Δ(Jabberwocky - Scrambled)
3. Position-wise curves (word-aligned) for surprisal buildup
"""

import torch
import numpy as np
import json
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
from collections import defaultdict
from word_aligned_metrics import process_text_with_word_metrics
import warnings
warnings.filterwarnings('ignore')

def run_full_experiment(stimuli_file='stimuli_context_matched.json',
                       output_file='experiment_results_final.json',
                       model_name='gpt2'):
    """
    Run complete experiment with word-aligned metrics.
    """
    print("=" * 80)
    print(f"MORPHOSYNTAX EXPERIMENT - FINAL ANALYSIS")
    print("=" * 80)
    print(f"\nModel: {model_name}")
    print(f"Stimuli: {stimuli_file}")

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\nLoading model... (device: {device})")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets\n")

    # Process all stimuli
    results = []

    for item in tqdm(stimuli, desc="Processing stimuli"):
        set_results = {
            'set_id': item['set_id'],
            'conditions': {}
        }

        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky',
                         'word_list_real', 'skeleton_function_words',
                         'word_list_nonce_1tok', 'word_list_nonce_2tok']:
            if condition in item:
                text = item[condition]
                metrics = process_text_with_word_metrics(model, tokenizer, text, device)

                # Store comprehensive metrics
                set_results['conditions'][condition] = {
                    'text': text,
                    # Token-level (secondary)
                    'n_tokens': metrics['n_tokens'],
                    'mean_token_entropy': metrics['mean_token_entropy'],
                    'mean_token_surprisal': metrics['mean_token_surprisal'],
                    # Word-level (primary)
                    'n_words': metrics['n_words'],
                    'mean_word_entropy': metrics['mean_word_entropy'],
                    'mean_word_surprisal': metrics['mean_word_surprisal'],
                    'mean_word_entropy_sum': metrics['mean_word_entropy_sum'],
                    'mean_word_surprisal_sum': metrics['mean_word_surprisal_sum'],
                    # Per-word details for position analysis
                    'word_entropies': metrics.get('word_entropies_mean', []),
                    'word_surprisals': metrics.get('word_surprisals_mean', []),
                }

        results.append(set_results)

        # Save intermediate results
        if item['set_id'] % 10 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nExperiment complete!")
    print(f"Results saved to: {output_file}\n")

    return results

def analyze_results(results_file, output_prefix):
    """
    Analyze results and generate:
    1. Summary table
    2. Effect sizes
    3. Position-wise curves
    """
    print("=" * 80)
    print("RESULTS ANALYSIS")
    print("=" * 80)

    with open(results_file, 'r') as f:
        results = json.load(f)

    # ========================================================================
    # 1. SUMMARY TABLE
    # ========================================================================
    print("\n" + "=" * 80)
    print("1. SUMMARY TABLE - WORD-LEVEL METRICS (PRIMARY)")
    print("=" * 80)

    # Collect metrics by condition
    condition_metrics = defaultdict(lambda: {
        'word_entropy': [],
        'word_surprisal': [],
        'token_entropy': [],
        'token_surprisal': []
    })

    for item in results:
        for condition, data in item['conditions'].items():
            condition_metrics[condition]['word_entropy'].append(data['mean_word_entropy'])
            condition_metrics[condition]['word_surprisal'].append(data['mean_word_surprisal'])
            condition_metrics[condition]['token_entropy'].append(data['mean_token_entropy'])
            condition_metrics[condition]['token_surprisal'].append(data['mean_token_surprisal'])

    # Print table
    print(f"\n{'Condition':30s} | {'Word-Mean Entropy':>18s} | {'Word-Mean Surprisal':>20s}")
    print("-" * 75)

    condition_order = ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky',
                      'word_list_real', 'skeleton_function_words',
                      'word_list_nonce_1tok', 'word_list_nonce_2tok']

    summary_stats = {}

    for condition in condition_order:
        if condition in condition_metrics:
            ent_vals = condition_metrics[condition]['word_entropy']
            surp_vals = condition_metrics[condition]['word_surprisal']

            ent_mean = np.mean(ent_vals)
            ent_se = np.std(ent_vals) / np.sqrt(len(ent_vals))
            surp_mean = np.mean(surp_vals)
            surp_se = np.std(surp_vals) / np.sqrt(len(surp_vals))

            summary_stats[condition] = {
                'entropy_mean': ent_mean,
                'entropy_se': ent_se,
                'surprisal_mean': surp_mean,
                'surprisal_se': surp_se
            }

            print(f"{condition:30s} | {ent_mean:7.3f} ± {ent_se:5.3f} | {surp_mean:7.3f} ± {surp_se:5.3f}")

    # Token-level (secondary)
    print("\n" + "=" * 80)
    print("TOKEN-LEVEL METRICS (SECONDARY)")
    print("=" * 80)

    print(f"\n{'Condition':30s} | {'Token-Mean Entropy':>18s} | {'Token-Mean Surprisal':>20s}")
    print("-" * 75)

    for condition in condition_order:
        if condition in condition_metrics:
            ent_vals = condition_metrics[condition]['token_entropy']
            surp_vals = condition_metrics[condition]['token_surprisal']

            ent_mean = np.mean(ent_vals)
            ent_se = np.std(ent_vals) / np.sqrt(len(ent_vals))
            surp_mean = np.mean(surp_vals)
            surp_se = np.std(surp_vals) / np.sqrt(len(surp_vals))

            print(f"{condition:30s} | {ent_mean:7.3f} ± {ent_se:5.3f} | {surp_mean:7.3f} ± {surp_se:5.3f}")

    # ========================================================================
    # 2. SIGNATURE EFFECT SIZES
    # ========================================================================
    print("\n" + "=" * 80)
    print("2. SIGNATURE EFFECT SIZES")
    print("=" * 80)

    # Effect 1: Δ(Sentence - Jabberwocky) - semantic contribution
    if 'sentence' in summary_stats and 'jabberwocky_matched' in summary_stats:
        sent_surp = summary_stats['sentence']['surprisal_mean']
        jab_surp = summary_stats['jabberwocky_matched']['surprisal_mean']
        delta1 = sent_surp - jab_surp

        print(f"\nEffect 1: Δ(Sentence - Jabberwocky)")
        print(f"  Sentence surprisal:     {sent_surp:.3f}")
        print(f"  Jabberwocky surprisal:  {jab_surp:.3f}")
        print(f"  Δ (Sem - Syn):          {delta1:.3f} bits")
        print(f"  Interpretation: {'Semantics REDUCES surprisal' if delta1 < 0 else 'Semantics INCREASES surprisal'}")

    # Effect 2: Δ(Jabberwocky - Scrambled Jabberwocky) - syntactic contribution
    if 'jabberwocky_matched' in summary_stats and 'scrambled_jabberwocky' in summary_stats:
        jab_surp = summary_stats['jabberwocky_matched']['surprisal_mean']
        scram_surp = summary_stats['scrambled_jabberwocky']['surprisal_mean']
        delta2 = jab_surp - scram_surp

        print(f"\nEffect 2: Δ(Jabberwocky - Scrambled Jabberwocky)")
        print(f"  Jabberwocky surprisal:          {jab_surp:.3f}")
        print(f"  Scrambled Jabberwocky surprisal: {scram_surp:.3f}")
        print(f"  Δ (Syntax - No Structure):      {delta2:.3f} bits")
        print(f"  Interpretation: {'Syntax REDUCES surprisal' if delta2 < 0 else 'Syntax INCREASES surprisal'}")

    # ========================================================================
    # 3. POSITION-WISE CURVES
    # ========================================================================
    print("\n" + "=" * 80)
    print("3. POSITION-WISE SURPRISAL CURVES (WORD-ALIGNED)")
    print("=" * 80)

    # Collect per-position surprisal
    position_data = defaultdict(lambda: defaultdict(list))

    for item in results:
        for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
            if condition in item['conditions']:
                word_surprisals = item['conditions'][condition]['word_surprisals']
                for pos, surp in enumerate(word_surprisals):
                    position_data[condition][pos].append(surp)

    # Compute mean and SE per position
    max_position = max(max(position_data[c].keys()) for c in position_data.keys())

    print(f"\nMaximum sentence length: {max_position + 1} words")

    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = {
        'sentence': '#2E86AB',
        'jabberwocky_matched': '#A23B72',
        'scrambled_jabberwocky': '#F18F01'
    }

    labels = {
        'sentence': 'Sentence (Sem+Syn)',
        'jabberwocky_matched': 'Jabberwocky (Syntax)',
        'scrambled_jabberwocky': 'Scrambled (No structure)'
    }

    for condition in ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']:
        positions = []
        means = []
        sems = []

        for pos in range(max_position + 1):
            if pos in position_data[condition]:
                vals = position_data[condition][pos]
                if len(vals) >= 3:  # At least 3 data points
                    positions.append(pos)
                    means.append(np.mean(vals))
                    sems.append(np.std(vals) / np.sqrt(len(vals)))

        if positions:
            ax.plot(positions, means, 'o-', color=colors[condition],
                   label=labels[condition], linewidth=2, markersize=6)
            ax.fill_between(positions,
                           np.array(means) - np.array(sems),
                           np.array(means) + np.array(sems),
                           color=colors[condition], alpha=0.2)

    ax.set_xlabel('Word Position', fontsize=12)
    ax.set_ylabel('Surprisal (bits)', fontsize=12)
    ax.set_title('Position-wise Surprisal Buildup (Word-Aligned)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_prefix}_position_curves.png', dpi=300, bbox_inches='tight')
    print(f"\nPosition curve saved to: {output_prefix}_position_curves.png")

    plt.close()

    # Print numerical summary
    print("\nNumerical Summary (first 8 positions):")
    print(f"\n{'Pos':>3s} | {'Sentence':>12s} | {'Jabberwocky':>12s} | {'Scrambled':>12s}")
    print("-" * 50)

    for pos in range(min(8, max_position + 1)):
        sent_val = np.mean(position_data['sentence'][pos]) if pos in position_data['sentence'] else np.nan
        jab_val = np.mean(position_data['jabberwocky_matched'][pos]) if pos in position_data['jabberwocky_matched'] else np.nan
        scram_val = np.mean(position_data['scrambled_jabberwocky'][pos]) if pos in position_data['scrambled_jabberwocky'] else np.nan

        print(f"{pos:3d} | {sent_val:12.3f} | {jab_val:12.3f} | {scram_val:12.3f}")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run full morphosyntax analysis')
    parser.add_argument('--model', type=str, required=True,
                       choices=['gpt2', 'EleutherAI/pythia-410m'],
                       help='Model to use')
    parser.add_argument('--stimuli', type=str, default='stimuli_context_matched.json',
                       help='Stimuli file')
    parser.add_argument('--run-experiment', action='store_true',
                       help='Run experiment (otherwise just analyze existing results)')
    parser.add_argument('--results', type=str,
                       help='Results file to analyze (if not running experiment)')

    args = parser.parse_args()

    # Determine output filenames
    model_short = args.model.split('/')[-1]
    output_file = f'experiment_results_{model_short}_final.json'
    output_prefix = f'analysis_{model_short}'

    # Run experiment if requested
    if args.run_experiment:
        print(f"Running experiment with {args.model}...")
        results = run_full_experiment(
            stimuli_file=args.stimuli,
            output_file=output_file,
            model_name=args.model
        )

    # Analyze results
    results_to_analyze = args.results if args.results else output_file
    print(f"\nAnalyzing results from {results_to_analyze}...")
    analyze_results(results_to_analyze, output_prefix)
