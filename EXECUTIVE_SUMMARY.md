# Executive Summary: Morphosyntax Constraint Experiment

**Date:** December 7, 2025
**Model Tested:** GPT-3.5-turbo (OpenAI)
**Total Stimuli:** 120 items (30 sets × 4 conditions)
**Analysis Method:** Token-by-token entropy from logprobs

---

## Research Question

**Does morphosyntactic structure (function words and morphological markers) constrain next-token predictions in language models independently of semantic content?**

### Hypothesis
"Syntax" is an epiphenomenon of distributional learning over high-leverage tokens (function words like THE, WAS, TO and morphological markers like -ING, -ED, -LY) rather than a separate rule-governed system. If true, these morphosyntactic elements should reduce prediction uncertainty even when surrounded by nonsense content words.

### Predicted Pattern
If morphosyntax constrains predictions distributionally:
```
Entropy: Real Sentences < Jabberwocky < Stripped ≈ Random Nonwords
```

Where:
- **Jabberwocky < Stripped** = function words reduce uncertainty
- **Stripped ≈ Nonwords** = no structure without morphosyntax

---

## Experimental Design

### Four Conditions (Matched for Length)

1. **Real Sentences** - Baseline: grammatical English with real content words
   - Example: *"The teacher was explaining the concept to the students clearly"*

2. **Jabberwocky** - Function words + morphology intact, content words → phonotactically legal nonwords
   - Example: *"The blicket was florping the daxen to the wuggles grentily"*
   - Preserves: THE, WAS, TO, -ING, -LY
   - Replaces: teacher→blicket, explaining→florping, etc.

3. **Stripped** - All nonwords, no function words, no morphological markers
   - Example: *"Ke blicket nar florp ke daxen po ke wuggle grenti"*
   - Replaces: THE→ke, WAS→nar, TO→po
   - Strips: -ing, -ly suffixes

4. **Random Nonwords** - Floor condition: completely random nonwords
   - Example: *"blimp pliff flurn dwel verm zent flimp geff trel klent"*

### Measurement
- **Token-by-token entropy**: H = -Σ p(token) × log₂(p(token))
- Calculated from top-20 logprobs returned by OpenAI API
- Lower entropy = more constrained/predictable predictions
- Higher entropy = more uncertain/variable predictions

### Stimuli Generation
- 30 diverse sentence structures (simple, complex, with auxiliaries, prepositional phrases, etc.)
- Consistent nonword roots across conditions within each set
- Systematic morphological manipulation

---

## Key Results

### Observed Pattern
```
Stripped (0.63) < Sentences (1.08) ≈ Nonwords (1.01) < Jabberwocky (1.63) bits
```

**This is the OPPOSITE of what was predicted!**

### Descriptive Statistics

| Condition    | Mean Entropy | SD    | Range |
|-------------|-------------:|------:|------:|
| **Stripped**     | **0.626 bits** | 0.441 | 0.09 - 1.75 |
| **Nonwords**     | 1.014 bits | 0.695 | 0.21 - 2.78 |
| **Sentences**    | 1.084 bits | 0.981 | 0.01 - 3.21 |
| **Jabberwocky**  | **1.632 bits** | 0.902 | 0.33 - 3.25 |

### Statistical Comparisons

#### Critical Test: Jabberwocky vs Stripped
- **Difference**: +1.006 bits (Jabberwocky HIGHER)
- **Statistics**: t(29) = 5.175, p < 0.001
- **Effect size**: Cohen's d = 1.417 (very large)
- **Interpretation**: Function words + morphology INCREASED uncertainty by ~1 bit

#### Other Key Findings

1. **Sentence vs Jabberwocky**: -0.548 bits (p = 0.013, d = -0.582)
   - Real content words REDUCE entropy compared to nonsense
   - Content semantics matter more than morphosyntax

2. **Jabberwocky vs Nonwords**: +0.617 bits (p = 0.002, d = 0.767)
   - Adding morphosyntax to nonwords INCREASES entropy
   - Moderate-large effect

