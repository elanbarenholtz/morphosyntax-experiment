# Morphosyntax Experiment - Complete Project Summary

**Location**: `/Users/elanbarenholtz/morphosyntax-experiment/`

**Last Updated**: 2026-01-06

---

## 📋 OVERVIEW

This project tests whether language models' morphosyntactic constraints are driven by:
- **Content-word sequencing** (lexical semantics)
- **Function-word skeleton** (syntactic structure)

**Key Finding So Far**: Function-word skeleton is sufficient for morphosyntactic constraint (JABBERWOCKY ≈ SENTENCE, but FUNCTION_SCRAMBLED fails).

---

## 🗂️ PROJECT STRUCTURE

### **1. COMPREHENSIVE INVESTIGATION FRAMEWORK**

This is the main analysis framework with 6 conditions × 6 cue families.

#### Core Scripts
```
cue_families.py                    # 6 cue family definitions (infinitival_to, modals, etc.)
word_level_analysis.py             # BPE-aware word-level analyzer
run_comprehensive_audit.py         # Main audit script (6 conditions × 6 families)
analyze_comprehensive_results.py   # Statistical analysis with FDR correction
```

#### Stimulus Files
```
stimuli_comprehensive.json         # 30 stimulus sets × 6 conditions
generate_comprehensive_stimuli.py  # Script to regenerate stimuli
```

#### Execution Scripts
```
run_cross_model_replication.sh     # Batch script for 5 models
```

#### Context Ablation (Add-on)
```
run_context_ablation.py            # Tests k ∈ {1,2,4,full} context lengths
analyze_context_ablation.py        # Ablation analysis with interpretation
```

#### Documentation
```
COMPREHENSIVE_INVESTIGATION_README.md   # Full framework documentation
CONTEXT_ABLATION_README.md              # Ablation-specific docs
Comprehensive_Morphosyntax_Audit_Colab.ipynb  # Ready-to-run Colab notebook
```

---

### **2. EARLIER EXPERIMENTS (Fibonacci/Digit Learning)**

These were earlier proof-of-concept experiments testing sequence learning.

```
fibonacci-experiment/
├── data_generation.py              # Generate Fibonacci sequences
├── train.py                        # Train on sequences
├── evaluate.py                     # Test accuracy
├── visualize.py                    # Create plots
├── experiments_digit/              # Digit-tokenization experiments
├── visualizations/                 # Generated plots
└── results/                        # Saved results
```

---

### **3. LEGACY MORPHOSYNTAX EXPERIMENTS**

Earlier versions of the morphosyntax investigation (before comprehensive framework).

```
run_experiment_local.py             # Earlier 4-condition experiment
run_full_analysis.py                # Full analysis with scrambled conditions
stimuli_controlled.json             # 4 conditions (SENTENCE, JABBERWOCKY, etc.)
stimuli_with_scrambled.json         # Extended with SCRAMBLED condition
stimuli_6conditions.json            # 6 conditions (all variants)
```

#### Specialized Analysis Scripts
```
analyze_entropy_effects.py          # Entropy analysis
morphosyntax_audit_refined.py       # Refined audit with multiple metrics
debug_medium_nan.py                 # Debugging NaN issues
```

---

## 🚀 QUICK START COMMANDS

### **Resume Comprehensive Investigation**

#### Option A: Run Single Model (Quick Test)
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# 1. Run comprehensive audit (~25 min CPU, ~5 min GPU)
python3 run_comprehensive_audit.py --model gpt2

# 2. Analyze results (~1 min)
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json

# 3. Run context ablation (~15 min)
python3 run_context_ablation.py --model gpt2

# 4. Analyze ablation (~1 min)
python3 analyze_context_ablation.py context_ablation_gpt2.csv
```

#### Option B: Full Cross-Model Replication (5 Models)
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Run all 5 models sequentially (~5-10 hours)
chmod +x run_cross_model_replication.sh
./run_cross_model_replication.sh
```

#### Option C: Google Colab (Recommended for GPU)
```bash
# Upload to Colab and run:
# Comprehensive_Morphosyntax_Audit_Colab.ipynb
```

---

## 📊 EXPECTED OUTPUT FILES

### Comprehensive Audit Outputs (Per Model)
```
comprehensive_audit_{model}.json                      # Full results (JSON)
comprehensive_audit_{model}_comparisons.csv           # Statistical tests with FDR
comprehensive_audit_{model}_summary.png               # Summary plot
comprehensive_audit_{model}_infinitival_to_paired.png # Cue-family specific plots
comprehensive_audit_{model}_modals_paired.png
comprehensive_audit_{model}_determiners_paired.png
# ... (6 total cue-family plots)
```

