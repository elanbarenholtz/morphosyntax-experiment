# Save results to CSV/JSON - Run this in Colab after the audit completes
# Upload this file to Colab and run: exec(open('save_results.py').read())

model_slug = MODEL_NAME.replace('/', '_')
results_flat = []
for r in results:
    row = {'set_id': r['set_id'], 'cue_family': r['cue_family'], 'cue_word': r['cue_word'], 'condition': r['condition'], 'context_k': r['context_k'], 'target_mass': r['target_mass']}
    for class_name, mass in r['class_mass'].items():
        row[f'mass_{class_name}'] = mass
    results_flat.append(row)

df_flat = pd.DataFrame(results_flat)
df_flat.to_csv(f'{OUTPUT_DIR}/locked_audit_{model_slug}_raw.csv', index=False)
print(f"Saved: locked_audit_{model_slug}_raw.csv ({len(df_flat)} rows)")

with open(f'{OUTPUT_DIR}/locked_audit_{model_slug}_raw.json', 'w') as f:
    json.dump({'metadata': {'model': MODEL_NAME}, 'results': results}, f, indent=2)
print(f"Saved: locked_audit_{model_slug}_raw.json")

summary = df[df['context_k'] == 'full'].pivot_table(values='target_mass', index='cue_family', columns='condition', aggfunc='mean')
summary.to_csv(f'{OUTPUT_DIR}/locked_audit_{model_slug}_summary.csv')
print(f"Saved: locked_audit_{model_slug}_summary.csv")

contrasts_df.to_csv(f'{OUTPUT_DIR}/locked_audit_{model_slug}_contrasts.csv', index=False)
print(f"Saved: locked_audit_{model_slug}_contrasts.csv")

ablation = df.pivot_table(values='target_mass', index=['cue_family', 'condition'], columns='context_k', aggfunc='mean')
ablation.to_csv(f'{OUTPUT_DIR}/locked_audit_{model_slug}_ablation.csv')
print(f"Saved: locked_audit_{model_slug}_ablation.csv")

pd.DataFrame(stimuli).to_csv(f'{OUTPUT_DIR}/stimuli_locked.csv', index=False)
print(f"Saved: stimuli_locked.csv")

print(f"\nDone! Files saved to: {OUTPUT_DIR}")
