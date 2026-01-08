# Running Content-Scrambled Morphosyntax Audit on Google Colab

## Motivation

**Problem with old SCRAMBLED control**:
- Imbalanced n (10 vs 30) because full scrambling destroys "to" adjacency
- Non-comparable cue contexts

**Solution: CONTENT_SCRAMBLED control**:
- Preserves function skeleton (including "to" position)
- Only shuffles content words (nonce words in Jabberwocky)
- **Matched n=30/30 "to" instances**
- Clean test of content sequencing vs syntactic skeleton

---

## Quick Start

### Step 1: Open Colab
Go to: https://colab.research.google.com/

### Step 2: Upload Notebook
- Click **"Upload"** tab
- Select: `Morphosyntax_Audit_Content_Scrambled_Colab.ipynb`

### Step 3: Upload Stimuli File
- Click the **folder icon** in left sidebar (Files panel)
- Click the **upload button** (document with up arrow)
- Select: `stimuli_content_scrambled.json`

### Step 4: Run All Cells
- Menu: **Runtime** → **Run all** (or Ctrl+F9)
- Wait ~10-15 minutes

### Step 5: Download Results
After completion, right-click these files in the file browser:
- `morphosyntax_audit_content_scrambled_results.json` → Download
- `morphosyntax_content_scrambled_summary.csv` → Download
- `morphosyntax_content_scrambled_paired_plot.png` → Download

---

## What to Expect

### The Comparison

**JABBERWOCKY (preserved structure)**:
```
"the prell decided to cleb the bril braz"
```

**CONTENT_SCRAMBLED (function skeleton preserved, content shuffled)**:
```
"the cleb decided to braz the bril prell"
```

Both conditions have:
- ✓ Same function words in same positions
- ✓ "to" at position 3 (matched!)
- ✓ n=30 for both

### Possible Outcomes

**Outcome A: JABBERWOCKY > CONTENT_SCRAMBLED**
- Content SEQUENCING matters
- Model is sensitive to linear order of content words
- Evidence: VERB prediction depends on content word positions

**Outcome B: JABBERWOCKY ≈ CONTENT_SCRAMBLED**
- Content sequencing does NOT matter
- Only function-word SKELETON drives predictions
- Evidence: Supports purely structural (not sequential) constraint

---

## For Your Paper

**If JABBERWOCKY > CONTENT_SCRAMBLED**:

> "To test whether morphosyntactic constraint reflects content sequencing or function-word structure, we compared Jabberwocky (preserved structure) with Content-Scrambled Jabberwocky (preserved function skeleton, shuffled content). VERB probability mass after infinitival *to* was significantly higher in Jabberwocky (M = X.XX) than Content-Scrambled (M = X.XX), paired t(29) = X.XX, p < .05, d = X.XX. This demonstrates that GPT-2's category-level predictions depend on content word sequencing, not just the function-word skeleton."

**If JABBERWOCKY ≈ CONTENT_SCRAMBLED**:

> "To test whether morphosyntactic constraint reflects content sequencing or function-word structure, we compared Jabberwocky (preserved structure) with Content-Scrambled Jabberwocky (preserved function skeleton, shuffled content). VERB probability mass after infinitival *to* showed no significant difference between Jabberwocky (M = X.XX) and Content-Scrambled (M = X.XX), paired t(29) = X.XX, p = .XX. This demonstrates that GPT-2's category-level predictions depend only on the function-word skeleton, not content word sequencing, supporting a purely structural constraint."

---

## Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `stimuli_content_scrambled.json` | NEW stimuli with matched controls | ✅ Use this! |
| `Morphosyntax_Audit_Content_Scrambled_Colab.ipynb` | Colab notebook | ✅ Ready to run |
| `generate_content_scrambled_stimuli.py` | Generator (for reference) | ℹ️ Already run |

---

## Timeline

1. Upload files: 2 minutes
2. Run audit: 10-15 minutes
3. Download results: 30 seconds

**Total: ~15-20 minutes**

---

Ready to run! This will provide a much cleaner test than the old fully-scrambled control.
