#!/usr/bin/env python3
"""
Statistical Analysis for Locked Design Morphosyntax Audit

Computes:
- Key paired differences (Jabberwocky vs each scramble condition)
- FDR-corrected p-values (Benjamini-Hochberg)
- Bootstrap confidence intervals
- Effect sizes (Cohen's d)
- Summary tables per cue family

Key Contrasts:
1. JABBERWOCKY vs FULL_SCRAMBLED (skeleton effect)
2. JABBERWOCKY vs CONTENT_SCRAMBLED (content ordering effect)
3. JABBERWOCKY vs FUNCTION_SCRAMBLED (skeleton necessity)
4. SENTENCE vs JABBERWOCKY (nonce substitution effect)

Usage:
    python analyze_locked_results.py locked_audit_gpt2.json
"""

import json
import argparse
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# STATISTICAL FUNCTIONS
# ============================================================================

def paired_ttest(x: np.ndarray, y: np.ndarray) -> Tuple[float, float]:
    """Paired t-test returning (t-statistic, p-value)."""
    with np.errstate(invalid='ignore'):
        result = stats.ttest_rel(x, y)
    return result.statistic, result.pvalue


def cohens_d_paired(x: np.ndarray, y: np.ndarray) -> float:
    """Cohen's d for paired samples."""
    diff = x - y
    return np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0.0


def bootstrap_ci(
    data: np.ndarray,
    n_bootstrap: int = 10000,
    ci: float = 0.95,
    seed: int = 42
) -> Tuple[float, float]:
    """Bootstrap confidence interval for mean."""
    rng = np.random.RandomState(seed)
    boot_means = []

    for _ in range(n_bootstrap):
        boot_sample = rng.choice(data, size=len(data), replace=True)
        boot_means.append(np.mean(boot_sample))

    lower = np.percentile(boot_means, (1 - ci) / 2 * 100)
    upper = np.percentile(boot_means, (1 + ci) / 2 * 100)

    return lower, upper


def fdr_correction(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """
    Benjamini-Hochberg FDR correction.

    Returns:
        (adjusted_p_values, significant_mask)
    """
    n = len(p_values)
    if n == 0:
        return np.array([]), np.array([], dtype=bool)

    # Sort p-values
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]

    # Calculate adjusted p-values
    adjusted_p = np.zeros(n)
    for i, p in enumerate(sorted_p):
        adjusted_p[i] = p * n / (i + 1)

    # Ensure monotonicity (from end to start)
    for i in range(n - 2, -1, -1):
        adjusted_p[i] = min(adjusted_p[i], adjusted_p[i + 1])

    # Cap at 1
    adjusted_p = np.minimum(adjusted_p, 1.0)

    # Restore original order
    result = np.zeros(n)
    result[sorted_idx] = adjusted_p

    significant = result < alpha

    return result, significant


# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def load_results(filepath: str) -> Tuple[Dict, pd.DataFrame]:
    """Load results JSON into metadata dict and DataFrame."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    metadata = data['metadata']
    results = data['results']

    df = pd.DataFrame(results)
    return metadata, df


def compute_contrasts(df: pd.DataFrame, context_k: str = 'full') -> pd.DataFrame:
    """
    Compute key paired contrasts for each cue family.

    Returns DataFrame with statistical results.
    """
    # Filter to specified context length
    df_k = df[df['context_k'] == context_k].copy()

    contrasts = [
        ('SENTENCE', 'JABBERWOCKY'),
        ('JABBERWOCKY', 'FULL_SCRAMBLED'),
        ('JABBERWOCKY', 'CONTENT_SCRAMBLED'),
        ('JABBERWOCKY', 'FUNCTION_SCRAMBLED'),
        ('JABBERWOCKY', 'CUE_DELETED'),
    ]

    results = []

    for family in df_k['cue_family'].unique():
        df_fam = df_k[df_k['cue_family'] == family]

        for cond_a, cond_b in contrasts:
            # Get paired values by set_id
            df_a = df_fam[df_fam['condition'] == cond_a].set_index('set_id')['target_mass']
            df_b = df_fam[df_fam['condition'] == cond_b].set_index('set_id')['target_mass']

            # Ensure alignment
            common_ids = df_a.index.intersection(df_b.index)
            if len(common_ids) == 0:
                continue

            x = df_a.loc[common_ids].values
            y = df_b.loc[common_ids].values

            # Statistics
            mean_a = np.mean(x)
            mean_b = np.mean(y)
            diff = mean_a - mean_b
            t_stat, p_val = paired_ttest(x, y)
            d = cohens_d_paired(x, y)

            # Bootstrap CI for difference
            diff_vals = x - y
            ci_low, ci_high = bootstrap_ci(diff_vals)

            results.append({
                'cue_family': family,
                'contrast': f"{cond_a} - {cond_b}",
                'cond_a': cond_a,
                'cond_b': cond_b,
                'mean_a': mean_a,
                'mean_b': mean_b,
                'diff': diff,
                'ci_low': ci_low,
                'ci_high': ci_high,
                't_stat': t_stat,
                'p_value': p_val,
                'cohens_d': d,
                'n': len(common_ids),
            })

    df_results = pd.DataFrame(results)

    # Apply FDR correction
    if len(df_results) > 0:
        p_vals = df_results['p_value'].values
        adjusted_p, significant = fdr_correction(p_vals)
        df_results['p_adjusted'] = adjusted_p
        df_results['significant'] = significant

    return df_results


def compute_summary_table(df: pd.DataFrame, context_k: str = 'full') -> pd.DataFrame:
    """
    Compute summary table: mean ± SE for each family × condition.
    """
    df_k = df[df['context_k'] == context_k].copy()

    summary = df_k.groupby(['cue_family', 'condition'])['target_mass'].agg(
        ['mean', 'std', 'count']
    ).reset_index()

    summary['se'] = summary['std'] / np.sqrt(summary['count'])
    summary['ci'] = 1.96 * summary['se']

    # Pivot to wide format
    pivot = summary.pivot(index='cue_family', columns='condition', values='mean')

    return pivot


def compute_context_ablation_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute context ablation summary: mean target mass by k for each family.
    """
    # Focus on JABBERWOCKY condition for ablation
    df_jab = df[df['condition'] == 'JABBERWOCKY'].copy()

    summary = df_jab.groupby(['cue_family', 'context_k'])['target_mass'].agg(
        ['mean', 'std', 'count']
    ).reset_index()

    summary['se'] = summary['std'] / np.sqrt(summary['count'])

    # Pivot
    pivot = summary.pivot(index='cue_family', columns='context_k', values='mean')

    # Reorder columns
    col_order = ['1', '2', '4', '8', 'full']
    pivot = pivot[[c for c in col_order if c in pivot.columns]]

    return pivot


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze locked design morphosyntax audit results'
    )
    parser.add_argument('results_file', type=str, help='Path to results JSON')
    parser.add_argument('--output-prefix', type=str, default=None,
                       help='Prefix for output files')

    args = parser.parse_args()

    # Determine output prefix
    if args.output_prefix is None:
        args.output_prefix = args.results_file.replace('.json', '')

    print("=" * 80)
    print("LOCKED DESIGN ANALYSIS")
    print("=" * 80)
    print()

    # Load data
    print(f"Loading: {args.results_file}")
    metadata, df = load_results(args.results_file)
    print(f"  Model: {metadata['model']}")
    print(f"  Stimuli: {metadata['stimuli_file']}")
    print(f"  Results: {len(df)} rows")
    print()

    # 1. Summary table
    print("=" * 80)
    print("SUMMARY TABLE (k=full)")
    print("=" * 80)
    print()

    summary = compute_summary_table(df, context_k='full')
    print(summary.round(3).to_string())
    print()

    # Save summary
    summary_file = f"{args.output_prefix}_summary.csv"
    summary.to_csv(summary_file)
    print(f"Saved: {summary_file}")
    print()

    # 2. Statistical contrasts
    print("=" * 80)
    print("KEY CONTRASTS (FDR-corrected)")
    print("=" * 80)
    print()

    contrasts = compute_contrasts(df, context_k='full')

    # Format for display
    display_cols = ['cue_family', 'contrast', 'diff', 'ci_low', 'ci_high',
                   'p_value', 'p_adjusted', 'cohens_d', 'significant']

    print(contrasts[display_cols].round(4).to_string(index=False))
    print()

    # Save contrasts
    contrasts_file = f"{args.output_prefix}_contrasts.csv"
    contrasts.to_csv(contrasts_file, index=False)
    print(f"Saved: {contrasts_file}")
    print()

    # 3. Key findings
    print("=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print()

    # Group by contrast type
    contrast_types = contrasts['contrast'].unique()

    for ct in contrast_types:
        ct_df = contrasts[contrasts['contrast'] == ct]
        n_sig = ct_df['significant'].sum()
        n_total = len(ct_df)

        avg_diff = ct_df['diff'].mean()
        avg_d = ct_df['cohens_d'].mean()

        print(f"{ct}:")
        print(f"  Significant families: {n_sig}/{n_total}")
        print(f"  Average difference: {avg_diff:.4f}")
        print(f"  Average Cohen's d: {avg_d:.3f}")
        print()

    # 4. Context ablation
    print("=" * 80)
    print("CONTEXT ABLATION (JABBERWOCKY condition)")
    print("=" * 80)
    print()

    ablation = compute_context_ablation_summary(df)
    print(ablation.round(3).to_string())
    print()

    ablation_file = f"{args.output_prefix}_ablation.csv"
    ablation.to_csv(ablation_file)
    print(f"Saved: {ablation_file}")
    print()

    # 5. Interpretation
    print("=" * 80)
    print("INTERPRETATION GUIDE")
    print("=" * 80)
    print()

    print("Key contrasts to report:")
    print()
    print("1. JABBERWOCKY vs FULL_SCRAMBLED:")
    print("   Tests: Does ANY structure help?")
    print("   If JAB > FULL: Yes, structure matters")
    print()
    print("2. JABBERWOCKY vs FUNCTION_SCRAMBLED:")
    print("   Tests: Is function-word skeleton NECESSARY?")
    print("   If JAB > FUNC_S: Yes, skeleton is necessary")
    print()
    print("3. JABBERWOCKY vs CONTENT_SCRAMBLED:")
    print("   Tests: Does content word ORDER matter?")
    print("   If JAB ≈ CONT_S (p > 0.05): No, content order doesn't matter")
    print("   This would support 'skeleton sufficiency'")
    print()
    print("4. SENTENCE vs JABBERWOCKY:")
    print("   Tests: Does nonce substitution hurt?")
    print("   If SENT ≈ JAB: Nonce words don't impair constraint")
    print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Output files:")
    print(f"  {summary_file}")
    print(f"  {contrasts_file}")
    print(f"  {ablation_file}")
    print()
    print("Next: Generate figures with:")
    print(f"  python generate_locked_figures.py {args.results_file}")


if __name__ == '__main__':
    main()
