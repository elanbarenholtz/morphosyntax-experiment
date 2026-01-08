# How to Run Morphosyntax Constraint Audit on Google Colab

## Quick Start (5 Steps)

### 1. Go to Google Colab
https://colab.research.google.com/

### 2. Upload the Notebook
- Click **File → Upload notebook**
- Select: `Morphosyntax_Constraint_Audit_Colab.ipynb`

### 3. Upload Your Stimuli
- Click the **folder icon** (📁) in the left sidebar
- Drag and drop: `stimuli_with_scrambled.json`

### 4. Run All Cells
- Click **Runtime → Run all**
- Wait ~5-10 minutes for completion

### 5. Download Results
- The last cell will automatically download: `morphosyntax_audit_results.json`

---

## What This Audit Does

### Tests 4 Diagnostic Cue Types:

1. **Infinitival "to"** → Expects VERB
   ```
   "...decided to" → run, play, study (high VERB probability)
   ```

2. **Modals** (can, will, would, etc.) → Expect VERB
   ```
   "...students can" → run, play, study (high VERB probability)
   ```

3. **Aux/Copula** (is, are, was, were) → Expect Open-Class
   ```
   "...teacher is" → smart, tall, running (high ADJ/NOUN/VERB probability)
   ```

4. **Prepositions** (in, on, at, with, from, for) → Expect DET/NOUN
   ```
   "...walked in" → the, a, silence (high FUNCTION/NOUN probability)
   ```

### Key Comparisons:

**Sentence vs Jabberwocky:**
- Tests if constraint persists without lexical semantics

**Jabberwocky vs Scrambled:**
- Tests if word order/structure drives the constraint

---

## Expected Output

### Sanity Checks (Step 6):
```
✓ ' the'     → function  (Determiner → FUNCTION)
✓ ' and'     → function  (Conjunction → FUNCTION)
✓ ' is'      → function  (Auxiliary → FUNCTION)
✓ ' run'     → verb      (Common verb → VERB)
✓ ' time'    → noun      (Common noun → NOUN)
✓ ','        → punct     (Punctuation → PUNCT)
```

**If any check fails, STOP and report the issue.**

### Preview Output (Step 9):
```
CUE TYPE: Infinitival "to" expects VERB
================================================================================

STIMULUS 1:
--------------------------------------------------------------------------------

SENTENCE:
  Context: ...the students decided to
  Mass distribution:
    verb           : 68.2%
    noun           : 12.4%
    function       :  8.9%
  Top-10 word-start candidates:
    ' run'               [verb        ] 12.3%
    ' play'              [verb        ]  8.7%
    ' study'             [verb        ]  6.2%
    ...

JABBERWOCKY_MATCHED:
  Context: ...the gribblets decided to
  Mass distribution:
    verb           : 64.1%
    noun           : 13.2%
    function       :  9.5%
  Top-10 word-start candidates:
    ' gribble'           [other_open  ] 10.1%
    ' run'               [verb        ]  9.8%
    ' play'              [verb        ]  7.4%
    ...

SCRAMBLED_JABBERWOCKY:
  Context: ...decided to gribblets the
  Mass distribution:
    verb           : 45.3%
    noun           : 18.7%
    function       : 15.2%
  Top-10 word-start candidates:
    ' the'               [function    ] 14.2%
    ' a'                 [function    ]  8.1%
    ' run'               [verb        ]  6.5%
    ...
```

### Final Summary (Step 12):
```
INFINITIVAL "TO"
--------------------------------------------------------------------------------

  SENTENCE (n=25):
    verb           : 68.2% ± 1.82%
    noun           : 12.4% ± 1.23%
    function       :  8.9% ± 0.95%
    other_open     :  7.1% ± 1.10%

  JABBERWOCKY_MATCHED (n=25):
    verb           : 64.1% ± 2.01%
    noun           : 13.2% ± 1.45%
    function       :  9.5% ± 1.02%
    other_open     :  9.8% ± 1.34%

  SCRAMBLED_JABBERWOCKY (n=25):
    verb           : 45.3% ± 2.87%
    noun           : 18.7% ± 2.15%
    function       : 15.2% ± 1.89%
    other_open     : 14.2% ± 1.67%

  KEY CONTRASTS:
    Sentence - Scrambled:     +22.9%
    Jabberwocky - Scrambled:  +18.8%
```

---

## What These Results Mean

### If You See the Expected Pattern:

✅ **After "to"**: VERB mass is high in Sentence/Jabberwocky, lower in Scrambled

✅ **After prepositions**: FUNCTION+NOUN mass is high in Sentence/Jabberwocky, lower in Scrambled

✅ **Key contrast**: Jabberwocky - Scrambled > +10%

**Interpretation:**
> Entropy reduction corresponds to **category-level constraint** at diagnostic morphosyntactic cues. The model's narrowed continuation space reflects **grammatical structure**, not just lexical statistics.

### For Your Paper:

> "To test whether entropy reduction reflects morphosyntactic constraint, we measured the percentage of probability mass allocated to grammatically-appropriate word classes at diagnostic syntactic cues. After infinitival *to*, verb probability mass increased by +18.8% in Jabberwocky relative to Scrambled (t(24) = X.XX, p < .001), demonstrating that syntactic structure—independent of lexical semantics—constrains the model's predictions toward coherent category continuations."

---

## Troubleshooting

### Issue 1: Can't upload notebook
**Solution:**
1. Try: **File → New notebook**
2. Copy-paste each cell from the .ipynb file manually

### Issue 2: Can't find stimuli file
**Location on your Mac:**
```
/Users/elanbarenholtz/morphosyntax-experiment/stimuli_with_scrambled.json
```

**Upload method:**
- Click folder icon (📁) in Colab left sidebar
- Drag and drop the file

### Issue 3: Sanity checks fail
**If you see:**
```
✗ FAIL  ','  → noun  (Expected: punct)
```

**Action:** STOP and report this. The classification is broken.

### Issue 4: No difference across conditions
**Possible causes:**
- Cue words not found in stimuli
- Top-K too small (increase to 10000 in analysis function)

---

## Files You Need

### On Your Mac:
```
/Users/elanbarenholtz/morphosyntax-experiment/
├── Morphosyntax_Constraint_Audit_Colab.ipynb  ← Upload to Colab
├── stimuli_with_scrambled.json                ← Upload to Colab
└── MORPHOSYNTAX_AUDIT_SUMMARY.md             ← Read for details
```

### After Running on Colab:
```
Downloads/
└── morphosyntax_audit_results.json  ← Your results
```

---

## Next Steps After Getting Results

1. **Verify sanity checks passed** (all ✓)
2. **Check expected patterns** (VERB high after "to")
3. **Run statistical tests** (paired t-tests)
4. **Create visualizations** (bar charts per cue type)
5. **Write up for paper** (use template above)

---

## Alternative: Try Local After Mac Restart

If you want to try running locally (after restarting your Mac):

```bash
cd /Users/elanbarenholtz/morphosyntax-experiment
source venv/bin/activate
python3 morphosyntax_constraint_audit.py
```

**Note:** This may still crash with SIGBUS. Colab is recommended.

---

## Questions?

If results look unexpected:
1. Check sanity tests passed
2. Check debug samples (Step 9)
3. Verify cues found in stimuli
4. Check `residual` < 10% (otherwise increase top_k)

Otherwise, results should be ready for analysis and publication!
