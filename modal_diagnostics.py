#!/usr/bin/env python3
"""
Modal Cue Family Diagnostics

Investigates why SENTENCE ≈ JABBERWOCKY for modals while other families show SENTENCE > JABBERWOCKY.

Outputs:
1. modal_cue_alignment_log.txt - Verify cue words are correct
2. modal_next_token_diagnostics.md - Top-30 predictions for 10 sampled items
3. modal_mass_decomposition.csv - Mass breakdown by bucket (VERB, AUX, NEG, BEHAVE, etc.)
4. modal_summary_altTargets.csv - Summary with alternate target definitions
5. modal_contrasts_altTargets.csv - Statistical contrasts under both definitions
6. figure_modals_altTargets.png - Paper-ready figure

Usage:
    python modal_diagnostics.py --model gpt2
"""

import json
import random
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
from scipy import stats
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm import tqdm
import os
# Disable progress bars if running non-interactively
DISABLE_TQDM = os.environ.get('DISABLE_TQDM', 'false').lower() == 'true'

# ============================================================================
# CONFIGURATION
# ============================================================================

MODALS_LIST = {'can', 'will', 'could', 'would', 'should', 'must', 'may', 'might'}

# Target class definitions
VERB_SET = {
    'be', 'have', 'do', 'say', 'go', 'get', 'make', 'know', 'think', 'take',
    'see', 'come', 'want', 'use', 'find', 'give', 'tell', 'work', 'call', 'try',
    'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep', 'let', 'begin',
    'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'live', 'believe',
    'bring', 'happen', 'write', 'sit', 'stand', 'lose', 'pay', 'meet', 'continue',
    'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak',
    'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'teach', 'offer',
    'remember', 'love', 'consider', 'appear', 'buy', 'serve', 'die', 'send', 'build', 'stay',
    'fall', 'cut', 'reach', 'kill', 'raise', 'pass', 'sell', 'decide', 'return', 'explain',
    'hope', 'develop', 'carry', 'break', 'receive', 'agree', 'support', 'hit', 'produce', 'eat',
    'study', 'research', 'investigate', 'examine', 'analyze', 'explore',
    'paint', 'draw', 'design', 'construct', 'perform', 'practice',
    'publish', 'edit', 'revise', 'prepare', 'cook', 'repair', 'fix',
    'solve', 'calculate', 'improve', 'enhance', 'test', 'validate',
    'organize', 'arrange', 'defend', 'protect', 'film', 'record',
    'sail', 'navigate', 'discuss', 'debate', 'assemble', 'combine',
    'plan', 'schedule', 'finish', 'complete', 'start', 'end',
}

# BE/HAVE/DO auxiliary forms (literal token check)
BEHAVE_SET = {
    'be', 'been', 'being', 'am', 'is', 'are', 'was', 'were',
    'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'done', 'doing',
}

# Negation tokens
NEG_SET = {'not', "n't", "nt"}  # We'll also check for n't in token strings

