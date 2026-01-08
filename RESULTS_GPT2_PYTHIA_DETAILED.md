# Morphosyntax Experiment Results: GPT-2 and Pythia-410m
## Complete Analysis with Context-Matched Tokenization

**Date**: 2025-12-16
**Stimuli**: `stimuli_context_matched.json` (30 stimulus sets)
**Tokenization**: In-context matched (100% exact match rate)
**Metrics**: Word-aligned using offset mapping

---

## Models Tested

1. **GPT-2** (124M parameters)
2. **Pythia-410m** (410M parameters)

---

# GPT-2 Results (124M params)

## 1. Summary Table - Word-Level Metrics (PRIMARY)

| Condition                    | Word-Mean Entropy     | Word-Mean Surprisal   |
|------------------------------|----------------------:|----------------------:|
| sentence                     | 7.597 ± 0.095        | 7.090 ± 0.224        |
| jabberwocky_matched          | 8.341 ± 0.133        | 14.338 ± 0.332       |
| word_list_real               | 8.574 ± 0.121        | 12.074 ± 0.235       |
| skeleton_function_words      | 8.225 ± 0.168        | 14.452 ± 0.308       |
| word_list_nonce_1tok         | 8.487 ± 0.165        | 18.026 ± 0.235       |
| word_list_nonce_2tok         | 9.242 ± 0.069        | 12.439 ± 0.135       |

## 2. Token-Level Metrics (SECONDARY)

| Condition                    | Token-Mean Entropy    | Token-Mean Surprisal  |
|------------------------------|----------------------:|----------------------:|
| sentence                     | 7.579 ± 0.098        | 7.084 ± 0.225        |
| jabberwocky_matched          | 8.340 ± 0.133        | 14.343 ± 0.330       |
| word_list_real               | 8.680 ± 0.117        | 12.027 ± 0.220       |
| skeleton_function_words      | 8.225 ± 0.168        | 14.452 ± 0.308       |
| word_list_nonce_1tok         | 8.590 ± 0.149        | 17.896 ± 0.227       |
| word_list_nonce_2tok         | 9.235 ± 0.068        | 12.624 ± 0.139       |

## 3. Signature Effect Sizes

### Effect 1: Δ(Sentence - Jabberwocky)
**Tests**: Does semantics reduce surprisal beyond syntax?

- **Sentence surprisal**: 7.090 bits
- **Jabberwocky surprisal**: 14.338 bits
- **Δ (Sem - Syn)**: **-7.248 bits**
- **Interpretation**: ✅ Semantics REDUCES surprisal

### Effect 2: Δ(Jabberwocky - Word List 2-tok)
**Tests**: Does syntactic structure reduce surprisal vs scrambled baseline?

- **Jabberwocky surprisal**: 14.338 bits
- **Word List 2-tok surprisal**: 12.439 bits
- **Δ (Syn - Scrambled)**: **+1.899 bits**
- **Interpretation**: ⚠️ Syntax INCREASES surprisal (unexpected)

## 4. Position-wise Surprisal (Word-Aligned)

| Position | Sentence    | Jabberwocky | Word List 2-tok |
|---------:|------------:|------------:|----------------:|
| 0        | 12.271      | 14.368      | 15.401          |
| 1        | 6.033       | 14.531      | 14.725          |
| 2        | 8.391       | 16.470      | 13.083          |
| 3        | 4.430       | 12.871      | 12.392          |
| 4        | 5.277       | 13.736      | 11.643          |
| 5        | 7.915       | 12.277      | 11.383          |
| 6        | 4.962       | 15.403      | 10.782          |
| 7        | 4.306       | 14.861      | 10.453          |

**Plot**: `analysis_gpt2_position_curves.png`

---

# Pythia-410m Results (410M params)

## 1. Summary Table - Word-Level Metrics (PRIMARY)