### Context Ablation Outputs (Per Model)
```
context_ablation_{model}.csv                          # Raw ablation results
context_ablation_{model}_infinitival_to_summary.csv   # Summary table
context_ablation_{model}_determiners_summary.csv
context_ablation_{model}_infinitival_to_ablation_plot.png  # Ablation curves
context_ablation_{model}_determiners_ablation_plot.png
```

---

## 🔬 CURRENTLY RUNNING BACKGROUND PROCESSES

As of last session, multiple experiments were running in background. Check their status:

```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# List all background jobs
jobs

# Check specific experiment outputs
tail -50 gpt2_6conditions_output.log
tail -50 pythia410m_6conditions_output.log
tail -50 pythia_160m_output.log
tail -50 morphosyntax_audit_output.log

# Check if result files exist
ls -lh experiment_results_*.json
```

### Known Background Processes (from last session)
1. **GPT-2 with 6 conditions** → `experiment_results_gpt2_6conditions.json`
2. **Pythia-410m with 6 conditions** → `experiment_results_pythia410m_6conditions.json`
3. **Pythia-160m final** → `experiment_results_pythia_160m_final.json`
4. **Morphosyntax refined audit** → `morphosyntax_audit_output.log`
5. **Multiple GPT-2 variants** (medium, large) - check logs for completion

---

## 📁 KEY RESULT FILES (If Completed)

Check if these exist to see what's been completed:

```bash
# Comprehensive framework results
ls -lh comprehensive_audit_*.json
ls -lh context_ablation_*.csv

# Legacy experiment results
ls -lh experiment_results_*.json

# Entropy analyses
ls -lh entropy_analysis_*.txt

# Output logs
ls -lh *_output.log
```

---

## 🔍 HOW TO CHECK EXPERIMENT STATUS

### Check Completion of Background Jobs
```bash
# See if processes are still running
ps aux | grep python3

# Check progress for comprehensive audit (if running)
tail -f comprehensive_audit_gpt2.json  # Will show incremental saves

# Check progress for legacy experiments
python3 -c "
import json
import sys
try:
    with open('experiment_results_gpt2_6conditions.json') as f:
        results = json.load(f)
    print(f'GPT-2 6-conditions: {len(results)}/30 completed')
except:
    print('File not found or incomplete')
"
```

### Monitor Real-Time Progress
```bash
# If monitoring scripts exist
./monitor_final_experiments.sh
./monitor_pythia_160m.sh
./monitor_scrambled_experiments.sh
```

---

## 🧪 THE 6 STIMULUS CONDITIONS

1. **SENTENCE** - Original grammatical English
   - "the scientist decided to study the ancient artifacts"

2. **JABBERWOCKY** - Content words → nonce, function words preserved
   - "the prell decided to cleb the bril braz"

3. **FULL_SCRAMBLED** - All words randomly shuffled
   - "to decided braz cleb the bril the prell"

4. **CONTENT_SCRAMBLED** - Content words shuffled, function words in place
   - "the braz decided to cleb the prell bril"

5. **FUNCTION_SCRAMBLED** - Function words shuffled, content words in place
   - "the prell the decided cleb to bril braz"

6. **CUE_DELETED** - Critical cue replaced (e.g., "to" → "ke")
   - "the prell decided ke cleb the bril braz"

---

## 🎯 THE 6 CUE FAMILIES

1. **Infinitival TO** - Expects VERB ("to study", "to examine")
2. **Modals** - Expects VERB ("can study", "will examine")
3. **Determiners** - Expects NOUN/ADJ ("the scientist", "the ancient artifacts")
4. **Prepositions** - Expects NP_START ("in the lab", "on the table")
5. **Auxiliaries** - Expects PARTICIPLE ("was studying", "has examined")
6. **Complementizers** - Expects CLAUSE_START ("that the scientist", "whether the study")

---

## 📈 KEY STATISTICAL COMPARISONS

### Primary Test (Skeleton Sufficiency)
- **JABBERWOCKY vs CONTENT_SCRAMBLED**
  - If p > 0.05 → Skeleton alone is sufficient
  - If p < 0.05 → Content sequencing also matters

### Control Tests
- **SENTENCE vs JABBERWOCKY** - Is nonce substitution harmful?
- **JABBERWOCKY vs FUNCTION_SCRAMBLED** - Is skeleton necessary?
- **JABBERWOCKY vs CUE_DELETED** - Is specific cue necessary?

### FDR Correction
- Benjamini-Hochberg correction across 6 cue families
- Protects against false positives from multiple testing

---

## 🔧 TROUBLESHOOTING

### If Stimuli Missing
```bash
# Regenerate comprehensive stimuli
python3 generate_comprehensive_stimuli.py
```

### If Dependencies Missing
```bash
# Reinstall environment
python3 -m venv venv
source venv/bin/activate
pip install transformers torch spacy pandas matplotlib seaborn scipy tqdm
python3 -m spacy download en_core_web_sm
```

