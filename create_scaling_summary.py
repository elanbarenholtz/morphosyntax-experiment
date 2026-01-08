"""
Create comprehensive scaling analysis summary:
1. Table with all models
2. Scaling plot
3. Methods note
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Model information
models = [
    {
        'name': 'GPT-2',
        'size': '124M',
        'params': 124,
        'file': 'experiment_results_gpt2_final.json',
        'analysis': 'entropy_analysis_gpt2.txt'
    },
    {
        'name': 'Pythia',
        'size': '160M',
        'params': 162,
        'file': 'experiment_results_pythia_160m_final.json',
        'analysis': 'entropy_analysis_pythia_160m.txt'
    },
    {
        'name': 'Pythia',
        'size': '410M',
        'params': 410,
        'file': 'experiment_results_pythia_410m_final.json',
        'analysis': 'entropy_analysis_pythia.txt'
    },
    {
        'name': 'GPT-2',
        'size': '774M',
        'params': 774,
        'file': 'experiment_results_gpt2_large_final.json',
        'analysis': 'entropy_analysis_gpt2_large.txt'
    }
]

def extract_from_analysis(filename):
    """Extract key metrics from entropy analysis file."""
    with open(filename) as f:
        content = f.read()

    # Extract values using string parsing
    lines = content.split('\n')

    jab_entropy = None
    jab_entropy_sd = None
    scr_entropy = None
    scr_entropy_sd = None
    delta_entropy = None
    cohens_d = None

    for line in lines:
        if 'Jabberwocky (Syntax):' in line and 'bits (entropy)' in line:
            # Format: "Jabberwocky (Syntax):          8.341 ± 0.133 bits (entropy)"
            parts = line.split()
            jab_entropy = float(parts[2])
            jab_entropy_sd = float(parts[4])
        elif 'Scrambled (No Structure):' in line and 'bits (entropy)' in line:
            # Format: "Scrambled (No Structure):      8.769 ± 0.147 bits (entropy)"
            parts = line.split()
            scr_entropy = float(parts[3])
            scr_entropy_sd = float(parts[5])
        elif 'Δ Entropy (Syntax - Scrambled):' in line:
            # Format: "Δ Entropy (Syntax - Scrambled): -0.427 bits"
            # Split by colon and take the number
            value_str = line.split(':')[1].strip()
            delta_entropy = float(value_str.split()[0])
        elif 'Entropy:   d =' in line:
            # Format: "  Entropy:   d = -0.557"
            parts = line.split('=')
            cohens_d = float(parts[1].strip())

    return {
        'jab_entropy': jab_entropy,
        'jab_entropy_sd': jab_entropy_sd,
        'scr_entropy': scr_entropy,
        'scr_entropy_sd': scr_entropy_sd,
        'delta_entropy': delta_entropy,
        'cohens_d': cohens_d
    }

# Extract data for all models
results = []
for model in models:
    if Path(model['analysis']).exists():
        metrics = extract_from_analysis(model['analysis'])
        results.append({
            'model': model['name'],
            'size': model['size'],
            'params': model['params'],
            **metrics
        })

# 1. Create table
print("="*100)
print("SCALING ANALYSIS: Syntactic Constraint Effect Across Model Sizes")
print("="*100)
print()
print("Table 1: Entropy Reduction Effect by Model Size")
print("-"*100)
print(f"{'Model':<12} {'Size':<8} {'Params':<8} {'Jab Entropy':<20} {'Scr Entropy':<20} {'ΔEntropy':<12} {'Cohen d':<10}")
print(f"{'':12} {'':8} {'(M)':8} {'(mean ± SD bits)':<20} {'(mean ± SD bits)':<20} {'(bits)':<12} {'':<10}")
print("-"*100)

for r in results:
    jab_str = f"{r['jab_entropy']:.3f} ± {r['jab_entropy_sd']:.3f}"
    scr_str = f"{r['scr_entropy']:.3f} ± {r['scr_entropy_sd']:.3f}"
    print(f"{r['model']:<12} {r['size']:<8} {r['params']:<8} {jab_str:<20} {scr_str:<20} {r['delta_entropy']:>11.3f} {r['cohens_d']:>10.3f}")

print("-"*100)
print()

# 2. Create plot
fig, ax = plt.subplots(1, 1, figsize=(8, 5))

# Separate GPT-2 and Pythia models
gpt2_models = [r for r in results if r['model'] == 'GPT-2']
pythia_models = [r for r in results if r['model'] == 'Pythia']

# Plot GPT-2
gpt2_params = [r['params'] for r in gpt2_models]
gpt2_delta = [r['delta_entropy'] for r in gpt2_models]
ax.plot(gpt2_params, gpt2_delta, 'o-', color='#1f77b4', linewidth=2, markersize=8,
        label='GPT-2', markeredgecolor='white', markeredgewidth=1.5)

# Plot Pythia
pythia_params = [r['params'] for r in pythia_models]
pythia_delta = [r['delta_entropy'] for r in pythia_models]
ax.plot(pythia_params, pythia_delta, 's-', color='#ff7f0e', linewidth=2, markersize=8,
        label='Pythia', markeredgecolor='white', markeredgewidth=1.5)

# Formatting
ax.set_xscale('log')
ax.set_xlabel('Model Size (millions of parameters)', fontsize=12, fontweight='bold')
ax.set_ylabel('ΔEntropy (Jabberwocky − Scrambled)\n[bits]', fontsize=12, fontweight='bold')
ax.set_title('Syntactic Constraint Effect Decreases with Model Scale', fontsize=14, fontweight='bold')
ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
ax.grid(True, alpha=0.3, linestyle=':')
ax.legend(loc='best', fontsize=11, framealpha=0.9)

# Add annotation
ax.text(0.05, 0.95, 'More negative = stronger\nsyntactic constraint',
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.savefig('scaling_plot.png', dpi=300, bbox_inches='tight')
print("Saved: scaling_plot.png")
print()

# 3. Methods note
methods_note = """
METHODS NOTE: Word-Aligned Entropy Analysis

