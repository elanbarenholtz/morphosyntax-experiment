#!/usr/bin/env python3
"""
Locked Design Morphosyntax Audit with Integrated Context Ablation

Features:
- Uses per-cue-family locked stimuli (30 sentences × 6 families × 6 conditions)
- Runs context ablation in parallel (k ∈ {1, 2, 4, 8, full})
- Computes target-class probability mass for each cue family
- Outputs structured results for statistical analysis

Target Classes per Cue Family:
- infinitival_to → VERB (base form)
- modals → VERB (base form)
- determiners → NOUN or ADJ
- prepositions → NP_START (det, adj, or noun)
- auxiliaries → PARTICIPLE (V-ing or V-ed)
- complementizers → CLAUSE_START (pronoun, det, or noun)

Usage:
    python run_locked_audit.py --model gpt2
    python run_locked_audit.py --model EleutherAI/pythia-410m
"""

import json
import argparse
import torch
import numpy as np
from tqdm import tqdm
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer

# ============================================================================
# TARGET CLASS DEFINITIONS (Expanded Word Sets)
# ============================================================================

VERB_SET = {
    # Common base-form verbs
    'be', 'have', 'do', 'say', 'go', 'get', 'make', 'know', 'think', 'take',
    'see', 'come', 'want', 'use', 'find', 'give', 'tell', 'work', 'call', 'try',
    'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep', 'let', 'begin',
    'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'live', 'believe',
    'bring', 'happen', 'write', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue',
    'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak',
    'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'teach', 'offer',
    'remember', 'love', 'consider', 'appear', 'buy', 'serve', 'die', 'send', 'build', 'stay',
    'fall', 'cut', 'reach', 'kill', 'raise', 'pass', 'sell', 'decide', 'return', 'explain',
    'hope', 'develop', 'carry', 'break', 'receive', 'agree', 'support', 'hit', 'produce', 'eat',
    # Domain-specific verbs
    'study', 'research', 'investigate', 'examine', 'analyze', 'explore',
    'paint', 'draw', 'design', 'construct', 'perform', 'practice', 'rehearse',
    'publish', 'edit', 'revise', 'prepare', 'cook', 'bake', 'repair', 'fix', 'mend',
    'solve', 'calculate', 'compute', 'improve', 'enhance', 'upgrade',
    'debug', 'test', 'validate', 'organize', 'arrange', 'sort',
    'defend', 'protect', 'guard', 'film', 'record', 'capture',
    'sail', 'navigate', 'steer', 'discuss', 'debate', 'argue',
    'assemble', 'combine', 'join', 'refine', 'polish', 'perfect',
    'plan', 'schedule', 'finish', 'complete', 'conclude', 'start', 'end',
    'measure', 'weigh', 'count', 'observe', 'monitor', 'track',
}

NOUN_SET = {
    # Common nouns
    'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life', 'hand',
    'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case', 'point', 'government',
    'company', 'number', 'group', 'problem', 'fact', 'house', 'area', 'money', 'story', 'student',
    'word', 'family', 'head', 'water', 'room', 'mother', 'information', 'night', 'home', 'side',
    'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community',
    'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'back', 'parent', 'face',
    'level', 'office', 'door', 'health', 'art', 'war', 'history', 'party', 'result', 'change',
    'morning', 'reason', 'research', 'girl', 'guy', 'moment', 'air', 'teacher', 'force', 'education',
    # Domain-specific nouns
    'scientist', 'artist', 'musician', 'author', 'chef', 'mechanic', 'programmer',
    'engineer', 'architect', 'sailor', 'athlete', 'researcher', 'historian',
    'artifacts', 'paintings', 'symphony', 'novel', 'meal', 'software',
    'blueprint', 'boat', 'strategy', 'findings', 'documents', 'specimens',
    'composition', 'recipe', 'engine', 'code', 'building', 'vessel', 'data',
    'manuscript', 'dish', 'bug', 'system', 'structure', 'ship', 'experiment',
    'book', 'techniques', 'methods', 'tools', 'equipment', 'materials',
    'doctor', 'patient', 'professor', 'detective', 'captain', 'director',
}

