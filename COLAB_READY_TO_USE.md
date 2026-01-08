# Ready-to-Use Colab Code (Copy-Paste into Colab)

**Just copy each cell below into Google Colab and run!**
**Google Drive mounting is automatic - you'll only need to authorize once.**

---

## 📋 CELL 1: Mount Google Drive & Setup

```python
# ============================================================================
# CELL 1: Mount Google Drive & Setup Environment
# ============================================================================

from google.colab import drive
import os
import sys

print("=" * 80)
print("STEP 1: MOUNTING GOOGLE DRIVE")
print("=" * 80)
print()

# Mount Google Drive (will prompt for authorization on first run)
drive.mount('/content/drive')

# Create project directory in Google Drive
PROJECT_DIR = '/content/drive/MyDrive/morphosyntax_experiment'
os.makedirs(PROJECT_DIR, exist_ok=True)

# Change to project directory
os.chdir(PROJECT_DIR)

print(f"✓ Google Drive mounted")
print(f"✓ Working directory: {PROJECT_DIR}")
print(f"✓ All results will automatically save to Google Drive")
print()
print("=" * 80)
print("STEP 2: INSTALLING DEPENDENCIES")
print("=" * 80)
print()

# Install required packages
!pip install -q transformers torch pandas matplotlib seaborn scipy tqdm

print("✓ Dependencies installed")
print()
```

**What happens:**
- First time: You'll see a link → click it → sign in → copy code → paste back
- After that: Google Drive auto-mounts every session
- All files save to `Google Drive/morphosyntax_experiment/` automatically

---

## 📋 CELL 2: Upload Required Files (One-Time Only)

```python
# ============================================================================
# CELL 2: Upload Files (only needed first time)
# ============================================================================

import os
from google.colab import files

# Check if files already exist in Google Drive
required_files = [
    'cue_families.py',
    'word_level_analysis.py',
    'run_comprehensive_audit.py',
    'analyze_comprehensive_results.py',
    'stimuli_comprehensive.json',
    'run_context_ablation.py',
    'analyze_context_ablation.py'
]

print("=" * 80)
print("CHECKING FOR REQUIRED FILES IN GOOGLE DRIVE")
print("=" * 80)
print()

missing_files = []
for f in required_files:
    if os.path.exists(f):
        size_kb = os.path.getsize(f) / 1024
        print(f"✓ {f:40s} ({size_kb:>6.1f} KB)")
    else:
        print(f"✗ {f:40s} MISSING")
        missing_files.append(f)

print()

if missing_files:
    print(f"⚠️  Missing {len(missing_files)} files")
    print()
    print("Please upload the following files:")
    for f in missing_files:
        print(f"  - {f}")
    print()
    print("Click the button below to upload files...")
    print("(Files will be saved to Google Drive and persist across sessions)")
    print()

    uploaded = files.upload()

    print()
    print(f"✓ Uploaded {len(uploaded)} files to Google Drive")
    print("✓ These files will persist - you won't need to upload again!")
else:
    print("✓ All required files present in Google Drive")
    print("✓ Ready to run experiments!")

print()
```

**Note:** Files upload to Google Drive, so you only do this ONCE!

---

## 📋 CELL 3: Run Comprehensive Audit

```python
# ============================================================================
# CELL 3: Run Comprehensive Audit
# ============================================================================

import subprocess
import time

# Configuration
MODEL = 'gpt2'  # Options: gpt2, gpt2-medium, gpt2-large, EleutherAI/pythia-410m

print("=" * 80)
print(f"RUNNING COMPREHENSIVE AUDIT: {MODEL}")
print("=" * 80)
print()
print(f"Started: {time.strftime('%H:%M:%S')}")
print(f"Expected runtime: ~5-10 min (with GPU)")
print()
print("Progress:")
print()

# Run comprehensive audit
result = subprocess.run(
    ['python', 'run_comprehensive_audit.py', '--model', MODEL],
    capture_output=False,  # Show output in real-time
    text=True
)

print()
if result.returncode == 0:
    model_slug = MODEL.replace('/', '_')
    result_file = f'comprehensive_audit_{model_slug}.json'

    print("✓ Experiment complete!")
    print(f"✓ Results saved to Google Drive: {result_file}")
    print()
    print(f"Finished: {time.strftime('%H:%M:%S')}")
else:
    print("✗ Experiment failed - check error messages above")

print()
```

