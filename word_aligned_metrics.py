"""
Word-aligned metrics for morphosyntax experiment.

Maps tokenizer outputs to whitespace words using offset mapping,
then aggregates entropy and surprisal at the word level.

This is NECESSARY but does not eliminate all tokenization confounds -
we still need normalization and tokenization matching.
"""

import torch
import numpy as np
from typing import List, Dict, Tuple

def map_tokens_to_words(text: str, token_offsets: List[Tuple[int, int]]) -> List[List[int]]:
    """
    Map token indices to word indices using character offsets.

    Args:
        text: The input text string
        token_offsets: List of (start, end) character offsets for each token

    Returns:
        List of lists, where word_to_tokens[i] contains token indices for word i
    """
    # Find word boundaries (whitespace-delimited)
    words = []
    word_starts = []
    word_ends = []

    current_word_start = None
    for i, char in enumerate(text):
        if char.isspace():
            if current_word_start is not None:
                # End of word
                word_starts.append(current_word_start)
                word_ends.append(i)
                current_word_start = None
        else:
            if current_word_start is None:
                # Start of new word
                current_word_start = i

    # Handle last word if text doesn't end with whitespace
    if current_word_start is not None:
        word_starts.append(current_word_start)
        word_ends.append(len(text))

    # Map tokens to words based on overlap
    word_to_tokens = [[] for _ in range(len(word_starts))]

    for token_idx, (tok_start, tok_end) in enumerate(token_offsets):
        # Find which word(s) this token overlaps with
        for word_idx in range(len(word_starts)):
            word_start = word_starts[word_idx]
            word_end = word_ends[word_idx]

            # Check for overlap
            if tok_start < word_end and tok_end > word_start:
                word_to_tokens[word_idx].append(token_idx)
                break  # Assign to first matching word

    return word_to_tokens

def compute_word_aligned_metrics(text: str,
                                 token_entropies: List[float],
                                 token_surprisals: List[float],
                                 token_offsets: List[Tuple[int, int]]) -> Dict:
    """
    Aggregate token-level metrics to word-level.

    Args:
        text: Input text
        token_entropies: List of entropy values for each token
        token_surprisals: List of surprisal values for each token
        token_offsets: List of (start, end) character offsets for each token

    Returns:
        Dict with word-level aggregated metrics
    """
    # Map tokens to words
    word_to_tokens = map_tokens_to_words(text, token_offsets)

    # Aggregate metrics per word
    word_entropies_mean = []
    word_entropies_sum = []
    word_surprisals_mean = []
    word_surprisals_sum = []

    for token_indices in word_to_tokens:
        if token_indices:
            # Get metrics for this word's tokens
            word_ent = [token_entropies[i] for i in token_indices if i < len(token_entropies)]
            word_surp = [token_surprisals[i] for i in token_indices if i < len(token_surprisals)]

            if word_ent and word_surp:
                word_entropies_mean.append(np.mean(word_ent))
                word_entropies_sum.append(np.sum(word_ent))
                word_surprisals_mean.append(np.mean(word_surp))
                word_surprisals_sum.append(np.sum(word_surp))

    return {
        'n_words': len(word_to_tokens),
        'word_entropies_mean': word_entropies_mean,
        'word_entropies_sum': word_entropies_sum,
        'word_surprisals_mean': word_surprisals_mean,
        'word_surprisals_sum': word_surprisals_sum,
        'mean_word_entropy': np.mean(word_entropies_mean) if word_entropies_mean else 0,
        'mean_word_entropy_sum': np.mean(word_entropies_sum) if word_entropies_sum else 0,
        'mean_word_surprisal': np.mean(word_surprisals_mean) if word_surprisals_mean else 0,
        'mean_word_surprisal_sum': np.mean(word_surprisals_sum) if word_surprisals_sum else 0,
    }

