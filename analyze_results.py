"""
Statistical analysis and visualization for morphosyntax experiment.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_results(results_file="experiment_results.json"):
    """Load experiment results from JSON."""
    with open(results_file, 'r') as f:
        results = json.load(f)
    return results

def extract_data_for_analysis(results):
    """
    Extract data into a pandas DataFrame for easier analysis.
    """
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
                    'mean_top1': cond_data['mean_top1'],
                    'num_tokens': cond_data['num_tokens'],
                    'token_entropies': cond_data['token_entropies']
                })

    df = pd.DataFrame(rows)
    return df

def calculate_cohens_d(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std

def run_statistical_tests(df):
    """Run paired statistical tests across conditions."""
    print("\n" + "=" * 70)
    print("STATISTICAL TESTS")
    print("=" * 70)

    # Get data for each condition
    conditions = ['sentence', 'jabberwocky', 'stripped', 'nonwords']
    condition_data = {}

    for cond in conditions:
        cond_df = df[df['condition'] == cond].sort_values('set_id')
        condition_data[cond] = cond_df['mean_entropy'].values

    # Key comparisons
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

        # Wilcoxon signed-rank test (non-parametric alternative)
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

def create_visualizations(df, output_dir="visualizations"):
    """Create all visualizations."""
    Path(output_dir).mkdir(exist_ok=True)

    # 1. Bar plot of mean entropy by condition
    plt.figure(figsize=(10, 6))

    condition_order = ['sentence', 'jabberwocky', 'stripped', 'nonwords']
    condition_labels = ['Real\nSentences', 'Jabberwocky\n(Morphosyntax Intact)',
                        'Stripped\n(No Morphosyntax)', 'Random\nNonwords']

    means = [df[df['condition'] == c]['mean_entropy'].mean() for c in condition_order]
    sems = [df[df['condition'] == c]['mean_entropy'].sem() for c in condition_order]

    colors = ['#2ecc71', '#3498db', '#e74c3c', '#95a5a6']

    bars = plt.bar(range(len(condition_order)), means, yerr=sems, capsize=5,
                   color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)

    plt.xlabel('Condition', fontsize=14, fontweight='bold')
    plt.ylabel('Mean Entropy (bits)', fontsize=14, fontweight='bold')
    plt.title('Next-Token Entropy by Morphosyntactic Condition', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(condition_order)), condition_labels, fontsize=11)
    plt.ylim(0, max(means) * 1.2)

    # Add value labels on bars
    for i, (bar, mean, sem) in enumerate(zip(bars, means, sems)):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + sem + 0.1,
                f'{mean:.2f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/mean_entropy_by_condition.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/mean_entropy_by_condition.png")
    plt.close()

    # 2. Position-by-position entropy (averaged across stimuli)
    plt.figure(figsize=(14, 7))

    max_tokens = df['num_tokens'].max()

    for condition, label, color in zip(condition_order, condition_labels,  colors):
        cond_df = df[df['condition'] == condition]

        # Collect entropy at each position
        position_entropies = [[] for _ in range(max_tokens)]

        for _, row in cond_df.iterrows():
            token_ents = row['token_entropies']
            for pos, ent in enumerate(token_ents):
                if pos < max_tokens:
                    position_entropies[pos].append(ent)

        # Calculate mean and SEM at each position
        means = [np.mean(ents) if ents else np.nan for ents in position_entropies]
        sems = [np.std(ents) / np.sqrt(len(ents)) if ents else np.nan for ents in position_entropies]

        positions = range(len(means))
        plt.plot(positions, means, marker='o', label=label.replace('\n', ' '),
                color=color, linewidth=2, markersize=4)
        plt.fill_between(positions,
                        [m - s if not np.isnan(m) else np.nan for m, s in zip(means, sems)],
                        [m + s if not np.isnan(m) else np.nan for m, s in zip(means, sems)],
                        alpha=0.2, color=color)

    plt.xlabel('Token Position', fontsize=14, fontweight='bold')
    plt.ylabel('Mean Entropy (bits)', fontsize=14, fontweight='bold')
    plt.title('Entropy by Token Position Across Conditions', fontsize=16, fontweight='bold', pad=20)
    plt.legend(fontsize=11, frameon=True, shadow=True)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/entropy_by_position.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/entropy_by_position.png")
    plt.close()

    # 3. Violin plot showing distributions
    plt.figure(figsize=(12, 7))

    sns.violinplot(data=df, x='condition', y='mean_entropy', order=condition_order,
                   palette=colors, inner='box', linewidth=1.5)

    plt.xlabel('Condition', fontsize=14, fontweight='bold')
    plt.ylabel('Mean Entropy (bits)', fontsize=14, fontweight='bold')
    plt.title('Distribution of Entropy Across Conditions', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(condition_order)), condition_labels, fontsize=11)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/entropy_distribution.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/entropy_distribution.png")
    plt.close()

    # 4. Paired comparison plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    key_comparisons = [
        ('sentence', 'jabberwocky', 'Sentence vs\nJabberwocky'),
        ('jabberwocky', 'stripped', 'Jabberwocky vs\nStripped'),
        ('stripped', 'nonwords', 'Stripped vs\nNonwords')
    ]

    for ax, (cond1, cond2, title) in zip(axes, key_comparisons):
        data1 = df[df['condition'] == cond1].sort_values('set_id')['mean_entropy'].values
        data2 = df[df['condition'] == cond2].sort_values('set_id')['mean_entropy'].values

        # Scatter plot with diagonal
        ax.scatter(data1, data2, alpha=0.6, s=60, edgecolors='black', linewidth=0.5)
        lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])]
        ax.plot(lims, lims, 'k--', alpha=0.5, zorder=0)

        ax.set_xlabel(cond1.capitalize(), fontsize=12, fontweight='bold')
        ax.set_ylabel(cond2.capitalize(), fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/paired_comparisons.png", dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/paired_comparisons.png")
    plt.close()

def generate_summary_report(df, stats_df, output_file="analysis_summary.txt"):
    """Generate a text summary of the analysis."""
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("MORPHOSYNTAX CONSTRAINT EXPERIMENT - SUMMARY REPORT\n")
        f.write("=" * 70 + "\n\n")

        f.write("DESCRIPTIVE STATISTICS\n")
        f.write("-" * 70 + "\n")

        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
            cond_data = df[df['condition'] == condition]['mean_entropy']
            f.write(f"\n{condition.upper()}\n")
            f.write(f"  Mean: {cond_data.mean():.3f} bits\n")
            f.write(f"  SD:   {cond_data.std():.3f} bits\n")
            f.write(f"  Min:  {cond_data.min():.3f} bits\n")
            f.write(f"  Max:  {cond_data.max():.3f} bits\n")
            f.write(f"  N:    {len(cond_data)}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("STATISTICAL COMPARISONS\n")
        f.write("=" * 70 + "\n\n")

        for _, row in stats_df.iterrows():
            f.write(f"{row['comparison']}\n")
            f.write(f"  {row['condition1']}: M={row['mean1']:.3f}\n")
            f.write(f"  {row['condition2']}: M={row['mean2']:.3f}\n")
            f.write(f"  Difference: {row['diff']:.3f} bits\n")
            f.write(f"  t={row['t_statistic']:.3f}, p={row['p_value']:.4f}\n")
            f.write(f"  Cohen's d={row['cohens_d']:.3f}\n")

            if row['p_value'] < 0.001:
                sig = "***"
            elif row['p_value'] < 0.01:
                sig = "**"
            elif row['p_value'] < 0.05:
                sig = "*"
            else:
                sig = "n.s."
            f.write(f"  Significance: {sig}\n\n")

        f.write("=" * 70 + "\n")
        f.write("INTERPRETATION\n")
        f.write("=" * 70 + "\n\n")

        jab_ent = df[df['condition'] == 'jabberwocky']['mean_entropy'].mean()
        strip_ent = df[df['condition'] == 'stripped']['mean_entropy'].mean()
        sent_ent = df[df['condition'] == 'sentence']['mean_entropy'].mean()
        nonword_ent = df[df['condition'] == 'nonwords']['mean_entropy'].mean()

        f.write("Predicted pattern if morphosyntax constrains predictions:\n")
        f.write("  Sentences < Jabberwocky < Stripped ≈ Nonwords\n\n")

        f.write("Observed pattern:\n")
        f.write(f"  Sentences ({sent_ent:.3f}) < " if sent_ent < jab_ent else f"  Sentences ({sent_ent:.3f}) > ")
        f.write(f"Jabberwocky ({jab_ent:.3f}) < " if jab_ent < strip_ent else f"Jabberwocky ({jab_ent:.3f}) > ")
        f.write(f"Stripped ({strip_ent:.3f})")
        if abs(strip_ent - nonword_ent) < 0.5:
            f.write(f" ≈ Nonwords ({nonword_ent:.3f})\n\n")
        elif strip_ent < nonword_ent:
            f.write(f" < Nonwords ({nonword_ent:.3f})\n\n")
        else:
            f.write(f" > Nonwords ({nonword_ent:.3f})\n\n")

        f.write("Key finding (Jabberwocky vs Stripped):\n")
        jab_strip_diff = jab_ent - strip_ent
        if jab_strip_diff < -0.3:
            f.write(f"  Function words and morphology REDUCE entropy by {abs(jab_strip_diff):.3f} bits.\n")
            f.write("  This supports the hypothesis that morphosyntactic tokens constrain\n")
            f.write("  predictions independently of content word semantics.\n")
        else:
            f.write(f"  Function words show minimal effect ({jab_strip_diff:.3f} bits).\n")
            f.write("  This suggests limited morphosyntactic constraint in isolation.\n")

    print(f"\nSaved: {output_file}")

def main():
    """Run full analysis pipeline."""
    print("\n" + "=" * 70)
    print("MORPHOSYNTAX CONSTRAINT EXPERIMENT - ANALYSIS")
    print("=" * 70)

    # Load results
    results = load_results("experiment_results.json")
    print(f"\nLoaded results for {len(results)} stimulus sets")

    # Extract data
    df = extract_data_for_analysis(results)
    print(f"Extracted data: {len(df)} rows")

    # Save raw data to CSV
    df_export = df.drop('token_entropies', axis=1)
    df_export.to_csv("experiment_data.csv", index=False)
    print("Saved: experiment_data.csv")

    # Statistical tests
    stats_df = run_statistical_tests(df)
    stats_df.to_csv("statistical_tests.csv", index=False)
    print("\nSaved: statistical_tests.csv")

    # Visualizations
    print("\nGenerating visualizations...")
    create_visualizations(df)

    # Summary report
    print("\nGenerating summary report...")
    generate_summary_report(df, stats_df)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - experiment_data.csv")
    print("  - statistical_tests.csv")
    print("  - analysis_summary.txt")
    print("  - visualizations/mean_entropy_by_condition.png")
    print("  - visualizations/entropy_by_position.png")
    print("  - visualizations/entropy_distribution.png")
    print("  - visualizations/paired_comparisons.png")

if __name__ == "__main__":
    main()
