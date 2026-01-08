# NEW TERMINAL STARTUP GUIDE

**Use this guide when you open a new terminal and want to resume work.**

---

## 📦 GitHub Repository

**All code is now on GitHub:**
```bash
# Clone from GitHub (if starting fresh)
git clone https://github.com/elanbarenholtz/medical-chart-analyzer.git morphosyntax-experiment
cd morphosyntax-experiment

# Or pull latest changes (if already cloned)
cd /Users/elanbarenholtz/morphosyntax-experiment
git pull origin main
```

**Repository contains:**
- Complete experimental framework (all Python scripts)
- All stimuli files
- Comprehensive results from 3 models (GPT-2, GPT-2-medium, Pythia-410m)
- Context ablation results (infinitival_to, determiners)
- All documentation and guides

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Navigate to project
cd /Users/elanbarenholtz/morphosyntax-experiment

# 2. Activate virtual environment
source venv/bin/activate

# 3. Check project status
./check_status.sh
```

---

## 📊 Check What's Been Completed

### Completed Experiments (Already in Repository)

**✅ Comprehensive Audit (3 models):**
- GPT-2 (124M)
- GPT-2-medium (355M)
- Pythia-410m (410M)

**✅ Context Ablation (GPT-2):**
- infinitival_to: Shows sharp k=2 threshold
- determiners: Shows gradual accumulation

**✅ Key Findings:**
- JABBERWOCKY ≈ CONTENT_SCRAMBLED (function-word skeleton sufficient)
- JABBERWOCKY >> FUNCTION_SCRAMBLED (p<0.001, d~1.3-1.6)
- Local bigram constraint for infinitival_to
- Cue-family heterogeneity (infinitival_to vs determiners)

### Check Local Status

```bash
# See comprehensive framework status
ls -lh "Comprehensive Results/"

# See ablation results
ls -lh "Ablation Results/"

# See legacy experiment results
ls -lh experiment_results_*.json

# Check if any background processes are still running
ps aux | grep python3 | grep -v grep
```

---

## 🏃 Run Comprehensive Investigation (Main Framework)

### Option 1: Quick Test (Single Model - ~40 min)
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Run GPT-2 base model
python3 run_comprehensive_audit.py --model gpt2

# Analyze results
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json

# Run context ablation
python3 run_context_ablation.py --model gpt2

# Analyze ablation
python3 analyze_context_ablation.py context_ablation_gpt2.csv
```

### Option 2: Full Replication (5 Models - ~5-10 hours)
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Run all models
./run_cross_model_replication.sh

# Then analyze each
for model in gpt2 gpt2-medium gpt2-large EleutherAI_pythia-160m EleutherAI_pythia-410m; do
    python3 analyze_comprehensive_results.py comprehensive_audit_${model}.json
    python3 analyze_context_ablation.py context_ablation_${model}.csv
done
```

---

## 📖 Key Documentation Files

```bash
# Overall project summary
cat PROJECT_SUMMARY.md

# Comprehensive framework guide
cat COMPREHENSIVE_INVESTIGATION_README.md

# Context ablation guide
cat CONTEXT_ABLATION_README.md

# This startup guide
cat NEW_TERMINAL_STARTUP.md
```

---

## 🔍 Inspect Results

### View Statistical Results
```bash
# View CSV comparisons (if exists)
cat comprehensive_audit_gpt2_comparisons.csv

# View with proper formatting
python3 -c "
import pandas as pd
df = pd.read_csv('comprehensive_audit_gpt2_comparisons.csv')
print(df.to_string())
"
```

### View Plots
```bash
# List all generated plots
ls -lh *.png

# Open a specific plot (macOS)
open comprehensive_audit_gpt2_summary.png