# Common adverbs that might follow modals
ADV_SET = {
    'also', 'always', 'never', 'ever', 'just', 'still', 'only', 'even',
    'already', 'often', 'soon', 'now', 'then', 'perhaps', 'probably',
    'certainly', 'definitely', 'possibly', 'actually', 'really', 'simply',
    'easily', 'quickly', 'slowly', 'well', 'better', 'best',
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_cue_position(condition_text, cue_word, expected_occurrence=1):
    """
    Dynamically locate the cue word in a condition string.

    Args:
        condition_text: The full text of the condition
        cue_word: The cue word to find (e.g., 'can', 'must')
        expected_occurrence: Expected number of occurrences (default 1)

    Returns:
        tuple: (cue_index, status, message)
            - cue_index: word position (0-indexed) or None if not found
            - status: 'ok', 'missing', 'ambiguous'
            - message: diagnostic message
    """
    # Normalize: lowercase and split on whitespace
    words = condition_text.lower().split()
    cue_lower = cue_word.lower()

    # Find all indices where word matches cue (strip punctuation for matching)
    matches = []
    for i, w in enumerate(words):
        w_clean = w.strip('.,!?;:"\'-()[]{}')
        if w_clean == cue_lower:
            matches.append(i)

    if len(matches) == 0:
        return None, 'missing', f"Cue '{cue_word}' not found in text"
    elif len(matches) == 1:
        return matches[0], 'ok', f"Cue '{cue_word}' found at position {matches[0]}"
    else:
        # Multiple matches - use first and note ambiguity
        return matches[0], 'ambiguous', f"Cue '{cue_word}' found {len(matches)} times at positions {matches}, using first"


def is_word_start_token(tokenizer, token_id):
    """Check if token is word-start (space-prefixed)."""
    token_str = tokenizer.decode([token_id])
    if token_str in ['<|endoftext|>', '<unk>', '<pad>', '']:
        return False, None
    if token_str.startswith(' ') or token_str.startswith('\n'):
        word = token_str.strip().lower().strip('.,!?;:"\'-')
        return True, word
    return False, None

def contains_negation(token_str):
    """Check if token contains negation (including n't contractions)."""
    token_lower = token_str.lower().strip()
    if token_lower in NEG_SET:
        return True
    if "n't" in token_lower or "nt" in token_lower:
        return True
    return False

def classify_token(word, token_str):
    """Classify a token into buckets."""
    if word is None:
        return 'OTHER'

    word_lower = word.lower()

    # Check negation first (includes contractions)
    if contains_negation(token_str):
        return 'NEG'

    # Check BE/HAVE/DO auxiliaries
    if word_lower in BEHAVE_SET:
        return 'BEHAVE'

    # Check verbs (excluding BE/HAVE which are in BEHAVE)
    if word_lower in VERB_SET and word_lower not in BEHAVE_SET:
        return 'VERB'

    # Check adverbs
    if word_lower in ADV_SET:
        return 'ADV'

    return 'OTHER'

def get_context_at_cue(text, cue_position):
    """Get context up to and including cue."""
    words = text.split()
    return ' '.join(words[:cue_position + 1])

def compute_mass_decomposition(probs, tokenizer, top_k=1000):
    """Compute probability mass in each bucket."""
    top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

    mass = {
        'VERB': 0.0,
        'BEHAVE': 0.0,
        'NEG': 0.0,
        'ADV': 0.0,
        'OTHER': 0.0,
    }

    for prob, token_id in zip(top_k_probs, top_k_ids):
        is_start, word = is_word_start_token(tokenizer, token_id.item())
        if not is_start:
            continue

        token_str = tokenizer.decode([token_id.item()])
        bucket = classify_token(word, token_str)
        mass[bucket] += prob.item()

    return mass

def get_top_predictions(probs, tokenizer, top_k=30):
    """Get top-k predictions with classification."""
    top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

    predictions = []
    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id.item()])
        is_start, word = is_word_start_token(tokenizer, token_id.item())

        if is_start:
            bucket = classify_token(word, token_str)
            in_verb_only = word.lower() in VERB_SET if word else False
        else:
            bucket = 'SUBWORD'
            in_verb_only = False

        predictions.append({
            'token': token_str,
            'prob': prob.item(),
            'word': word,
            'bucket': bucket,
            'in_VerbOnly': in_verb_only,
        })

    return predictions

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def run_modal_diagnostics(model_name='gpt2', stimuli_file='stimuli_locked.json', output_dir='.'):
    """Run complete modal diagnostics."""

    print("=" * 70)
    print("MODAL CUE FAMILY DIAGNOSTICS")
    print("=" * 70)
    print(f"Model: {model_name}")
    print(f"Stimuli: {stimuli_file}")
    print(f"Output: {output_dir}")
    print()

    # Load model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    print(f"Device: {device}")
    print()

    # Load stimuli
    print("Loading stimuli...")
    with open(stimuli_file, 'r') as f:
        all_stimuli = json.load(f)

    # Filter to modals only
    modal_stimuli = [s for s in all_stimuli if s['cue_family'] == 'modals']
    print(f"Modal stimuli: {len(modal_stimuli)}")
    print()

    # =========================================================================
    # STEP 0: Cue alignment check with DYNAMIC cue location
    # =========================================================================
    print("=" * 70)
    print("STEP 0: Cue Alignment Check (Dynamic Location)")
    print("=" * 70)

    alignment_log = []
    alignment_log.append("MODAL CUE ALIGNMENT LOG (DYNAMIC LOCATION)")
    alignment_log.append(f"Generated: {datetime.now().isoformat()}")
    alignment_log.append("=" * 60)
    alignment_log.append("")
    alignment_log.append("This version DYNAMICALLY locates the cue in each condition,")
    alignment_log.append("so scrambled conditions are now analyzed correctly.")
    alignment_log.append("")

    conditions = ['sentence', 'jabberwocky', 'full_scrambled', 'content_scrambled', 'function_scrambled']

    # Track cue location statistics
    cue_location_stats = {cond: {'ok': 0, 'missing': 0, 'ambiguous': 0, 'positions': []} for cond in conditions}
    issues_found = 0

    for stim in modal_stimuli:
        item_id = stim['set_id']
        cue_word = stim['cue_word'].lower()
        original_cue_pos = stim['cue_position']

        # Check cue word is valid modal
        if cue_word not in MODALS_LIST:
            alignment_log.append(f"[FAIL] Item {item_id}: cue_word '{cue_word}' not in MODALS_LIST")
            issues_found += 1
            continue

        # Check for contractions
        for cond in conditions:
            text = stim[cond]
            if "n't" in text or "'ll" in text or "'d" in text:
                alignment_log.append(f"[WARN] Item {item_id} {cond}: contains contraction in '{text}'")

        # Dynamically locate cue in each condition
        for cond in conditions:
            text = stim[cond]
            cue_pos, status, message = find_cue_position(text, cue_word)

            cue_location_stats[cond][status] += 1
            if cue_pos is not None:
                cue_location_stats[cond]['positions'].append(cue_pos)

            if status == 'missing':
                alignment_log.append(f"[FAIL] Item {item_id} {cond}: {message}")
                issues_found += 1
            elif status == 'ambiguous':
                alignment_log.append(f"[WARN] Item {item_id} {cond}: {message}")

    # Summary statistics
    alignment_log.append("")
    alignment_log.append("=" * 60)
    alignment_log.append("DYNAMIC CUE LOCATION SUMMARY")
    alignment_log.append("=" * 60)
    alignment_log.append("")

    for cond in conditions:
        stats = cue_location_stats[cond]
        total = stats['ok'] + stats['missing'] + stats['ambiguous']
        valid = stats['ok'] + stats['ambiguous']  # ambiguous still usable (first match)

        positions = stats['positions']
        if positions:
            pos_min, pos_max = min(positions), max(positions)
            pos_mean = sum(positions) / len(positions)
            pos_range = f"range [{pos_min}-{pos_max}], mean={pos_mean:.1f}"
        else:
            pos_range = "no valid positions"

        alignment_log.append(f"{cond.upper()}:")
        alignment_log.append(f"  Valid items: {valid}/{total} ({100*valid/total:.1f}%)")
        alignment_log.append(f"  - ok: {stats['ok']}, missing: {stats['missing']}, ambiguous: {stats['ambiguous']}")
        alignment_log.append(f"  Cue positions: {pos_range}")
        alignment_log.append("")

    alignment_log.append(f"Total issues (missing cues): {issues_found}")
    alignment_log.append("Status: " + ("PASS" if issues_found == 0 else "ISSUES FOUND"))

    with open(f'{output_dir}/modal_cue_alignment_log.txt', 'w') as f:
        f.write('\n'.join(alignment_log))
    print(f"Saved: modal_cue_alignment_log.txt")
    print(f"Issues found (missing cues): {issues_found}")

    # Print summary to console
    print("\nCue location summary by condition:")
    for cond in conditions:
        stats = cue_location_stats[cond]
        valid = stats['ok'] + stats['ambiguous']
        positions = stats['positions']
        if positions:
            print(f"  {cond}: {valid} valid, positions {min(positions)}-{max(positions)}")
        else:
            print(f"  {cond}: {valid} valid, no positions")
    print()

    # =========================================================================
    # STEP 1: Next-token diagnostics (10 sampled items) - DYNAMIC CUE LOCATION
    # =========================================================================
    print("=" * 70)
    print("STEP 1: Next-Token Diagnostics (Dynamic Cue Location)")
    print("=" * 70)

    # Sample 10 items
    random.seed(42)
    sampled_items = random.sample(modal_stimuli, min(10, len(modal_stimuli)))

    diagnostics_md = []
    diagnostics_md.append("# Modal Next-Token Diagnostics (Dynamic Cue Location)")
    diagnostics_md.append(f"\nGenerated: {datetime.now().isoformat()}")
    diagnostics_md.append(f"\nModel: {model_name}")
    diagnostics_md.append(f"\nSampled items: {len(sampled_items)}")
    diagnostics_md.append("\n**Note:** Cue position is dynamically located in each condition.")
    diagnostics_md.append("")

    for stim in tqdm(sampled_items, desc="Sampling diagnostics", disable=DISABLE_TQDM):
        item_id = stim['set_id']
        cue_word = stim['cue_word']

        diagnostics_md.append(f"\n## Item {item_id} (cue: '{cue_word}')")
        diagnostics_md.append("")

        # Now analyze ALL conditions with dynamic cue location
        for cond in conditions:
            text = stim[cond]

            # Dynamically locate cue
            cue_pos, status, message = find_cue_position(text, cue_word)

            diagnostics_md.append(f"### {cond.upper()}")

            if cue_pos is None:
                diagnostics_md.append(f"**SKIPPED:** {message}")
                diagnostics_md.append("")
                continue

            context = get_context_at_cue(text, cue_pos)

            diagnostics_md.append(f"**Cue position:** {cue_pos} ({status})")
            diagnostics_md.append(f"**Context:** `{context}`")
            diagnostics_md.append(f"**Full text:** `{text}`")
            diagnostics_md.append("")

            # Get predictions
            inputs = tokenizer(context, return_tensors='pt').to(device)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1).cpu()

            top_preds = get_top_predictions(probs, tokenizer, top_k=30)

            diagnostics_md.append("| Rank | Token | Prob | Word | Bucket | In VerbOnly |")
            diagnostics_md.append("|------|-------|------|------|--------|-------------|")

            for i, p in enumerate(top_preds):
                token_display = p['token'].replace('|', '\\|').replace('\n', '\\n')
                in_vo = "✓" if p['in_VerbOnly'] else ""
                diagnostics_md.append(f"| {i+1} | `{token_display}` | {p['prob']:.4f} | {p['word']} | {p['bucket']} | {in_vo} |")

            diagnostics_md.append("")

    with open(f'{output_dir}/modal_next_token_diagnostics.md', 'w') as f:
        f.write('\n'.join(diagnostics_md))
    print(f"Saved: modal_next_token_diagnostics.md")
    print()

    # =========================================================================
    # STEP 2: Mass decomposition for ALL modal items - DYNAMIC CUE LOCATION
    # =========================================================================
    print("=" * 70)
    print("STEP 2: Mass Decomposition (Dynamic Cue Location)")
    print("=" * 70)

    decomposition_results = []
    skipped_counts = {cond: 0 for cond in conditions}

    for stim in tqdm(modal_stimuli, desc="Computing mass decomposition", disable=DISABLE_TQDM):
        item_id = stim['set_id']
        cue_word = stim['cue_word']

        for cond in conditions:
            text = stim[cond]

            # Dynamically locate cue
            cue_pos, status, message = find_cue_position(text, cue_word)

            if cue_pos is None:
                skipped_counts[cond] += 1
                continue  # Skip items where cue is missing

            context = get_context_at_cue(text, cue_pos)

            # Get predictions
            inputs = tokenizer(context, return_tensors='pt').to(device)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits[0, -1, :]
            probs = torch.softmax(logits, dim=-1).cpu()

            # Compute mass decomposition
            mass = compute_mass_decomposition(probs, tokenizer, top_k=1000)

            decomposition_results.append({
                'item_id': item_id,
                'condition': cond.upper(),
                'cue_word': cue_word,
                'cue_position': cue_pos,  # Record actual position used
                'mass_VERB': mass['VERB'],
                'mass_BEHAVE': mass['BEHAVE'],
                'mass_NEG': mass['NEG'],
                'mass_ADV': mass['ADV'],
                'mass_OTHER': mass['OTHER'],
                'mass_VerbOnly': mass['VERB'],  # Current target
                'mass_VPStart': mass['VERB'] + mass['BEHAVE'] + mass['NEG'],  # Alternate target
            })

    # Report skipped items
    print("\nSkipped items (missing cue):")
    for cond in conditions:
        if skipped_counts[cond] > 0:
            print(f"  {cond}: {skipped_counts[cond]} items skipped")

    decomp_df = pd.DataFrame(decomposition_results)
    decomp_df.to_csv(f'{output_dir}/modal_mass_decomposition.csv', index=False)
    print(f"Saved: modal_mass_decomposition.csv")

    # Print summary
    print("\nMass decomposition summary (mean ± SE):")
    print("-" * 80)
    summary = decomp_df.groupby('condition').agg({
        'mass_VERB': ['mean', 'std', 'count'],
        'mass_BEHAVE': ['mean', 'std'],
        'mass_NEG': ['mean', 'std'],
        'mass_ADV': ['mean', 'std'],
        'mass_VerbOnly': ['mean', 'std'],
        'mass_VPStart': ['mean', 'std'],
    })

    for cond in ['SENTENCE', 'JABBERWOCKY', 'FULL_SCRAMBLED', 'CONTENT_SCRAMBLED', 'FUNCTION_SCRAMBLED']:
        if cond in summary.index:
            row = summary.loc[cond]
            n = row[('mass_VERB', 'count')]
            print(f"\n{cond}:")
            print(f"  VERB:     {row[('mass_VERB', 'mean')]:.4f} ± {row[('mass_VERB', 'std')]/np.sqrt(n):.4f}")
            print(f"  BEHAVE:   {row[('mass_BEHAVE', 'mean')]:.4f} ± {row[('mass_BEHAVE', 'std')]/np.sqrt(n):.4f}")
            print(f"  NEG:      {row[('mass_NEG', 'mean')]:.4f} ± {row[('mass_NEG', 'std')]/np.sqrt(n):.4f}")
            print(f"  ADV:      {row[('mass_ADV', 'mean')]:.4f} ± {row[('mass_ADV', 'std')]/np.sqrt(n):.4f}")
            print(f"  ---")
            print(f"  VerbOnly: {row[('mass_VerbOnly', 'mean')]:.4f} ± {row[('mass_VerbOnly', 'std')]/np.sqrt(n):.4f}")
            print(f"  VPStart:  {row[('mass_VPStart', 'mean')]:.4f} ± {row[('mass_VPStart', 'std')]/np.sqrt(n):.4f}")

    print()

    # =========================================================================
    # STEP 3: Alternate target definitions summary
    # =========================================================================
    print("=" * 70)
    print("STEP 3: Alternate Target Definitions")
    print("=" * 70)

    # Summary table
    summary_alt = decomp_df.groupby('condition').agg({
        'mass_VerbOnly': ['mean', 'std', 'count'],
        'mass_VPStart': ['mean', 'std'],
    }).reset_index()

    summary_alt.columns = ['condition', 'VerbOnly_mean', 'VerbOnly_std', 'n', 'VPStart_mean', 'VPStart_std']
    summary_alt['VerbOnly_se'] = summary_alt['VerbOnly_std'] / np.sqrt(summary_alt['n'])
    summary_alt['VPStart_se'] = summary_alt['VPStart_std'] / np.sqrt(summary_alt['n'])

    summary_alt.to_csv(f'{output_dir}/modal_summary_altTargets.csv', index=False)
    print(f"Saved: modal_summary_altTargets.csv")
    print(summary_alt[['condition', 'VerbOnly_mean', 'VerbOnly_se', 'VPStart_mean', 'VPStart_se']].round(4).to_string(index=False))
    print()

    # Contrasts
    contrasts_results = []
    contrast_pairs = [
        ('SENTENCE', 'JABBERWOCKY'),
        ('JABBERWOCKY', 'FULL_SCRAMBLED'),
        ('JABBERWOCKY', 'CONTENT_SCRAMBLED'),
        ('JABBERWOCKY', 'FUNCTION_SCRAMBLED'),
    ]

    for target_col in ['mass_VerbOnly', 'mass_VPStart']:
        target_name = 'VerbOnly' if 'VerbOnly' in target_col else 'VPStart'

        for cond_a, cond_b in contrast_pairs:
            df_a = decomp_df[decomp_df['condition'] == cond_a].set_index('item_id')[target_col]
            df_b = decomp_df[decomp_df['condition'] == cond_b].set_index('item_id')[target_col]

            common = df_a.index.intersection(df_b.index)
            if len(common) == 0:
                continue

            x, y = df_a.loc[common].values, df_b.loc[common].values
            diff = np.mean(x) - np.mean(y)
            t_stat, p_val = stats.ttest_rel(x, y)
            d = np.mean(x - y) / np.std(x - y, ddof=1) if np.std(x - y, ddof=1) > 0 else 0

            contrasts_results.append({
                'target_def': target_name,
                'contrast': f"{cond_a} - {cond_b}",
                'mean_a': np.mean(x),
                'mean_b': np.mean(y),
                'diff': diff,
                't_stat': t_stat,
                'p_value': p_val,
                'cohens_d': d,
                'n': len(common),
            })

    contrasts_df = pd.DataFrame(contrasts_results)
    contrasts_df.to_csv(f'{output_dir}/modal_contrasts_altTargets.csv', index=False)
    print(f"Saved: modal_contrasts_altTargets.csv")
    print(contrasts_df[['target_def', 'contrast', 'diff', 'p_value', 'cohens_d']].round(4).to_string(index=False))
    print()

    # =========================================================================
    # STEP 4: Figure
    # =========================================================================
    print("=" * 70)
    print("STEP 4: Generate Figure")
    print("=" * 70)

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    conditions_order = ['SENTENCE', 'JABBERWOCKY', 'FULL_SCRAMBLED', 'CONTENT_SCRAMBLED', 'FUNCTION_SCRAMBLED']
    condition_labels = ['Sent', 'Jab', 'Full', 'Cont', 'Func']
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']

    for ax_idx, (target_col, title) in enumerate([('mass_VerbOnly', 'VerbOnly (Current)'), ('mass_VPStart', 'VPStart (VERB+AUX+NEG)')]):
        ax = axes[ax_idx]

        means = []
        ses = []
        for cond in conditions_order:
            cond_data = decomp_df[decomp_df['condition'] == cond][target_col]
            means.append(cond_data.mean())
            ses.append(cond_data.std() / np.sqrt(len(cond_data)))

        x = np.arange(len(conditions_order))
        bars = ax.bar(x, means, yerr=ses, capsize=4, color=colors, alpha=0.8, edgecolor='white')

        ax.set_title(f'Modal Target: {title}', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(condition_labels)
        ax.set_ylabel('Target Class Mass')
        ax.set_ylim(0, max(means) * 1.3)

        # Add value labels
        for i, (m, s) in enumerate(zip(means, ses)):
            ax.text(i, m + s + 0.01, f'{m:.3f}', ha='center', va='bottom', fontsize=8)

    plt.suptitle(f'Modal Cue Family - Alternate Target Definitions ({model_name})', fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/figure_modals_altTargets.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: figure_modals_altTargets.png")
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    # Key comparison: SENTENCE vs JABBERWOCKY under both targets
    sent_vo = decomp_df[decomp_df['condition'] == 'SENTENCE']['mass_VerbOnly'].mean()
    jab_vo = decomp_df[decomp_df['condition'] == 'JABBERWOCKY']['mass_VerbOnly'].mean()
    sent_vp = decomp_df[decomp_df['condition'] == 'SENTENCE']['mass_VPStart'].mean()
    jab_vp = decomp_df[decomp_df['condition'] == 'JABBERWOCKY']['mass_VPStart'].mean()

    print(f"\nSENTENCE vs JABBERWOCKY comparison:")
    print(f"  VerbOnly:  SENT={sent_vo:.4f}, JAB={jab_vo:.4f}, diff={sent_vo-jab_vo:+.4f}")
    print(f"  VPStart:   SENT={sent_vp:.4f}, JAB={jab_vp:.4f}, diff={sent_vp-jab_vp:+.4f}")

    # Get p-values
    vo_contrast = contrasts_df[(contrasts_df['target_def'] == 'VerbOnly') & (contrasts_df['contrast'] == 'SENTENCE - JABBERWOCKY')]
    vp_contrast = contrasts_df[(contrasts_df['target_def'] == 'VPStart') & (contrasts_df['contrast'] == 'SENTENCE - JABBERWOCKY')]

    if len(vo_contrast) > 0:
        print(f"  VerbOnly p-value: {vo_contrast['p_value'].values[0]:.4f}")
    if len(vp_contrast) > 0:
        print(f"  VPStart p-value:  {vp_contrast['p_value'].values[0]:.4f}")

    # BE/HAVE breakdown
    sent_behave = decomp_df[decomp_df['condition'] == 'SENTENCE']['mass_BEHAVE'].mean()
    jab_behave = decomp_df[decomp_df['condition'] == 'JABBERWOCKY']['mass_BEHAVE'].mean()
    sent_neg = decomp_df[decomp_df['condition'] == 'SENTENCE']['mass_NEG'].mean()
    jab_neg = decomp_df[decomp_df['condition'] == 'JABBERWOCKY']['mass_NEG'].mean()

    print(f"\nBE/HAVE/DO mass:")
    print(f"  SENTENCE:    {sent_behave:.4f}")
    print(f"  JABBERWOCKY: {jab_behave:.4f}")
    print(f"  Difference:  {sent_behave - jab_behave:+.4f}")

    print(f"\nNegation mass:")
    print(f"  SENTENCE:    {sent_neg:.4f}")
    print(f"  JABBERWOCKY: {jab_neg:.4f}")
    print(f"  Difference:  {sent_neg - jab_neg:+.4f}")

    print()
    print("=" * 70)
    print("INTERPRETATION (with Dynamic Cue Location)")
    print("=" * 70)
    print("\nNote: This analysis uses DYNAMIC cue location for all conditions,")
    print("so scrambled baselines now correctly measure 'prediction after the")
    print("modal cue with disrupted structure' - not arbitrary position 2.")
    print()

    if sent_vp > jab_vp and (sent_vo - jab_vo) < (sent_vp - jab_vp):
        print("→ The VerbOnly target definition appears to be an ARTIFACT.")
        print("  When BE/HAVE/NEG are included (VPStart), SENTENCE > JABBERWOCKY as expected.")
        print("  Real sentences use more auxiliary/negation continuations after modals.")
    else:
        print("→ Modals appear to be genuinely CUE-DRIVEN.")
        print("  Even with expanded target definition, SENTENCE ≈ JABBERWOCKY.")
        print("  The modal cue alone saturates morphosyntactic constraint.")

    print()
    print("=" * 70)
    print("OUTPUT FILES")
    print("=" * 70)
    print(f"1. {output_dir}/modal_cue_alignment_log.txt")
    print(f"2. {output_dir}/modal_next_token_diagnostics.md")
    print(f"3. {output_dir}/modal_mass_decomposition.csv")
    print(f"4. {output_dir}/modal_summary_altTargets.csv")
    print(f"5. {output_dir}/modal_contrasts_altTargets.csv")
    print(f"6. {output_dir}/figure_modals_altTargets.png")
    print()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='gpt2')
    parser.add_argument('--stimuli', type=str, default='stimuli_locked.json')
    parser.add_argument('--output-dir', type=str, default='.')
    args = parser.parse_args()

    run_modal_diagnostics(args.model, args.stimuli, args.output_dir)