ADJECTIVE_SET = {
    # Common adjectives
    'new', 'good', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
    'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
    'few', 'public', 'bad', 'same', 'able', 'social', 'national', 'black', 'white', 'political',
    'best', 'full', 'simple', 'left', 'late', 'hard', 'real', 'top', 'whole', 'sure',
    'better', 'free', 'special', 'clear', 'recent', 'beautiful', 'strong', 'particular', 'certain', 'open',
    'red', 'difficult', 'available', 'likely', 'short', 'single', 'medical', 'current', 'wrong', 'private',
    'past', 'foreign', 'fine', 'common', 'poor', 'natural', 'significant', 'similar', 'hot', 'dead',
    'central', 'happy', 'serious', 'ready', 'easy', 'effective', 'aware', 'human', 'local',
    # Domain-specific adjectives
    'ancient', 'complex', 'delicious', 'broken', 'faulty', 'efficient',
    'sturdy', 'seaworthy', 'winning', 'comprehensive', 'historical', 'rare', 'valuable',
    'intricate', 'challenging', 'innovative', 'experimental', 'preliminary', 'final',
    'elaborate', 'fundamental', 'critical', 'remarkable', 'unusual', 'mysterious',
    'fascinating', 'practical', 'theoretical', 'advanced', 'basic', 'modern',
}

# Participles (both -ing and -ed forms)
PARTICIPLE_SET = {
    # -ing forms
    'being', 'having', 'doing', 'saying', 'going', 'getting', 'making', 'knowing',
    'studying', 'examining', 'analyzing', 'exploring', 'investigating', 'reviewing',
    'inspecting', 'evaluating', 'assessing', 'testing', 'repairing', 'building',
    'designing', 'creating', 'developing', 'improving', 'fixing', 'completing',
    'finishing', 'preparing', 'organizing', 'documenting', 'presenting', 'explaining',
    'discussing', 'publishing', 'researching', 'demonstrating', 'solving', 'processing',
    'working', 'running', 'walking', 'talking', 'reading', 'writing', 'playing',
    'watching', 'listening', 'thinking', 'looking', 'waiting', 'trying', 'helping',
    # -ed forms (past participles)
    'been', 'had', 'done', 'said', 'gone', 'gotten', 'made', 'known', 'thought', 'taken',
    'seen', 'come', 'wanted', 'used', 'found', 'given', 'told', 'worked', 'called', 'tried',
    'studied', 'examined', 'analyzed', 'explored', 'investigated', 'reviewed',
    'inspected', 'evaluated', 'assessed', 'tested', 'repaired', 'built',
    'designed', 'created', 'developed', 'improved', 'fixed', 'completed',
    'finished', 'prepared', 'organized', 'documented', 'presented', 'explained',
    'discussed', 'published', 'researched', 'demonstrated', 'solved', 'processed',
    'broken', 'written', 'taken', 'given', 'shown', 'chosen', 'spoken', 'frozen',
}

# NP_START: words that can start a noun phrase
NP_START_SET = NOUN_SET | ADJECTIVE_SET | {
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her',
    'its', 'our', 'their', 'some', 'any', 'each', 'every', 'all', 'both', 'many',
    'few', 'several', 'other', 'another', 'such', 'no', 'one', 'two', 'three',
}

# CLAUSE_START: words that can start an embedded clause
CLAUSE_START_SET = {
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those', 'who', 'what', 'which', 'where', 'when', 'why', 'how',
    'the', 'a', 'an', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'some', 'any', 'all', 'both', 'each', 'every', 'no', 'everyone', 'someone', 'anyone',
} | NOUN_SET

# Target class mapping per cue family
TARGET_CLASSES = {
    'infinitival_to': {
        'primary': 'VERB',
        'word_sets': {'VERB': VERB_SET},
    },
    'modals': {
        'primary': 'VERB',
        'word_sets': {'VERB': VERB_SET},
    },
    'determiners': {
        'primary': 'NOUN_OR_ADJ',
        'word_sets': {'NOUN': NOUN_SET, 'ADJ': ADJECTIVE_SET},
    },
    'prepositions': {
        'primary': 'NP_START',
        'word_sets': {'NP_START': NP_START_SET},
    },
    'auxiliaries': {
        'primary': 'PARTICIPLE',
        'word_sets': {'PARTICIPLE': PARTICIPLE_SET},
    },
    'complementizers': {
        'primary': 'CLAUSE_START',
        'word_sets': {'CLAUSE_START': CLAUSE_START_SET},
    },
}

# ============================================================================
# WORD-LEVEL ANALYZER
# ============================================================================