# Or view in terminal (if using iTerm2 with imgcat)
# imgcat comprehensive_audit_gpt2_summary.png
```

### Inspect Raw Results
```bash
# Pretty-print JSON results
python3 -c "
import json
with open('comprehensive_audit_gpt2.json') as f:
    data = json.load(f)
    print('Metadata:', data['metadata'])
    print(f\"Total results: {len(data['results'])}\")
    print('Sample result:', json.dumps(data['results'][0], indent=2))
"
```

---

## 🐛 Troubleshooting

### If Virtual Environment Missing
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
python3 -m venv venv
source venv/bin/activate
pip install transformers torch spacy pandas matplotlib seaborn scipy tqdm
python3 -m spacy download en_core_web_sm
```

### If Stimuli Missing
```bash
source venv/bin/activate
python3 generate_comprehensive_stimuli.py
```

### If Scripts Aren't Executable
```bash
chmod +x run_cross_model_replication.sh
chmod +x check_status.sh
chmod +x monitor_*.sh
```

### If Getting Import Errors
```bash
# Verify all core modules are present
python3 -c "from cue_families import CUE_FAMILIES; print('✓ cue_families.py works')"
python3 -c "from word_level_analysis import WordLevelAnalyzer; print('✓ word_level_analysis.py works')"
```

---

## 💾 Save and Sync Results

### Push New Results to GitHub
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment

# Add any new results
git add "Comprehensive Results/" "Ablation Results/" *.py *.json *.md

# Commit with descriptive message
git commit -m "Add new experimental results"

# Push to GitHub
git push origin main
```

### Copy Results to Safe Location (Optional)
```bash
# Create backup directory
mkdir -p ~/morphosyntax_results_backup

# Copy all results
cp -r "Comprehensive Results/" ~/morphosyntax_results_backup/
cp -r "Ablation Results/" ~/morphosyntax_results_backup/
cp *.json ~/morphosyntax_results_backup/

echo "Results backed up to ~/morphosyntax_results_backup/"
```

### Archive Complete Project
```bash
cd /Users/elanbarenholtz
tar -czf morphosyntax_experiment_$(date +%Y%m%d).tar.gz morphosyntax-experiment/
echo "Project archived to: morphosyntax_experiment_$(date +%Y%m%d).tar.gz"
```

---

## 🌐 Upload to Colab (If Switching to Cloud)

### Required Files to Upload
```
cue_families.py
word_level_analysis.py
run_comprehensive_audit.py
analyze_comprehensive_results.py
stimuli_comprehensive.json
```

### Steps
1. Open `Comprehensive_Morphosyntax_Audit_Colab.ipynb` in Google Colab
2. Enable GPU: Runtime → Change runtime type → GPU → Save
3. Upload the 5 files above when prompted
4. Run all cells: Runtime → Run all

---

## 📋 File Locations Quick Reference

```
PROJECT ROOT: /Users/elanbarenholtz/morphosyntax-experiment/

CORE FRAMEWORK:
├── cue_families.py                          # 6 cue family definitions
├── word_level_analysis.py                   # BPE-aware analyzer
├── run_comprehensive_audit.py               # Main audit script
├── analyze_comprehensive_results.py         # Statistical analysis
├── run_context_ablation.py                  # Ablation analysis
└── analyze_context_ablation.py              # Ablation stats

STIMULI:
├── stimuli_comprehensive.json               # 30 sets × 6 conditions
└── generate_comprehensive_stimuli.py        # Regenerate if needed

EXECUTION:
├── run_cross_model_replication.sh           # Batch script for 5 models
└── check_status.sh                          # Status checker

DOCUMENTATION:
├── PROJECT_SUMMARY.md                       # Complete overview (READ THIS FIRST)
├── COMPREHENSIVE_INVESTIGATION_README.md    # Framework guide
├── CONTEXT_ABLATION_README.md               # Ablation guide
├── NEW_TERMINAL_STARTUP.md                  # This file
└── Comprehensive_Morphosyntax_Audit_Colab.ipynb  # Colab notebook

RESULTS (Generated after running):
├── comprehensive_audit_{model}.json         # Full results per model
├── comprehensive_audit_{model}_*.csv        # Statistical tables
├── comprehensive_audit_{model}_*.png        # Plots
├── context_ablation_{model}.csv             # Ablation data
└── context_ablation_{model}_*.png           # Ablation plots

LEGACY RESULTS:
├── experiment_results_*.json                # Earlier experiments
├── entropy_analysis_*.txt                   # Entropy analyses
└── *_output.log                            # Run logs
```

---

## 🎯 Common Tasks

### Just Want to Check Status
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
./check_status.sh
```

### Resume a Paused Experiment
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# Check if any results exist
ls -lh comprehensive_audit_*.json

# Run missing models only
# (script automatically skips completed models)
./run_cross_model_replication.sh
```

### Analyze Already-Completed Results
```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate

# If you have comprehensive_audit_gpt2.json but no analysis
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json

# If you have context_ablation_gpt2.csv but no analysis
python3 analyze_context_ablation.py context_ablation_gpt2.csv
```

### Generate Only Plots from Existing Data
```bash
# Plots are automatically generated by analysis scripts
# Just re-run the analysis if you deleted plots
python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json
```

---

## ⏱️ Expected Runtimes

**Single Model (GPT-2 base):**
- Comprehensive audit: ~25 min (CPU) or ~5 min (GPU)
- Statistical analysis: ~1 min
- Context ablation: ~15 min (CPU) or ~3 min (GPU)
- Ablation analysis: ~1 min
- **Total: ~40 min (CPU) or ~10 min (GPU)**

**All 5 Models:**
- GPT-2 (124M): ~40 min
- GPT-2-medium (355M): ~60 min
- GPT-2-large (774M): ~90 min (may need more RAM)
- Pythia-160m: ~40 min
- Pythia-410m: ~60 min
- **Total: ~5-6 hours (CPU) or ~1-2 hours (GPU)**

---

## 🆘 Need Help?

### Check Logs
```bash
# If experiment failed, check the last output
tail -100 *_output.log
```

### Verify Environment
```bash
# Check Python version (should be 3.7+)
python3 --version

# Check installed packages
pip list | grep -E "transformers|torch|spacy"

# Test GPU availability
python3 -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

### Reset Everything
```bash
# Nuclear option: delete venv and reinstall
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install transformers torch spacy pandas matplotlib seaborn scipy tqdm
python3 -m spacy download en_core_web_sm

# Regenerate stimuli
python3 generate_comprehensive_stimuli.py

# Verify all scripts are present
./check_status.sh
```

---

## ✅ You're Ready!

Now you can:
- ✅ Check project status anytime with `./check_status.sh`
- ✅ Run comprehensive audit with any model
- ✅ Analyze existing results
- ✅ Upload to Colab for GPU acceleration
- ✅ Resume work from any terminal

**For complete overview, read**: `PROJECT_SUMMARY.md`

**To start running experiments now**:
```bash
source venv/bin/activate
python3 run_comprehensive_audit.py --model gpt2
```

---

**Happy analyzing!**
