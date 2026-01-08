"""
Compare DistilGPT-2, GPT-2, and GPT-2-LARGE results.
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

def compare_three_models():
    """Compare DistilGPT-2, GPT-2, and GPT-2-large results."""

    print("="*80)
    print("THREE-MODEL COMPARISON: DistilGPT-2 < GPT-2 < GPT-2-LARGE")
    print("="*80)

    # Load results
    distil_results = load_results('experiment_results_distilgpt2.json')
    gpt2_results = load_results('experiment_results_controlled.json')
    large_results = load_results('experiment_results_gpt2_large.json')

    # Extract entropies
    distil_ent = extract_condition_entropies(distil_results)
    gpt2_ent = extract_condition_entropies(gpt2_results)
    large_ent = extract_condition_entropies(large_results)

    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS ACROSS MODEL SIZES")
    print("="*80)

    print("\nDistilGPT-2 (82M parameters):")
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        mean = np.mean(distil_ent[condition])
        std = np.std(distil_ent[condition])
        print(f"  {condition:15s}: {mean:.3f} ± {std:.3f} bits")

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

    # Test monotonicity for random nonwords
    print("\n" + "="*80)
    print("CALIBRATION FINDING: ENTROPY ON RANDOM NONWORDS")
    print("="*80)

    distil_nonwords = np.mean(distil_ent['nonwords'])
    gpt2_nonwords = np.mean(gpt2_ent['nonwords'])
    large_nonwords = np.mean(large_ent['nonwords'])

    print(f"\nDistilGPT-2 (82M):   {distil_nonwords:.3f} bits")
    print(f"GPT-2 (124M):        {gpt2_nonwords:.3f} bits")
    print(f"GPT-2-LARGE (774M):  {large_nonwords:.3f} bits")

    print(f"\nChange from DistilGPT-2 to GPT-2:       {gpt2_nonwords - distil_nonwords:+.3f} bits")
    print(f"Change from GPT-2 to GPT-2-LARGE:       {large_nonwords - gpt2_nonwords:+.3f} bits")
    print(f"Total change (82M → 774M):              {large_nonwords - distil_nonwords:+.3f} bits")

    if distil_nonwords > gpt2_nonwords > large_nonwords:
        print("\n✅ MONOTONIC DECREASE: Larger models show LOWER entropy on random nonwords")
        print("   → Consistent with overconfidence hypothesis")
    else:
        print("\n⚠️  NON-MONOTONIC pattern observed")

    # Morphosyntax effect across models
    print("\n" + "="*80)
    print("MORPHOSYNTAX EFFECT (Jabberwocky vs Stripped) ACROSS MODEL SIZES")
    print("="*80)

    models = [
        ("DistilGPT-2 (82M)", distil_ent),
        ("GPT-2 (124M)", gpt2_ent),
        ("GPT-2-LARGE (774M)", large_ent)
    ]

    effect_sizes = []

    for name, entropies in models:
        jab = np.array(entropies['jabberwocky'])
        strip = np.array(entropies['stripped'])

        mean_jab = np.mean(jab)
        mean_strip = np.mean(strip)
        diff = mean_jab - mean_strip

        # Paired t-test
        t_stat, p_val = stats.ttest_rel(jab, strip)

        # Cohen's d
        diff_scores = jab - strip
        cohens_d = np.mean(diff_scores) / np.std(diff_scores, ddof=1)

        effect_sizes.append(abs(diff))

        print(f"\n{name}:")
        print(f"  Jabberwocky:  {mean_jab:.3f} bits")
        print(f"  Stripped:     {mean_strip:.3f} bits")
        print(f"  Difference:   {diff:.3f} bits")
        print(f"  Cohen's d:    {cohens_d:.3f}")
        print(f"  p-value:      {p_val:.2e}")
        if p_val < 0.0001:
            print(f"  ✅ HIGHLY SIGNIFICANT")

    # Check if effect weakens monotonically
    print("\n" + "="*80)
    print("EFFECT SIZE TREND")
    print("="*80)
    print(f"\nMorphosyntax effect magnitude:")
    print(f"  DistilGPT-2:  {effect_sizes[0]:.3f} bits")
    print(f"  GPT-2:        {effect_sizes[1]:.3f} bits")
    print(f"  GPT-2-LARGE:  {effect_sizes[2]:.3f} bits")

    if effect_sizes[0] > effect_sizes[1] > effect_sizes[2]:
        print("\n✅ MONOTONIC DECREASE: Effect weakens with model size")
        print("   → Larger models rely less on morphosyntactic scaffolding")
    else:
        print("\n⚠️  NON-MONOTONIC pattern")

    # Overall entropy reduction
    print("\n" + "="*80)
    print("OVERALL LANGUAGE MODELING IMPROVEMENT")
    print("="*80)

    distil_overall = np.mean([np.mean(distil_ent[c]) for c in distil_ent.keys()])
    gpt2_overall = np.mean([np.mean(gpt2_ent[c]) for c in gpt2_ent.keys()])
    large_overall = np.mean([np.mean(large_ent[c]) for c in large_ent.keys()])

    print(f"\nAverage entropy across all conditions:")
    print(f"  DistilGPT-2:  {distil_overall:.3f} bits")
    print(f"  GPT-2:        {gpt2_overall:.3f} bits")
    print(f"  GPT-2-LARGE:  {large_overall:.3f} bits")

    print(f"\nImprovements:")
    print(f"  Distil → GPT-2:       {distil_overall - gpt2_overall:.3f} bits ({((distil_overall - gpt2_overall)/distil_overall)*100:.1f}%)")
    print(f"  GPT-2 → GPT-2-LARGE:  {gpt2_overall - large_overall:.3f} bits ({((gpt2_overall - large_overall)/gpt2_overall)*100:.1f}%)")
    print(f"  Total (82M → 774M):   {distil_overall - large_overall:.3f} bits ({((distil_overall - large_overall)/distil_overall)*100:.1f}%)")

    # Save comparison
    comparison_data = {
        'distilgpt2': {condition: {'mean': np.mean(distil_ent[condition]),
                                  'std': np.std(distil_ent[condition])}
                      for condition in distil_ent.keys()},
        'gpt2': {condition: {'mean': np.mean(gpt2_ent[condition]),
                           'std': np.std(gpt2_ent[condition])}
                for condition in gpt2_ent.keys()},
        'gpt2_large': {condition: {'mean': np.mean(large_ent[condition]),
                                  'std': np.std(large_ent[condition])}
                      for condition in large_ent.keys()},
        'nonwords_monotonicity': {
            'distilgpt2': distil_nonwords,
            'gpt2': gpt2_nonwords,
            'gpt2_large': large_nonwords,
            'is_monotonic': distil_nonwords > gpt2_nonwords > large_nonwords
        },
        'morphosyntax_effect': {
            'distilgpt2': effect_sizes[0],
            'gpt2': effect_sizes[1],
            'gpt2_large': effect_sizes[2],
            'is_monotonic': effect_sizes[0] > effect_sizes[1] > effect_sizes[2]
        }
    }

    with open('three_model_comparison.json', 'w') as f:
        json.dump(comparison_data, f, indent=2)

    print("\n" + "="*80)
    print("Comparison saved to: three_model_comparison.json")
    print("="*80)

if __name__ == "__main__":
    compare_three_models()
