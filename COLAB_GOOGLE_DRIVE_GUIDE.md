# Google Drive Integration for Colab Experiments

**Protect your results from disconnections by auto-saving to Google Drive**

---

## 🎯 Why Use Google Drive?

**Problem:** Colab sessions disconnect after:
- 12 hours of runtime
- 90 minutes of inactivity
- Random disconnections

**Solution:** Mount Google Drive and save all results there automatically. When you reconnect, all results are preserved.

---

## 🚀 Quick Setup (Add to ANY Colab Notebook)

### Step 1: Add Mount Cell at Top of Notebook

```python
# Cell 1: Mount Google Drive
from google.colab import drive
import os

# Mount Google Drive
drive.mount('/content/drive')

# Create project directory in Google Drive
PROJECT_DIR = '/content/drive/MyDrive/morphosyntax_experiment'
os.makedirs(PROJECT_DIR, exist_ok=True)

# Change to project directory
os.chdir(PROJECT_DIR)

print(f"✓ Google Drive mounted")
print(f"✓ Working directory: {PROJECT_DIR}")
print(f"✓ All files will be saved to Google Drive automatically")
```

**What happens:**
1. You'll see a popup asking to authorize Google Drive access
2. Click the link, sign in to your Google account
3. Copy the authorization code and paste it back in Colab
4. Done! All files now save to `Google Drive/morphosyntax_experiment/`

### Step 2: Upload Required Files

```python
# Cell 2: Upload framework files (only needed once)
from google.colab import files
import os

# Check if files already exist
required_files = [
    'cue_families.py',
    'word_level_analysis.py',
    'run_comprehensive_audit.py',
    'analyze_comprehensive_results.py',
    'stimuli_comprehensive.json',
    'run_context_ablation.py',
    'analyze_context_ablation.py'
]

missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    print(f"Missing files: {missing_files}")
    print("Please upload them using the file picker...")
    uploaded = files.upload()
    print(f"✓ Uploaded {len(uploaded)} files")
else:
    print(f"✓ All required files present in Google Drive")
```

**Note:** Files upload to Google Drive, so you only need to upload ONCE. Next session they'll already be there!

### Step 3: Run Experiments (Normal workflow)

```python
# Cell 3: Run experiment
!pip install -q transformers torch pandas matplotlib seaborn scipy tqdm

# Run comprehensive audit
!python run_comprehensive_audit.py --model gpt2

# Results automatically save to Google Drive!
```

---

## 📁 Recommended Google Drive Structure

```
Google Drive/
└── morphosyntax_experiment/
    ├── cue_families.py
    ├── word_level_analysis.py
    ├── run_comprehensive_audit.py
    ├── analyze_comprehensive_results.py
    ├── run_context_ablation.py
    ├── analyze_context_ablation.py
    ├── stimuli_comprehensive.json
    │
    ├── results/                          # Auto-created
    │   ├── comprehensive_audit_gpt2.json
    │   ├── comprehensive_audit_gpt2_comparisons.csv
    │   ├── comprehensive_audit_gpt2_summary.png
    │   ├── context_ablation_gpt2.csv
    │   └── ...
    │
    └── logs/                             # Optional
        ├── experiment_20260107.log
        └── ...
```

---

## 🔄 Complete Colab Notebook Template

### Option 1: Comprehensive Audit

```python
# ============================================================================
# CELL 1: Mount Google Drive
# ============================================================================

from google.colab import drive
import os

drive.mount('/content/drive')
PROJECT_DIR = '/content/drive/MyDrive/morphosyntax_experiment'
os.makedirs(PROJECT_DIR, exist_ok=True)
os.chdir(PROJECT_DIR)

# Create results directory
os.makedirs('results', exist_ok=True)

print(f"✓ Working in: {PROJECT_DIR}")
print(f"✓ Results will be saved to: {PROJECT_DIR}/results/")

# ============================================================================
# CELL 2: Setup Environment
# ============================================================================

!pip install -q transformers torch pandas matplotlib seaborn scipy tqdm

import subprocess
import sys

# ============================================================================
# CELL 3: Upload Files (only if not present)
# ============================================================================

required_files = [
    'cue_families.py',
    'word_level_analysis.py',
    'run_comprehensive_audit.py',
    'analyze_comprehensive_results.py',
    'stimuli_comprehensive.json'
]

missing = [f for f in required_files if not os.path.exists(f)]

if missing:
    print(f"Please upload: {missing}")
    from google.colab import files
    uploaded = files.upload()
else:
    print("✓ All files present")

# ============================================================================
# CELL 4: Select Model and Run
# ============================================================================

# Choose your model
MODEL = 'gpt2'  # Options: gpt2, gpt2-medium, gpt2-large, EleutherAI/pythia-410m

print(f"Running comprehensive audit for: {MODEL}")
print(f"Expected runtime: ~5-10 min (GPU)")

result = subprocess.run(
    ['python', 'run_comprehensive_audit.py', '--model', MODEL],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.returncode != 0:
    print("ERROR:", result.stderr)
else:
    print(f"\n✓ Experiment complete!")
    print(f"✓ Results saved to Google Drive")

# ============================================================================
# CELL 5: Analyze Results
# ============================================================================

model_slug = MODEL.replace('/', '_')
result_file = f'comprehensive_audit_{model_slug}.json'

if os.path.exists(result_file):
    result = subprocess.run(
        ['python', 'analyze_comprehensive_results.py', result_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(f"\n✓ Analysis complete!")
    print(f"✓ Plots saved to Google Drive")
else:
    print(f"Result file not found: {result_file}")

# ============================================================================
# CELL 6: Download Results (Optional)
# ============================================================================

# Download specific files to your local machine
from google.colab import files

# Download main results
files.download(result_file)
files.download(f'{result_file.replace(".json", "_comparisons.csv")}')

# Download plots
import glob
for plot in glob.glob(f'comprehensive_audit_{model_slug}_*.png'):
    files.download(plot)

print("✓ Downloads complete")
```