Normalization: All stimuli were length-matched within triplets (real sentence, jabberwocky,
scrambled jabberwocky) to control for sequence length effects on entropy. Nonce words were
constructed to match real words in syllable count and phonotactic structure.

In-context tokenization: To avoid tokenization confounds from BPE sensitivity to leading
whitespace and context, all stimuli were tokenized as complete sequences (not word-by-word),
and token-level predictions were aggregated to word boundaries using offset mapping. This
ensures that entropy reflects the model's predictions in natural reading context rather than
artifacts of isolated word tokenization.

Word-aligned entropy: For each word position w, we computed Shannon entropy H(w) =
-Σ p(token) × log₂(p(token)) over the model's predicted distribution at the final token
of word w. When a word spans multiple BPE tokens, we used the distribution at the final
token position, as this reflects the model's prediction after processing the complete word
form. Word-level entropies were then averaged across all content positions (excluding
sentence-initial and sentence-final words).

Scrambled control: For each jabberwocky stimulus, we created a scrambled version by
randomly permuting word order while preserving the exact lexical items (including all
nonce words). This eliminates syntactic structure while controlling for lexical identity,
allowing us to isolate the effect of word order/syntactic relationships on predictive
entropy. Scrambling was performed deterministically with a fixed random seed to ensure
reproducibility.

Effect size: We report Cohen's d as (μ_jab - μ_scr) / σ_pooled, where σ_pooled is the
pooled standard deviation across the 30 stimulus triplets. Negative d indicates lower
entropy (stronger constraint) in syntactically structured jabberwocky relative to
scrambled controls.
"""

print("="*100)
print(methods_note)
print("="*100)

# Save to file
with open('SCALING_SUMMARY.txt', 'w') as f:
    f.write("="*100 + "\n")
    f.write("SCALING ANALYSIS: Syntactic Constraint Effect Across Model Sizes\n")
    f.write("="*100 + "\n\n")

    f.write("Table 1: Entropy Reduction Effect by Model Size\n")
    f.write("-"*100 + "\n")
    f.write(f"{'Model':<12} {'Size':<8} {'Params':<8} {'Jab Entropy':<20} {'Scr Entropy':<20} {'ΔEntropy':<12} {'Cohen d':<10}\n")
    f.write(f"{'':12} {'':8} {'(M)':8} {'(mean ± SD bits)':<20} {'(mean ± SD bits)':<20} {'(bits)':<12} {'':<10}\n")
    f.write("-"*100 + "\n")

    for r in results:
        jab_str = f"{r['jab_entropy']:.3f} ± {r['jab_entropy_sd']:.3f}"
        scr_str = f"{r['scr_entropy']:.3f} ± {r['scr_entropy_sd']:.3f}"
        f.write(f"{r['model']:<12} {r['size']:<8} {r['params']:<8} {jab_str:<20} {scr_str:<20} {r['delta_entropy']:>11.3f} {r['cohens_d']:>10.3f}\n")

    f.write("-"*100 + "\n\n")
    f.write("Figure 1: See scaling_plot.png\n\n")
    f.write("="*100 + "\n")
    f.write(methods_note)
    f.write("="*100 + "\n")

print("\nSaved: SCALING_SUMMARY.txt")
print("\nAll files generated successfully!")
