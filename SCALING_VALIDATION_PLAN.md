# Entropy Effect Validation: Model Scaling Analysis

**Status**: IN PROGRESS
**Date**: 2025-12-16
**Goal**: Test if syntactic entropy effect replicates across model sizes

---

## Key Finding to Validate

From GPT-2 base and Pythia-410m, we discovered the "confident-wrong" signature:

**Syntax DOES constrain predictions (reduces entropy) without improving nonce accuracy (surprisal unchanged)**

- GPT-2 base (124M): Δ Entropy = -0.427 bits (Cohen's d = -0.557)
- Pythia-410m (410M): Δ Entropy = -0.270 bits (Cohen's d = -0.382)

---

## Research Question

**Does the syntactic entropy effect scale with model size?**

### Hypotheses:

1. **Null hypothesis**: Effect size constant across scales
   - Syntax provides fixed constraint regardless of capacity
   - Basic architectural property

2. **Scaling hypothesis**: Larger models show stronger effect
   - More parameters → richer syntactic representations
   - Better abstraction of structural patterns
   - Prediction: d should increase with size

3. **Semantic-dependency hypothesis**: Larger models show weaker effect
   - Larger models rely more on semantics
   - Syntax-only processing becomes less engaged
   - Prediction: d should decrease with size

---

## Models to Test

### Completed ✓

| Model | Params | Δ Entropy | Cohen's d | Status |
|-------|--------|-----------|-----------|--------|
| GPT-2 base | 124M | -0.427 bits | -0.557 | ✓ DONE |
| Pythia-410m | 410M | -0.270 bits | -0.382 | ✓ DONE |

### In Progress ⏳

| Model | Params | Scaling | ETA | Status |
|-------|--------|---------|-----|--------|
| GPT-2-medium | 355M | 2.9× base | ~20 min | RUNNING |
| GPT-2-large | 774M | 6.2× base | ~50 min | RUNNING |

### Potential Extensions

| Model | Params | Scaling | Notes |
|-------|--------|---------|-------|
| GPT-2-xl | 1.5B | 12× base | Very slow, only if pattern unclear |
| Pythia-1b | 1B | 2.4× pythia-410m | Alternative architecture |
| Pythia-2.8b | 2.8B | 6.8× pythia-410m | Large-scale validation |

---

## Analysis Pipeline

Once models complete, for each:

1. **Run entropy analysis**:
   ```bash
   python3 analyze_entropy_effects.py --results experiment_results_{model}_scrambled.json > entropy_analysis_{model}.txt
   ```

2. **Extract key metrics**:
   - Δ Entropy (Jabberwocky - Scrambled)
   - Cohen's d effect size
   - Confident-wrong gap difference

3. **Compare across models**:
   - Plot effect size vs model size
   - Test for linear/log relationship
   - Identify which hypothesis fits

---

## Expected Patterns

### If Null Hypothesis (constant effect):
```
Effect Size (d) vs Model Size
    |
-0.6|  ●─────●─────●─────●
    |
-0.4|
    |
-0.2|
    |___________________
    124M  355M  774M  1.5B
```

### If Scaling Hypothesis (grows with size):
```
Effect Size (d) vs Model Size
    |
-0.8|              ●────●
    |          ●
-0.6|      ●
    |  ●
-0.4|
    |___________________
    124M  355M  774M  1.5B
```

### If Semantic-Dependency (decreases with size):
```
Effect Size (d) vs Model Size
    |
-0.6|  ●
    |      ●
-0.4|          ●
    |              ●
-0.2|                  ●
    |___________________
    124M  355M  774M  1.5B
```

---

## Theoretical Implications

### Constant Effect → Architecture-level phenomenon
- Syntax emerges from basic prediction objective
- Not dependent on capacity or training
- Fundamental to autoregressive modeling

### Growing Effect → Emergent syntactic specialization
- Larger models develop dedicated syntax circuits
- Scales with representational capacity
- Supports syntax as learned abstraction

### Decreasing Effect → Semantic dominance at scale
- Larger models prioritize semantic prediction
- Syntax becomes secondary/vestigial
- Challenges syntax-first theories

---

## Current Progress

**Monitor running**: Shows real-time progress for gpt2-medium and gpt2-large

**When complete**: Will automatically run entropy analysis and generate comparison plots

**Files being generated**:
- `experiment_results_gpt2_medium_scrambled.json`
- `experiment_results_gpt2_large_scrambled.json`
- `entropy_analysis_gpt2_medium.txt`
- `entropy_analysis_gpt2_large.txt`
- `scaling_analysis_plot.png` (comparison across all models)

---

## Next Steps After Completion

1. **Immediate**: Analyze gpt2-medium and gpt2-large results
2. **Compare**: Create scaling plot showing all 4 models
3. **Decide**: Based on pattern, determine if gpt2-xl/pythia-larger needed
4. **Document**: Update ENTROPY_RESULTS_FINAL.md with scaling findings
5. **Publish**: Submit findings with complete scaling analysis

---

**Last Updated**: 2025-12-16 18:51
**Running Jobs**: 2 (gpt2-medium, gpt2-large)
**Monitor**: `./monitor_scrambled_experiments.sh` running in background
