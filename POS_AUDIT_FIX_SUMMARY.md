# POS Audit: Problems and Better Alternative

## What Went Wrong with Original POS Audit

### Problem 1: BPE Tokenization
GPT-2 uses **byte-pair encoding (BPE)**, which means next-token predictions are often **subword fragments**, not complete words:
- Examples: `"g"`, `"ing"`, `","`, `"-"`
- **Cannot meaningfully assign POS tags to subword tokens**
- POS tags only apply to complete words in context

### Problem 2: Broken POS Tagging
The simple rule-based tagger assigns `NOUN` as default to everything:
- Punctuation (`","`, `"."`, `"-"`) → tagged as `NOUN` ✗
- Random letters (`"g"`, `"d"`, `"p"`) → tagged as `NOUN` ✗
- Result: **Meaningless percentages**

### Problem 3: Constant Values
Same `expected_pct` value (71.38023572852265) appeared multiple times across different items:
- Suggests: Cached value, fallback default, OR
- Computation isn't actually varying per-item

### Problem 4: No Context
POS depends on context:
- "run" → NOUN ("a run") OR VERB ("to run")
- Tagging isolated tokens without context is fundamentally wrong

---

## The Core Issue

**POS is not defined for subword tokens (BPE pieces).**

Any workflow that tags raw next-token candidates is **structurally doomed** unless you first:
1. Filter to word-boundary tokens only
2. Tag in full sentence context
3. Verify sanity (e.g., "," → PUNCT, "the" → DET)

---

## Better Alternative: Word-Class Constraint Audit

Instead of POS tagging, test **distributional constraint** directly:

### What It Does
For each syntactic position (e.g., after determiners):
1. **Classify tokens** as:
   - `word_start`: Tokens that begin new words (space + letter)
   - `punctuation`: Punctuation marks
   - `fragment`: Mid-word continuations
2. **Compute probability mass** on each class
3. **Compare** Jabberwocky vs. Scrambled

### Why It's Better
- **No POS tagger needed** → No fragile dependencies
- **Works with BPE** → Directly classifies subword tokens
- **Reviewer-proof** → Simple, interpretable classes
- **Tests the same claim**: "Structure narrows the continuation space"

### Expected Pattern
```
After "the" (determiner):
  Sentence/Jabberwocky:  ~60-70% word_start  (structure intact)
  Scrambled:             ~40-50% word_start  (structure disrupted)
```

### Interpretation
Higher `word_start` % → Model putting more probability on content-word continuations
→ Syntactic structure constrains the distribution

---

## Implementation Status

### ✓ Created: `word_class_constraint_audit.py`
- Implements word-class classification approach
- Includes sanity tests for token classification
- Computes distributional metrics
- **Blocked by SIGBUS crash** (same macOS issue as before)

### To Run (After Restart or on Colab)
```bash
source venv/bin/activate
python3 word_class_constraint_audit.py 2>&1 | tee word_class_results.txt
```

---

## Recommendation

**Use the Word-Class Constraint Audit** instead of POS tagging:

### Advantages
1. **Simpler**: No POS tagger, no spaCy, no contextual complexity
2. **More robust**: Works with BPE tokenization
3. **More interpretable**: Clear classes (word vs. fragment vs. punctuation)
4. **Tests same hypothesis**: Structure constrains distribution

### For Your Paper
You can report:
> "To test whether syntactic structure narrows the continuation space, we measured the percentage of probability mass allocated to word-initial tokens (vs. fragments/punctuation) after diagnostic syntactic cues (e.g., determiners). Jabberwocky showed significantly higher word-initial probability than Scrambled (Δ = +X%), demonstrating that syntactic structure—independent of semantics—constrains the model's predictions toward coherent lexical continuations."

---

## Alternative: Fix the POS Audit (If You Really Want It)

### Required Changes
1. **Word-boundary filtering**: Only consider tokens that start new words
   - GPT-2: Tokens with leading space + letter
   - Ignore mid-word subtokens entirely

2. **Contextual tagging**: For each candidate:
   - Construct: `context + candidate_string`
   - Tag the final word in full context
   - Use spaCy or stanza (contextual POS tagger)

3. **Sanity tests** (Hard requirement):
   - Verify: `","` → `PUNCT`
   - Verify: `"the"` → `DET`
   - Verify: `"and"` → `CCONJ`
   - **If any fail, STOP**

4. **Per-item verification**:
   - Log: (a) context, (b) top-k candidates, (c) POS counts, (d) expected_pct
   - Ensure values vary across items

### Complexity
This is **significantly more complex** than the word-class approach and requires:
- Proper BPE→word mapping
- Contextual POS tagger (spaCy with full pipeline)
- Extensive validation
- **Same SIGBUS crash risk**

---

## Conclusion

**Recommended approach**: Use `word_class_constraint_audit.py`

**Why**: Simpler, more robust, tests the same hypothesis, easier to explain to reviewers.

**To run**: After Mac restart OR on Google Colab (see `COLAB_INSTRUCTIONS.md`)

---

**Files Created**:
- `word_class_constraint_audit.py` - Recommended implementation
- `POS_AUDIT_FIX_SUMMARY.md` - This document

**Note**: Both approaches blocked by SIGBUS on your Mac. Try after restart or use Colab.