3. **Sentences vs Nonwords**: +0.069 bits (p = 0.757, n.s.)
   - Real sentences are NOT more predictable than random nonwords
   - Non-significant difference

4. **Stripped vs Nonwords**: -0.388 bits (p = 0.026, d = -0.667)
   - Stripped nonwords MORE predictable than random nonwords
   - Suggests model learned patterns even for nonsense tokens

---

## Interpretation

### What We Found

1. **Function words INCREASE uncertainty when paired with nonsense content**
   - Jabberwocky had the HIGHEST entropy of all conditions
   - Effect size of 1.4 is very large and highly significant

2. **The model has strong semantic expectations**
   - After seeing "the", the model expects a noun that makes semantic sense
   - After seeing "was __ing", it expects a semantically appropriate verb
   - When these expectations are violated (nonsense follows), uncertainty spikes

3. **Stripped nonsense is most predictable**
   - Without grammatical cues, the model treats it as a sequence of random tokens
   - May have learned distributional patterns even for novel nonwords
   - Lower uncertainty because there are no violated expectations

4. **Content words provide more constraint than function words**
   - Real sentences < Jabberwocky (p = 0.013)
   - Semantic content reduces entropy by ~0.5 bits
   - This is a moderate effect (d = -0.58)

### Why This Contradicts the Hypothesis

**Original hypothesis**: Morphosyntactic tokens constrain predictions independently through distributional statistics.

**What we found instead**: Morphosyntactic tokens create *semantic expectations* that INCREASE uncertainty when violated.

The model doesn't just learn "THE is followed by nouns" distributionally. It learns "THE is followed by semantically appropriate nouns in context." When function words appear with nonsense content, the mismatch creates prediction conflict.

### Analogy
Think of it like reading: "The elephant was ______"
- If the blank is "trumpeting" → low uncertainty (semantically coherent)
- If the blank is "glorping" → HIGH uncertainty (what does that even mean? Is it a verb? What kind?)

The function words create a grammatical frame that comes with semantic expectations. Violating those expectations doesn't just remove constraint—it creates *additional* uncertainty.

---

## Implications

### For Language Model Architecture

1. **Syntax and semantics are deeply integrated**
   - Models don't learn "syntax" as a separate distributional pattern
   - Grammatical structure is bound to semantic expectations
   - Cannot separate morphosyntax from meaning

2. **Function words are semantic cues, not just distributional markers**
   - "The" doesn't just predict "a noun follows"
   - It predicts "a contextually appropriate, semantically coherent noun follows"

3. **Prediction uncertainty reflects expectation violation**
   - High entropy in Jabberwocky = conflicting signals
   - Grammar says "noun should follow"
   - Semantics says "this isn't a real noun"
   - Result: uncertainty about what comes next

### For Linguistic Theory

1. **Evidence against "syntax as pure distribution"**
   - If syntax were just statistical patterns over function words, Jabberwocky should be constrained
   - Instead, grammatical structure without semantic support creates maximal uncertainty

2. **Support for integrated processing**
   - Grammatical and semantic information processed together, not separately
   - Morphosyntax doesn't "work" without semantic coherence

3. **Challenges to emergentist accounts of syntax**
   - Can't explain syntax as emerging from high-frequency function word patterns alone
   - Semantic content is necessary for grammatical constraints to reduce uncertainty

---

## Methodological Strengths

1. ✅ **Matched stimuli across conditions** (same length, same nonword roots)
2. ✅ **Large sample size** (30 sets, 120 total items)
3. ✅ **Direct measurement** (token-by-token entropy from logprobs, not indirect metrics)
4. ✅ **Strong statistical power** (large effect sizes, clear significant differences)
5. ✅ **Replicable** (all code, data, and stimuli available)

---

## Limitations

1. **Single model tested** (GPT-3.5-turbo only)
   - Results may differ for other models (GPT-4, Claude, etc.)
   - Larger models might show different patterns

