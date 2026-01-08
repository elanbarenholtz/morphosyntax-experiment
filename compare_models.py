"""
Compare GPT-2 and GPT-2-large results.
"""

import json
import numpy as np
from scipy import stats
import pandas as pd

def load_results(filepath):
    """Load experiment results."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_condition_entropies(results):
    """Extract mean entropy for each condition across all stimulus sets."""
    condition_entropies = {
        'sentence': [],
        'jabberwocky': [],
        'stripped': [],
        'nonwords': []
    }

    for result in results:
        for condition in condition_entropies.keys():
            if condition in result['conditions']:
                mean_ent = result['conditions'][condition]['mean_entropy']
                condition_entropies[condition].append(mean_ent)

    return condition_entropies

def run_statistical_tests(entropies):
    """Run paired t-tests between conditions."""
    comparisons = [
        ('Jabberwocky vs Stripped', 'jabberwocky', 'stripped'),
        ('Jabberwocky vs Nonwords', 'jabberwocky', 'nonwords'),
        ('Sentence vs Jabberwocky', 'sentence', 'jabberwocky'),
        ('Sentence vs Nonwords', 'sentence', 'nonwords'),
        ('Stripped vs Nonwords', 'stripped', 'nonwords')
    ]

    results = []

    for name, cond1, cond2 in comparisons:
        data1 = np.array(entropies[cond1])
        data2 = np.array(entropies[cond2])

        mean1 = np.mean(data1)
        mean2 = np.mean(data2)
        diff = mean1 - mean2

        # Paired t-test
        t_stat, p_val = stats.ttest_rel(data1, data2)

        # Cohen's d
        diff_scores = data1 - data2
        cohens_d = np.mean(diff_scores) / np.std(diff_scores, ddof=1)

        results.append({
            'comparison': name,
            'mean1': mean1,
            'mean2': mean2,
            'difference': diff,
            't_statistic': t_stat,
            'p_value': p_val,
            'cohens_d': cohens_d
        })

    return pd.DataFrame(results)

def compare_models(gpt2_file, gpt2_large_file):
    """Compare GPT-2 and GPT-2-large results."""

    print("="*80)
    print("MODEL COMPARISON: GPT-2 vs GPT-2-LARGE")
    print("="*80)

    # Load results
    gpt2_results = load_results(gpt2_file)
    large_results = load_results(gpt2_large_file)

    # Extract entropies
    gpt2_ent = extract_condition_entropies(gpt2_results)
    large_ent = extract_condition_entropies(large_results)

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)

    print("\nGPT-2 (124M parameters):")
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        mean = np.mean(gpt2_ent[condition])
        std = np.std(gpt2_ent[condition])
        print(f"  {condition:15s}: {mean:.3f} ± {std:.3f} bits")

    print("\nGPT-2-LARGE (774M parameters):")
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        mean = np.mean(large_ent[condition])
        std = np.std(large_ent[condition])
        print(f"  {condition:15s}: {mean:.3f} ± {std:.3f} bits")

    print("\nDifference (GPT-2 - GPT-2-LARGE):")
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        diff = np.mean(gpt2_ent[condition]) - np.mean(large_ent[condition])
        print(f"  {condition:15s}: {diff:+.3f} bits")

    # Statistical tests for GPT-2-LARGE
    print("\n" + "="*80)
    print("STATISTICAL TESTS - GPT-2-LARGE")
    print("="*80)

    large_stats = run_statistical_tests(large_ent)

    print("\nKey Finding: Jabberwocky vs Stripped (Morphosyntax Effect)")
    morph_test = large_stats[large_stats['comparison'] == 'Jabberwocky vs Stripped'].iloc[0]
    print(f"  Jabberwocky: {morph_test['mean1']:.3f} bits")
    print(f"  Stripped:    {morph_test['mean2']:.3f} bits")
    print(f"  Difference:  {morph_test['difference']:.3f} bits")
    print(f"  t-statistic: {morph_test['t_statistic']:.3f}")
    print(f"  p-value:     {morph_test['p_value']:.2e}")
    print(f"  Cohen's d:   {morph_test['cohens_d']:.3f}")

    if morph_test['p_value'] < 0.0001:
        print("  ✅ HIGHLY SIGNIFICANT (p < 0.0001)")

    print("\nAll Comparisons:")
    print(large_stats.to_string(index=False))

    # Model comparison
    print("\n" + "="*80)
    print("MODEL SIZE EFFECTS")
    print("="*80)

    # Compare morphosyntax effect size across models
    gpt2_stats = run_statistical_tests(gpt2_ent)
    gpt2_morph = gpt2_stats[gpt2_stats['comparison'] == 'Jabberwocky vs Stripped'].iloc[0]

    print("\nMorphosyntax Effect (Jabberwocky vs Stripped):")
    print(f"  GPT-2:       {gpt2_morph['difference']:.3f} bits (d = {gpt2_morph['cohens_d']:.2f})")
    print(f"  GPT-2-LARGE: {morph_test['difference']:.3f} bits (d = {morph_test['cohens_d']:.2f})")

    effect_change = morph_test['difference'] - gpt2_morph['difference']
    print(f"\n  Effect change: {effect_change:+.3f} bits")

    if abs(effect_change) < 0.1:
        print("  → Effect size is STABLE across model sizes ✅")
    elif effect_change < 0:
        print("  → Effect STRENGTHENS with larger model")
    else:
        print("  → Effect WEAKENS with larger model")

    # Overall entropy reduction
    print("\nOverall Entropy (averaged across conditions):")
    gpt2_overall = np.mean([np.mean(gpt2_ent[c]) for c in gpt2_ent.keys()])
    large_overall = np.mean([np.mean(large_ent[c]) for c in large_ent.keys()])
    print(f"  GPT-2:       {gpt2_overall:.3f} bits")
    print(f"  GPT-2-LARGE: {large_overall:.3f} bits")
    print(f"  Reduction:   {gpt2_overall - large_overall:.3f} bits ({((gpt2_overall - large_overall)/gpt2_overall)*100:.1f}%)")

    # Save comparison
    comparison_data = {
        'gpt2': {condition: {'mean': np.mean(gpt2_ent[condition]),
                            'std': np.std(gpt2_ent[condition])}
                for condition in gpt2_ent.keys()},
        'gpt2_large': {condition: {'mean': np.mean(large_ent[condition]),
                                  'std': np.std(large_ent[condition])}
                      for condition in large_ent.keys()},
        'gpt2_large_statistics': large_stats.to_dict('records')
    }

    with open('model_comparison.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print("\n" + "="*80)
    print("Comparison saved to: model_comparison.json")
    print("="*80)

if __name__ == "__main__":
    compare_models(
        'experiment_results_controlled.json',
        'experiment_results_gpt2_large.json'
    )