---

## 📋 CELL 4: Analyze Results

```python
# ============================================================================
# CELL 4: Statistical Analysis
# ============================================================================

import subprocess
import glob

model_slug = MODEL.replace('/', '_')
result_file = f'comprehensive_audit_{model_slug}.json'

print("=" * 80)
print("STATISTICAL ANALYSIS")
print("=" * 80)
print()

if os.path.exists(result_file):
    print(f"Analyzing: {result_file}")
    print()

    result = subprocess.run(
        ['python', 'analyze_comprehensive_results.py', result_file],
        capture_output=False,
        text=True
    )

    print()
    if result.returncode == 0:
        print("✓ Analysis complete!")
        print()
        print("Generated files (saved to Google Drive):")

        # List generated files
        for pattern in [f'*{model_slug}*.csv', f'*{model_slug}*.png']:
            for f in sorted(glob.glob(pattern)):
                size_kb = os.path.getsize(f) / 1024
                print(f"  ✓ {f:50s} ({size_kb:>6.1f} KB)")
    else:
        print("✗ Analysis failed")
else:
    print(f"✗ Result file not found: {result_file}")
    print("Run CELL 3 first to generate results")

print()
```

---

## 📋 CELL 5: Run Context Ablation (Optional)

```python
# ============================================================================
# CELL 5: Context-Length Ablation
# ============================================================================

import subprocess
import time

print("=" * 80)
print(f"RUNNING CONTEXT ABLATION: {MODEL}")
print("=" * 80)
print()
print(f"Started: {time.strftime('%H:%M:%S')}")
print(f"Expected runtime: ~15-20 min (with GPU)")
print()
print("This tests how much context is needed for morphosyntactic constraints")
print("Context lengths: k=1, k=2, k=4, k=full")
print()

# Run context ablation
result = subprocess.run(
    ['python', 'run_context_ablation.py',
     '--model', MODEL,
     '--stimuli', 'stimuli_comprehensive.json',
     '--output', f'context_ablation_{MODEL}.csv'],
    capture_output=False,
    text=True
)

print()
if result.returncode == 0:
    print("✓ Ablation complete!")
    print(f"✓ Results saved to Google Drive: context_ablation_{MODEL}.csv")
    print()
    print(f"Finished: {time.strftime('%H:%M:%S')}")
else:
    print("✗ Ablation failed - check error messages above")

print()
```

---

## 📋 CELL 6: Analyze Ablation Results

```python
# ============================================================================
# CELL 6: Analyze Context Ablation
# ============================================================================

import subprocess

ablation_file = f'context_ablation_{MODEL}.csv'

print("=" * 80)
print("CONTEXT ABLATION ANALYSIS")
print("=" * 80)
print()

if os.path.exists(ablation_file):
    print(f"Analyzing: {ablation_file}")
    print()

    result = subprocess.run(
        ['python', 'analyze_context_ablation.py', ablation_file],
        capture_output=False,
        text=True
    )

    print()
    if result.returncode == 0:
        print("✓ Ablation analysis complete!")
        print("✓ Plots saved to Google Drive")
    else:
        print("✗ Analysis failed")
else:
    print(f"✗ Ablation file not found: {ablation_file}")
    print("Run CELL 5 first to generate ablation results")

print()
```

---

## 📋 CELL 7: View Results Summary

