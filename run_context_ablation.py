#!/usr/bin/env python3
"""
Context-Length Ablation for Morphosyntax Audit

Tests how much of each cue-family effect is driven by the immediately
preceding cue word vs. the broader prefix/scaffold.

Method:
- For each cue at position i, test with last k words only
- k ∈ {1, 2, 4, full}
- k=1 means just the cue word itself ("to", "the")

Scope (focused):
- 2 cue families: infinitival_to, determiners
- 2-3 conditions: JABBERWOCKY, FUNCTION_SCRAMBLED, FULL_SCRAMBLED
"""

import json
import argparse
import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from cue_families import CUE_FAMILIES
from word_level_analysis import WordLevelAnalyzer


# ============================================================================
# CONFIGURATION
# ============================================================================

# Focus on 2 cue families for ablation
TARGET_CUE_FAMILIES = ['infinitival_to', 'determiners']

# Test 2-3 conditions
TARGET_CONDITIONS = ['JABBERWOCKY', 'FUNCTION_SCRAMBLED', 'FULL_SCRAMBLED']

# Context lengths to test
CONTEXT_K_VALUES = [1, 2, 4, None]  # None = full context

CONDITION_MAP = {
    'sentence': 'SENTENCE',
    'jabberwocky': 'JABBERWOCKY',
    'full_scrambled': 'FULL_SCRAMBLED',
    'content_scrambled': 'CONTENT_SCRAMBLED',
    'function_scrambled': 'FUNCTION_SCRAMBLED',
    'cue_deleted': 'CUE_DELETED',
}


# ============================================================================
# CONTEXT TRUNCATION
# ============================================================================

def get_k_word_suffix(text, k):
    """
    Get last k whitespace words from text.

    Args:
        text: Full text string
        k: Number of words to keep (None = keep all)

    Returns:
        Truncated text with last k words
    """
    if k is None:
        return text

    words = text.split()

    if k >= len(words):
        return text

    return ' '.join(words[-k:])


def compute_entropy(probs, analyzer):
    """
    Compute entropy over word-start tokens.

    Args:
        probs: Probability distribution (torch tensor)
        analyzer: WordLevelAnalyzer instance

    Returns:
        Entropy in bits
    """
    # Get top-k word-start tokens
    top_k = 1000
    top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

    # Filter to word-start only
    word_start_probs = []

    for prob, token_id in zip(top_k_probs, top_k_ids):
        if analyzer.is_word_start_token(token_id.item()):
            word_start_probs.append(prob.item())

    # Normalize
    word_start_probs = np.array(word_start_probs)
    if len(word_start_probs) == 0:
        return np.nan

    word_start_probs = word_start_probs / word_start_probs.sum()

    # Compute entropy (in bits)
    entropy = -np.sum(word_start_probs * np.log2(word_start_probs + 1e-10))

    return entropy


# ============================================================================
# ABLATION ANALYSIS
# ============================================================================