### If Results Look Weird
```bash
# Check for NaN values
python3 -c "
import json
with open('comprehensive_audit_gpt2.json') as f:
    data = json.load(f)
    results = data['results']
    nan_count = sum(1 for r in results if r['target_mass'] == 'NaN' or r['target_mass'] is None)
    print(f'NaN values: {nan_count}/{len(results)}')
"
```

### If Out of Memory
```bash
# Use smaller model
python3 run_comprehensive_audit.py --model gpt2  # Instead of gpt2-large

# Or reduce batch processing in script
# (Edit run_comprehensive_audit.py, use model.cpu() if needed)
```

---

## 📝 NEXT STEPS (If Starting Fresh)

### Minimal Test Run (1 hour)
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Quick test with GPT-2 base
python3 run_comprehensive_audit.py --model gpt2 --top-k 100  # Faster with smaller top-k
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json
```

### Full Publication-Ready Analysis (1 day)
```bash
# 1. Run all 5 models
./run_cross_model_replication.sh

# 2. Analyze each model
for model in gpt2 gpt2-medium gpt2-large EleutherAI_pythia-160m EleutherAI_pythia-410m; do
    python3 analyze_comprehensive_results.py comprehensive_audit_${model}.json
    python3 run_context_ablation.py --model ${model//_//}
    python3 analyze_context_ablation.py context_ablation_${model}.csv
done

# 3. Cross-model comparison (you'll need to write this)
# Compare results across models to test scaling effects
```

---

## 📚 DOCUMENTATION FILES TO READ

1. **`COMPREHENSIVE_INVESTIGATION_README.md`** - Full framework overview
2. **`CONTEXT_ABLATION_README.md`** - Ablation analysis details
3. **`SHARE_WITH_AI.md`** - Earlier experimental documentation (Fibonacci)
4. **`EXPERIMENTAL_LOG.md`** - Fibonacci experiment log
5. **This file** (`PROJECT_SUMMARY.md`) - Overview of everything

---

## 💾 IMPORTANT: BEFORE CLOSING TERMINAL

If you have background processes running and want to preserve them:

```bash
# Check what's running
jobs -l

# Use screen or tmux to preserve sessions
screen -S morphosyntax
# ... run your commands ...
# Ctrl+A, D to detach
# screen -r morphosyntax to reattach

# Or use nohup for fire-and-forget
nohup python3 run_comprehensive_audit.py --model gpt2 > audit.log 2>&1 &
```

---

## 🎓 FOR YOUR PAPER

### Methods Section Template
> "We tested morphosyntactic constraint across 6 stimulus conditions and 6 cue families using word-level probability analysis. Stimuli were generated by transforming 30 base sentences into JABBERWOCKY (content→nonce), FUNCTION_SCRAMBLED, CONTENT_SCRAMBLED, FULL_SCRAMBLED, and CUE_DELETED conditions. For each cue occurrence (e.g., infinitival *to*), we measured probability mass on the expected word class (e.g., VERB) using only word-start tokens to avoid BPE artifacts. Paired comparisons used FDR-corrected t-tests (Benjamini-Hochberg) with bootstrapped 95% CIs (10,000 samples)."

### Results Section Template (Example)
> "GPT-2 maintained morphosyntactic constraint in JABBERWOCKY despite nonce content words. Infinitival *to* predicted VERB class with equal strength in SENTENCE and JABBERWOCKY conditions (M_SENT=0.52±0.04, M_JAB=0.51±0.05, p=0.73, d=0.02, FDR-corrected). This pattern replicated across all 6 cue families (all p>0.05 after FDR correction), indicating that the function-word skeleton alone is sufficient for morphosyntactic constraint."

---

## ✅ CHECKLIST: What You Have

- ✅ Complete investigation framework (6 conditions × 6 families)
- ✅ Word-level analysis (avoids BPE artifacts)
- ✅ Statistical pipeline (FDR correction, bootstrap CIs)
- ✅ Context ablation analysis (cue vs scaffold)
- ✅ Cross-model replication scripts (5 models)
- ✅ Google Colab notebook (GPU-ready)
- ✅ Comprehensive documentation
- ✅ Earlier Fibonacci/digit experiments (proof of concept)

---

## 📞 CONTACT / COLLABORATION

All code is self-contained and documented. If sharing with collaborators:

**Required files for minimal run:**
```
cue_families.py
word_level_analysis.py
run_comprehensive_audit.py
analyze_comprehensive_results.py
stimuli_comprehensive.json
```

**For Colab:**
```
Comprehensive_Morphosyntax_Audit_Colab.ipynb
(Upload the 5 files above when running)
```

---

**Ready to run!** Pick any of the "Quick Start Commands" above to resume work.
