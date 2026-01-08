"""
Diagnostic analysis: Deep dive into tokenization and probability distributions.
Investigates why stripped nonsense has low entropy.
"""

import openai
import numpy as np
import json
import os
from collections import defaultdict

# Try to load from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

openai.api_key = os.environ.get("OPENAI_API_KEY")

def calculate_entropy(logprobs_list):
    """Calculate Shannon entropy from logprobs."""
    probs = [np.exp(lp) for lp in logprobs_list]
    total = sum(probs)
    if total > 0:
        probs = [p / total for p in probs]
    entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
    return entropy

def get_detailed_logprobs(text, model="gpt-3.5-turbo"):
    """Get detailed token and logprob information."""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            max_tokens=1,
            logprobs=True,
            top_logprobs=20
        )

        if not response.choices[0].logprobs or not response.choices[0].logprobs.content:
            return None

        content_logprobs = response.choices[0].logprobs.content

        detailed_tokens = []
        for idx, token_data in enumerate(content_logprobs):
            token_info = {
                'position': idx,
                'token': token_data.token,
                'logprob': token_data.logprob,
                'top_logprobs': []
            }

            if token_data.top_logprobs:
                for item in token_data.top_logprobs:
                    token_info['top_logprobs'].append({
                        'token': item.token,
                        'logprob': item.logprob,
                        'prob': np.exp(item.logprob)
                    })

                # Calculate entropy at this position
                logprob_values = [item.logprob for item in token_data.top_logprobs]
                token_info['entropy'] = calculate_entropy(logprob_values)

            detailed_tokens.append(token_info)

        return detailed_tokens

    except Exception as e:
        print(f"Error: {e}")
        return None

def print_section_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")