def calculate_entropy_and_surprisal(logits: torch.Tensor,
                                    actual_token_id: int) -> Tuple[float, float]:
    """
    Calculate both entropy and surprisal from logits.

    Args:
        logits: Model output logits for next token prediction
        actual_token_id: The actual next token ID

    Returns:
        (entropy, surprisal) tuple
    """
    # Convert logits to probabilities
    probs = torch.softmax(logits, dim=-1)

    # Entropy: H = -Σ p(token) × log₂(p(token))
    log_probs = torch.log2(probs + 1e-10)
    entropy = -(probs * log_probs).sum().item()

    # Surprisal: -log₂(p(actual_token))
    actual_prob = probs[actual_token_id].item()
    surprisal = -np.log2(actual_prob + 1e-10)

    return entropy, surprisal

def process_text_with_word_metrics(model, tokenizer, text: str, device='cpu') -> Dict:
    """
    Process text and compute both token-level and word-level metrics.

    Args:
        model: The language model
        tokenizer: The tokenizer
        text: Input text
        device: Device to run on

    Returns:
        Dict with comprehensive metrics at both token and word levels
    """
    # Tokenize with offset mapping
    encoding = tokenizer(text, return_tensors="pt", return_offsets_mapping=True,
                        add_special_tokens=False)

    input_ids = encoding['input_ids'].to(device)
    offset_mapping = encoding['offset_mapping'][0].tolist()

    # Get model outputs
    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        logits = outputs.logits

    # Compute token-level metrics
    token_entropies = []
    token_surprisals = []

    for i in range(input_ids.shape[1] - 1):  # Exclude last position (no next token)
        next_token_logits = logits[0, i, :]
        actual_next_token = input_ids[0, i + 1].item()

        entropy, surprisal = calculate_entropy_and_surprisal(next_token_logits, actual_next_token)

        token_entropies.append(entropy)
        token_surprisals.append(surprisal)

    # Compute word-level metrics
    word_metrics = compute_word_aligned_metrics(
        text, token_entropies, token_surprisals, offset_mapping[:-1]  # Exclude last offset
    )

    return {
        # Token-level metrics (secondary)
        'n_tokens': len(token_entropies),
        'token_entropies': token_entropies,
        'token_surprisals': token_surprisals,
        'mean_token_entropy': np.mean(token_entropies) if token_entropies else 0,
        'mean_token_surprisal': np.mean(token_surprisals) if token_surprisals else 0,

        # Word-level metrics (primary)
        **word_metrics
    }

if __name__ == "__main__":
    # Test the word-aligned metrics
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print("Testing word-aligned metrics...")

    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    model = AutoModelForCausalLM.from_pretrained('gpt2')
    model.eval()

    test_text = "the teacher was explaining the concept to the students clearly."

    print(f"\nTest text: {test_text}")
    print(f"Words: {test_text.split()}")

    metrics = process_text_with_word_metrics(model, tokenizer, test_text)

    print(f"\n{'='*80}")
    print("TOKEN-LEVEL METRICS (secondary)")
    print(f"{'='*80}")
    print(f"Number of tokens: {metrics['n_tokens']}")
    print(f"Mean entropy: {metrics['mean_token_entropy']:.4f} bits")
    print(f"Mean surprisal: {metrics['mean_token_surprisal']:.4f} bits")

    print(f"\n{'='*80}")
    print("WORD-LEVEL METRICS (primary)")
    print(f"{'='*80}")
    print(f"Number of words: {metrics['n_words']}")
    print(f"Mean word entropy (avg): {metrics['mean_word_entropy']:.4f} bits")
    print(f"Mean word entropy (sum): {metrics['mean_word_entropy_sum']:.4f} bits")
    print(f"Mean word surprisal (avg): {metrics['mean_word_surprisal']:.4f} bits")
    print(f"Mean word surprisal (sum): {metrics['mean_word_surprisal_sum']:.4f} bits")

    print(f"\n{'='*80}")
    print("PER-WORD BREAKDOWN")
    print(f"{'='*80}")
    words = test_text.split()
    for i, word in enumerate(words):
        if i < len(metrics['word_entropies_mean']):
            print(f"{word:15s} | Ent(mean): {metrics['word_entropies_mean'][i]:.4f} | "
                  f"Surp(mean): {metrics['word_surprisals_mean'][i]:.4f}")
