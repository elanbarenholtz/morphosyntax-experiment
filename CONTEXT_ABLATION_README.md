# Context-Length Ablation Analysis

## Purpose

Quantify how much of each cue-family effect is driven by the immediately preceding cue word vs. the broader prefix/scaffold.

**Key Question**: Do morphosyntactic effects saturate at k=1 (cue-only), or do they increase with broader context (scaffold-dependent)?

---

## Scope (Focused)

- **Cue families**: 2 (infinitival_to, determiners)
- **Conditions**: 3 (JABBERWOCKY, FUNCTION_SCRAMBLED, FULL_SCRAMBLED)
- **Context lengths**: k ∈ {1, 2, 4, full}

**k=1**: Just the cue word ("to", "the")
**k=full**: Full prefix up to and including cue

---

## Method

For each cue occurrence at position i:

1. Full context: `words[:i+1]` (e.g., "the prell decided to")
2. Truncated context (k words): Last k words only
   - k=1: "to"
   - k=2: "decided to"
   - k=4: "the prell decided to"
   - k=full: "the prell decided to"
3. Measure target class mass (e.g., VERB mass for TO; NOUN/ADJ mass for determiners)
4. Optionally: entropy over word-start tokens

---

## Usage

### Step 1: Run Ablation

```bash
python3 run_context_ablation.py --model gpt2
```

**Output**: `context_ablation_gpt2.csv`

**Runtime**: ~10-15 minutes (faster than comprehensive audit since only 2 families)

### Step 2: Analyze Results

```bash
python3 analyze_context_ablation.py context_ablation_gpt2.csv
```

**Outputs**:
- `context_ablation_gpt2_infinitival_to_summary.csv` - Summary table
- `context_ablation_gpt2_determiners_summary.csv` - Summary table
- `context_ablation_gpt2_infinitival_to_ablation_plot.png` - Plot
- `context_ablation_gpt2_determiners_ablation_plot.png` - Plot

---

## Expected Outcomes

### Interpretation A: Cue-Only Effect

**Pattern**: Curves saturate at k=1

```
JABBERWOCKY:
  k=1:    0.40 ± 0.05
  k=2:    0.41 ± 0.05
  k=4:    0.41 ± 0.05
  k=full: 0.42 ± 0.05
```

**Interpretation**: Effect is driven almost entirely by the cue word itself. Broader scaffold adds little.

### Interpretation B: Scaffold-Dependent Effect

**Pattern**: Curves increase with k

```
JABBERWOCKY:
  k=1:    0.30 ± 0.05
  k=2:    0.35 ± 0.05
  k=4:    0.38 ± 0.05
  k=full: 0.40 ± 0.05
```

**Interpretation**: Broader scaffold matters. Model integrates information from multiple preceding words.

### Interpretation C: Function Skeleton Critical

**Pattern**: JABBERWOCKY increases with k, but FUNCTION_SCRAMBLED does not

```
JABBERWOCKY:
  k=1:    0.30 → k=full: 0.40  (Δ = +0.10)

FUNCTION_SCRAMBLED:
  k=1:    0.28 → k=full: 0.30  (Δ = +0.02)
```

**Interpretation**: Function skeleton is necessary for scaffold effect. Without it, only cue word matters.

---

## For Your Paper

### Methods Section (Context Ablation)

> "To test whether morphosyntactic constraint depends on the immediately preceding cue or broader scaffolding, we performed a context-length ablation. For each cue occurrence, we measured target class probability mass using only the last k words of the prefix, with k ∈ {1, 2, 4, full}. We tested two cue families (infinitival *to*, determiners) across three conditions (JABBERWOCKY, FUNCTION_SCRAMBLED, FULL_SCRAMBLED)."

### Results Section (Example: Cue-Only)

> "Context-length ablation revealed that morphosyntactic effects were primarily cue-driven. For infinitival *to*, VERB probability mass at k=1 (cue only) was 0.40 ± 0.05, increasing minimally to 0.42 ± 0.05 at k=full (Δ = +0.02, 5% increase). This pattern held across determiners (Δ = +0.03, 7% increase). These results suggest that the function word cue itself carries sufficient information to activate category-level predictions, with minimal contribution from broader scaffolding."

### Results Section (Example: Scaffold-Dependent)

> "Context-length ablation revealed that morphosyntactic effects depend on broader scaffolding. For infinitival *to* in JABBERWOCKY, VERB probability mass increased from 0.30 ± 0.05 at k=1 (cue only) to 0.40 ± 0.05 at k=full (Δ = +0.10, 33% increase). Critically, this scaffold effect was abolished in FUNCTION_SCRAMBLED (Δ = +0.02, 7% increase), demonstrating that broader context matters only when the function-word skeleton is intact."

---

## File Summary

| File | Purpose |
|------|---------|
| `run_context_ablation.py` | Run ablation analysis |
| `analyze_context_ablation.py` | Generate summary tables and plots |
| `context_ablation_{model}.csv` | Raw results (all measurements) |
| `context_ablation_{model}_{family}_summary.csv` | Summary table by k |
| `context_ablation_{model}_{family}_ablation_plot.png` | Plot: target_mass vs k |

---

## Implementation Details

### Reuses Existing Infrastructure

- `WordLevelAnalyzer` for word-aligned cue detection
- `compute_class_mass()` for target class measurement
- Same word-start token filtering (avoids BPE artifacts)

### Only Difference

**Standard audit**: Tokenizes full context
```python
context = "the prell decided to"
inputs = tokenizer(context, return_tensors='pt')
```

**Ablation**: Tokenizes last k words only
```python
context_full = "the prell decided to"
context_k = get_k_word_suffix(context_full, k=2)  # "decided to"
inputs = tokenizer(context_k, return_tensors='pt')
```

---

## Cross-Model Replication

To run ablation on multiple models:

```bash
# GPT-2
python3 run_context_ablation.py --model gpt2

# GPT-2-medium
python3 run_context_ablation.py --model gpt2-medium

# Pythia-410m
python3 run_context_ablation.py --model EleutherAI/pythia-410m
```

Then analyze each:
```bash
python3 analyze_context_ablation.py context_ablation_gpt2.csv
python3 analyze_context_ablation.py context_ablation_gpt2-medium.csv
python3 analyze_context_ablation.py context_ablation_EleutherAI_pythia-410m.csv
```

---

## Advantages

1. **Light**: Only 2 families × 3 conditions × 4 k-values × 30 stimuli = ~720 measurements
2. **Fast**: ~10-15 minutes per model
3. **Interpretable**: Clear distinction between cue-only vs scaffold-dependent
4. **Complementary**: Addresses reviewer questions about mechanism

---

## Troubleshooting

**If results are noisy**:
- Increase n_bootstrap in analysis (default: 10000)
- Aggregate across more sentence sets (current: 30)

**If plots show unexpected patterns**:
- Check that k=1 contexts are truly single words
- Verify that "full" contexts match main audit results

**If analysis is slow**:
- Reduce --top-k (default: 1000) to 100
- Use GPU (auto-detected)

---

## Expected Timeline

- Run ablation (GPT-2): ~10-15 minutes
- Analyze results: ~1 minute
- Interpret plots: ~5 minutes

**Total: ~20 minutes for full analysis**

---

Ready to run! This will provide clean evidence for whether your morphosyntactic effects are cue-driven or scaffold-dependent.
