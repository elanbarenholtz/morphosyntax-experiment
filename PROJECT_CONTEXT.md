# Morphosyntax Experiment - Project Context

**For AI Assistants:** Read this file first to understand the project. Do NOT read `.json` files directly - they are too large and will error.

## Research Question

**Do "meaning-depleted but grammatical" sentences (like Jabberwocky) work because of an autonomous syntactic scaffold, or because morphosyntactic form carries predictive constraint?**

We test whether function words, morphology, and word order narrow the distribution over plausible continuations in autoregressive language models, even when open-class content words are replaced with nonsense (nonce) words.

## Two Competing Hypotheses

1. **Rule-based scaffolding hypothesis**: Grammatical constraint requires a specialized autonomous structure-building mechanism separate from probabilistic prediction.

2. **Predictive-constraint hypothesis** (what we're testing): Morphosyntactic form primarily functions as probabilistic constraint that narrows plausible continuations. Sentence-like effects arise from a single expectation-based mechanism.

## Key Finding

**The function-word skeleton carries the dominant constraint signal.** Preserving morphosyntactic scaffolding (function words, word order) yields lower predictive entropy than scrambled baselines, even when content words are nonce forms. The exact sequencing of nonce content words contributes little.

---

## Experimental Conditions

| Condition | Description | Example |
|-----------|-------------|---------|
| **SENTENCE** | Natural English sentence | "The chef can prepare the meal" |
| **JABBERWOCKY** | Open-class → nonce, function words preserved | "The blicket can wug the dax" |
| **CONTENT_SCRAMBLED** | Jabberwocky with nonce words shuffled (function skeleton intact) | "The dax can blicket the wug" |
| **FULL_SCRAMBLED** | All words randomly shuffled | "wug the can blicket dax the" |
| **FUNCTION_SCRAMBLED** | Only function words shuffled | "can blicket the wug the dax" |
| **CUE_DELETED** | Cue word removed entirely | Baseline for cue-driven effects |

## Cue Families

We test specific "cue words" that should predict particular continuation classes:

| Cue Family | Cue Words | Target Class | Example |
|------------|-----------|--------------|---------|
| **infinitival_to** | "to" | VERB | "decided to **run**" |
| **determiners** | "the", "a" | NOUN/ADJ | "the **big** dog" |
| **modals** | can, will, could, would, should, must, may, might | VERB/VP-start | "can **see**" |
| **auxiliaries** | is, are, was, were, has, have, had | PARTICIPLE | "is **running**" |
| **prepositions** | in, on, at, with, by, for, from | NP-start | "in **the** box" |
| **complementizers** | that, whether, if | CLAUSE-start | "said that **she**" |

## Key Metrics

1. **Entropy**: Shannon entropy over next-token distribution. Lower = more constrained predictions.
2. **Target-class mass**: Probability mass on grammatically appropriate continuations after a cue.
3. **Surprisal**: -log₂ P(actual next token). Sanity check that models are "confident but wrong" on nonce words.

---

## Main Results Summary

### Entropy Analysis
- Jabberwocky has **lower entropy** than scrambled baselines (more constrained predictions)
- Effect sizes: GPT-2 base d=-0.56, Pythia-410m d=-0.38, GPT-2 large d=-0.13

### Slot Constraint Analysis (GPT-2, infinitival "to" → VERB)
| Condition | Mean Target Mass |
|-----------|------------------|
| Sentence | 0.563 |
| Jabberwocky | 0.279 |
| Content-scrambled | 0.262 |
| Full-scrambled | 0.071 |
| Function-scrambled | 0.074 |

**Key insight**: Jabberwocky ≈ Content-scrambled means the **function-word skeleton** drives constraint, not nonce word sequencing.

### Modal Cue Family - Special Case
Modals show SENTENCE ≈ JABBERWOCKY under broad "VPStart" target definition because the modal cue itself saturates the constraint. Under strict "VerbOnly" definition, SENTENCE > JABBERWOCKY.

| Target Definition | SENTENCE | JABBERWOCKY | Significant? |
|-------------------|----------|-------------|--------------|
| VerbOnly | 0.249 | 0.180 | Yes (p<0.001) |
| VPStart | 0.610 | 0.598 | No (p=0.47) |

---

## File Structure

### Core Scripts
- `generate_locked_stimuli.py` - Creates 180 stimuli (30 per cue family × 6 families)
- `run_locked_audit.py` - Main audit with context ablation
- `analyze_locked_results.py` - Statistical analysis with FDR correction
- `generate_locked_figures.py` - Publication-ready figures
- `modal_diagnostics.py` - Deep dive into modal cue family

### Colab Notebooks (run these in Google Colab - crashes locally)
- `Locked_Design_Morphosyntax_Audit_Colab.ipynb` - Main experiment
- `Modal_Diagnostics_DynamicCue_Colab.ipynb` - Modal analysis with dynamic cue fix

### Data Files (DO NOT READ - too large)
- `stimuli_locked.json` - 180 stimuli across 6 cue families
- `experiment_results_*.json` - Raw results from various models

### Results (in `Locked Results/` and `Modal Diagnostics/`)
- CSV summaries and PNG figures from Colab runs

---

## Critical Technical Detail: Dynamic Cue Location

### The Bug (Fixed)
Originally, code assumed cue word was always at position 2 in the sentence. This was **invalid for scrambled conditions** where words move around.

### The Fix
`find_cue_position(condition_text, cue_word)` dynamically locates the cue word in each condition string before computing the next-token distribution.

```python
def find_cue_position(condition_text, cue_word):
    words = condition_text.lower().split()
    for i, w in enumerate(words):
        if w.strip('.,!?') == cue_word.lower():
            return i, 'ok', f"Found at position {i}"
    return None, 'missing', "Cue not found"
```

### Why It Matters
Without this fix, scrambled baselines were measuring predictions at arbitrary positions, not after the actual cue. With the fix, scrambled baselines correctly measure "prediction after the cue with disrupted structure."

---

## Current Status

✅ Locked design framework complete (180 stimuli)
✅ Main Colab notebook runs successfully
✅ Modal diagnostics with dynamic cue location fix
✅ Results saved to Google Drive

### Pending
- Run modal diagnostics notebook in Colab to regenerate results with dynamic cue fix
- Verify scrambled baseline contrasts are now valid
- Update manuscript tables if results change

---

## How to Continue Work

### In Colab
1. Upload `stimuli_locked.json` when prompted
2. Run `Modal_Diagnostics_DynamicCue_Colab.ipynb`
3. Results save to Google Drive `/morphosyntax_modal_diagnostics/`

### Locally (if needed)
```bash
cd ~/morphosyntax-experiment
source venv/bin/activate
python modal_diagnostics.py --model gpt2 --stimuli stimuli_locked.json
```
Note: May crash on Mac due to memory/multiprocessing issues. Colab recommended.

---

## Repository

https://github.com/elanbarenholtz/morphosyntax-experiment

## Contact

[Author information from manuscript]
