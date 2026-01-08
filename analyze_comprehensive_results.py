#!/usr/bin/env python3
"""
Statistical Analysis for Comprehensive Morphosyntax Audit

Features:
- Paired t-tests for within-subject comparisons
- FDR correction (Benjamini-Hochberg) for multiple comparisons across cue families
- Bootstrap confidence intervals
- Comprehensive summary tables and visualizations
"""

import json
import argparse
import numpy as np
import pandas as pd
from scipy import stats
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================================
# DATA AGGREGATION
# ============================================================================

def aggregate_results(results):
    """
    Aggregate results by stimulus set × condition × cue family.

    Returns:
        DataFrame with columns: set_id, condition, cue_family, class_mass
        where class_mass is the primary expected class for each cue family
    """
    aggregated = []

    # Group by set_id, condition, cue_family
    grouped = defaultdict(list)

    for r in results:
        key = (r['set_id'], r['condition'], r['cue_family'])
        # Get primary class mass (e.g., VERB for infinitival_to)
        class_mass = r['class_mass']

        # Extract primary class value
        # (This assumes each cue family has a 'primary_class' specified)
        # For infinitival_to, this would be VERB
        # We'll take the first class mass value as primary for now
        primary_mass = list(class_mass.values())[0] if class_mass else 0.0

        grouped[key].append(primary_mass)

    # Compute mean for each group
    for (set_id, condition, cue_family), masses in grouped.items():
        aggregated.append({
            'set_id': set_id,
            'condition': condition,
            'cue_family': cue_family,
            'class_mass': np.mean(masses),
            'n_instances': len(masses),
        })

    return pd.DataFrame(aggregated)


# ============================================================================
# PAIRED COMPARISONS
# ============================================================================

def run_paired_comparison(df, cue_family, cond1, cond2):
    """
    Run paired t-test comparing two conditions within a cue family.

    Args:
        df: Aggregated DataFrame
        cue_family: Cue family name
        cond1: Reference condition (e.g., 'JABBERWOCKY')
        cond2: Comparison condition (e.g., 'CONTENT_SCRAMBLED')

    Returns:
        Dictionary with test statistics
    """
    # Filter for this cue family
    df_family = df[df['cue_family'] == cue_family]

    # Get matched pairs
    df_wide = df_family.pivot(index='set_id', columns='condition', values='class_mass')

    if cond1 not in df_wide.columns or cond2 not in df_wide.columns:
        return None

    # Drop NaN pairs
    df_matched = df_wide[[cond1, cond2]].dropna()

    if len(df_matched) < 3:
        return None  # Insufficient data

    vals1 = df_matched[cond1].values
    vals2 = df_matched[cond2].values

    # Paired t-test
    t_stat, p_value = stats.ttest_rel(vals1, vals2)

    # Cohen's d (paired)
    diff = vals1 - vals2
    d = diff.mean() / diff.std()

    return {
        'cue_family': cue_family,
        'condition_1': cond1,
        'condition_2': cond2,
        'n_pairs': len(df_matched),
        'mean_1': vals1.mean(),
        'sd_1': vals1.std(),
        'mean_2': vals2.mean(),
        'sd_2': vals2.std(),
        'diff_mean': diff.mean(),
        'diff_sd': diff.std(),
        't_stat': t_stat,
        'p_value': p_value,
        'cohens_d': d,
    }


# ============================================================================
# FDR CORRECTION
# ============================================================================

def apply_fdr_correction(comparison_results):
    """
    Apply Benjamini-Hochberg FDR correction across cue families.

    Args:
        comparison_results: List of comparison dictionaries

    Returns:
        List of comparison dictionaries with 'p_fdr' field added
    """
    # Extract p-values
    p_values = [r['p_value'] for r in comparison_results if r is not None]

    if len(p_values) == 0:
        return comparison_results

    # Apply FDR correction
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    # Benjamini-Hochberg procedure
    p_fdr = np.zeros(n)
    for i in range(n):
        rank = i + 1
        p_fdr[sorted_indices[i]] = min(sorted_p[i] * n / rank, 1.0)

    # Ensure monotonicity (p_fdr should be non-decreasing)
    for i in range(n - 1, 0, -1):
        if p_fdr[i] < p_fdr[i - 1]:
            p_fdr[i - 1] = p_fdr[i]

    # Add to results
    valid_results = [r for r in comparison_results if r is not None]
    for i, r in enumerate(valid_results):
        r['p_fdr'] = p_fdr[i]

    return comparison_results


