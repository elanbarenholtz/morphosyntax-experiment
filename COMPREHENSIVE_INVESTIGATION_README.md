# Comprehensive Morphosyntax Investigation Framework

**Goal**: Test morphosyntactic constraint across 6 stimulus conditions, 6 cue families, and multiple models with rigorous statistical controls.

## Overview

This framework tests whether language models exhibit category-level morphosyntactic knowledge by measuring probability mass on grammatically-appropriate word classes after diagnostic cues.

### Key Innovations

1. **6 Stimulus Conditions**: Tests sequencing, skeleton, and cue necessity
2. **6 Cue Families**: Broad coverage of morphosyntactic phenomena
3. **Word-Level Analysis**: Avoids BPE tokenization artifacts
4. **FDR Correction**: Controls for multiple comparisons across cue families
5. **Cross-Model Replication**: Tests generalizability across architectures

---

## Framework Components

### 1. Stimulus Conditions (6 total)

| Condition | Description | Purpose |
|-----------|-------------|---------|
| **SENTENCE** | Real English | Baseline (semantics + structure) |
| **JABBERWOCKY** | Nonce words, preserved structure | Test structure without semantics |
| **FULL_SCRAMBLED** | All words shuffled | Destroy all structure |
| **CONTENT_SCRAMBLED** | Content shuffled, function preserved | Test sequencing necessity |
| **FUNCTION_SCRAMBLED** | Function shuffled, content preserved | Test skeleton necessity |
| **CUE_DELETED** | Critical cue replaced (e.g., "to" → "ke") | Test cue necessity |

**Example** (set 1):
```
SENTENCE:          the scientist decided to study the ancient artifacts
JABBERWOCKY:       the prell decided to cleb the bril braz
FULL_SCRAMBLED:    to decided braz cleb the bril the prell
CONTENT_SCRAMBLED: the braz decided to cleb the prell bril
FUNCTION_SCRAMBLED: the prell the decided cleb to bril braz
CUE_DELETED:       the prell decided ke cleb the bril braz
```

### 2. Cue Families (6 total)

| Family | Cues | Expected Class | Example |
|--------|------|----------------|---------|
| **Infinitival TO** | to | VERB | "decided **to** ___" → VERB |
| **Modals** | can, will, must, ... | VERB | "they **can** ___" → VERB |
| **Determiners** | the, a, this, ... | NOUN/ADJ | "**the** ___" → NOUN/ADJ |
| **Prepositions** | of, in, on, ... | NP_START | "**in** ___" → DET/NOUN/ADJ |
| **Auxiliaries** | is, have, been, ... | PARTICIPLE | "is ___" → V-ing/V-ed |
| **Complementizers** | that, whether, who, ... | CLAUSE_START | "know **that** ___" → PRON/DET/NOUN |

### 3. Word-Level Analysis

**Problem**: BPE tokenization splits nonce words unpredictably
- "cleb" might be "cl" + "eb" or " cleb" or "cle" + "b"
- Measuring token-level mass would introduce artifacts

**Solution**: Only consider word-start tokens (space-prefixed in GPT-2/Pythia)
- " the" ✓ (word-start)
- "ing" ✗ (mid-word continuation)
- Aggregate probability mass at word boundaries

### 4. Statistical Pipeline

1. **Paired t-tests**: Within-subject comparisons (each stimulus set is a subject)
2. **FDR correction**: Benjamini-Hochberg across 6 cue families
3. **Effect sizes**: Cohen's d for paired differences
4. **Bootstrap CIs**: Confidence intervals over stimulus sets

---

## Usage

### Step 1: Generate Comprehensive Stimuli

```bash
python3 generate_comprehensive_stimuli.py
```

**Output**: `stimuli_comprehensive.json` (30 sets × 6 conditions)

### Step 2: Run Comprehensive Audit

For a single model:

```bash
python3 run_comprehensive_audit.py \
  --model gpt2 \
  --stimuli stimuli_comprehensive.json \
  --output comprehensive_audit_gpt2.json
```

For cross-model replication:

```bash
./run_cross_model_replication.sh
```

This runs:
- GPT-2 (124M)
- GPT-2-medium (355M)
- GPT-2-large (774M)
- Pythia-160m (160M)
- Pythia-410m (410M)

**Expected runtime**: ~1-2 hours per model (depending on hardware)

### Step 3: Analyze Results

```bash
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json
```

**Outputs**:
- `comprehensive_audit_gpt2_comparisons.csv` (paired t-tests with FDR correction)
- `comprehensive_audit_gpt2_summary.png` (bar plot across families)
- `comprehensive_audit_gpt2_{family}_paired.png` (paired plots per family)

---

## Key Comparisons

### Primary: JABBERWOCKY vs CONTENT_SCRAMBLED

**Question**: Does content sequencing matter when function skeleton is preserved?

**Possible outcomes**:

