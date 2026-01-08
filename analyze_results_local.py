"""
Analysis script for local model results.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_results(results_file="experiment_results_local.json"):
    """Load experiment results from JSON."""
    with open(results_file, 'r') as f:
        results = json.load(f)
    return results

def extract_data(results):
    """Extract data into pandas DataFrame."""
    rows = []

    for result in results:
        set_id = result['set_id']

        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
            if condition in result['conditions']:
                cond_data = result['conditions'][condition]

                rows.append({
                    'set_id': set_id,
                    'condition': condition,
                    'text': cond_data['text'],
                    'mean_entropy': cond_data['mean_entropy'],
                    'mean_next_token_prob': cond_data['mean_next_token_prob'],
                    'num_tokens': cond_data['num_tokens'],
                    'token_entropies': cond_data['token_entropies']
                })

    return pd.DataFrame(rows)

def calculate_cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def run_statistical_tests(df):
    """Run paired statistical tests."""
    print("\n" + "=" * 80)
    print("STATISTICAL TESTS")
    print("=" * 80)

    conditions = ['sentence', 'jabberwocky', 'stripped', 'nonwords']
    condition_data = {}

    for cond in conditions:
        cond_df = df[df['condition'] == cond].sort_values('set_id')
        condition_data[cond] = cond_df['mean_entropy'].values

    comparisons = [
        ('jabberwocky', 'stripped', "Jabberwocky vs Stripped (function word contribution)"),
        ('jabberwocky', 'nonwords', "Jabberwocky vs Nonwords (total morphosyntactic contribution)"),
        ('sentence', 'jabberwocky', "Sentence vs Jabberwocky (content word contribution)"),
        ('sentence', 'nonwords', "Sentence vs Nonwords (full constraint)"),
        ('stripped', 'nonwords', "Stripped vs Nonwords (residual constraint)")
    ]

    results = []

    for cond1, cond2, description in comparisons:
        data1 = condition_data[cond1]
        data2 = condition_data[cond2]

        # Paired t-test
        t_stat, p_value = stats.ttest_rel(data1, data2)

        # Wilcoxon signed-rank test
        w_stat, w_pvalue = stats.wilcoxon(data1, data2)

        # Cohen's d
        cohens_d = calculate_cohens_d(data1, data2)

        print(f"\n{description}")
        print(f"  {cond1}: M={np.mean(data1):.3f}, SD={np.std(data1):.3f}")
        print(f"  {cond2}: M={np.mean(data2):.3f}, SD={np.std(data2):.3f}")
        print(f"  Difference: {np.mean(data1) - np.mean(data2):.3f} bits")
        print(f"  Paired t-test: t={t_stat:.3f}, p={p_value:.4f}")
        print(f"  Wilcoxon test: W={w_stat:.1f}, p={w_pvalue:.4f}")
        print(f"  Cohen's d: {cohens_d:.3f}")

        results.append({
            'comparison': description,
            'condition1': cond1,
            'condition2': cond2,
            'mean1': np.mean(data1),
            'mean2': np.mean(data2),
            'diff': np.mean(data1) - np.mean(data2),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d
        })

    return pd.DataFrame(results)

def create_visualizations(df, output_dir="visualizations_local"):
    """Create visualizations."""
    import os
    os.makedirs(output_dir, exist_ok=True)

    condition_order = ['sentence', 'jabberwocky', 'stripped', 'nonwords']
    condition_labels = ['Real\nSentences', 'Jabberwocky\n(Morphosyntax Intact)',
                        'Stripped\n(No Morphosyntax)', 'Random\nNonwords']

    # 1. Bar plot
    plt.figure(figsize=(10, 6))

    means = [df[df['condition'] == c]['mean_entropy'].mean() for c in condition_order]
    sems = [df[df['condition'] == c]['mean_entropy'].sem() for c in condition_order]

    colors = ['#2ecc71', '#3498db', '#e74c3c', '#95a5a6']

    bars = plt.bar(range(len(condition_order)), means, yerr=sems, capsize=5,
                   color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)

    plt.xlabel('Condition', fontsize=14, fontweight='bold')
    plt.ylabel('Mean Entropy (bits)', fontsize=14, fontweight='bold')
    plt.title('Next-Token Entropy by Morphosyntactic Condition\n(GPT-2 Local Model - CORRECTED)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(condition_order)), condition_labels, fontsize=11)
    plt.ylim(0, max(means) * 1.2)

    for i, (bar, mean, sem) in enumerate(zip(bars, means, sems)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + sem + 0.1,
                f'{mean:.2f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/mean_entropy_by_condition_CORRECTED.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/mean_entropy_by_condition_CORRECTED.png")
    plt.close()

    # 2. Violin plot
    plt.figure(figsize=(12, 7))

    sns.violinplot(data=df, x='condition', y='mean_entropy', order=condition_order,
                   palette=colors, inner='box', linewidth=1.5, hue='condition', legend=False)

    plt.xlabel('Condition', fontsize=14, fontweight='bold')
    plt.ylabel('Mean Entropy (bits)', fontsize=14, fontweight='bold')
    plt.title('Distribution of Entropy Across Conditions (CORRECTED)',
              fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(condition_order)), condition_labels, fontsize=11)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/entropy_distribution_CORRECTED.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/entropy_distribution_CORRECTED.png")
    plt.close()

def main():
    """Run analysis."""
    print("\n" + "=" * 80)
    print("ANALYSIS - LOCAL MODEL RESULTS (CORRECTED)")
    print("=" * 80)

    results = load_results()
    df = extract_data(results)

    # Save to CSV
    df_export = df.drop('token_entropies', axis=1)
    df_export.to_csv("experiment_data_local.csv", index=False)
    print(f"\nSaved: experiment_data_local.csv")

    # Statistical tests
    stats_df = run_statistical_tests(df)
    stats_df.to_csv("statistical_tests_local.csv", index=False)
    print("\nSaved: statistical_tests_local.csv")

    # Visualizations
    print("\nGenerating visualizations...")
    create_visualizations(df)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
