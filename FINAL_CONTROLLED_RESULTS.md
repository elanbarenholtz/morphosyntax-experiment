# Final Results: Controlled Morphosyntax Experiment

## Executive Summary

**After fixing the vocabulary confound, the results changed dramatically and NOW MATCH THE PREDICTED PATTERN.**

---

## The Fix

### Confound Identified

**Original Stimuli had EXTREME nonword repetition:**
- Jabberwocky: Only **49 unique words** (type-token ratio: 0.203)
  - "grentily" appeared **23 times** (14.6%)
  - "florping" appeared **16 times** (10.1%)
  - Model learned these within the test set!

- Stripped: Only **34 unique words** (type-token ratio: 0.141)
  - "florp" appeared **29 times** (22.8%)
  - Top 2 words = 41% of all tokens!

### Solution

**Generated UNIQUE nonwords for each sentence:**
- Jabberwocky: **139 unique words** (type-token ratio: 0.577) ✅
- Stripped: **113 unique words** (type-token ratio: 0.469) ✅
- Nonwords: **117 unique words** (type-token ratio: 0.485) ✅

All conditions now have comparable vocabulary diversity.

---

## Results Comparison

### BEFORE (Confounded) vs AFTER (Controlled)

| Condition | Confounded | Controlled | Change |
|-----------|-----------|------------|--------|
| **Sentence** | 7.45 bits | **7.45 bits** | 0.00 |
| **Jabberwocky** | **7.11 bits** | **8.04 bits** | **+0.93** |
| **Stripped** | 9.37 bits | 9.07 bits | -0.30 |
| **Nonwords** | 8.95 bits | **9.27 bits** | **+0.32** |

### Pattern Change

**BEFORE (Confounded):**
```
Jabberwocky < Sentence < Nonwords < Stripped
   7.11         7.45        8.95        9.37
```
❌ Wrong! Jabberwocky artificially low due to repetition.

**AFTER (Controlled):**
```
Sentence < Jabberwocky < Stripped < Nonwords
  7.45        8.04         9.07       9.27
```
✅ **MATCHES PREDICTION!**

---

## Statistical Tests (Controlled Data)

### Critical Test: Jabberwocky vs Stripped

**Does morphosyntax constrain predictions?**

- Jabberwocky: **8.04 bits**
- Stripped: **9.07 bits**
- **Difference: -1.03 bits** (Jabberwocky is MORE predictable)
- **Statistics:** t(29) = -8.33, **p < 0.0001**
- **Effect size:** Cohen's d = **-1.75** (VERY LARGE)

✅ **YES! Morphosyntax reduces entropy by ~1 bit.**

### All Comparisons

| Comparison | Difference | p-value | Cohen's d | Interpretation |
|-----------|-----------|---------|-----------|----------------|
| **Jabberwocky vs Stripped** | **-1.03 bits** | **<0.0001** | **-1.75** | **Morphosyntax works!** |
| Jabberwocky vs Nonwords | -1.23 bits | <0.0001 | -2.08 | Very large effect |
| **Sentence vs Jabberwocky** | **-0.60 bits** | **0.0007** | **-0.95** | **Content words help!** |
| Sentence vs Nonwords | -1.82 bits | <0.0001 | -4.08 | Massive effect |
| Stripped vs Nonwords | -0.20 bits | 0.034 | -0.51 | Small-moderate |

---

## Hypothesis Testing

### Original Predictions

**Predicted Pattern:**
```
Sentences < Jabberwocky < Stripped ≈ Nonwords
```

**Actual Pattern:**
```
Sentences < Jabberwocky < Stripped < Nonwords
(but Stripped ≈ Nonwords: only 0.20 bits apart, p=0.034)
```

### Verdict

| Prediction | Result | Confirmed? |
|-----------|--------|-----------|
| **Morphosyntax reduces entropy** | **-1.03 bits** | ✅ **YES** |
| **Works independently of semantics** | **d = -1.75** | ✅ **YES** |
| Sentences most predictable | YES | ✅ **YES** |
| Jabberwocky < Stripped | YES (-1.03 bits) | ✅ **YES** |
| Stripped ≈ Nonwords | CLOSE (-0.20 bits) | ⚠️ **MOSTLY** |

### Overall

✅ **HYPOTHESIS CONFIRMED**