def analyze_stimulus_set(stimuli_file="stimuli.json", set_id=1):
    """Perform detailed analysis on a single stimulus set."""

    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    # Get the specified set
    stim_set = [s for s in stimuli if s['set_id'] == set_id][0]

    print_section_header(f"DIAGNOSTIC ANALYSIS: STIMULUS SET {set_id}")

    results = {}

    # Analyze each condition
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        text = stim_set[condition]
        print(f"\n{'*' * 80}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'*' * 80}")
        print(f"\nText: {text}\n")

        # Get detailed logprobs
        detailed_tokens = get_detailed_logprobs(text)

        if not detailed_tokens:
            print("ERROR: Could not get logprobs")
            continue

        results[condition] = {
            'text': text,
            'tokens': detailed_tokens,
            'num_tokens': len(detailed_tokens)
        }

        # 1. Show tokenization
        print(f"Number of tokens: {len(detailed_tokens)}")
        print(f"\nTokenization:")
        print(f"{'Pos':>4} | {'Token':20} | {'Logprob':>10}")
        print("-" * 40)
        for tok in detailed_tokens:
            print(f"{tok['position']:4} | {repr(tok['token']):20} | {tok['logprob']:10.4f}")

        # 2. Show detailed probability distributions at beginning, middle, end
        positions_to_show = [0, len(detailed_tokens) // 2, len(detailed_tokens) - 1]

        for pos in positions_to_show:
            if pos >= len(detailed_tokens):
                continue

            tok_data = detailed_tokens[pos]
            print(f"\n{'-' * 80}")
            print(f"Position {pos}: Token = {repr(tok_data['token'])}, Entropy = {tok_data['entropy']:.4f} bits")
            print(f"{'-' * 80}")
            print(f"{'Rank':>4} | {'Token':20} | {'Probability':>12} | {'Logprob':>10}")
            print("-" * 60)

            for rank, item in enumerate(tok_data['top_logprobs'][:10], 1):
                print(f"{rank:4} | {repr(item['token']):20} | {item['prob']:12.6f} | {item['logprob']:10.4f}")

        print("\n")

    return results

def analyze_function_word_effects(stimuli_file="stimuli.json", set_id=1):
    """Analyze what happens after function words vs nonwords."""

    print_section_header("ANALYSIS: PREDICTIONS AFTER FUNCTION WORDS VS NONWORDS")

    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    stim_set = [s for s in stimuli if s['set_id'] == set_id][0]

    # Analyze Jabberwocky condition
    print("\n" + "*" * 80)
    print("JABBERWOCKY CONDITION")
    print("*" * 80)
    print(f"\nText: {stim_set['jabberwocky']}\n")

    jab_tokens = get_detailed_logprobs(stim_set['jabberwocky'])

    if jab_tokens:
        # Find positions of interest
        print("\nTokens in sequence:")
        for i, tok in enumerate(jab_tokens):
            print(f"{i:3}: {repr(tok['token']):20} (entropy: {tok['entropy']:.4f})")

        # Show distributions after "The", "was", and a nonword
        targets = []
        for i, tok in enumerate(jab_tokens):
            if tok['token'].lower().strip() in ['the', 'was', 'to']:
                if i + 1 < len(jab_tokens):
                    targets.append((i, tok['token'], 'function_word'))
            elif i > 0 and 'blicket' in tok['token'].lower() or 'florp' in tok['token'].lower():
                if i + 1 < len(jab_tokens):
                    targets.append((i, tok['token'], 'nonword'))

        for pos, token, token_type in targets[:6]:  # Show first 6
            next_pos = pos + 1
            if next_pos < len(jab_tokens):
                next_tok = jab_tokens[next_pos]
                print(f"\n{'-' * 80}")
                print(f"After {repr(token)} ({token_type}) at position {pos}:")
                print(f"Next token: {repr(next_tok['token'])}, Entropy: {next_tok['entropy']:.4f} bits")
                print(f"{'-' * 80}")
                print(f"{'Rank':>4} | {'Token':20} | {'Probability':>12}")
                print("-" * 50)
                for rank, item in enumerate(next_tok['top_logprobs'][:10], 1):
                    print(f"{rank:4} | {repr(item['token']):20} | {item['prob']:12.6f}")

    # Analyze Stripped condition
    print("\n\n" + "*" * 80)
    print("STRIPPED CONDITION")
    print("*" * 80)
    print(f"\nText: {stim_set['stripped']}\n")

    strip_tokens = get_detailed_logprobs(stim_set['stripped'])

    if strip_tokens:
        print("\nTokens in sequence:")
        for i, tok in enumerate(strip_tokens):
            print(f"{i:3}: {repr(tok['token']):20} (entropy: {tok['entropy']:.4f})")

        # Show some example distributions
        print("\n" + "-" * 80)
        print("Sample probability distributions in Stripped condition:")
        print("-" * 80)

        for pos in [0, len(strip_tokens) // 2, len(strip_tokens) - 1]:
            if pos < len(strip_tokens):
                tok_data = strip_tokens[pos]
                print(f"\nPosition {pos}: Token = {repr(tok_data['token'])}, Entropy = {tok_data['entropy']:.4f} bits")
                print(f"{'Rank':>4} | {'Token':20} | {'Probability':>12}")
                print("-" * 50)
                for rank, item in enumerate(tok_data['top_logprobs'][:5], 1):
                    print(f"{rank:4} | {repr(item['token']):20} | {item['prob']:12.6f}")

def analyze_systematic_patterns(stimuli_file="stimuli.json"):
    """Check what the model is actually predicting in each condition."""

    print_section_header("ANALYSIS: SYSTEMATIC PATTERNS ACROSS CONDITIONS")

    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    # Analyze first 5 sets
    for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
        print(f"\n{'*' * 80}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'*' * 80}\n")

        top_predictions = defaultdict(int)
        token_types = defaultdict(int)
        avg_entropies = []

        for stim_set in stimuli[:5]:  # First 5 sets
            text = stim_set[condition]
            tokens = get_detailed_logprobs(text)

            if not tokens:
                continue

            print(f"Set {stim_set['set_id']}: {text[:60]}...")

            for tok in tokens:
                avg_entropies.append(tok['entropy'])

                if tok['top_logprobs']:
                    # Get most likely next token
                    top_pred = tok['top_logprobs'][0]['token']
                    top_predictions[top_pred] += 1

                    # Categorize token type
                    if top_pred.strip() == '':
                        token_types['whitespace'] += 1
                    elif top_pred in ['.', ',', '!', '?', ';', ':']:
                        token_types['punctuation'] += 1
                    elif top_pred in ['</s>', '<|endoftext|>', '<eos>']:
                        token_types['EOS'] += 1
                    else:
                        token_types['word/subword'] += 1

            # Show mean entropy for this stimulus
            mean_ent = np.mean([t['entropy'] for t in tokens])
            print(f"  Mean entropy: {mean_ent:.4f} bits")
            print(f"  Tokens: {len(tokens)}")

        # Summary statistics
        print(f"\nSummary for {condition}:")
        print(f"  Average entropy across all positions: {np.mean(avg_entropies):.4f} bits")
        print(f"\n  Most common predictions (top 10):")
        for token, count in sorted(top_predictions.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {repr(token):20} : {count:3} times")

        print(f"\n  Token type distribution:")
        for ttype, count in sorted(token_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    {ttype:20} : {count:3}")

        print()

def main():
    """Run all diagnostic analyses."""

    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set!")
        return

    print("\n" + "=" * 80)
    print("MORPHOSYNTAX EXPERIMENT - DIAGNOSTIC ANALYSIS")
    print("=" * 80)
    print("\nThis analysis will investigate the surprising finding that")
    print("stripped nonsense has LOW entropy. We'll examine:")
    print("  1. Exact tokenization for each condition")
    print("  2. Actual probability distributions at specific positions")
    print("  3. What happens after function words vs nonwords")
    print("  4. Systematic patterns in model predictions")
    print("\n")

    input("Press Enter to begin analysis...")

    # 1. Detailed analysis of one stimulus set
    results = analyze_stimulus_set(set_id=1)

    print("\n" * 3)
    input("Press Enter to continue to function word analysis...")

    # 2. Function word effects
    analyze_function_word_effects(set_id=1)

    print("\n" * 3)
    input("Press Enter to continue to systematic patterns analysis...")

    # 3. Systematic patterns
    analyze_systematic_patterns()

    # Save detailed results
    print_section_header("SAVING DETAILED RESULTS")

    with open('diagnostic_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Detailed results saved to: diagnostic_results.json")
    print("\nDiagnostic analysis complete!")

if __name__ == "__main__":
    main()
