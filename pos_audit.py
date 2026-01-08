"""
POS Audit: Category-level Constraint Analysis

Operationalizes syntactic constraint as measurable shifts in the model's
continuation distribution toward expected POS categories at diagnostic cue positions.

Key insight: If syntax constrains prediction, we should see:
- After determiners (the/a) → noun/adjective-like candidates
- After "to" → verb-like candidates
- After auxiliaries (was/has) → verb/participle-like candidates

This pattern should hold for Sentence and Jabberwocky, but weaken for Scrambled.
"""

import json
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import spacy
from collections import defaultdict
from typing import Dict, List, Tuple
import argparse

# spaCy will be loaded in main function to avoid macOS issues
nlp = None

# Define diagnostic cues and expected categories
DIAGNOSTIC_CUES = {
    'determiners': ['the', 'a'],
    'infinitive_to': ['to'],
    'auxiliaries': ['was', 'has'],
    'prepositions': ['in', 'on']
}

EXPECTED_CATEGORIES = {
    'determiners': {'NOUN', 'ADJ', 'PROPN'},
    'infinitive_to': {'VERB'},
    'auxiliaries': {'VERB', 'ADJ'},
    'prepositions': {'NOUN', 'DET', 'PROPN', 'PRON'}
}

def get_top_k_predictions(model, tokenizer, text: str, position: int, k=100):
    """
    Get top-k next-token predictions at a specific word position.

    Returns list of (token_string, probability, token_id) tuples.
    """
    # Tokenize up to position
    words = text.split()
    context = ' '.join(words[:position+1])

    # Get model predictions
    inputs = tokenizer(context, return_tensors='pt')

    with torch.no_grad():
        outputs = model(**inputs)
        next_token_logits = outputs.logits[0, -1, :]

    # Get top-k
    probs = torch.softmax(next_token_logits, dim=-1)
    top_k_probs, top_k_ids = torch.topk(probs, k)

    # Decode tokens
    candidates = []
    for prob, token_id in zip(top_k_probs, top_k_ids):
        token_str = tokenizer.decode([token_id], skip_special_tokens=True)

        # Only include substantive tokens (not empty strings)
        if token_str.strip():
            candidates.append({
                'token': token_str.strip(),
                'prob': prob.item(),
                'token_id': token_id.item()
            })

    return candidates

def pos_tag_candidates(candidates: List[Dict]) -> List[Dict]:
    """
    Add POS tags to candidates using spaCy.
    """
    tagged = []
    for cand in candidates:
        # Get first word if multi-token
        first_word = cand['token'].split()[0] if cand['token'] else ''

        if first_word:
            doc = nlp(first_word)
            pos = doc[0].pos_ if len(doc) > 0 else 'UNK'

            tagged.append({
                **cand,
                'pos': pos,
                'first_word': first_word
            })

    return tagged

def find_cue_positions(text: str, cue_words: List[str]) -> List[int]:
    """
    Find all positions in text where cue words appear.
    Returns list of word indices.
    """
    words = text.split()
    positions = []

    for i, word in enumerate(words[:-1]):  # Don't check last word
        # Clean word (remove punctuation)
        clean_word = word.strip('.,!?;:').lower()
        if clean_word in cue_words:
            positions.append(i)

    return positions

def analyze_condition(stimuli: List[Dict], condition: str, model, tokenizer, k=100):
    """
    Analyze all diagnostic cue positions for one condition.
    """
    results = defaultdict(list)

    for stim_idx, stim in enumerate(stimuli):
        text = stim[condition]

        # Check each cue type
        for cue_type, cue_words in DIAGNOSTIC_CUES.items():
            positions = find_cue_positions(text, cue_words)

            for pos in positions:
                # Get top-k predictions at this position
                candidates = get_top_k_predictions(model, tokenizer, text, pos, k)

                # POS tag
                tagged = pos_tag_candidates(candidates)

                # Compute POS distribution (weighted by probability)
                pos_dist = defaultdict(float)
                total_prob = sum(c['prob'] for c in tagged)

                for c in tagged:
                    pos_dist[c['pos']] += c['prob'] / total_prob if total_prob > 0 else 0

                # Compute % in expected categories
                expected_cats = EXPECTED_CATEGORIES[cue_type]
                expected_prob = sum(pos_dist[cat] for cat in expected_cats)

                results[cue_type].append({
                    'stimulus_idx': stim_idx,
                    'position': pos,
                    'cue_word': text.split()[pos],
                    'pos_distribution': dict(pos_dist),
                    'expected_category_prob': expected_prob,
                    'top_10_candidates': tagged[:10]
                })

    return results

