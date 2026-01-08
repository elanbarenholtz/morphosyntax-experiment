#!/usr/bin/env python3
"""
Analyze Context-Length Ablation Results

Generates:
- Summary tables with mean±CI by k for each condition
- Plots: target_mass vs k for each condition (one per cue family)
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


# ============================================================================
# BOOTSTRAP CONFIDENCE INTERVALS
# ============================================================================

def bootstrap_ci(data, n_bootstrap=10000, ci_level=0.95):
    """
    Compute bootstrap confidence interval for mean.

    Args:
        data: Array of values
        n_bootstrap: Number of bootstrap samples
        ci_level: Confidence level

    Returns:
        (lower, upper) bounds
    """
    if len(data) == 0:
        return np.nan, np.nan

    bootstrap_means = []

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(sample))

    alpha = 1 - ci_level
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)

    return lower, upper


# ============================================================================
# SUMMARY TABLES
# ============================================================================

def generate_summary_tables(df, output_prefix):
    """
    Generate summary tables for each cue family.

    Args:
        df: Results DataFrame
        output_prefix: Prefix for output files
    """
    print("=" * 80)
    print("SUMMARY TABLES")
    print("=" * 80)
    print()

    # K values in order
    k_order = ['1', '2', '4', 'full']

    for cue_family in df['cue_family'].unique():
        df_family = df[df['cue_family'] == cue_family]

        print(f"Cue Family: {cue_family}")
        print()

        # Create summary table
        summary_rows = []

        for condition in df_family['condition'].unique():
            df_cond = df_family[df_family['condition'] == condition]

            for k in k_order:
                df_k = df_cond[df_cond['k'] == k]

                if len(df_k) == 0:
                    continue

                # Aggregate by sentence_id (each sentence has one or more cue instances)
                # Average across cue instances within each sentence
                df_agg = df_k.groupby('sentence_id')['target_mass'].mean().reset_index()

                values = df_agg['target_mass'].values

                # Compute statistics
                mean = values.mean()
                std = values.std()
                sem = values.std() / np.sqrt(len(values))
                ci_lower, ci_upper = bootstrap_ci(values)

                summary_rows.append({
                    'condition': condition,
                    'k': k,
                    'n_sentences': len(df_agg),
                    'mean': mean,
                    'std': std,
                    'sem': sem,
                    'ci_lower': ci_lower,
                    'ci_upper': ci_upper,
                })

        summary_df = pd.DataFrame(summary_rows)

        # Save to CSV
        output_file = f'{output_prefix}_{cue_family}_summary.csv'
        summary_df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file}")

        # Display table
        print()
        print(summary_df.to_string(index=False))
        print()
        print()

    print("=" * 80)
    print()


# ============================================================================
# PLOTS
# ============================================================================

def plot_ablation_curves(df, output_prefix):
    """
    Plot target_mass vs k for each condition.

    Args:
        df: Results DataFrame
        output_prefix: Prefix for output files
    """
    print("=" * 80)
    print("GENERATING PLOTS")
    print("=" * 80)
    print()

    # K values in numeric order (for plotting)
    k_order = ['1', '2', '4', 'full']
    k_positions = [1, 2, 4, 8]  # Use 8 for "full" on x-axis

    # Color palette
    colors = {
        'JABBERWOCKY': '#2ecc71',
        'FUNCTION_SCRAMBLED': '#e74c3c',
        'FULL_SCRAMBLED': '#95a5a6',
    }

    for cue_family in df['cue_family'].unique():
        df_family = df[df['cue_family'] == cue_family]

        fig, ax = plt.subplots(figsize=(10, 6))

        for condition in df_family['condition'].unique():
            df_cond = df_family[df_family['condition'] == condition]

            # Aggregate by sentence, then compute mean and CI across sentences
            means = []
            cis_lower = []
            cis_upper = []

            for k in k_order:
                df_k = df_cond[df_cond['k'] == k]

                if len(df_k) == 0:
                    means.append(np.nan)
                    cis_lower.append(np.nan)
                    cis_upper.append(np.nan)
                    continue

                # Aggregate by sentence
                df_agg = df_k.groupby('sentence_id')['target_mass'].mean().reset_index()
                values = df_agg['target_mass'].values

                mean = values.mean()
                ci_lower, ci_upper = bootstrap_ci(values)

                means.append(mean)
                cis_lower.append(ci_lower)
                cis_upper.append(ci_upper)

            # Convert to arrays
            means = np.array(means)
            cis_lower = np.array(cis_lower)
            cis_upper = np.array(cis_upper)

            # Remove NaN entries
            valid = ~np.isnan(means)
            x_positions = np.array(k_positions)[valid]
            means = means[valid]
            cis_lower = cis_lower[valid]
            cis_upper = cis_upper[valid]

            # Plot
            color = colors.get(condition, '#3498db')

            ax.plot(x_positions, means, 'o-', label=condition, color=color,
                   linewidth=2, markersize=8)

            # Error bars (CIs)
            ax.fill_between(x_positions, cis_lower, cis_upper,
                           alpha=0.2, color=color)

        # Formatting
        ax.set_xlabel('Context Length (k words)', fontsize=12)
        ax.set_ylabel('Target Class Probability Mass', fontsize=12)
        ax.set_title(f'Context-Length Ablation: {cue_family}',
                    fontsize=14, fontweight='bold')

        # X-axis: log scale or custom ticks
        ax.set_xscale('log', base=2)
        ax.set_xticks([1, 2, 4, 8])
        ax.set_xticklabels(['1', '2', '4', 'full'])

        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)

        # Y-axis: start from 0
        ax.set_ylim(bottom=0)

        plt.tight_layout()

        # Save
        output_file = f'{output_prefix}_{cue_family}_ablation_plot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_file}")

        plt.close()

    print()
    print("=" * 80)
    print()


# ============================================================================
# INTERPRETATION
# ============================================================================

def interpret_results(df):
    """
    Provide interpretation guidance based on results.

    Args:
        df: Results DataFrame
    """
    print("=" * 80)
    print("INTERPRETATION GUIDANCE")
    print("=" * 80)
    print()

    k_order = ['1', '2', '4', 'full']

    for cue_family in df['cue_family'].unique():
        df_family = df[df['cue_family'] == cue_family]

        print(f"Cue Family: {cue_family}")
        print()

        # Check if Jabberwocky saturates early
        df_jab = df_family[df_family['condition'] == 'JABBERWOCKY']

        if len(df_jab) > 0:
            # Aggregate by sentence for each k
            k_means = []
            for k in k_order:
                df_k = df_jab[df_jab['k'] == k]
                if len(df_k) > 0:
                    df_agg = df_k.groupby('sentence_id')['target_mass'].mean()
                    k_means.append(df_agg.mean())
                else:
                    k_means.append(np.nan)

            # Check if saturates at k=1
            if not np.isnan(k_means[0]) and not np.isnan(k_means[-1]):
                k1_mass = k_means[0]
                full_mass = k_means[-1]
                increase = full_mass - k1_mass

                print(f"  JABBERWOCKY:")
                print(f"    k=1: {k1_mass:.4f}")
                print(f"    k=full: {full_mass:.4f}")
                print(f"    Increase: {increase:.4f} ({increase/k1_mass*100:.1f}%)")
                print()

                if increase < 0.05:  # Less than 5% increase
                    print("  → Effect is mostly CUE-ONLY (saturates at k=1)")
                else:
                    print("  → Broader SCAFFOLD matters (increases with k)")

                print()

        # Check if FUNCTION_SCRAMBLED shows reduced scaffold effect
        df_func = df_family[df_family['condition'] == 'FUNCTION_SCRAMBLED']

        if len(df_func) > 0 and len(df_jab) > 0:
            # Compare slopes (k=1 to k=full)
            jab_k1 = df_jab[df_jab['k'] == '1'].groupby('sentence_id')['target_mass'].mean().mean()
            jab_full = df_jab[df_jab['k'] == 'full'].groupby('sentence_id')['target_mass'].mean().mean()
            jab_slope = jab_full - jab_k1

            func_k1 = df_func[df_func['k'] == '1'].groupby('sentence_id')['target_mass'].mean().mean()
            func_full = df_func[df_func['k'] == 'full'].groupby('sentence_id')['target_mass'].mean().mean()
            func_slope = func_full - func_k1

            print(f"  Scaffold effect comparison:")
            print(f"    JABBERWOCKY slope: {jab_slope:.4f}")
            print(f"    FUNCTION_SCRAMBLED slope: {func_slope:.4f}")
            print()

            if func_slope < jab_slope * 0.5:  # Less than half the slope
                print("  → Function skeleton is critical for scaffold effect")
            else:
                print("  → Scaffold effect persists even without function skeleton")

            print()

        print("-" * 80)
        print()


# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def analyze_context_ablation(input_file, output_prefix=None):
    """
    Analyze context-length ablation results.

    Args:
        input_file: Path to ablation results CSV
        output_prefix: Prefix for output files (default: derived from input)
    """
    print("=" * 80)
    print("CONTEXT-LENGTH ABLATION ANALYSIS")
    print("=" * 80)
    print()
    print(f"Input: {input_file}")
    print()

    # Load results
    print("Loading results...")
    df = pd.read_csv(input_file)
    print(f"✓ Loaded {len(df)} measurements")
    print()

    # Determine output prefix
    if output_prefix is None:
        output_prefix = input_file.replace('.csv', '')

    # Generate summary tables
    generate_summary_tables(df, output_prefix)

    # Generate plots
    plot_ablation_curves(df, output_prefix)

    # Interpret results
    interpret_results(df)

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Output files:")
    print(f"  - {output_prefix}_{{cue_family}}_summary.csv")
    print(f"  - {output_prefix}_{{cue_family}}_ablation_plot.png")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze context-length ablation results'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Path to ablation results CSV'
    )

    parser.add_argument(
        '--output-prefix',
        type=str,
        default=None,
        help='Prefix for output files (default: derived from input filename)'
    )

    args = parser.parse_args()

    analyze_context_ablation(args.input_file, args.output_prefix)


if __name__ == '__main__':
    main()