| Condition                    | Word-Mean Entropy     | Word-Mean Surprisal   |
|------------------------------|----------------------:|----------------------:|
| sentence                     | 7.329 ± 0.100        | 6.933 ± 0.248        |
| jabberwocky_matched          | 8.364 ± 0.117        | 13.359 ± 0.249       |
| word_list_real               | 8.277 ± 0.132        | 11.933 ± 0.300       |
| skeleton_function_words      | 8.179 ± 0.182        | 13.883 ± 0.345       |
| word_list_nonce_1tok         | 7.914 ± 0.147        | 17.054 ± 0.341       |
| word_list_nonce_2tok         | 9.057 ± 0.076        | 12.348 ± 0.148       |

## 2. Token-Level Metrics (SECONDARY)

| Condition                    | Token-Mean Entropy    | Token-Mean Surprisal  |
|------------------------------|----------------------:|----------------------:|
| sentence                     | 7.295 ± 0.102        | 6.919 ± 0.251        |
| jabberwocky_matched          | 8.318 ± 0.120        | 13.191 ± 0.230       |
| word_list_real               | 8.298 ± 0.122        | 11.838 ± 0.281       |
| skeleton_function_words      | 8.139 ± 0.180        | 13.876 ± 0.348       |
| word_list_nonce_1tok         | 7.993 ± 0.133        | 16.784 ± 0.363       |
| word_list_nonce_2tok         | 9.049 ± 0.076        | 12.503 ± 0.154       |

## 3. Signature Effect Sizes

### Effect 1: Δ(Sentence - Jabberwocky)
**Tests**: Does semantics reduce surprisal beyond syntax?

- **Sentence surprisal**: 6.933 bits
- **Jabberwocky surprisal**: 13.359 bits
- **Δ (Sem - Syn)**: **-6.426 bits**
- **Interpretation**: ✅ Semantics REDUCES surprisal

### Effect 2: Δ(Jabberwocky - Word List 2-tok)
**Tests**: Does syntactic structure reduce surprisal vs scrambled baseline?

- **Jabberwocky surprisal**: 13.359 bits
- **Word List 2-tok surprisal**: 12.348 bits
- **Δ (Syn - Scrambled)**: **+1.011 bits**
- **Interpretation**: ⚠️ Syntax INCREASES surprisal (unexpected)

## 4. Position-wise Surprisal (Word-Aligned)

| Position | Sentence    | Jabberwocky | Word List 2-tok |
|---------:|------------:|------------:|----------------:|
| 0        | 12.346      | 13.872      | 15.162          |
| 1        | 6.396       | 13.641      | 14.189          |
| 2        | 8.244       | 15.048      | 13.106          |
| 3        | 4.270       | 12.287      | 12.087          |
| 4        | 4.804       | 12.874      | 11.685          |
| 5        | 7.969       | 11.676      | 11.211          |
| 6        | 4.201       | 14.243      | 10.984          |
| 7        | 3.689       | 12.127      | 10.203          |

**Plot**: `analysis_pythia-410m_position_curves.png`

---

# Cross-Model Comparison

## Semantic Effect (Sentence vs Jabberwocky)

| Model        | Δ Surprisal | Interpretation           |
|--------------|------------:|--------------------------|
| GPT-2        | -7.248 bits | Semantics reduces by 7.2 |
| Pythia-410m  | -6.426 bits | Semantics reduces by 6.4 |

**Conclusion**: Both models show strong semantic effect (6-7 bits reduction)

## Syntactic Effect (Jabberwocky vs Word List)

| Model        | Δ Surprisal | Interpretation              |
|--------------|------------:|-----------------------------|
| GPT-2        | +1.899 bits | Syntax increases (!?)       |
| Pythia-410m  | +1.011 bits | Syntax increases (!?)       |

**Unexpected Finding**: Both models show HIGHER surprisal for jabberwocky than scrambled word lists. This requires further investigation.

## Position-wise Trends

### GPT-2:
- **Sentence**: Strong reduction from position 0 (12.3) to position 7 (4.3) - 8.0 bit drop
- **Jabberwocky**: Variable, stays high (14-15 range) throughout
- **Word List**: Steady decline from 15.4 to 10.5