def summarize_results(all_results: Dict):
    """
    Compute aggregate statistics across conditions and cue types.
    """
    summary = {}

    for condition in all_results:
        summary[condition] = {}

        for cue_type in all_results[condition]:
            instances = all_results[condition][cue_type]

            if not instances:
                continue

            # Average POS distribution
            avg_pos_dist = defaultdict(float)
            for inst in instances:
                for pos, prob in inst['pos_distribution'].items():
                    avg_pos_dist[pos] += prob / len(instances)

            # Average expected category probability
            avg_expected_prob = np.mean([inst['expected_category_prob']
                                        for inst in instances])
            std_expected_prob = np.std([inst['expected_category_prob']
                                       for inst in instances])

            summary[condition][cue_type] = {
                'n_instances': len(instances),
                'avg_pos_distribution': dict(avg_pos_dist),
                'expected_category_prob_mean': avg_expected_prob,
                'expected_category_prob_std': std_expected_prob
            }

    return summary

def print_summary_report(summary: Dict):
    """
    Print formatted summary report.
    """
    print("\n" + "="*80)
    print("POS AUDIT: Category-level Constraint Analysis")
    print("="*80)
    print()

    print("Expected categories by cue type:")
    for cue_type, cats in EXPECTED_CATEGORIES.items():
        print(f"  {cue_type:20s}: {', '.join(cats)}")
    print()

    # Print results by cue type
    cue_types = list(DIAGNOSTIC_CUES.keys())
    conditions = ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']

    for cue_type in cue_types:
        print(f"\n{cue_type.upper()}")
        print("-" * 80)
        print(f"{'Condition':<25} {'N':<6} {'Expected %':<15} {'Top Categories':<30}")
        print("-" * 80)

        for condition in conditions:
            if condition in summary and cue_type in summary[condition]:
                data = summary[condition][cue_type]

                # Format expected probability
                exp_prob = data['expected_category_prob_mean'] * 100
                exp_std = data['expected_category_prob_std'] * 100
                exp_str = f"{exp_prob:.1f} ± {exp_std:.1f}%"

                # Get top 3 POS categories
                pos_dist = data['avg_pos_distribution']
                top_3 = sorted(pos_dist.items(), key=lambda x: -x[1])[:3]
                top_str = ', '.join([f"{pos}:{prob*100:.0f}%" for pos, prob in top_3])

                print(f"{condition:<25} {data['n_instances']:<6} {exp_str:<15} {top_str:<30}")

        print()

    # Compute deltas (Jab - Scrambled)
    print("\n" + "="*80)
    print("KEY RESULT: ΔExpected% (Jabberwocky - Scrambled)")
    print("="*80)
    print(f"{'Cue Type':<20} {'ΔExpected%':<15} {'Interpretation':<40}")
    print("-" * 80)

    for cue_type in cue_types:
        if (cue_type in summary.get('jabberwocky_matched', {}) and
            cue_type in summary.get('scrambled_jabberwocky', {})):

            jab = summary['jabberwocky_matched'][cue_type]['expected_category_prob_mean']
            scr = summary['scrambled_jabberwocky'][cue_type]['expected_category_prob_mean']
            delta = (jab - scr) * 100

            interp = "Structure helps ✓" if delta > 5 else "Weak/no effect"

            print(f"{cue_type:<20} {delta:>+6.1f}%         {interp:<40}")

    print("="*80)

def run_pos_audit(stimuli_file: str, model_name: str, output_file: str, k=100):
    """
    Main function to run POS audit.
    """
    global nlp

    print(f"\nRunning POS audit for {model_name}")
    print(f"Stimuli: {stimuli_file}")
    print(f"Top-k: {k}")
    print()

    # Load spaCy model
    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_sm")
    print("spaCy loaded.")

    # Load model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()
    print("Model loaded.")

    # Load stimuli
    with open(stimuli_file) as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets.")
    print()

    # Analyze each condition
    all_results = {}
    conditions = ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky']

    for condition in conditions:
        print(f"Analyzing {condition}...")
        all_results[condition] = analyze_condition(stimuli, condition,
                                                   model, tokenizer, k)

    # Summarize
    summary = summarize_results(all_results)

    # Print report
    print_summary_report(summary)

    # Save results
    output = {
        'model_name': model_name,
        'stimuli_file': stimuli_file,
        'k': k,
        'diagnostic_cues': DIAGNOSTIC_CUES,
        'expected_categories': {k: list(v) for k, v in EXPECTED_CATEGORIES.items()},
        'detailed_results': all_results,
        'summary': summary
    }

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='POS category audit')
    parser.add_argument('--stimuli', default='stimuli_with_scrambled.json',
                       help='Stimuli file')
    parser.add_argument('--model', default='gpt2',
                       help='Model name')
    parser.add_argument('--output', default='pos_audit_results.json',
                       help='Output file')
    parser.add_argument('--k', type=int, default=100,
                       help='Top-k candidates to analyze')

    args = parser.parse_args()

    run_pos_audit(args.stimuli, args.model, args.output, args.k)