def run_context_ablation(
    model_name: str,
    stimuli_file: str,
    output_file: str,
    top_k: int = 1000,
):
    """
    Run context-length ablation analysis.

    Args:
        model_name: HuggingFace model name
        stimuli_file: Path to stimuli JSON
        output_file: Path to save results CSV
        top_k: Number of top tokens to consider
    """
    print("=" * 80)
    print("CONTEXT-LENGTH ABLATION ANALYSIS")
    print("=" * 80)
    print()
    print(f"Model: {model_name}")
    print(f"Stimuli: {stimuli_file}")
    print(f"Cue families: {TARGET_CUE_FAMILIES}")
    print(f"Conditions: {TARGET_CONDITIONS}")
    print(f"Context lengths (k): {CONTEXT_K_VALUES}")
    print(f"Output: {output_file}")
    print()

    # Load model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    if torch.cuda.is_available():
        model = model.cuda()
        print("✓ Using GPU")
    else:
        print("✓ Using CPU")
    print()

    # Load stimuli
    print("Loading stimuli...")
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)
    print(f"✓ Loaded {len(stimuli)} stimulus sets")
    print()

    # Create analyzer
    analyzer = WordLevelAnalyzer(tokenizer, CUE_FAMILIES)
    print("✓ Analyzer ready")
    print()

    # Run ablation
    print("=" * 80)
    print("RUNNING ABLATION")
    print("=" * 80)
    print()

    results = []

    # Count total iterations
    total_iterations = 0
    for stim_set in stimuli:
        for cond_key, cond_name in CONDITION_MAP.items():
            if cond_name not in TARGET_CONDITIONS:
                continue

            text = stim_set[cond_key]

            for family_name in TARGET_CUE_FAMILIES:
                # Find cues
                cue_positions = analyzer.find_cue_positions(text, family_name)
                total_iterations += len(cue_positions) * len(CONTEXT_K_VALUES)

    with tqdm(total=total_iterations, desc="Progress") as pbar:
        for stim_set in stimuli:
            set_id = stim_set['set_id']

            for cond_key, cond_name in CONDITION_MAP.items():
                if cond_name not in TARGET_CONDITIONS:
                    continue

                text = stim_set[cond_key]

                for family_name in TARGET_CUE_FAMILIES:
                    # Find cue positions
                    cue_positions = analyzer.find_cue_positions(text, family_name)

                    for word_idx, cue_word, full_context in cue_positions:
                        # Test each context length k
                        for k in CONTEXT_K_VALUES:
                            # Truncate to last k words
                            context_k = get_k_word_suffix(full_context, k)

                            # Tokenize
                            inputs = tokenizer(context_k, return_tensors='pt')
                            if torch.cuda.is_available():
                                inputs = {key: val.cuda() for key, val in inputs.items()}

                            # Get predictions
                            with torch.no_grad():
                                outputs = model(**inputs)

                            logits = outputs.logits[0, -1, :]
                            probs = torch.softmax(logits, dim=-1)

                            # Compute class mass
                            class_mass = analyzer.compute_class_mass(probs, family_name, top_k=top_k)

                            # Get primary class mass (e.g., VERB for infinitival_to)
                            family_spec = CUE_FAMILIES[family_name]
                            primary_class = family_spec['primary_class']
                            target_mass = class_mass.get(primary_class, 0.0)

                            # Compute total mass on all expected classes (open-class mass)
                            open_class_mass = sum(class_mass.values())

                            # Compute entropy
                            entropy = compute_entropy(probs, analyzer)

                            # Store result
                            results.append({
                                'model': model_name,
                                'cue_family': family_name,
                                'condition': cond_name,
                                'sentence_id': set_id,
                                'cue_index': word_idx,
                                'cue_word': cue_word,
                                'k': k if k is not None else 'full',
                                'context_truncated': context_k,
                                'target_mass': target_mass,
                                'open_class_mass': open_class_mass,
                                'entropy': entropy,
                                'num_tokens': len(inputs['input_ids'][0]),
                            })

                            pbar.update(1)

    print()
    print("=" * 80)
    print("ABLATION COMPLETE")
    print("=" * 80)
    print()

    # Summary
    print(f"Total measurements: {len(results)}")
    print()

    # Breakdown
    print("Measurements per condition:")
    for cond in TARGET_CONDITIONS:
        n = sum(1 for r in results if r['condition'] == cond)
        print(f"  {cond:20s}: {n:4d}")
    print()

    print("Measurements per cue family:")
    for family in TARGET_CUE_FAMILIES:
        n = sum(1 for r in results if r['cue_family'] == family)
        family_spec = CUE_FAMILIES[family]
        print(f"  {family_spec['name']:30s}: {n:4d}")
    print()

    print("Measurements per k:")
    for k in CONTEXT_K_VALUES:
        k_label = k if k is not None else 'full'
        n = sum(1 for r in results if r['k'] == k_label)
        print(f"  k={str(k_label):>4s}: {n:4d}")
    print()

    # Save as CSV
    print(f"Saving results to: {output_file}")

    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)

    print("✓ Results saved")
    print()

    # Quick summary statistics
    print("=" * 80)
    print("QUICK SUMMARY (mean target_mass by k)")
    print("=" * 80)
    print()

    for family in TARGET_CUE_FAMILIES:
        family_spec = CUE_FAMILIES[family]
        print(f"{family_spec['name']}:")
        print()

        df_family = df[df['cue_family'] == family]

        for cond in TARGET_CONDITIONS:
            df_cond = df_family[df_family['condition'] == cond]

            if len(df_cond) == 0:
                continue

            print(f"  {cond}:")

            for k in CONTEXT_K_VALUES:
                k_label = k if k is not None else 'full'
                df_k = df_cond[df_cond['k'] == k_label]

                if len(df_k) == 0:
                    continue

                mean = df_k['target_mass'].mean()
                std = df_k['target_mass'].std()
                print(f"    k={str(k_label):>4s}: {mean:.4f} ± {std:.4f}")

            print()

    print("=" * 80)
    print("NEXT STEP: ANALYZE RESULTS")
    print("=" * 80)
    print()
    print(f"python analyze_context_ablation.py {output_file}")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Run context-length ablation analysis'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='gpt2',
        help='HuggingFace model name (default: gpt2)'
    )

    parser.add_argument(
        '--stimuli',
        type=str,
        default='stimuli_comprehensive.json',
        help='Path to stimuli JSON (default: stimuli_comprehensive.json)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output CSV file (default: context_ablation_{model}.csv)'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=1000,
        help='Number of top tokens to consider (default: 1000)'
    )

    args = parser.parse_args()

    # Generate output filename if not specified
    if args.output is None:
        model_slug = args.model.replace('/', '_')
        args.output = f'context_ablation_{model_slug}.csv'

    # Run ablation
    run_context_ablation(
        model_name=args.model,
        stimuli_file=args.stimuli,
        output_file=args.output,
        top_k=args.top_k,
    )


if __name__ == '__main__':
    main()
