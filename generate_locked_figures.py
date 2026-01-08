#!/usr/bin/env python3
"""
Publication-Ready Figure Generation for Locked Design Morphosyntax Audit

Generates three key figures:

1. MORPHOSYNTAX SLOT CONSTRAINT (Primary Figure)
   - y: target-class mass
   - x: condition (SENTENCE, JABBERWOCKY, FULL_S, CONTENT_S, FUNCTION_S, CUE_DEL)
   - panels: cue family (6 panels)
   - Can overlay multiple models with different colors

2. KEY PAIRED-DIFFERENCE PLOT
   - Per-item paired differences:
     - Jabberwocky − FullScrambled
     - Jabberwocky − ContentScrambled
     - Jabberwocky − FunctionScrambled
   - Shows distribution and significance

3. CONTEXT ABLATION CURVES
   - y: target-class mass
   - x: k (context length: 1, 2, 4, 8, full)
   - lines: conditions
   - panels: cue family

Usage:
    python generate_locked_figures.py locked_audit_gpt2.json
    python generate_locked_figures.py locked_audit_gpt2.json locked_audit_gpt2-medium.json --models gpt2 gpt2-medium
"""

import json
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from typing import List, Dict, Optional
from pathlib import Path

# Publication-quality settings
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'sans-serif',
})

# Color palette
CONDITION_COLORS = {
    'SENTENCE': '#2ecc71',        # Green
    'JABBERWOCKY': '#3498db',     # Blue
    'FULL_SCRAMBLED': '#e74c3c',  # Red
    'CONTENT_SCRAMBLED': '#f39c12', # Orange
    'FUNCTION_SCRAMBLED': '#9b59b6', # Purple
    'CUE_DELETED': '#95a5a6',     # Gray
}

CONDITION_ORDER = [
    'SENTENCE', 'JABBERWOCKY', 'FULL_SCRAMBLED',
    'CONTENT_SCRAMBLED', 'FUNCTION_SCRAMBLED', 'CUE_DELETED'
]

CONDITION_LABELS = {
    'SENTENCE': 'Sentence',
    'JABBERWOCKY': 'Jabberwocky',
    'FULL_SCRAMBLED': 'Full Scr.',
    'CONTENT_SCRAMBLED': 'Content Scr.',
    'FUNCTION_SCRAMBLED': 'Function Scr.',
    'CUE_DELETED': 'Cue Del.',
}

CUE_FAMILY_ORDER = [
    'infinitival_to', 'modals', 'determiners',
    'prepositions', 'auxiliaries', 'complementizers'
]

CUE_FAMILY_LABELS = {
    'infinitival_to': 'Infinitival TO → VERB',
    'modals': 'Modals → VERB',
    'determiners': 'Determiners → NOUN/ADJ',
    'prepositions': 'Prepositions → NP',
    'auxiliaries': 'Auxiliaries → PARTICIPLE',
    'complementizers': 'Complementizers → CLAUSE',
}

MODEL_COLORS = ['#2c3e50', '#e74c3c', '#27ae60', '#8e44ad', '#f39c12']
MODEL_MARKERS = ['o', 's', '^', 'D', 'v']


# ============================================================================
# DATA LOADING
# ============================================================================

