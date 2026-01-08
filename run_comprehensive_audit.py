#!/usr/bin/env python3
"""
Comprehensive Morphosyntax Constraint Audit

Tests morphosyntactic knowledge across:
- 6 stimulus conditions (SENTENCE, JABBERWOCKY, FULL_SCRAMBLED, CONTENT_SCRAMBLED, FUNCTION_SCRAMBLED, CUE_DELETION)
- 6 cue families (infinitival_to, modals, determiners, prepositions, auxiliaries, complementizers)
- Word-level analysis (avoiding BPE artifacts)

Output: Structured results for statistical analysis with FDR correction and bootstrap CIs.
"""

import json
import argparse
import torch
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer

from cue_families import CUE_FAMILIES
from word_level_analysis import WordLevelAnalyzer


# ============================================================================
# STIMULUS CONDITION MAPPING
# ============================================================================

CONDITION_MAP = {
    'sentence': 'SENTENCE',
    'jabberwocky': 'JABBERWOCKY',
    'full_scrambled': 'FULL_SCRAMBLED',
    'content_scrambled': 'CONTENT_SCRAMBLED',
    'function_scrambled': 'FUNCTION_SCRAMBLED',
    'cue_deleted': 'CUE_DELETED',
}

CUE_FAMILY_NAMES = [
    'infinitival_to',
    'modals',
    'determiners',
    'prepositions',
    'auxiliaries',
    'complementizers',
]


# ============================================================================
# MAIN AUDIT FUNCTION
# ============================================================================

def run_comprehensive_audit(
    model_name: str,
    stimuli_file: str,
    output_file: str,
    method: str = 'lexicon',
    top_k: int = 1000,
):
    """
    Run comprehensive morphosyntax audit.

    Args:
        model_name: HuggingFace model name (e.g., 'gpt2', 'EleutherAI/pythia-410m')
        stimuli_file: Path to stimuli JSON (stimuli_comprehensive.json)
        output_file: Path to save results JSON
        method: Classification method ('lexicon', 'pos', 'classifier')
        top_k: Number of top tokens to consider
    """
    print("=" * 80)
    print("COMPREHENSIVE MORPHOSYNTAX CONSTRAINT AUDIT")
    print("=" * 80)
    print()
    print(f"Model: {model_name}")
    print(f"Stimuli: {stimuli_file}")
    print(f"Method: {method}")
    print(f"Output: {output_file}")
    print()

    # Load model and tokenizer
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
    print("Initializing word-level analyzer...")
    analyzer = WordLevelAnalyzer(tokenizer, CUE_FAMILIES)
    print("✓ Analyzer ready")
    print()

    # Run audit
    print("=" * 80)
    print("RUNNING AUDIT")
    print("=" * 80)
    print()

    results = []
    total_combinations = len(stimuli) * len(CONDITION_MAP) * len(CUE_FAMILY_NAMES)

    with tqdm(total=total_combinations, desc="Progress") as pbar:
        for stim_set in stimuli:
            set_id = stim_set['set_id']

            # For each stimulus condition
            for cond_key, cond_name in CONDITION_MAP.items():
                text = stim_set[cond_key]

                # For each cue family
                for family_name in CUE_FAMILY_NAMES:
                    # Analyze predictions after cues
                    cue_results = analyzer.analyze_cue_predictions(
                        text, family_name, model, top_k=top_k
                    )

                    # Store results for each cue instance
                    for cue_res in cue_results:
                        result_entry = {
                            'set_id': set_id,
                            'condition': cond_name,
                            'cue_family': family_name,
                            'cue_word': cue_res['cue_word'],
                            'word_index': cue_res['word_index'],
                            'context': cue_res['context'],
                            'class_mass': cue_res['class_mass'],
                            'num_tokens': cue_res['num_tokens'],
                            'text': text,
                        }
                        results.append(result_entry)

                    pbar.update(1)

    print()
    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()

    # Summary statistics
    print("Summary:")
    print(f"  Total instances analyzed: {len(results)}")
    print()

    # Breakdown by condition
    print("Instances per condition:")
    for cond_name in set(CONDITION_MAP.values()):
        n = sum(1 for r in results if r['condition'] == cond_name)
        print(f"  {cond_name:20s}: {n:4d}")

    print()

    # Breakdown by cue family
    print("Instances per cue family:")
    for family_name in CUE_FAMILY_NAMES:
        n = sum(1 for r in results if r['cue_family'] == family_name)
        family_spec = CUE_FAMILIES[family_name]
        print(f"  {family_spec['name']:30s}: {n:4d}")

    print()

    # Save results
    print(f"Saving results to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump({
            'metadata': {
                'model': model_name,
                'stimuli_file': stimuli_file,
                'method': method,
                'top_k': top_k,
                'num_stimulus_sets': len(stimuli),
                'num_conditions': len(CONDITION_MAP),
                'num_cue_families': len(CUE_FAMILY_NAMES),
            },
            'results': results,
        }, f, indent=2)

    print("✓ Results saved")
    print()
    print("=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print()
    print("Run statistical analysis:")
    print(f"  python analyze_comprehensive_results.py {output_file}")
    print()


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Run comprehensive morphosyntax constraint audit'
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
        help='Path to stimuli JSON file (default: stimuli_comprehensive.json)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: comprehensive_audit_{model}.json)'
    )

    parser.add_argument(
        '--method',
        type=str,
        default='lexicon',
        choices=['lexicon', 'pos', 'classifier'],
        help='Classification method (default: lexicon)'
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
        args.output = f'comprehensive_audit_{model_slug}.json'

    # Run audit
    run_comprehensive_audit(
        model_name=args.model,
        stimuli_file=args.stimuli,
        output_file=args.output,
        method=args.method,
        top_k=args.top_k,
    )


if __name__ == '__main__':
    main()