### Pythia-410m:
- **Sentence**: Strong reduction from position 0 (12.3) to position 7 (3.7) - 8.6 bit drop
- **Jabberwocky**: Variable, fluctuates around 12-15 range
- **Word List**: Steady decline from 15.2 to 10.2

**Shared Pattern**: Both models show sentences build strong predictive constraint, while jabberwocky remains unpredictable despite syntactic structure.

---

# Key Observations

## 1. Word-Level vs Token-Level Metrics

For both models, word-level and token-level metrics are nearly identical, confirming:
- ✅ Word-aligned aggregation working correctly
- ✅ Tokenization matching is tight (100% exact match verified)
- ✅ No systematic bias from aggregation method

## 2. Semantic Constraint is Strong

Both models show 6-7 bits of reduction when adding semantics to syntactic structure:
- **GPT-2**: 7.25 bits
- **Pythia-410m**: 6.43 bits

This is robust and replicable across architectures.

## 3. Syntactic Constraint is Paradoxical

**Unexpected result**: Jabberwocky (syntax only) has HIGHER surprisal than scrambled word lists.

**Possible explanations**:
1. **Tokenization artifact**: Despite 100% match, nonce words may have different distributional properties
2. **Baseline effect**: Scrambled word lists might have accidental n-gram structure
3. **Model training**: Models may not effectively use morphosyntactic cues in absence of semantics
4. **Position effects**: The "buildup" in word lists shows declining surprisal, suggesting models adapt

**Recommendation**: Further investigation needed with:
- Scrambled jabberwocky condition (same nonces, different order)
- N-gram analysis of word lists
- Probing for syntactic representations in jabberwocky

## 4. Position-wise Buildup

Both models show clear evidence of **predictive constraint buildup** in sentences:
- Position 0-1: High surprisal (establishing context)
- Position 2-7: Progressive reduction (constraints accumulate)
- Final positions: Lowest surprisal (highly constrained)

This pattern is ABSENT in jabberwocky and word lists, suggesting:
- ✅ Semantic + syntactic integration drives buildup
- ⚠️ Syntax alone does NOT produce buildup effect

---

# Methodological Notes

## Tokenization Control

**Stimuli**: `stimuli_context_matched.json`
- ✅ 100% exact token count match (30/30 stimulus sets)
- ✅ Position-by-position distribution matching verified
- ✅ In-context tokenization (position 0 vs position i>0)

**Verification**: `verify_full_dataset_matching.py` confirmed:
- Sanity Check 1: 30/30 (100%) exact matches
- Sanity Check 2: All 10 positions have matching token distributions

## Aggregation Method

**Primary metric**: Word-mean (average of mean entropy/surprisal per word)
**Secondary metric**: Token-mean (for comparison)

**Validation**: Metrics are nearly identical, confirming robust measurement.

## Statistical Reporting

All values reported as: **Mean ± SEM** (Standard Error of the Mean)
- N = 30 stimulus sets
- SEM = SD / √N

---

# Raw Data Files

- **GPT-2 Results**: `experiment_results_gpt2_final.json`
- **Pythia Results**: `experiment_results_pythia-410m_final.json`
- **GPT-2 Plot**: `analysis_gpt2_position_curves.png`
- **Pythia Plot**: `analysis_pythia-410m_position_curves.png`

---

# Next Steps

1. **Investigate syntactic paradox**: Why does jabberwocky have higher surprisal than scrambled?
2. **Add scrambled jabberwocky**: Test if reordering nonces changes surprisal
3. **N-gram analysis**: Check if word lists have accidental structure
4. **Probing experiments**: Test if models represent syntax in jabberwocky hidden states
5. **Scale analysis**: Run larger models (gpt2-medium, gpt2-large, gpt2-xl) to see if effect changes

---

**Generated**: 2025-12-16
**Analysis Script**: `run_full_analysis.py`
**Tokenization Solution**: See `TOKENIZATION_SOLUTION_SUMMARY.md`
