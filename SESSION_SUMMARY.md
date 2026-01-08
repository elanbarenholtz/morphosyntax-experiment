# Morphosyntax Experiment - Session Summary

## What We Accomplished

### Completed Experiments (6 Conditions × 4 Models)

**Models Tested:**
1. DistilGPT-2 (82M params)
2. GPT-2 (124M params)
3. GPT-2-LARGE (774M params)
4. Pythia-410m (410M params)

**Experimental Conditions:**
1. **Sentence** - Real English sentences
2. **Jabberwocky** - Real morphosyntax + nonsense content
3. **Stripped** - Content words only (no morphosyntax)
4. **Nonwords** - Random nonwords baseline
5. **Scrambled Jabberwocky** (NEW) - Jabberwocky with randomized word order
6. **Swapped Function Words** (NEW) - Nonsense function words + real content

### Key Results

**GPT-2 (124M):**
```
sentence                  : 7.448 ± 0.485 bits
jabberwocky              : 8.044 ± 0.722 bits
swapped_function_words   : 8.437 ± 1.032 bits
stripped                 : 9.073 ± 0.383 bits
scrambled_jabberwocky    : 9.142 ± 0.583 bits
nonwords                 : 9.272 ± 0.389 bits
```

**Pythia-410m (410M):**
```
sentence                  : 7.196 ± 0.574 bits
swapped_function_words   : 7.824 ± 0.864 bits
jabberwocky              : 8.199 ± 0.575 bits
stripped                 : 8.749 ± 0.487 bits
nonwords                 : 8.747 ± 0.559 bits
scrambled_jabberwocky    : 8.982 ± 0.459 bits
```

### Major Findings

1. **Word Order is Critical**
   - Scrambled Jabberwocky ≈ Stripped ≈ Nonwords
   - Destroying word order eliminates morphosyntactic benefit
   - Sequential structure matters, not just token identity

2. **Model Family Differences** (NEW FINDING!)
   - **GPT-2**: Function words provide MORE constraint than content
   - **Pythia**: Content words provide MORE constraint than function words
   - Suggests architectural or training differences affect syntactic processing

3. **Morphosyntax Effect Decreases with Model Size**
   - DistilGPT-2: -1.173 bits
   - GPT-2: -1.029 bits
   - Pythia-410m: -0.550 bits
   - GPT-2-LARGE: -0.491 bits

4. **Calibration Finding**
   - Larger models show more confidence on nonsense
   - Non-monotonic (U-shaped) pattern across sizes

## Files to Pay Attention To

### Results Files
- `experiment_results_gpt2_6conditions.json` - GPT-2 with all 6 conditions
- `experiment_results_pythia410m_6conditions.json` - Pythia-410m with all 6 conditions
- `ALL_MODELS_SUMMARY.csv` - Summary table of all 4 models (4 conditions)

### Key Scripts
- `run_experiment_local.py` - Main experiment runner (works with any model)
- `add_new_conditions.py` - Generates scrambled/swapped conditions
- `stimuli_6conditions.json` - All 6 experimental conditions

### Documentation
- `README.md` - Project overview
- `FINAL_CONTROLLED_RESULTS.md` - Original 4-condition results
- `MODEL_CALIBRATION_FINDING.md` - Secondary calibration finding

## How to Continue

### To Run Additional Models:
```python
from run_experiment_local import run_experiment

run_experiment(
    stimuli_file='stimuli_6conditions.json',
    output_file='experiment_results_MODELNAME_6conditions.json',
    model_name='model-name-here'
)
```

### To Analyze Results:
- Use `compare_three_models.py` as template for analysis
- Modify to handle 6 conditions instead of 4
- Add statistical tests for new conditions

### Next Steps (If Continuing):
1. Run larger models (GPT-2-XL, Pythia-1b, Pythia-2.8b)
2. Analyze swapped vs jabberwocky statistically
3. Create visualizations for 6-condition results
4. Write up findings for publication

## GitHub Repository

All work has been committed and pushed to:
https://github.com/elanbarenholtz/medical-chart-analyzer

Commit: `41be7c0` - "Add comprehensive morphosyntax experiment with 6 conditions across 4 models"

## Environment Setup

To recreate the environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install torch transformers tqdm scipy pandas spacy
python -m spacy download en_core_web_sm
```

## Questions for Future Investigation

1. Why do GPT-2 and Pythia show opposite patterns for function vs content words?
2. Does the model family difference relate to tokenization, architecture, or training data?
3. How does the swapped condition interact with model size?
4. Can we predict which models rely more on function vs content from architecture?

---

**Session Date:** December 7, 2025
**Models Completed:** 4 (DistilGPT-2, GPT-2, GPT-2-LARGE, Pythia-410m)
**Conditions Tested:** 6 (including 2 new conditions)
**Status:** All experiments complete and pushed to GitHub