class WordLevelAnalyzer:
    """Analyze model predictions at word level (avoiding BPE artifacts)."""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self._token_cache = {}

    def is_word_start_token(self, token_id: int) -> bool:
        """Check if token represents start of a word (space-prefixed in GPT-2/Pythia)."""
        if token_id in self._token_cache:
            return self._token_cache[token_id][0]

        token_str = self.tokenizer.decode([token_id])

        # Skip special tokens
        if token_str in ['<|endoftext|>', '<unk>', '<pad>', '']:
            self._token_cache[token_id] = (False, None)
            return False

        # Word-start tokens begin with space or newline
        is_start = token_str.startswith(' ') or token_str.startswith('\n')

        # Extract word if it's a word-start token
        if is_start:
            word = token_str.strip().lower().strip('.,!?;:"\'-')
            self._token_cache[token_id] = (True, word)
        else:
            self._token_cache[token_id] = (False, None)

        return is_start

    def get_word_from_token(self, token_id: int) -> Optional[str]:
        """Get word from token (only for word-start tokens)."""
        if token_id not in self._token_cache:
            self.is_word_start_token(token_id)
        return self._token_cache[token_id][1]

    def compute_class_mass(
        self,
        probs: torch.Tensor,
        word_sets: Dict[str, Set[str]],
        top_k: int = 1000
    ) -> Dict[str, float]:
        """
        Compute probability mass for each word class.

        Args:
            probs: Probability distribution over vocabulary
            word_sets: Dict mapping class names to word sets
            top_k: Number of top tokens to consider

        Returns:
            Dict mapping class names to probability mass
        """
        top_k_probs, top_k_ids = torch.topk(probs, min(top_k, len(probs)))

        class_mass = {class_name: 0.0 for class_name in word_sets}

        for prob, token_id in zip(top_k_probs, top_k_ids):
            word = self.get_word_from_token(token_id.item())

            if word is None:
                continue

            for class_name, word_set in word_sets.items():
                if word in word_set:
                    class_mass[class_name] += prob.item()

        return class_mass


# ============================================================================
# CONTEXT ABLATION
# ============================================================================

def truncate_context(text: str, cue_position: int, k: int) -> str:
    """
    Truncate context to last k words before (and including) the cue.

    Args:
        text: Full sentence
        cue_position: 0-indexed word position of cue
        k: Number of words to include (including cue)

    Returns:
        Truncated context string
    """
    words = text.split()

    if k >= cue_position + 1:
        # Full context up to and including cue
        return ' '.join(words[:cue_position + 1])
    else:
        # Truncated: last k words ending at cue
        start_idx = max(0, cue_position + 1 - k)
        return ' '.join(words[start_idx:cue_position + 1])


# ============================================================================
# MAIN AUDIT FUNCTION
# ============================================================================