2. **English only**
   - Morphosyntax works differently across languages
   - Results may not generalize to morphologically rich languages

3. **Limited entropy estimate**
   - Top-20 logprobs underestimate true entropy
   - Bias should be consistent across conditions, but absolute values are lower bounds

4. **Confound: nonword familiarity**
   - Some nonwords may have been in training data (though unlikely for "blicket", "florping", etc.)
   - Could affect predictions

5. **No position-level function word analysis**
   - Didn't isolate entropy specifically after "the", "was", etc.
   - Future work could examine local constraint effects

---

## Technical Implementation

### What Was Built

1. **Stimulus Generator** (`generate_stimuli.py`)
   - Created 30 matched sets across 4 conditions
   - Systematic morphological transformation
   - Phonotactically legal nonwords

2. **Experiment Runner** (`run_experiment.py`)
   - OpenAI API integration with logprobs extraction
   - Token-by-token entropy calculation
   - Rate limiting and error handling
   - 120 API calls completed successfully

3. **Analysis Pipeline** (`analyze_results.py`)
   - Paired statistical tests (t-tests, Wilcoxon)
   - Effect size calculations (Cohen's d)
   - 4 publication-ready visualizations
   - Automated report generation

4. **Documentation**
   - Full README with setup instructions
   - Requirements file for dependencies
   - Executable shell script for full pipeline
   - Results tables and summary reports

### Files Generated
- `stimuli.json` - All 120 stimuli
- `experiment_results.json` - Raw logprobs and entropy data
- `experiment_data.csv` - Processed data table
- `statistical_tests.csv` - All comparisons
- `analysis_summary.txt` - Statistical report
- `results_tables.txt` - Formatted tables
- `visualizations/` - 4 PNG plots
- `EXECUTIVE_SUMMARY.md` - This document

**Total Cost**: ~$0.15 USD (120 API calls)

---

## Conclusions

### Primary Finding
**Function words and morphological markers do NOT constrain predictions independently of semantic content. Instead, they create semantic expectations that INCREASE uncertainty when violated.**

### Specific Conclusions

1. **Jabberwocky sentences (grammatical structure + nonsense content) produce the HIGHEST entropy**
   - 1.63 bits vs 0.63 bits for stripped nonsense (p < 0.001, d = 1.4)
   - This is a very large, highly significant effect in the opposite direction of the hypothesis

2. **Real sentences are no more predictable than random nonwords**
   - 1.08 vs 1.01 bits (p = 0.76, n.s.)
   - Suggests semantic coherence and grammatical structure offset each other in overall uncertainty

3. **Stripped nonsense (no grammar, no semantics) is most predictable**
   - Lowest entropy of all conditions
   - Model may treat it as a simple sequence without competing expectations

4. **Content words reduce entropy more than function words**
   - Sentences < Jabberwocky by 0.55 bits (p = 0.013)
   - Semantic content is more constraining than morphosyntactic structure

### Broader Impact

This experiment challenges the view that syntax emerges purely from distributional patterns over high-frequency function words. Instead, it suggests that:

- **Grammatical knowledge is semantically grounded**
- **Morphosyntactic structure creates expectations, not just constraints**
- **Language models integrate syntax and semantics inseparably**

The results are more consistent with accounts where grammatical structure and semantic content are learned together in an integrated system, rather than syntax arising separately from distributional regularities.

---

## Future Directions

1. **Test other models** (GPT-4, Claude, Llama, etc.) - do results generalize?
2. **Cross-linguistic replication** - especially morphologically rich languages
3. **Position-level analysis** - examine entropy specifically after function words
4. **Graded manipulation** - vary semantic plausibility continuously
5. **Training dynamics** - when do models learn these integrated representations?
6. **Ablation studies** - remove specific function words to test individual contributions

---

## Repository Contents

All code, data, and results available at:
`/Users/elanbarenholtz/morphosyntax-experiment/`

**To replicate:**
```bash
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
./run_full_experiment.sh
```

---

**Contact**: For questions about this experiment, see README.md for documentation.
