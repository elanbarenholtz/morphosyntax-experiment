# Model Calibration Finding: Uncertainty and Model Size

## Secondary Discovery from Morphosyntax Experiment

While testing the morphosyntax hypothesis across different model sizes, we discovered an interesting pattern related to **model calibration and uncertainty awareness**.

---

## The Finding

**Larger models show lower entropy (higher confidence) on ALL conditions, including random nonword sequences where no valid predictions exist.**

### Data

| Condition | GPT-2 (124M) | GPT-2-LARGE (774M) | Reduction |
|-----------|--------------|---------------------|-----------|
| **Sentence** | 7.45 bits | 7.21 bits | -0.24 bits |
| **Jabberwocky** | 8.04 bits | 8.04 bits | -0.00 bits |
| **Stripped** | 9.07 bits | 8.53 bits | -0.54 bits |
| **Random Nonwords** | 9.27 bits | 8.70 bits | **-0.57 bits** |

### The Puzzle

For **real sentences**, lower entropy is clearly better - the model is making more accurate predictions.

But for **random nonwords** like "Ke blorp nar flump", there IS no correct next token. These sequences have no valid linguistic structure.

**Question:** What does it mean for a model to be "more confident" about inherently unpredictable sequences?

---

## Interpretation

### Two Competing Explanations

**1. Overfitting to Distributional Patterns (Overconfidence)**

Larger models may be applying learned distributional patterns more uniformly, even when linguistic cues are absent or contradictory. They've learned so many micro-patterns that they can always find *something* to match.

Result: False confidence on meaningless input.

**2. Better Noise Modeling (Actually Correct)**

Alternatively, "random" nonwords still have statistical regularities (phonotactics, character n-grams). Larger models may be better at capturing these low-level regularities.

Result: Genuinely better predictions even on nonsense.

---

## Which Interpretation is Correct?

The key question is: **Should uncertainty increase when input is nonsensical?**

### Argument for "Uncertainty = Good Response to Nonsense"

From a Bayesian perspective, a well-calibrated model should:
- Be confident when it has strong evidence
- Be uncertain when evidence is weak or contradictory

Random nonwords provide **contradictory evidence** - they have surface-level statistical patterns but no higher-level structure. A smaller model's higher entropy might reflect appropriate epistemic humility.

### Argument for "Low Entropy = Better Even on Nonsense"

Counterargument: Even "random" nonwords aren't truly random. They:
- Follow phonotactic constraints (pronounceable sequences)
- Use English orthography
- Have character-level regularities

A larger model's lower entropy might reflect genuinely better modeling of these low-level patterns.

---

## The Calibration Hypothesis

**Core claim:** Larger language models may be **less calibrated** - they apply learned patterns more uniformly regardless of input validity.

### Evidence

1. **Differential improvement by condition**
   - Sentence: -0.24 bits (small improvement)
   - Random Nonwords: -0.57 bits (large improvement)

   The model improves MORE on the hardest, least structured condition.

2. **Morphosyntax effect weakens**
   - GPT-2: -1.03 bits (d = -1.52)
   - GPT-2-LARGE: -0.49 bits (d = -0.74)

   The larger model is LESS sensitive to structural cues, suggesting it relies more on low-level statistics.

3. **Relative compression**
   - Entropy gap between conditions narrows with model size
   - Smaller model: 1.8 bit range (7.45 to 9.27)
   - Larger model: 1.5 bit range (7.21 to 8.70)

   The larger model "compresses" the uncertainty space.

---

## Implications

### For Psycholinguistics

This finding suggests that **model size affects what linguistic information is used for prediction**:

- **Smaller models:** More reliant on explicit structural cues (morphosyntax)
- **Larger models:** More reliant on distributed statistical patterns at all levels

This parallels debates about **shallow vs. deep processing** in human language comprehension.

### For AI Safety and Robustness

If larger models are indeed **overconfident on nonsense**, this has implications for:

1. **Out-of-distribution detection:** Larger models may fail to recognize anomalous inputs
2. **Calibration:** Confidence scores may not reflect true prediction accuracy
3. **Adversarial robustness:** Models may confidently predict on adversarial examples

### For Scaling Laws

Current scaling laws focus on **perplexity on valid data**. This finding suggests we should also track:

- **Calibration metrics** (e.g., expected calibration error)
- **Uncertainty on OOD data**
- **Sensitivity to structural violations**

---

## Proposed Follow-Up Experiments

### 1. Calibration Analysis

For each model and condition, compare:
- Predicted probability of actual next token
- Model's confidence (1 - entropy)

A well-calibrated model should have high correlation. Poor calibration would show high confidence but low accuracy.

### 2. Truly Random Sequences

Test on genuinely random character sequences (no phonotactic constraints):
- Random letters: "xqzp mjkw"
- Random tokens: "ŧ€£ ¥§¶"

Does the larger model still show lower entropy? This would definitively indicate overconfidence.

### 3. Gradient of Nonsense

Create a graded series from real sentences to pure noise:
1. Real sentence: "The cat sat on the mat"
2. Jabberwocky: "The blick sat on the florp"
3. Phonotactic violation: "The xqzp kst ng fhe mlpq"
4. Random characters: "Kqz xjp mfw ng kpl zlmq"

Track how entropy changes across this gradient for each model size.

### 4. Human Comparison

Collect human uncertainty judgments on the same stimuli. Do humans show:
- Increasing uncertainty from Sentence → Jabberwocky → Stripped → Random?
- Or relatively uniform uncertainty across nonsense types?

This would tell us which model size better matches human calibration.

---

## Connection to Main Finding

This calibration finding **complements** the primary morphosyntax finding:

**Primary Finding:** Morphosyntactic structure reduces entropy (d = -1.75), confirming distributional syntax hypothesis.

**Secondary Finding:** Effect magnitude is model-size dependent, suggesting different models rely on different types of distributional information.

Together, they suggest:
1. ✅ Syntax emerges from distributional learning (confirmed)
2. ✅ But the specific patterns learned depend on model capacity (new insight)
3. ⚠️ Larger models may trade structural sensitivity for low-level pattern matching (potential concern)

---

## Summary

**Key Insight:** GPT-2-LARGE shows 0.57 bits lower entropy than GPT-2 on random nonwords, despite there being no "correct" predictions for such sequences.

**Interpretation:** This likely reflects **reduced calibration** in larger models - they confidently apply distributional patterns even to nonsensical input, rather than appropriately increasing uncertainty.

**Significance:**
- Independent interesting result about scaling and calibration
- Potential concern for AI safety and robustness
- Suggests need for calibration metrics in scaling laws
- Parallels human psycholinguistic debates about processing depth

**Status:** Hypothesis requiring further testing with calibration metrics and truly random sequences.

---

**Related Files:**
- Primary results: `FINAL_CONTROLLED_RESULTS.md`
- Model comparison: `model_comparison.json`
- Statistical tests: `statistical_tests_controlled.csv`
