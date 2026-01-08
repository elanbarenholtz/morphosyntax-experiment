"""
Create formatted tables for the experiment results.
"""

import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('experiment_data.csv')
stats_df = pd.read_csv('statistical_tests.csv')

print("=" * 80)
print("TABLE 1: DESCRIPTIVE STATISTICS BY CONDITION")
print("=" * 80)
print()

# Descriptive statistics
desc_stats = df.groupby('condition')['mean_entropy'].agg([
    ('N', 'count'),
    ('Mean', 'mean'),
    ('SD', 'std'),
    ('Min', 'min'),
    ('Max', 'max'),
    ('Median', 'median')
]).round(3)

# Reorder conditions
condition_order = ['sentence', 'jabberwocky', 'stripped', 'nonwords']
desc_stats = desc_stats.reindex(condition_order)

print(desc_stats.to_string())
print()

print("=" * 80)
print("TABLE 2: STATISTICAL COMPARISONS (Paired t-tests)")
print("=" * 80)
print()

# Statistical tests table
stats_table = stats_df[['comparison', 'mean1', 'mean2', 'diff', 't_statistic', 'p_value', 'cohens_d']].copy()
stats_table.columns = ['Comparison', 'Mean 1', 'Mean 2', 'Difference', 't-statistic', 'p-value', "Cohen's d"]
stats_table = stats_table.round(4)

# Add significance stars
def add_stars(p):
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    else:
        return 'n.s.'

stats_table['Sig.'] = stats_table['p-value'].apply(add_stars)

print(stats_table.to_string(index=False))
print()
print("Significance: *** p < 0.001, ** p < 0.01, * p < 0.05, n.s. = not significant")
print()

print("=" * 80)
print("TABLE 3: SAMPLE STIMULI AND ENTROPY VALUES (First 10 Sets)")
print("=" * 80)
print()

# Sample data - reshape to show all conditions for each set side by side
sample_sets = []
for set_id in range(1, 11):
    set_data = df[df['set_id'] == set_id]
    row = {'Set': set_id}
    for _, item in set_data.iterrows():
        cond = item['condition']
        row[f'{cond}_text'] = item['text'][:40] + '...' if len(item['text']) > 40 else item['text']
        row[f'{cond}_entropy'] = round(item['mean_entropy'], 3)
    sample_sets.append(row)

sample_df = pd.DataFrame(sample_sets)

# Print in a more readable format
for i, row in sample_df.iterrows():
    print(f"SET {row['Set']}")
    print(f"  Sentence:    {row.get('sentence_text', 'N/A'):45s} → {row.get('sentence_entropy', 0):.3f} bits")
    print(f"  Jabberwocky: {row.get('jabberwocky_text', 'N/A'):45s} → {row.get('jabberwocky_entropy', 0):.3f} bits")
    print(f"  Stripped:    {row.get('stripped_text', 'N/A'):45s} → {row.get('stripped_entropy', 0):.3f} bits")
    print(f"  Nonwords:    {row.get('nonwords_text', 'N/A'):45s} → {row.get('nonwords_entropy', 0):.3f} bits")
    print()

print("=" * 80)
print("TABLE 4: PAIRWISE EFFECT SIZES")
print("=" * 80)
print()

# Create a matrix of effect sizes
effect_matrix = pd.DataFrame(index=condition_order, columns=condition_order)

for _, row in stats_df.iterrows():
    c1 = row['condition1']
    c2 = row['condition2']
    d = row['cohens_d']
    effect_matrix.loc[c1, c2] = f"{d:.2f}"
    effect_matrix.loc[c2, c1] = f"{-d:.2f}"  # Reverse for symmetry

for cond in condition_order:
    effect_matrix.loc[cond, cond] = "—"

print(effect_matrix.to_string())
print()
print("Cohen's d interpretation: Small = 0.2, Medium = 0.5, Large = 0.8")
print()

# Save tables to file
with open('results_tables.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("MORPHOSYNTAX CONSTRAINT EXPERIMENT - RESULTS TABLES\n")
    f.write("=" * 80 + "\n\n")

    f.write("TABLE 1: DESCRIPTIVE STATISTICS BY CONDITION\n")
    f.write("=" * 80 + "\n")
    f.write(desc_stats.to_string())
    f.write("\n\n")

    f.write("TABLE 2: STATISTICAL COMPARISONS (Paired t-tests)\n")
    f.write("=" * 80 + "\n")
    f.write(stats_table.to_string(index=False))
    f.write("\n\nSignificance: *** p < 0.001, ** p < 0.01, * p < 0.05, n.s. = not significant\n\n")

    f.write("TABLE 4: PAIRWISE EFFECT SIZES (Cohen's d)\n")
    f.write("=" * 80 + "\n")
    f.write(effect_matrix.to_string())
    f.write("\n\nCohen's d interpretation: Small = 0.2, Medium = 0.5, Large = 0.8\n")

print("Tables saved to: results_tables.txt")