def load_results(filepath: str) -> pd.DataFrame:
    """Load results JSON into DataFrame."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data['results'])
    df['model'] = data['metadata']['model']
    return df


def load_multiple_results(filepaths: List[str], model_names: Optional[List[str]] = None) -> pd.DataFrame:
    """Load multiple results files and combine."""
    dfs = []
    for i, fp in enumerate(filepaths):
        df = load_results(fp)
        if model_names and i < len(model_names):
            df['model'] = model_names[i]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


# ============================================================================
# FIGURE 1: MORPHOSYNTAX SLOT CONSTRAINT
# ============================================================================

def plot_slot_constraint(
    df: pd.DataFrame,
    context_k: str = 'full',
    output_file: str = 'figure1_slot_constraint.png'
):
    """
    Primary figure: Target-class mass by condition for each cue family.

    Creates a 2×3 grid of panels (one per cue family).
    """
    df_k = df[df['context_k'] == context_k].copy()
    models = df_k['model'].unique()
    n_models = len(models)

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for idx, family in enumerate(CUE_FAMILY_ORDER):
        ax = axes[idx]
        df_fam = df_k[df_k['cue_family'] == family]

        # Compute means and SEs
        summary = df_fam.groupby(['model', 'condition'])['target_mass'].agg(
            ['mean', 'std', 'count']
        ).reset_index()
        summary['se'] = summary['std'] / np.sqrt(summary['count'])

        # Plot bars for each model
        x = np.arange(len(CONDITION_ORDER))
        width = 0.8 / n_models

        for m_idx, model in enumerate(models):
            model_data = summary[summary['model'] == model]

            means = []
            ses = []
            for cond in CONDITION_ORDER:
                cond_data = model_data[model_data['condition'] == cond]
                if len(cond_data) > 0:
                    means.append(cond_data['mean'].values[0])
                    ses.append(cond_data['se'].values[0])
                else:
                    means.append(0)
                    ses.append(0)

            offset = (m_idx - (n_models - 1) / 2) * width
            bars = ax.bar(
                x + offset, means, width,
                yerr=ses, capsize=2,
                label=model if idx == 0 else '',
                color=MODEL_COLORS[m_idx % len(MODEL_COLORS)],
                alpha=0.8,
                edgecolor='white',
            )

        # Styling
        ax.set_title(CUE_FAMILY_LABELS[family], fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([CONDITION_LABELS[c] for c in CONDITION_ORDER], rotation=45, ha='right')
        ax.set_ylabel('Target Class Mass')
        ax.set_ylim(0, None)
        ax.axhline(y=0, color='gray', linewidth=0.5)

        # Add horizontal line at chance level (approximate)
        # ax.axhline(y=0.1, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    # Legend
    if n_models > 1:
        fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=n_models)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


def plot_slot_constraint_lines(
    df: pd.DataFrame,
    context_k: str = 'full',
    output_file: str = 'figure1_slot_constraint_lines.png'
):
    """
    Alternative line plot version for multiple models.
    """
    df_k = df[df['context_k'] == context_k].copy()
    models = df_k['model'].unique()

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for idx, family in enumerate(CUE_FAMILY_ORDER):
        ax = axes[idx]
        df_fam = df_k[df_k['cue_family'] == family]

        for m_idx, model in enumerate(models):
            df_model = df_fam[df_fam['model'] == model]

            summary = df_model.groupby('condition')['target_mass'].agg(['mean', 'std', 'count'])
            summary['se'] = summary['std'] / np.sqrt(summary['count'])

            means = [summary.loc[c, 'mean'] if c in summary.index else np.nan for c in CONDITION_ORDER]
            ses = [summary.loc[c, 'se'] if c in summary.index else 0 for c in CONDITION_ORDER]

            x = np.arange(len(CONDITION_ORDER))

            ax.errorbar(
                x, means, yerr=ses,
                marker=MODEL_MARKERS[m_idx % len(MODEL_MARKERS)],
                color=MODEL_COLORS[m_idx % len(MODEL_COLORS)],
                label=model if idx == 0 else '',
                capsize=3, linewidth=1.5, markersize=6
            )

        ax.set_title(CUE_FAMILY_LABELS[family], fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([CONDITION_LABELS[c] for c in CONDITION_ORDER], rotation=45, ha='right')
        ax.set_ylabel('Target Class Mass')
        ax.set_ylim(0, None)

    if len(models) > 1:
        fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=len(models))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


# ============================================================================
# FIGURE 2: PAIRED DIFFERENCE PLOT
# ============================================================================

def plot_paired_differences(
    df: pd.DataFrame,
    context_k: str = 'full',
    output_file: str = 'figure2_paired_differences.png'
):
    """
    Show per-item paired differences for key contrasts.

    Contrasts:
    - Jabberwocky - FullScrambled
    - Jabberwocky - ContentScrambled
    - Jabberwocky - FunctionScrambled
    """
    df_k = df[df['context_k'] == context_k].copy()

    contrasts = [
        ('JABBERWOCKY', 'FULL_SCRAMBLED', 'JAB − Full Scr.'),
        ('JABBERWOCKY', 'CONTENT_SCRAMBLED', 'JAB − Content Scr.'),
        ('JABBERWOCKY', 'FUNCTION_SCRAMBLED', 'JAB − Function Scr.'),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for fam_idx, family in enumerate(CUE_FAMILY_ORDER):
        ax = axes[fam_idx]
        df_fam = df_k[df_k['cue_family'] == family]

        diff_data = []
        labels = []

        for cond_a, cond_b, label in contrasts:
            # Get paired values
            df_a = df_fam[df_fam['condition'] == cond_a].set_index('set_id')['target_mass']
            df_b = df_fam[df_fam['condition'] == cond_b].set_index('set_id')['target_mass']

            common_ids = df_a.index.intersection(df_b.index)
            if len(common_ids) == 0:
                continue

            diffs = (df_a.loc[common_ids] - df_b.loc[common_ids]).values
            diff_data.append(diffs)
            labels.append(label)

        # Create violin plot
        if diff_data:
            parts = ax.violinplot(diff_data, positions=range(len(labels)),
                                  showmeans=True, showmedians=False)

            # Color the violins
            colors = ['#3498db', '#f39c12', '#9b59b6']
            for i, pc in enumerate(parts['bodies']):
                pc.set_facecolor(colors[i % len(colors)])
                pc.set_alpha(0.7)

            # Add individual points
            for i, diffs in enumerate(diff_data):
                jitter = np.random.uniform(-0.1, 0.1, len(diffs))
                ax.scatter(np.full(len(diffs), i) + jitter, diffs,
                          alpha=0.3, s=15, color='gray')

            # Add zero line
            ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)

            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=30, ha='right')

        ax.set_title(CUE_FAMILY_LABELS[family], fontweight='bold')
        ax.set_ylabel('Difference in Target Mass')

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


def plot_paired_differences_summary(
    df: pd.DataFrame,
    context_k: str = 'full',
    output_file: str = 'figure2_paired_diff_summary.png'
):
    """
    Summary plot: Mean differences with 95% CI across all cue families.
    """
    df_k = df[df['context_k'] == context_k].copy()

    contrasts = [
        ('JABBERWOCKY', 'FULL_SCRAMBLED', 'JAB − Full'),
        ('JABBERWOCKY', 'CONTENT_SCRAMBLED', 'JAB − Content'),
        ('JABBERWOCKY', 'FUNCTION_SCRAMBLED', 'JAB − Function'),
    ]

    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(CUE_FAMILY_ORDER))
    width = 0.25

    for c_idx, (cond_a, cond_b, label) in enumerate(contrasts):
        means = []
        cis = []

        for family in CUE_FAMILY_ORDER:
            df_fam = df_k[df_k['cue_family'] == family]

            df_a = df_fam[df_fam['condition'] == cond_a].set_index('set_id')['target_mass']
            df_b = df_fam[df_fam['condition'] == cond_b].set_index('set_id')['target_mass']

            common_ids = df_a.index.intersection(df_b.index)
            if len(common_ids) > 0:
                diffs = (df_a.loc[common_ids] - df_b.loc[common_ids]).values
                means.append(np.mean(diffs))
                se = np.std(diffs) / np.sqrt(len(diffs))
                cis.append(1.96 * se)
            else:
                means.append(0)
                cis.append(0)

        offset = (c_idx - 1) * width
        bars = ax.bar(
            x + offset, means, width, yerr=cis, capsize=3,
            label=label, alpha=0.8
        )

    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([CUE_FAMILY_LABELS[f].split('→')[0].strip()
                        for f in CUE_FAMILY_ORDER], rotation=30, ha='right')
    ax.set_ylabel('Mean Difference in Target Mass')
    ax.set_title('Key Contrasts: Jabberwocky vs. Scrambled Conditions', fontweight='bold')
    ax.legend(loc='upper right')

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


# ============================================================================
# FIGURE 3: CONTEXT ABLATION CURVES
# ============================================================================

def plot_context_ablation(
    df: pd.DataFrame,
    output_file: str = 'figure3_context_ablation.png'
):
    """
    Context ablation curves: Target mass vs context length k.
    """
    # Map context_k to numeric for plotting
    k_order = ['1', '2', '4', '8', 'full']
    k_numeric = {'1': 1, '2': 2, '4': 4, '8': 8, 'full': 16}  # Use 16 for 'full'

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    # Focus conditions for ablation
    ablation_conditions = ['SENTENCE', 'JABBERWOCKY', 'FULL_SCRAMBLED', 'FUNCTION_SCRAMBLED']

    for fam_idx, family in enumerate(CUE_FAMILY_ORDER):
        ax = axes[fam_idx]
        df_fam = df[df['cue_family'] == family]

        for cond in ablation_conditions:
            df_cond = df_fam[df_fam['condition'] == cond]

            x_vals = []
            y_vals = []
            y_errs = []

            for k in k_order:
                df_k = df_cond[df_cond['context_k'] == k]
                if len(df_k) > 0:
                    x_vals.append(k_numeric[k])
                    y_vals.append(df_k['target_mass'].mean())
                    y_errs.append(df_k['target_mass'].std() / np.sqrt(len(df_k)))

            if x_vals:
                ax.errorbar(
                    x_vals, y_vals, yerr=y_errs,
                    marker='o', label=CONDITION_LABELS[cond] if fam_idx == 0 else '',
                    color=CONDITION_COLORS[cond],
                    capsize=3, linewidth=2, markersize=6
                )

        ax.set_title(CUE_FAMILY_LABELS[family], fontweight='bold')
        ax.set_xlabel('Context Length (k)')
        ax.set_ylabel('Target Class Mass')
        ax.set_xscale('log', base=2)
        ax.set_xticks([1, 2, 4, 8, 16])
        ax.set_xticklabels(['1', '2', '4', '8', 'full'])
        ax.set_ylim(0, None)

    # Legend
    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=len(ablation_conditions))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


def plot_context_ablation_jab_vs_scramble(
    df: pd.DataFrame,
    output_file: str = 'figure3_ablation_jab_comparison.png'
):
    """
    Focused ablation: Compare Jabberwocky to scrambled conditions only.
    """
    k_order = ['1', '2', '4', '8', 'full']
    k_numeric = {'1': 1, '2': 2, '4': 4, '8': 8, 'full': 16}

    conditions = ['JABBERWOCKY', 'FULL_SCRAMBLED', 'CONTENT_SCRAMBLED', 'FUNCTION_SCRAMBLED']

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for fam_idx, family in enumerate(CUE_FAMILY_ORDER):
        ax = axes[fam_idx]
        df_fam = df[df['cue_family'] == family]

        for cond in conditions:
            df_cond = df_fam[df_fam['condition'] == cond]

            x_vals = []
            y_vals = []
            y_errs = []

            for k in k_order:
                df_k = df_cond[df_cond['context_k'] == k]
                if len(df_k) > 0:
                    x_vals.append(k_numeric[k])
                    y_vals.append(df_k['target_mass'].mean())
                    y_errs.append(df_k['target_mass'].std() / np.sqrt(len(df_k)))

            if x_vals:
                linestyle = '-' if cond == 'JABBERWOCKY' else '--'
                ax.errorbar(
                    x_vals, y_vals, yerr=y_errs,
                    marker='o', label=CONDITION_LABELS[cond] if fam_idx == 0 else '',
                    color=CONDITION_COLORS[cond],
                    linestyle=linestyle,
                    capsize=3, linewidth=2, markersize=6
                )

        ax.set_title(CUE_FAMILY_LABELS[family], fontweight='bold')
        ax.set_xlabel('Context Length (k)')
        ax.set_ylabel('Target Class Mass')
        ax.set_xscale('log', base=2)
        ax.set_xticks([1, 2, 4, 8, 16])
        ax.set_xticklabels(['1', '2', '4', '8', 'full'])
        ax.set_ylim(0, None)

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 1.02), ncol=len(conditions))

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

    print(f"Saved: {output_file}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generate publication-ready figures for locked design audit'
    )
    parser.add_argument('results_files', type=str, nargs='+',
                       help='Path(s) to results JSON file(s)')
    parser.add_argument('--models', type=str, nargs='*', default=None,
                       help='Model names for legend (if multiple files)')
    parser.add_argument('--output-dir', type=str, default='figures',
                       help='Output directory for figures')

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Load data
    print("Loading results...")
    if len(args.results_files) == 1:
        df = load_results(args.results_files[0])
    else:
        df = load_multiple_results(args.results_files, args.models)

    print(f"  Models: {df['model'].unique().tolist()}")
    print(f"  Total rows: {len(df)}")
    print()

    # Generate figures
    print("Generating figures...")
    print()

    # Figure 1: Slot constraint
    plot_slot_constraint(
        df, context_k='full',
        output_file=str(output_dir / 'figure1_slot_constraint.png')
    )

    if len(df['model'].unique()) > 1:
        plot_slot_constraint_lines(
            df, context_k='full',
            output_file=str(output_dir / 'figure1_slot_constraint_lines.png')
        )

    # Figure 2: Paired differences
    plot_paired_differences(
        df, context_k='full',
        output_file=str(output_dir / 'figure2_paired_differences.png')
    )

    plot_paired_differences_summary(
        df, context_k='full',
        output_file=str(output_dir / 'figure2_paired_diff_summary.png')
    )

    # Figure 3: Context ablation
    plot_context_ablation(
        df,
        output_file=str(output_dir / 'figure3_context_ablation.png')
    )

    plot_context_ablation_jab_vs_scramble(
        df,
        output_file=str(output_dir / 'figure3_ablation_jab_comparison.png')
    )

    print()
    print("=" * 60)
    print("FIGURES GENERATED")
    print("=" * 60)
    print()
    print(f"Output directory: {output_dir}")
    print()
    print("Files created:")
    for f in sorted(output_dir.glob('*.png')):
        print(f"  {f.name}")


if __name__ == '__main__':
    main()