```python
# ============================================================================
# CELL 7: Results Summary
# ============================================================================

import os
import glob
from datetime import datetime

print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print()
print(f"Google Drive location: {os.getcwd()}")
print()

# List all generated files
file_categories = {
    'Comprehensive Audits': 'comprehensive_audit_*.json',
    'Statistical Analyses': 'comprehensive_audit_*_comparisons.csv',
    'Summary Plots': 'comprehensive_audit_*_summary.png',
    'Paired Plots': 'comprehensive_audit_*_paired.png',
    'Context Ablations': 'context_ablation_*.csv',
    'Ablation Plots': 'context_ablation_*.png',
}

for category, pattern in file_categories.items():
    files = sorted(glob.glob(pattern))
    if files:
        print(f"{category}:")
        for f in files:
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            size_kb = os.path.getsize(f) / 1024
            print(f"  ✓ {f:50s} {size_kb:>8.1f} KB  {mtime.strftime('%Y-%m-%d %H:%M')}")
        print()

# Check if any experiments are complete
json_files = glob.glob('comprehensive_audit_*.json')
if json_files:
    print(f"✓ {len(json_files)} model(s) completed")
else:
    print("No experiments completed yet - run CELL 3 first")

print()
print("=" * 80)
print("All files are safely stored in Google Drive!")
print("They will persist even if Colab disconnects.")
print("=" * 80)
```

---

## 📋 CELL 8: Download Results to Local Machine (Optional)

```python
# ============================================================================
# CELL 8: Download Results to Local Computer
# ============================================================================

from google.colab import files
import glob

print("=" * 80)
print("DOWNLOADING RESULTS TO YOUR COMPUTER")
print("=" * 80)
print()
print("Note: Files are already safe in Google Drive")
print("This downloads copies to your local Downloads folder")
print()

# Patterns to download
download_patterns = [
    f'comprehensive_audit_{MODEL.replace("/", "_")}*.json',
    f'comprehensive_audit_{MODEL.replace("/", "_")}*.csv',
    f'comprehensive_audit_{MODEL.replace("/", "_")}*.png',
    f'context_ablation_{MODEL}*.csv',
    f'context_ablation_{MODEL}*.png',
]

downloaded_count = 0
for pattern in download_patterns:
    for filepath in glob.glob(pattern):
        print(f"Downloading: {filepath}")
        try:
            files.download(filepath)
            downloaded_count += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")

print()
print(f"✓ Downloaded {downloaded_count} files")
print()
```

---

## 🎯 Complete Workflow Summary

1. **CELL 1**: Mount Google Drive (authorize once)
2. **CELL 2**: Upload files (only first time)
3. **CELL 3**: Run comprehensive audit (~10 min)
4. **CELL 4**: Analyze results (~1 min)
5. **CELL 5**: Run context ablation (~15 min) [OPTIONAL]
6. **CELL 6**: Analyze ablation (~1 min) [OPTIONAL]
7. **CELL 7**: View summary of all results
8. **CELL 8**: Download to local computer [OPTIONAL]

---

## ✨ Key Benefits

- ✅ **Zero manual downloads**: Everything auto-saves to Google Drive
- ✅ **Survives disconnections**: Resume anytime from Google Drive
- ✅ **One-time setup**: Upload files once, use forever
- ✅ **Access anywhere**: Open Google Drive from any device
- ✅ **No data loss**: Results persist permanently in Drive

---

## 🔄 Subsequent Sessions

When you return:

1. Open Colab
2. Run CELL 1 (mount Drive)
3. Run CELL 3+ (files already there!)

That's it! Your previous results are all preserved in Google Drive.

---

## 🆘 Troubleshooting

### "Authorization required" popup
- Click the link → Sign in → Copy code → Paste back
- This only happens once per Google account

### "Files not found" after mounting
- Make sure you're in the right directory: `/content/drive/MyDrive/morphosyntax_experiment`
- Check CELL 2 output to verify files uploaded

### Session disconnected
- Just reconnect and run CELL 1 again
- All your results are safe in Google Drive!

---

## 🎉 You're Done!

Copy these cells into Colab and run them in order. Your experiments will automatically save to Google Drive and survive any disconnections!
