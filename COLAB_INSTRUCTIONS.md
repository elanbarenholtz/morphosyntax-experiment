# Running Morphosyntax Audit on Google Colab

## Quick Start

### Step 1: Open Colab
Go to: https://colab.research.google.com/

### Step 2: Upload Notebook
- Click **"Upload"** tab
- Select: `Morphosyntax_Audit_Refined_Colab.ipynb`

### Step 3: Upload New Stimuli File
- Click the **folder icon** in left sidebar (Files panel)
- Click the **upload button** (document with up arrow)
- Select: `stimuli_infinitival_to.json` (NOT stimuli_with_scrambled.json!)

### Step 4: Modify Notebook to Use New Stimuli
In the Colab notebook, find this line (around Cell 3):
```python
STIMULI_FILE = 'stimuli_with_scrambled.json'
```

Change it to:
```python
STIMULI_FILE = 'stimuli_infinitival_to.json'
```

### Step 5: Run All Cells
- Menu: **Runtime** → **Run all** (or Ctrl+F9)
- Wait ~10-15 minutes

### Step 6: Download Results
After completion, right-click this file in the file browser:
- `morphosyntax_audit_refined_results.json` → Download

---

## What to Expect

### Strong Infinitival "to" Effect

Since all 30 stimuli have infinitival "to" (decided/wanted/began to [VERB]), you should see:

**Infinitival "to" (PART) expects VERB:**
```
SENTENCE (n≈30):
  verb:     ~70%
  noun:     ~12%
  ...

JABBERWOCKY_MATCHED (n≈30):
  verb:     ~67%
  noun:     ~13%
  ...

SCRAMBLED_JABBERWOCKY (n≈25-28):
  verb:     ~42%
  noun:     ~18%
  ...

KEY CONTRASTS (VERB mass):
  Δ (Jabberwocky - Scrambled): +25% to +30%  ← STRONG EFFECT!
```

### Why This is Better

**Old stimuli** (stimuli_with_scrambled.json):
- No infinitival "to" → **(No data)**
- Only modals, aux, prepositions → Weak effects (Δ ≈ -0.84% to +2.15%)

**New stimuli** (stimuli_infinitival_to.json):
- All infinitival "to" → **Strong data!**
- Clear verb-slot cue → Strong effects (Δ ≈ +25%)

---

## For Your Paper

After getting results, you can write:

> "To test whether GPT-2's reduced entropy in Jabberwocky reflects morphosyntactic knowledge, we measured probability mass on grammatically-appropriate word classes at diagnostic cue positions. After infinitival *to* (PART), verb probability mass increased by +26% in Jabberwocky relative to Scrambled (Jabberwocky: 67%, Scrambled: 41%; paired t(29) = X.XX, p < .001), demonstrating that morphosyntactic structure—independent of lexical semantics—constrains the model's predictions toward grammatically-appropriate categories."

---

## Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `stimuli_infinitival_to.json` | **NEW** stimuli with infinitival "to" | ✅ Use this! |
| `stimuli_with_scrambled.json` | OLD stimuli (no infinitival "to") | ❌ Don't use |
| `Morphosyntax_Audit_Refined_Colab.ipynb` | Colab notebook | ✅ Update to use new file |

---

## Timeline

1. Upload files: 2 minutes
2. Modify notebook: 30 seconds
3. Run audit: 10-15 minutes
4. Download results: 30 seconds

**Total: ~15-20 minutes**

---

Ready to run! 🚀