def run_audit(
    model_name: str,
    stimuli_file: str,
    output_file: str,
    context_lengths: List[int] = [1, 2, 4, 8, -1],  # -1 means full
    top_k: int = 1000,
):
    """
    Run comprehensive morphosyntax audit with context ablation.

    Args:
        model_name: HuggingFace model name
        stimuli_file: Path to locked stimuli JSON
        output_file: Path to save results
        context_lengths: List of k values for context ablation (-1 = full)
        top_k: Number of top tokens for class mass computation
    """
    print("=" * 80)
    print("LOCKED DESIGN MORPHOSYNTAX AUDIT")
    print("=" * 80)
    print()
    print(f"Model: {model_name}")
    print(f"Stimuli: {stimuli_file}")
    print(f"Context lengths: {context_lengths}")
    print(f"Output: {output_file}")
    print()

    # Load model
    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    print(f"  Device: {device}")
    print()

    # Load stimuli
    print("Loading stimuli...")
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)
    print(f"  Loaded {len(stimuli)} stimuli")
    print()

    # Create analyzer
    analyzer = WordLevelAnalyzer(tokenizer)

    # Conditions to test
    conditions = [
        'sentence', 'jabberwocky', 'full_scrambled',
        'content_scrambled', 'function_scrambled', 'cue_deleted'
    ]

    # Run audit
    print("Running audit...")
    results = []

    total_iters = len(stimuli) * len(conditions) * len(context_lengths)

    with tqdm(total=total_iters, desc="Progress") as pbar:
        for stim in stimuli:
            cue_family = stim['cue_family']
            cue_position = stim['cue_position']
            target_config = TARGET_CLASSES[cue_family]
            word_sets = target_config['word_sets']

            for condition in conditions:
                text = stim[condition]

                for k in context_lengths:
                    # Get context (full or truncated)
                    if k == -1:
                        context = ' '.join(text.split()[:cue_position + 1])
                        k_label = 'full'
                    else:
                        context = truncate_context(text, cue_position, k)
                        k_label = str(k)

                    # Tokenize and get predictions
                    inputs = tokenizer(context, return_tensors='pt').to(device)

                    with torch.no_grad():
                        outputs = model(**inputs)

                    logits = outputs.logits[0, -1, :]
                    probs = torch.softmax(logits, dim=-1).cpu()

                    # Compute class mass
                    class_mass = analyzer.compute_class_mass(probs, word_sets, top_k=top_k)

                    # Compute total target mass
                    if cue_family == 'determiners':
                        # For determiners, report both NOUN and ADJ, plus combined
                        target_mass = class_mass.get('NOUN', 0) + class_mass.get('ADJ', 0)
                    else:
                        primary_class = target_config['primary']
                        target_mass = sum(class_mass.values())

                    result = {
                        'set_id': stim['set_id'],
                        'cue_family': cue_family,
                        'cue_word': stim['cue_word'],
                        'condition': condition.upper(),
                        'context_k': k_label,
                        'context': context,
                        'target_mass': target_mass,
                        'class_mass': class_mass,
                        'num_tokens': len(inputs['input_ids'][0]),
                    }

                    results.append(result)
                    pbar.update(1)

    print()
    print("Audit complete!")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    # Group results for summary
    print("Target mass by cue family × condition (k=full):")
    print()
    print(f"{'Family':<18} {'SENT':>8} {'JAB':>8} {'FULL_S':>8} {'CONT_S':>8} {'FUNC_S':>8} {'CUE_D':>8}")
    print("-" * 78)

    for family in TARGET_CLASSES.keys():
        row = [family]
        for cond in ['SENTENCE', 'JABBERWOCKY', 'FULL_SCRAMBLED', 'CONTENT_SCRAMBLED', 'FUNCTION_SCRAMBLED', 'CUE_DELETED']:
            masses = [r['target_mass'] for r in results
                     if r['cue_family'] == family and r['condition'] == cond and r['context_k'] == 'full']
            if masses:
                row.append(f"{np.mean(masses):.3f}")
            else:
                row.append("N/A")
        print(f"{row[0]:<18} {row[1]:>8} {row[2]:>8} {row[3]:>8} {row[4]:>8} {row[5]:>8} {row[6]:>8}")

    print()

    # Context ablation summary
    print("Context ablation (JABBERWOCKY condition):")
    print()
    print(f"{'Family':<18} {'k=1':>8} {'k=2':>8} {'k=4':>8} {'k=8':>8} {'k=full':>8}")
    print("-" * 58)

    for family in TARGET_CLASSES.keys():
        row = [family]
        for k in ['1', '2', '4', '8', 'full']:
            masses = [r['target_mass'] for r in results
                     if r['cue_family'] == family and r['condition'] == 'JABBERWOCKY' and r['context_k'] == k]
            if masses:
                row.append(f"{np.mean(masses):.3f}")
            else:
                row.append("N/A")
        print(f"{row[0]:<18} {row[1]:>8} {row[2]:>8} {row[3]:>8} {row[4]:>8} {row[5]:>8}")

    print()

    # Save results
    print(f"Saving results to: {output_file}")

    output_data = {
        'metadata': {
            'model': model_name,
            'stimuli_file': stimuli_file,
            'timestamp': datetime.now().isoformat(),
            'context_lengths': context_lengths,
            'top_k': top_k,
            'num_stimuli': len(stimuli),
            'num_results': len(results),
        },
        'results': results,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Done!")
    print()
    print("Next steps:")
    print(f"  python analyze_locked_results.py {output_file}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Run locked design morphosyntax audit with context ablation'
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
        default='stimuli_locked.json',
        help='Path to locked stimuli JSON (default: stimuli_locked.json)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: locked_audit_{model}.json)'
    )

    parser.add_argument(
        '--context-lengths',
        type=str,
        default='1,2,4,8,-1',
        help='Comma-separated context lengths (-1=full) (default: 1,2,4,8,-1)'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=1000,
        help='Number of top tokens for class mass (default: 1000)'
    )

    args = parser.parse_args()

    # Parse context lengths
    context_lengths = [int(x) for x in args.context_lengths.split(',')]

    # Generate output filename if not specified
    if args.output is None:
        model_slug = args.model.replace('/', '_')
        args.output = f'locked_audit_{model_slug}.json'

    run_audit(
        model_name=args.model,
        stimuli_file=args.stimuli,
        output_file=args.output,
        context_lengths=context_lengths,
        top_k=args.top_k,
    )


if __name__ == '__main__':
    main()
