# Enhanced Context Logging for Morphosyntax Audit

## What Was Added

Both `morphosyntax_audit_refined.py` and `Morphosyntax_Audit_Refined_Colab.ipynb` now include **enhanced context logging** for every datapoint.

## New Fields in Output JSON

Each record in `morphosyntax_audit_refined_results.json` now includes:

```json
{
  "model": "gpt2",
  "cue_type": "infinitival_to",
  "condition": "jabberwocky_matched",
  "stimulus_id": 5,
  "cue_word": "to",
  "cue_word_index": 8,

  // NEW: Enhanced context logging
  "full_text": "The gribblets decided to fribble the zorp.",
  "context_prefix": "The gribblets decided to",
  "context_tokens": 6,

  "mass": {
    "verb": 0.658,
    "noun": 0.126,
    // ...
  }
}
```

## What Each Field Tells You

### `full_text`
- **Purpose**: The complete sentence/text being analyzed
- **Use**: Verify you're analyzing the intended stimulus
- **Example**: `"The gribblets decided to fribble the zorp."`

### `cue_word`
- **Purpose**: The actual cue word found in this position
- **Use**: Confirm it's the expected cue (e.g., infinitival "to" vs prepositional "to")
- **Example**: `"to"`

### `context_prefix`
- **Purpose**: The **exact string fed to the model** for next-token prediction
- **Use**: Critical for reproducibility - shows precisely what the model saw
- **Example**: `"The gribblets decided to"` (ends after the cue)

### `context_tokens`
- **Purpose**: Number of BPE tokens in the context
- **Use**: Verify tokenization, check context length, debug issues
- **Example**: `6` (for GPT-2's tokenization of the above context)

## Why This Matters

### 1. Reproducibility
You can now **exactly reproduce** any result by:
```python
# From the JSON record
context = record['context_prefix']
inputs = tokenizer(context, return_tensors='pt')
outputs = model(**inputs)
next_token_logits = outputs.logits[0, -1, :]
# Should match the recorded mass distribution
```

### 2. Verification
You can verify you're measuring the **intended cue occurrence**:
- Not a different "to" in the sentence
- Not a cached/reused context
- Correct position after filtering (e.g., sentence-initial excluded)

### 3. Debugging
If results look unexpected, you can:
- Check the actual text analyzed
- Verify the cue word position
- Inspect the exact context string
- Confirm BPE tokenization

## Example Use Cases

### Check if filtering worked correctly
```python
import json

with open('morphosyntax_audit_refined_results.json') as f:
    results = json.load(f)

# Check infinitival "to" filtering
to_results = [r for r in results if r['cue_type'] == 'infinitival_to']

for r in to_results[:5]:
    print(f"Stimulus {r['stimulus_id']}, {r['condition']}:")
    print(f"  Full text: {r['full_text']}")
    print(f"  Cue position: {r['cue_word_index']}")
    print(f"  Context: {r['context_prefix']}")
    print(f"  VERB mass: {r['mass']['verb']:.3f}")
    print()
```

### Verify position-0 filtering for "to"
```python
# Should be ZERO results (all sentence-initial "to" filtered)
initial_to = [r for r in to_results if r['cue_word_index'] == 0]
print(f"Sentence-initial 'to' (should be 0): {len(initial_to)}")
```

### Check context lengths
```python
import numpy as np

# Check if contexts are reasonable length
lengths = [r['context_tokens'] for r in results]
print(f"Context length: mean={np.mean(lengths):.1f}, min={min(lengths)}, max={max(lengths)}")
```

## Implementation Details

### Where it's added (morphosyntax_audit_refined.py:270-279)
```python
# ENHANCED LOGGING: Always include full context metadata
result = {
    'cue_word_index': cue_position,
    'mass': mass,
    # Context logging (Point 1 from requirements)
    'full_text': text,
    'cue_word': cue_word,
    'context_prefix': context,  # Exact string fed to model
    'context_tokens': len(inputs['input_ids'][0]),  # Number of BPE tokens
}
```

### Colab notebook (cell-18)
Same enhancement applied to the Colab version for consistency.

## Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Full text logged?** | ❌ No | ✅ Yes |
| **Context string logged?** | ⚠️ Only last 60 chars (debug) | ✅ Full prefix always |
| **Cue word logged?** | ✅ Yes (in separate field) | ✅ Yes |
| **Token count logged?** | ❌ No | ✅ Yes |
| **Reproducible?** | ⚠️ Difficult | ✅ Exact |
| **File size** | Smaller | Slightly larger (~20% increase) |

## File Size Impact

**Before**: ~500 KB (without full context)
**After**: ~600-700 KB (with full context)

Worth it for reproducibility and verification!

## Five Requirements from Your List

✅ **1. Log actual context for each datapoint**
- Full text, cue word, exact prefix, token count all saved

✅ **2. Fix POS tagging so punctuation can't be tagged as NOUN**
- Already fixed: `decode_to_word` preserves punctuation
- Punctuation-only tokens classified as 'punct' not 'other'

✅ **3. Restrict to word-start candidates**
- Already implemented: `is_word_start_token` filters to space+letter
- Fragment mass tracked separately as 'non_wordstart'

✅ **4. Reduce residual mass**
- Already implemented: `top_k=10000` (up from 5000)
- Target: residual <1%
- Warnings if residual >2%

✅ **5. Differentiate Jabberwocky vs Scrambled**
- Full audit designed for this comparison
- Expected: Stronger effects with refinements (+26.6% vs +18.8%)

## Next Steps

1. **Run the audit** (Colab recommended)
2. **Check enhanced logging** in the output JSON
3. **Verify filtering** using the example code above
4. **Confirm results** match expected patterns
5. **Publication-ready** analysis!

---

## Questions to Ask After Running

1. ✅ **Full text logged?** Check `full_text` field exists and is complete
2. ✅ **Context exact?** Compare `context_prefix` to expected cue position
3. ✅ **Filtering worked?** No sentence-initial "to" (position 0)
4. ✅ **Residual low?** Most positions <1%, warnings if >2%
5. ✅ **Effect strong?** Δ (Jab - Scr) > +20% for infinitival "to"

If all yes → **Ready for paper!**