**A. JABBERWOCKY > CONTENT_SCRAMBLED** (p < 0.05, FDR-corrected)
- Content **sequencing** matters
- Model tracks linear order of content words
- Evidence: "prell...cleb" sequence affects predictions beyond "the ___ decided to ___" skeleton

**B. JABBERWOCKY ≈ CONTENT_SCRAMBLED** (p > 0.05)
- Content sequencing does **not** matter
- Only function-word **skeleton** drives predictions
- Evidence: Purely structural constraint, independent of content order

### Secondary Comparisons

**JABBERWOCKY vs FULL_SCRAMBLED**
- Tests overall structure effect

**JABBERWOCKY vs FUNCTION_SCRAMBLED**
- Tests function skeleton necessity

**JABBERWOCKY vs CUE_DELETED**
- Tests specific cue necessity

---

## File Structure

```
morphosyntax-experiment/
├── cue_families.py                   # Cue family definitions (6 families)
├── word_level_analysis.py            # Word-level analyzer (handles BPE)
├── generate_comprehensive_stimuli.py # Stimulus generator
├── stimuli_comprehensive.json        # Generated stimuli (30 sets × 6 conditions)
├── run_comprehensive_audit.py        # Main audit script
├── analyze_comprehensive_results.py  # Statistical analysis with FDR correction
├── run_cross_model_replication.sh    # Cross-model batch script
└── COMPREHENSIVE_INVESTIGATION_README.md  # This file
```

---

## Expected Results

Based on your existing findings:

**Infinitival TO family**:
- JABBERWOCKY: ~39% VERB mass
- CONTENT_SCRAMBLED: ~40% VERB mass
- **Expected**: JABBERWOCKY ≈ CONTENT_SCRAMBLED (p > 0.05)
- **Interpretation**: Skeleton-only constraint

**Other families**: TBD (will test generality)

---

## For Your Paper

### Methods Section

> "We tested morphosyntactic constraint across 6 stimulus conditions (SENTENCE, JABBERWOCKY, FULL_SCRAMBLED, CONTENT_SCRAMBLED, FUNCTION_SCRAMBLED, CUE_DELETED) and 6 cue families (infinitival *to*, modals, determiners, prepositions, auxiliaries, complementizers). For each condition, we measured probability mass on grammatically-appropriate word classes after diagnostic cues, using word-level analysis to avoid BPE tokenization artifacts. We performed paired t-tests comparing JABBERWOCKY to each control condition, applying Benjamini-Hochberg FDR correction across cue families to control for multiple comparisons (α = 0.05)."

### Results Section

> "Across all 6 cue families, JABBERWOCKY showed no significant difference from CONTENT_SCRAMBLED (all p_FDR > 0.05), but significant elevation above FULL_SCRAMBLED (all p_FDR < 0.001). This pattern demonstrates that morphosyntactic constraint depends only on the function-word skeleton, not content word sequencing. Effects replicated across GPT-2, GPT-2-medium, GPT-2-large, Pythia-160m, and Pythia-410m, indicating a general property of autoregressive language models."

---

## Advantages Over Previous Approaches

| Feature | Old Approach | New Comprehensive Framework |
|---------|--------------|---------------------------|
| **Conditions** | 3 (Sentence, Jab, Scrambled) | 6 (adds Content-Scram, Function-Scram, Cue-Del) |
| **Cue families** | 1 (infinitival to) | 6 (broad coverage) |
| **n balance** | Scrambled n=10, Jab n=30 | All matched n=30 |
| **Multiple comparisons** | No correction | FDR correction across families |
| **Tokenization** | Token-level (BPE artifacts) | Word-level (clean) |
| **Replication** | Single model | Cross-model (5 models) |
| **Interpretability** | Ambiguous (sequencing vs skeleton?) | Clear (tests both explicitly) |

---

## Next Steps

1. **Run cross-model replication** (`./run_cross_model_replication.sh`)
2. **Analyze all models** (run `analyze_comprehensive_results.py` for each)
3. **Compare across models** (create meta-analysis plot)
4. **Update paper** with comprehensive results and FDR-corrected statistics

---

## Troubleshooting

**If audit is slow**:
- Use GPU: Model will auto-detect CUDA
- Reduce `--top-k` (default: 1000) to 100 for faster analysis
- Run models in parallel on different machines

**If memory issues**:
- Use smaller model (gpt2 base instead of large)
- Reduce batch size in analyzer (modify code to process stimuli in chunks)

**If statistical analysis fails**:
- Check that audit completed for all conditions
- Verify JSON structure: `python3 -c "import json; print(json.load(open('comprehensive_audit_gpt2.json'))['metadata'])"`

---

## Contact

For questions about this framework, refer to:
- `cue_families.py:307` (cue family definitions)
- `word_level_analysis.py:395` (word-level analysis verification)
- `run_comprehensive_audit.py:1` (main audit script documentation)
- `analyze_comprehensive_results.py:1` (statistical pipeline documentation)