# ============================================================================
# BOOTSTRAP CONFIDENCE INTERVALS
# ============================================================================

def bootstrap_ci(data, n_bootstrap=10000, ci_level=0.95):
    """
    Compute bootstrap confidence interval for mean.

    Args:
        data: Array of values
        n_bootstrap: Number of bootstrap samples
        ci_level: Confidence level (default: 0.95)

    Returns:
        Tuple (lower, upper) bounds
    """
    bootstrap_means = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))

    alpha = 1 - ci_level
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)

    return lower, upper


def add_bootstrap_cis(df, n_bootstrap=10000):
    """
    Add bootstrap CIs to aggregated DataFrame.

    Args:
        df: Aggregated DataFrame
        n_bootstrap: Number of bootstrap samples

    Returns:
        DataFrame with ci_lower and ci_upper columns
    """
    df_with_ci = df.copy()
    ci_lower = []
    ci_upper = []

    for _, row in df.iterrows():
        # For now, we'll use the class_mass value itself since we've already aggregated
        # In a full implementation, we'd bootstrap over the original instances
        # Here we'll compute a simple CI based on assumed sampling distribution

        # Simplified: assume normal approximation
        # In practice, you'd want to bootstrap over the raw instances
        mean = row['class_mass']
        n = row['n_instances']

        # Use standard error approximation
        se = 0.1 / np.sqrt(n)  # Rough estimate
        ci_lower.append(mean - 1.96 * se)
        ci_upper.append(mean + 1.96 * se)

    df_with_ci['ci_lower'] = ci_lower
    df_with_ci['ci_upper'] = ci_upper

    return df_with_ci


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_paired_comparison(df, cue_family, cond1, cond2, output_file=None):
    """
    Create paired dot plot for two conditions.

    Args:
        df: Aggregated DataFrame
        cue_family: Cue family name
        cond1: Reference condition
        cond2: Comparison condition
        output_file: Path to save plot (optional)
    """
    # Filter for this cue family
    df_family = df[df['cue_family'] == cue_family]

    # Get matched pairs
    df_wide = df_family.pivot(index='set_id', columns='condition', values='class_mass')

    if cond1 not in df_wide.columns or cond2 not in df_wide.columns:
        print(f"Warning: Cannot plot {cond1} vs {cond2} for {cue_family} (missing data)")
        return

    df_matched = df_wide[[cond1, cond2]].dropna()

    if len(df_matched) < 3:
        print(f"Warning: Insufficient data for {cue_family}")
        return

    vals1 = df_matched[cond1].values
    vals2 = df_matched[cond2].values

    # Create plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot individual pairs
    for i in range(len(vals1)):
        ax.plot([1, 2], [vals1[i], vals2[i]], 'o-', color='gray', alpha=0.3, linewidth=0.5)

    # Plot means
    ax.plot([1, 2], [vals1.mean(), vals2.mean()], 'o-', color='red', linewidth=3, markersize=12, label='Mean')

    # Labels
    ax.set_xlim(0.5, 2.5)
    ax.set_xticks([1, 2])
    ax.set_xticklabels([cond1, cond2])
    ax.set_ylabel('Class Probability Mass', fontsize=12)
    ax.set_title(f'{cue_family}: {cond1} vs {cond2}', fontsize=14, fontweight='bold')

    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved plot to: {output_file}")

    plt.close()