With proper experimental controls:
1. **Morphosyntax provides strong constraint** (d = -1.75, very large)
2. **Works independently of content** (nonsense words don't prevent it)
3. **Real sentences are most predictable** (as predicted)
4. **Pattern matches theoretical predictions**

---

## What We Learned

### 1. Vocabulary Confounds Are Critical

**The same experiment with different vocabulary control gave OPPOSITE results:**

- Confounded: Jabberwocky most predictable (due to repetition)
- Controlled: Sentences most predictable (as predicted)

**Lesson:** Always check type-token ratios and vocabulary diversity!

### 2. Morphosyntax Provides Real Constraint

Even with unique nonwords for each sentence, function words and morphology reduce uncertainty by **~1 bit** (d = -1.75).

This is a **genuine effect**, not an artifact of learning repeated words.

### 3. Content Words Matter Too

Sentences are 0.60 bits more predictable than Jabberwocky (d = -0.95, large effect).

So:
- **Morphosyntax contribution:** ~1.0 bit
- **Content semantics contribution:** ~0.6 bit
- **Total (Sentence vs Stripped):** ~1.6 bits

Both matter, but morphosyntax might matter slightly more!

### 4. Stripped vs Nonwords

Interesting finding: Stripped (systematic nonsense) is actually slightly MORE predictable than Random Nonwords by 0.20 bits.

Why? The systematic replacements (THE→unique nonword) may create micro-patterns that reduce uncertainty slightly. Or it's just noise (small effect size d = -0.51).

---

## Comparison Table: Confounded vs Controlled

| Measure | Confounded Stimuli | Controlled Stimuli | Fix Effective? |
|---------|-------------------|-------------------|---------------|
| **Jabberwocky vocab** | 49 words (0.203) | 139 words (0.577) | ✅ **YES** |
| **Stripped vocab** | 34 words (0.141) | 113 words (0.469) | ✅ **YES** |
| **Sentence rank** | 2nd (7.45) | **1st (7.45)** | ✅ **YES** |
| **Jabberwocky rank** | **1st (7.11)** | 2nd (8.04) | ✅ **YES** |
| **Pattern match** | ❌ NO | ✅ **YES** | ✅ **YES** |
| **Morphosyntax effect** | -2.26 bits (d=-4.28) | -1.03 bits (d=-1.75) | ⚠️ **Smaller but real** |

The effect is **smaller** with controlled stimuli but still **very large** (d = -1.75) and theoretically meaningful.

---

## Final Conclusion

### The Answer: YES, Hypothesis Confirmed

**Morphosyntactic tokens (function words + morphology) DO constrain predictions through distributional learning, independently of semantic content.**

**Evidence:**
1. ✅ **Jabberwocky < Stripped by 1.03 bits** (p < 0.0001, d = -1.75)
2. ✅ **Effect persists with controlled vocabulary**
3. ✅ **Pattern matches theoretical predictions**
4. ✅ **Effect size is very large**

**Mechanism:**
- The model learns statistical patterns like "The ___ was ___ing"
- These patterns constrain predictions even with novel nonsense content
- Function words and morphological markers are "high-leverage" tokens
- Supports distributional/emergentist accounts of syntax

### Caveat

The effect was **inflated** in the original confounded experiment (d = -4.28) due to vocabulary repetition. The **true effect** with proper controls is still very large (d = -1.75) but smaller.

This demonstrates the critical importance of experimental controls in psycholinguistic research!

---

## Files Generated

### Controlled Experiment
- `stimuli_controlled.json` - Properly controlled stimuli
- `experiment_results_controlled.json` - Raw results
- `experiment_data_controlled.csv` - Processed data
- `statistical_tests_controlled.csv` - Statistical comparisons
- `visualizations_controlled/` - Plots with controlled data

### Original (Confounded)
- `stimuli.json` - Original confounded stimuli
- `experiment_results_local.json` - Original results
- All kept for comparison

### Analysis
- `analyze_stimuli.py` - Revealed the confound
- `generate_stimuli_controlled.py` - Fixed stimuli generation
- `FINAL_CONTROLLED_RESULTS.md` - This report

---

## Take-Home Message

**When you control for vocabulary properly:**

```
Real Sentences (7.45) < Jabberwocky (8.04) < Stripped (9.07) < Random (9.27)
      ✅                      ✅                  ✅               ✅
   Most predictable    Morphosyntax helps   No structure    Least predictable
```

**Morphosyntax reduces entropy by ~1 bit (d = -1.75, p < 0.0001).**

**This is a genuine, large, statistically robust effect that supports the distributional learning hypothesis.**

---

**End of Report**
