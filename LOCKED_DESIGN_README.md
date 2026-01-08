# Locked Design Morphosyntax Audit Framework

This document describes the refactored experiment framework with guaranteed cue-family coverage, explicit scramble conditions, and integrated context ablation.

## Key Improvements Over Previous Framework

| Issue | Previous | New (Locked Design) |
|-------|----------|---------------------|
| Cue coverage | Variable n per family | Exactly 30 stimuli per family |
| Templates | Single template for all | Dedicated templates per family |
| Scramble definitions | Implicit | Explicit with sanity checks |
| Context ablation | Separate afterthought | Integrated into main pipeline |
| Target classes | Only VERB (for "to") | 6 families with specific targets |

## Cue Families and Target Classes

| Family | Cue | Template | Target Class |
|--------|-----|----------|--------------|
| infinitival_to | "to" | "The [N] [V-past] **to** [V] the [Adj] [N]" | VERB |
| modals | can/will/... | "The [N] **can** [V] the [Adj] [N]" | VERB |
| determiners | "a" | "The [N] [V-past] and saw **a** [Adj] [N]" | NOUN/ADJ |
| prepositions | with/in/at/... | "The [N] [V-past] **with** the [Adj] [N]" | NP_START |
| auxiliaries | is/was/... | "The [N] **was** [V-ing] the [Adj] [N]" | PARTICIPLE |
| complementizers | "that" | "The [N] [V-past] **that** the [N] [V-past]" | CLAUSE_START |

## The 6 Conditions

1. **SENTENCE** - Original grammatical English
2. **JABBERWOCKY** - Content words → nonce; function words + order preserved
3. **FULL_SCRAMBLED** - Random permutation of ALL tokens
4. **CONTENT_SCRAMBLED** - Content words shuffled among content slots only
5. **FUNCTION_SCRAMBLED** - Function words shuffled among function slots only
6. **CUE_DELETED** - Critical cue replaced with "ke"

## Files

### Core Scripts
```
generate_locked_stimuli.py    # Generate 180 stimuli (30 × 6 families)
run_locked_audit.py           # Main audit with context ablation
analyze_locked_results.py     # Statistical analysis with FDR
generate_locked_figures.py    # Publication-ready figures
run_locked_pipeline.sh        # Convenience script for full pipeline
```

### Output Files
```
stimuli_locked.json           # 180 stimuli with all conditions
stimuli_locked_sanity_check.log  # Verification log
locked_audit_{model}.json     # Raw results
locked_audit_{model}_summary.csv
locked_audit_{model}_contrasts.csv
locked_audit_{model}_ablation.csv
figures/                      # PNG figures
```

## Quick Start

### Run Full Pipeline
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Run with GPT-2 (default)
./run_locked_pipeline.sh

# Run with other models
./run_locked_pipeline.sh gpt2-medium
./run_locked_pipeline.sh EleutherAI/pythia-410m
```

### Run Steps Individually
```bash
# 1. Generate stimuli
python3 generate_locked_stimuli.py

# 2. Run audit with context ablation (k ∈ {1,2,4,8,full})
python3 run_locked_audit.py --model gpt2

# 3. Analyze results
python3 analyze_locked_results.py locked_audit_gpt2.json

# 4. Generate figures
python3 generate_locked_figures.py locked_audit_gpt2.json --output-dir figures
```

## Context Ablation

The audit computes target-class mass for each context length k ∈ {1, 2, 4, 8, full}:

- **k=1**: Only the cue word itself ("to")
- **k=2**: Cue + one preceding word ("decided to")
- **k=4**: Last 4 words up to cue ("the scientist decided to")
- **k=full**: Full context up to cue

This allows statements like:
> "Constraint emerges rapidly (k≈2-4 words) for intact scaffolds, and does not recover under full scrambling."

## Statistical Analysis

### Key Contrasts (all FDR-corrected)
1. **JABBERWOCKY vs FULL_SCRAMBLED** - Does ANY structure help?
2. **JABBERWOCKY vs FUNCTION_SCRAMBLED** - Is skeleton NECESSARY?
3. **JABBERWOCKY vs CONTENT_SCRAMBLED** - Does content ORDER matter?
4. **SENTENCE vs JABBERWOCKY** - Does nonce substitution hurt?

### Interpretation
- If JAB ≈ CONTENT_SCRAMBLED (p > 0.05): Content order doesn't matter
- If JAB > FUNCTION_SCRAMBLED (p < 0.05): Skeleton is necessary
- If JAB > FULL_SCRAMBLED (p < 0.05): Structure helps
- Together: "Function-word skeleton is necessary and sufficient"

## Figures Generated

1. **figure1_slot_constraint.png** - Primary figure
   - y: target-class mass
   - x: condition
   - panels: cue family
   - bars: models (if multiple)

2. **figure2_paired_differences.png** - Paired difference distributions
   - JAB − FULL_SCRAMBLED
   - JAB − CONTENT_SCRAMBLED
   - JAB − FUNCTION_SCRAMBLED

3. **figure3_context_ablation.png** - Context length curves
   - y: target-class mass
   - x: k (context length)
   - lines: conditions
   - panels: cue family

## Sanity Checks

The generator produces `stimuli_locked_sanity_check.log` with:
- Count verification (n=30 per family)
- Cue occurrence verification (exactly 1 per sentence)
- 3 examples per condition per family
- Scramble verification (all scrambles differ from jabberwocky)

## Expected Results Pattern

Based on the skeleton-sufficiency hypothesis:

| Contrast | Expected | Meaning |
|----------|----------|---------|
| JAB vs FULL_S | JAB >> FULL_S | Structure matters |
| JAB vs FUNC_S | JAB >> FUNC_S | Skeleton necessary |
| JAB vs CONT_S | JAB ≈ CONT_S | Content order doesn't matter |
| SENT vs JAB | SENT ≈ JAB | Nonce substitution harmless |

## Citation

If using this framework, please cite:
> "Morphosyntactic constraint in language models: Function-word skeleton is necessary and sufficient."