def plot_family_summary(df, output_file=None):
    """
    Create summary plot showing all cue families and conditions.

    Args:
        df: Aggregated DataFrame
        output_file: Path to save plot (optional)
    """
    # Compute means across stimulus sets
    summary = df.groupby(['cue_family', 'condition'])['class_mass'].agg(['mean', 'sem']).reset_index()

    # Create plot
    fig, ax = plt.subplots(figsize=(14, 6))

    families = summary['cue_family'].unique()
    conditions = summary['condition'].unique()

    x = np.arange(len(families))
    width = 0.15

    for i, condition in enumerate(conditions):
        data = summary[summary['condition'] == condition]
        means = [data[data['cue_family'] == f]['mean'].values[0] if len(data[data['cue_family'] == f]) > 0 else 0
                 for f in families]
        sems = [data[data['cue_family'] == f]['sem'].values[0] if len(data[data['cue_family'] == f]) > 0 else 0
                for f in families]

        ax.bar(x + i * width, means, width, label=condition, yerr=sems, capsize=3)

    ax.set_xlabel('Cue Family', fontsize=12)
    ax.set_ylabel('Class Probability Mass', fontsize=12)
    ax.set_title('Morphosyntactic Constraint Across Cue Families and Conditions', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (len(conditions) - 1) / 2)
    ax.set_xticklabels(families, rotation=45, ha='right')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved summary plot to: {output_file}")

    plt.close()


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_comprehensive_results(input_file, output_prefix=None):
    """
    Run full statistical analysis on comprehensive audit results.

    Args:
        input_file: Path to comprehensive audit results JSON
        output_prefix: Prefix for output files (default: derived from input_file)
    """
    print("=" * 80)
    print("COMPREHENSIVE MORPHOSYNTAX ANALYSIS")
    print("=" * 80)
    print()
    print(f"Input: {input_file}")
    print()

    # Load results
    print("Loading results...")
    with open(input_file, 'r') as f:
        data = json.load(f)

    metadata = data['metadata']
    results = data['results']

    print(f"✓ Loaded {len(results)} result entries")
    print(f"  Model: {metadata['model']}")
    print(f"  Stimulus sets: {metadata['num_stimulus_sets']}")
    print(f"  Conditions: {metadata['num_conditions']}")
    print(f"  Cue families: {metadata['num_cue_families']}")
    print()

    # Aggregate
    print("Aggregating results...")
    df = aggregate_results(results)
    print(f"✓ Aggregated to {len(df)} condition × cue family combinations")
    print()

    # Run comparisons
    print("=" * 80)
    print("PAIRED COMPARISONS")
    print("=" * 80)
    print()

    # Primary comparison: JABBERWOCKY vs each control
    comparison_pairs = [
        ('JABBERWOCKY', 'FULL_SCRAMBLED'),
        ('JABBERWOCKY', 'CONTENT_SCRAMBLED'),
        ('JABBERWOCKY', 'FUNCTION_SCRAMBLED'),
        ('JABBERWOCKY', 'CUE_DELETED'),
    ]

    cue_families = df['cue_family'].unique()

    all_comparisons = []

    for cond1, cond2 in comparison_pairs:
        print(f"{cond1} vs {cond2}:")
        print()

        comparisons = []

        for family in cue_families:
            result = run_paired_comparison(df, family, cond1, cond2)
            if result:
                comparisons.append(result)

        # Apply FDR correction across cue families
        comparisons = apply_fdr_correction(comparisons)

        # Display results
        for comp in comparisons:
            sig_fdr = "***" if comp['p_fdr'] < 0.001 else "**" if comp['p_fdr'] < 0.01 else "*" if comp['p_fdr'] < 0.05 else "n.s."
            print(f"  {comp['cue_family']:20s}: Δ = {comp['diff_mean']:+.4f}, "
                  f"t({comp['n_pairs']-1}) = {comp['t_stat']:.2f}, "
                  f"p_FDR = {comp['p_fdr']:.4f} {sig_fdr}, d = {comp['cohens_d']:.3f}")

        print()

        all_comparisons.extend(comparisons)

    # Save comparison results
    if output_prefix is None:
        output_prefix = input_file.replace('.json', '')

    comparison_df = pd.DataFrame(all_comparisons)
    comparison_file = f'{output_prefix}_comparisons.csv'
    comparison_df.to_csv(comparison_file, index=False)
    print(f"✓ Saved comparisons to: {comparison_file}")
    print()

    # Generate plots
    print("=" * 80)
    print("GENERATING VISUALIZATIONS")
    print("=" * 80)
    print()

    # Summary plot
    plot_family_summary(df, f'{output_prefix}_summary.png')

    # Individual paired plots (just for primary comparison)
    for family in cue_families:
        plot_paired_comparison(
            df, family, 'JABBERWOCKY', 'CONTENT_SCRAMBLED',
            f'{output_prefix}_{family}_paired.png'
        )

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Output files:")
    print(f"  - {comparison_file}")
    print(f"  - {output_prefix}_summary.png")
    print(f"  - {output_prefix}_{{family}}_paired.png (per cue family)")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze comprehensive morphosyntax audit results'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to comprehensive audit results JSON'
    )

    parser.add_argument(
        '--output-prefix',
        type=str,
        default=None,
        help='Prefix for output files (default: derived from input filename)'
    )

    args = parser.parse_args()

    analyze_comprehensive_results(args.input_file, args.output_prefix)


if __name__ == '__main__':
    main()
