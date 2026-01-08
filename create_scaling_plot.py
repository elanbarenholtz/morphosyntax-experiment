"""
Create scaling analysis plot showing entropy effects across model sizes.
"""

import matplotlib.pyplot as plt
import numpy as np
import re

# Model data
models = []

# Parse existing entropy analysis files
analysis_files = {
    'GPT-2 base\n(124M)': ('entropy_analysis_gpt2.txt', 124),
    'Pythia-410m\n(410M)': ('entropy_analysis_pythia.txt', 410),
    'GPT-2 medium\n(355M)': ('entropy_analysis_gpt2_medium.txt', 355),
    'GPT-2 large\n(774M)': ('entropy_analysis_gpt2_large.txt', 774),
}

for model_name, (fname, params) in analysis_files.items():
    try:
        with open(fname, 'r') as f:
            content = f.read()

        # Extract Δ Entropy
        delta_match = re.search(r'Δ Entropy \(Syntax - Scrambled\): ([+-]?\d+\.?\d*) bits', content)
        # Extract Cohen's d for entropy
        cohen_match = re.search(r'Entropy:\s+d = ([+-]?\d+\.?\d*)', content)

        if delta_match and cohen_match:
            delta_entropy = float(delta_match.group(1))
            cohens_d = float(cohen_match.group(1))
            models.append({
                'name': model_name,
                'params': params,
                'delta_entropy': delta_entropy,
                'cohens_d': cohens_d
            })
            print(f"Loaded {model_name}: Δ={delta_entropy:.3f}, d={cohens_d:.3f}")
    except FileNotFoundError:
        print(f"File not found: {fname}")
    except Exception as e:
        print(f"Error parsing {fname}: {e}")

if len(models) < 2:
    print(f"Not enough models ({len(models)}) for scaling plot. Need at least 2.")
    exit(1)

# Sort by parameter count
models = sorted(models, key=lambda x: x['params'])

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Delta Entropy vs Model Size
params = [m['params'] for m in models]
delta_entropies = [m['delta_entropy'] for m in models]

ax1.plot(params, delta_entropies, 'o-', markersize=10, linewidth=2, color='#2E86AB')
ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax1.set_xlabel('Model Parameters (Millions)', fontsize=12)
ax1.set_ylabel('Δ Entropy (Jabberwocky - Scrambled) [bits]', fontsize=12)
ax1.set_title('Syntactic Constraint Across Model Scales', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xscale('log')

# Annotate points
for m in models:
    ax1.annotate(f"{m['delta_entropy']:.3f}",
                xy=(m['params'], m['delta_entropy']),
                xytext=(10, -10),
                textcoords='offset points',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Plot 2: Cohen's d effect size vs Model Size
cohens_ds = [m['cohens_d'] for m in models]

ax2.plot(params, cohens_ds, 's-', markersize=10, linewidth=2, color='#A23B72')
ax2.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax2.axhline(-0.2, color='lightgray', linestyle=':', alpha=0.5, label='Small effect')
ax2.axhline(-0.5, color='lightgray', linestyle=':', alpha=0.5, label='Medium effect')
ax2.axhline(-0.8, color='lightgray', linestyle=':', alpha=0.5, label='Large effect')
ax2.set_xlabel('Model Parameters (Millions)', fontsize=12)
ax2.set_ylabel("Cohen's d (Effect Size)", fontsize=12)
ax2.set_title('Effect Size Across Model Scales', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xscale('log')
ax2.legend(fontsize=8, loc='lower right')

# Annotate points
for m in models:
    ax2.annotate(m['name'],
                xy=(m['params'], m['cohens_d']),
                xytext=(10, 5),
                textcoords='offset points',
                fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('scaling_analysis_plot.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved scaling_analysis_plot.png")

# Print summary table
print("\n" + "="*70)
print("SCALING ANALYSIS SUMMARY")
print("="*70)
print(f"{'Model':<25} {'Params':<12} {'Δ Entropy':<15} {'Cohen's d':<12}")
print("-"*70)
for m in models:
    print(f"{m['name']:<25} {m['params']:>6}M     {m['delta_entropy']:>8.3f} bits   {m['cohens_d']:>8.3f}")
print("="*70)

# Determine pattern
if len(models) >= 3:
    # Check if effect is growing, shrinking, or stable
    effect_changes = [cohens_ds[i+1] - cohens_ds[i] for i in range(len(cohens_ds)-1)]
    avg_change = np.mean(effect_changes)

    print("\nPattern Analysis:")
    if avg_change < -0.05:
        print("  → Effect DECREASES with scale (semantic-dependency hypothesis)")
    elif avg_change > 0.05:
        print("  → Effect INCREASES with scale (scaling hypothesis)")
    else:
        print("  → Effect STABLE across scales (null hypothesis)")
    print(f"     Average change: {avg_change:.3f} d-units per step")
print()