---

### Option 2: Context Ablation

```python
# ============================================================================
# CELL 1-3: Same as above (Mount, Setup, Upload)
# ============================================================================

# ============================================================================
# CELL 4: Run Context Ablation
# ============================================================================

MODEL = 'gpt2'

print(f"Running context ablation for: {MODEL}")
print(f"Expected runtime: ~15-20 min (GPU)")

result = subprocess.run(
    ['python', 'run_context_ablation.py',
     '--model', MODEL,
     '--stimuli', 'stimuli_comprehensive.json',
     '--output', f'context_ablation_{MODEL}.csv'],
    capture_output=True,
    text=True
)

print(result.stdout)
print(f"\n✓ Ablation complete!")

# ============================================================================
# CELL 5: Analyze Ablation Results
# ============================================================================

result_file = f'context_ablation_{MODEL}.csv'

if os.path.exists(result_file):
    result = subprocess.run(
        ['python', 'analyze_context_ablation.py', result_file],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(f"\n✓ Analysis complete!")
else:
    print(f"Result file not found: {result_file}")
```

---

## ⚡ Pro Tips

### 1. Check Files Before Starting

```python
# Verify files in Google Drive
import os
os.chdir('/content/drive/MyDrive/morphosyntax_experiment')

print("Files in project directory:")
for f in os.listdir('.'):
    size = os.path.getsize(f) if os.path.isfile(f) else 0
    print(f"  {f:40s} {size:>10,} bytes")
```

### 2. Resume Interrupted Experiment

```python
# Check what's already complete
import os
import glob

print("Completed experiments:")
for f in glob.glob('comprehensive_audit_*.json'):
    print(f"  ✓ {f}")

print("\nCompleted ablations:")
for f in glob.glob('context_ablation_*.csv'):
    print(f"  ✓ {f}")
```

### 3. Save Progress Periodically

```python
# Add to your experiment loop
import shutil
import time

# Every N iterations, create backup
if iteration % 5 == 0:
    backup_dir = f'backup_{int(time.time())}'
    os.makedirs(backup_dir, exist_ok=True)
    for f in glob.glob('*.json'):
        shutil.copy(f, backup_dir)
    print(f"Backup saved to: {backup_dir}")
```

### 4. Keep Session Alive

Add this cell and run it in the background:

```python
# Anti-idle script (run in background)
import time
from IPython.display import Javascript, display

def keep_alive():
    while True:
        display(Javascript('console.log("Keep alive")'))
        time.sleep(60)  # Every 60 seconds

# Run in thread
import threading
threading.Thread(target=keep_alive, daemon=True).start()
print("✓ Keep-alive thread started")
```

### 5. Monitor Progress with Timestamps

```python
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {message}")

# Use throughout your code
log("Starting experiment...")
log("Processing stimulus 1/30...")
log("Experiment complete!")
```

---

## 🔧 Troubleshooting

### Google Drive Won't Mount

```python
# Force remount
from google.colab import drive
drive.flush_and_unmount()
drive.mount('/content/drive', force_remount=True)
```

### Files Not Saving

```python
# Verify write access
import os
test_file = '/content/drive/MyDrive/morphosyntax_experiment/test.txt'
try:
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("✓ Write access confirmed")
except Exception as e:
    print(f"✗ Write error: {e}")
```

### Session Disconnected, Results Missing

```python
# Check if results are in Drive
import os
os.chdir('/content/drive/MyDrive/morphosyntax_experiment')

# List all JSON files with timestamps
import glob
from datetime import datetime

for f in sorted(glob.glob('*.json'), key=os.path.getmtime, reverse=True):
    mtime = datetime.fromtimestamp(os.path.getmtime(f))
    print(f"{f:40s} {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
```

---

## ✅ Complete Workflow Summary

1. **First time:**
   - Mount Google Drive
   - Upload 7 required files to `MyDrive/morphosyntax_experiment/`
   - Run experiment
   - Results auto-save to Google Drive

2. **Subsequent sessions:**
   - Mount Google Drive
   - Change to project directory
   - Run experiment (files already there!)
   - Results accumulate in Google Drive

3. **After disconnection:**
   - Reconnect and mount Google Drive
   - All previous results still there
   - Continue or analyze existing results

---

## 📊 Expected File Sizes

To help you verify successful saves:

```
cue_families.py                  ~10 KB
word_level_analysis.py           ~20 KB
run_comprehensive_audit.py       ~15 KB
stimuli_comprehensive.json       ~50 KB

comprehensive_audit_gpt2.json    ~200 KB
context_ablation_gpt2.csv        ~100 KB
*.png plots                      ~50-100 KB each
```

---

## 🎉 You're Protected!

With Google Drive mounting:
- ✅ No data loss on disconnection
- ✅ Resume anytime from any device
- ✅ Access results from desktop
- ✅ Share Drive folder for collaboration
- ✅ Automatic versioning via Drive

**Your experiments are now safe!**
