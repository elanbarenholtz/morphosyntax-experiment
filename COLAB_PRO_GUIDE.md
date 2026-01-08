# Google Colab Pro Setup Guide

## 📦 FILES READY FOR UPLOAD

✅ **Notebook**: `Comprehensive_Morphosyntax_Audit_Colab.ipynb`
✅ **Package**: `colab_upload_package.tar.gz` (contains all 5 required files)

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Upload Notebook to Colab

1. Go to **https://colab.research.google.com**
2. Click **File → Upload notebook**
3. Select: `Comprehensive_Morphosyntax_Audit_Colab.ipynb`
4. Wait for upload to complete

### Step 2: Enable GPU (Pro Advantage!)

1. In Colab, click **Runtime → Change runtime type**
2. Hardware accelerator: Select **GPU**
3. Click **Save**

**With Colab Pro you'll get:**
- V100 or A100 GPU (much faster than free tier's T4)
- Longer runtime (24 hours vs 12 hours)
- Higher RAM (up to 52GB vs 12GB)

### Step 3: Upload Required Files

**Option A: Upload Individual Files**

1. Click the **folder icon** in left sidebar
2. Click the **upload button** (⬆️)
3. Upload these 5 files:
   - `cue_families.py`
   - `word_level_analysis.py`
   - `run_comprehensive_audit.py`
   - `analyze_comprehensive_results.py`
   - `stimuli_comprehensive.json`

**Option B: Upload Package and Extract**

1. Upload `colab_upload_package.tar.gz`
2. Add a cell at the top and run:
```python
!tar -xzf colab_upload_package.tar.gz
!ls -lh  # Verify files extracted
```

### Step 4: Verify File Upload

The notebook has a verification cell that checks all files are present. Run it and look for:
```
✓ cue_families.py
✓ word_level_analysis.py
✓ run_comprehensive_audit.py
✓ analyze_comprehensive_results.py
✓ stimuli_comprehensive.json

✓ All required files present!
```

### Step 5: Run All Cells

1. Click **Runtime → Run all** (or press Ctrl+F9)
2. Accept any prompts about running code
3. Watch the progress bars

---

## ⏱️ EXPECTED RUNTIME (WITH PRO GPU)

**Single Model (GPT-2):**
- Dependencies install: ~2-3 minutes
- Comprehensive audit: ~5 minutes (vs ~25 min on CPU!)
- Statistical analysis: ~30 seconds
- Context ablation: ~3 minutes
- Total: **~10 minutes**

**All 5 Models (Sequential):**
- GPT-2 (124M): ~10 min
- GPT-2-medium (355M): ~12 min
- GPT-2-large (774M): ~15 min
- Pythia-160m: ~10 min
- Pythia-410m: ~12 min
- **Total: ~60 minutes** (vs ~5-10 hours on CPU!)

---

## 📥 DOWNLOAD RESULTS

After experiments complete, download these files:

**For Each Model:**
1. Right-click in file browser (left sidebar)
2. Select **Download**

**Files to download:**
```
comprehensive_audit_gpt2.json
comprehensive_audit_gpt2_comparisons.csv
comprehensive_audit_gpt2_summary.png
comprehensive_audit_gpt2_infinitival_to_paired.png
... (6 family-specific plots)

context_ablation_gpt2.csv
context_ablation_gpt2_infinitival_to_summary.csv
context_ablation_gpt2_determiners_summary.csv
context_ablation_gpt2_infinitival_to_ablation_plot.png
context_ablation_gpt2_determiners_ablation_plot.png
```

---

## 🔧 TROUBLESHOOTING

### "Runtime disconnected"
- **Cause**: Free tier timeout or network issue
- **Solution**: With Pro, you get 24h runtime. Just re-run the cells.

### "Out of memory"
- **Cause**: Model too large
- **Solution**: Pro has 52GB RAM. If still failing, use smaller model (gpt2 instead of gpt2-large)

### "GPU not available"
- **Cause**: Runtime type not set to GPU
- **Solution**: Runtime → Change runtime type → GPU → Save

### Files disappeared
- **Cause**: Colab clears files when disconnected
- **Solution**: Re-upload files or connect to Google Drive (see below)

---

## 💾 OPTIONAL: CONNECT TO GOOGLE DRIVE

To persist files across sessions:

**Add this cell at the top:**
```python
from google.colab import drive
drive.mount('/content/drive')

# Work in Drive directory
%cd /content/drive/MyDrive
!mkdir -p morphosyntax_experiment
%cd morphosyntax_experiment

# Now upload files here - they'll persist!
```

**Benefits:**
- Files survive disconnections
- Results automatically saved to Drive
- Can resume interrupted experiments

---

## 🎯 RUNNING SPECIFIC MODELS

The notebook defaults to GPT-2. To run other models:

**Find this cell:**
```python
!python run_comprehensive_audit.py \
    --model gpt2 \
    ...
```

**Change to:**
```python
# GPT-2-medium (355M)
!python run_comprehensive_audit.py --model gpt2-medium ...

# GPT-2-large (774M)
!python run_comprehensive_audit.py --model gpt2-large ...

# Pythia-160m
!python run_comprehensive_audit.py --model EleutherAI/pythia-160m ...

# Pythia-410m
!python run_comprehensive_audit.py --model EleutherAI/pythia-410m ...
```

---

## 🔥 RUNNING ALL 5 MODELS (BATCH MODE)

The notebook includes a cell for running all models sequentially:

**Find and run this cell:**
```python
models = ['gpt2', 'gpt2-medium', 'gpt2-large',
          'EleutherAI/pythia-160m', 'EleutherAI/pythia-410m']

for model in models:
    model_slug = model.replace('/', '_')
    output_file = f'comprehensive_audit_{model_slug}.json'

    print(f"Running: {model}")

    !python run_comprehensive_audit.py \
        --model {model} \
        --stimuli stimuli_comprehensive.json \
        --output {output_file}

    !python analyze_comprehensive_results.py {output_file}

    print(f"✓ {model} complete!")
```

**Runtime**: ~60 minutes with Pro GPU (vs ~5-10 hours on local CPU!)

---

## 📊 VIEW RESULTS IN COLAB

**Display statistical results:**
```python
import pandas as pd
df = pd.read_csv('comprehensive_audit_gpt2_comparisons.csv')
print(df.to_string(index=False))
```

**Display plots inline:**
```python
from IPython.display import Image, display
display(Image('comprehensive_audit_gpt2_summary.png'))
```

---

## ✅ VERIFICATION CHECKLIST

Before running:
- [ ] GPU enabled (Runtime → Change runtime type → GPU)
- [ ] All 5 files uploaded and verified
- [ ] Dependencies installed (run install cell)

After running:
- [ ] Check for errors in output
- [ ] Verify result files exist
- [ ] Download all result files
- [ ] (Optional) Save to Google Drive

---

## 🎓 PRO TIPS

1. **Use GPU**: Makes experiments 5-10x faster
2. **Connect to Drive**: Prevents file loss on disconnect
3. **Run overnight**: Pro allows 24h runtime for all 5 models
4. **Download immediately**: Don't rely on Colab to store files
5. **Monitor RAM**: Check "RAM/Disk" meter at top-right
6. **Save notebook edits**: File → Save a copy in Drive

---

## 🆘 NEED HELP?

**Check logs:**
```python
# View last 50 lines of output
!tail -50 morphosyntax_audit_output.log
```

**Test GPU:**
```python
import torch
print(f"GPU available: {torch.cuda.is_available()}")
print(f"GPU name: {torch.cuda.get_device_name(0)}")
```

**Check files:**
```python
!ls -lh *.py *.json
```

---

## 📁 FILE LOCATIONS IN COLAB

After upload, files are in:
```
/content/
├── cue_families.py
├── word_level_analysis.py
├── run_comprehensive_audit.py
├── analyze_comprehensive_results.py
├── stimuli_comprehensive.json
└── (results will be saved here)
```

If using Drive:
```
/content/drive/MyDrive/morphosyntax_experiment/
└── (all files and results)
```

---

## 🚀 READY TO GO!

1. Upload `Comprehensive_Morphosyntax_Audit_Colab.ipynb` to Colab
2. Enable GPU
3. Upload the 5 required files
4. Run all cells
5. Download results

**Total time with Pro GPU: ~10 minutes for single model, ~60 minutes for all 5!**
