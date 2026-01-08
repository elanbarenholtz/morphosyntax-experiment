"""
Main experiment script for morphosyntax constraint testing.
Uses OpenAI API to collect logprobs and calculate entropy.
"""

import openai
import numpy as np
import json
import os
from scipy.stats import entropy as scipy_entropy
import time
from pathlib import Path

# Try to load from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use environment variable

# Configure OpenAI API
openai.api_key = os.environ.get("OPENAI_API_KEY")

def calculate_entropy(logprobs_list):
    """
    Calculate Shannon entropy from a list of logprobs.
    H = -Σ p(token) × log₂(p(token))
    """
    # Convert logprobs to probabilities
    probs = [np.exp(lp) for lp in logprobs_list]

    # Normalize (should already be normalized, but ensure)
    total = sum(probs)
    if total > 0:
        probs = [p / total for p in probs]

    # Calculate entropy in bits
    entropy = -sum(p * np.log2(p) if p > 0 else 0 for p in probs)
    return entropy

def get_sequence_logprobs(text, model="gpt-3.5-turbo"):
    """
    Get logprobs for each token in the text using OpenAI chat completions.

    Returns:
        dict with token_entropies, top1_probs, tokens, etc.
    """
    try:
        # Use chat completions with logprobs
        # We send the text as a user message and set max_tokens=1 to just get input logprobs
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": text}],
            max_tokens=1,  # We only care about the prompt tokens
            logprobs=True,
            top_logprobs=20  # Get top 20 token probabilities
        )

        # Extract logprobs from the response
        # In the current API, logprobs are in response.choices[0].logprobs.content
        if not response.choices[0].logprobs or not response.choices[0].logprobs.content:
            print(f"Warning: No logprobs returned for text: {text[:50]}...")
            return None

        content_logprobs = response.choices[0].logprobs.content

        token_entropies = []
        top1_probs = []
        top1_tokens = []
        tokens = []

        # Process each token position
        for token_data in content_logprobs:
            # Get the token
            token = token_data.token
            tokens.append(token)

            # Get top logprobs for this position
            top_logprobs = token_data.top_logprobs

            if top_logprobs:
                # Extract logprob values
                logprob_values = [item.logprob for item in top_logprobs]

                # Calculate entropy
                token_entropy = calculate_entropy(logprob_values)
                token_entropies.append(token_entropy)

                # Get top-1 probability
                top1_prob = np.exp(logprob_values[0])
                top1_probs.append(top1_prob)
                top1_tokens.append(top_logprobs[0].token)

        return {
            'tokens': tokens,
            'token_entropies': token_entropies,
            'mean_entropy': np.mean(token_entropies) if token_entropies else 0,
            'top1_probs': top1_probs,
            'mean_top1': np.mean(top1_probs) if top1_probs else 0,
            'num_tokens': len(tokens)
        }

    except Exception as e:
        print(f"Error processing text '{text[:50]}...': {e}")
        return None

def run_experiment(stimuli_file="stimuli.json", output_file="experiment_results.json", model="gpt-3.5-turbo"):
    """
    Run the full experiment on all stimuli.
    """
    # Load stimuli
    with open(stimuli_file, 'r') as f:
        stimuli = json.load(f)

    print(f"Loaded {len(stimuli)} stimulus sets")
    print(f"Using model: {model}\n")

    # Results storage
    results = []

    # Process each stimulus set
    for idx, stim_set in enumerate(stimuli):
        print(f"Processing stimulus set {stim_set['set_id']}/30...")

        set_results = {
            'set_id': stim_set['set_id'],
            'conditions': {}
        }

        # Process each condition
        for condition in ['sentence', 'jabberwocky', 'stripped', 'nonwords']:
            text = stim_set[condition]

            print(f"  Condition: {condition:15s} - '{text[:50]}...'")

            # Get logprobs
            logprob_data = get_sequence_logprobs(text, model=model)

            if logprob_data:
                set_results['conditions'][condition] = {
                    'text': text,
                    'tokens': logprob_data['tokens'],
                    'token_entropies': logprob_data['token_entropies'],
                    'mean_entropy': logprob_data['mean_entropy'],
                    'top1_probs': logprob_data['top1_probs'],
                    'mean_top1': logprob_data['mean_top1'],
                    'num_tokens': logprob_data['num_tokens']
                }
                print(f"    → Mean entropy: {logprob_data['mean_entropy']:.3f} bits")
            else:
                print(f"    → Failed to get logprobs")

            # Rate limiting
            time.sleep(0.5)

        results.append(set_results)

        # Save intermediate results every 5 sets
        if (idx + 1) % 5 == 0:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"  Saved intermediate results\n")

    # Save final results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nExperiment complete! Results saved to {output_file}")
    return results

if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        exit(1)

    # Run experiment
    results = run_experiment(
        stimuli_file="stimuli.json",
        output_file="experiment_results.json",
        model="gpt-3.5-turbo"
    )

    print("\nSummary statistics:")
    print("-" * 50)

    # Calculate mean entropy across all sets for each condition
    condition_entropies = {'sentence': [], 'jabberwocky': [], 'stripped': [], 'nonwords': []}

    for result in results:
        for condition in condition_entropies.keys():
            if condition in result['conditions']:
                mean_ent = result['conditions'][condition]['mean_entropy']
                condition_entropies[condition].append(mean_ent)

    for condition, entropies in condition_entropies.items():
        if entropies:
            mean = np.mean(entropies)
            std = np.std(entropies)
            print(f"{condition:15s}: {mean:.3f} ± {std:.3f} bits")
