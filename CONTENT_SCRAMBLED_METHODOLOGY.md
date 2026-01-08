# Content-Scrambled Control: Methodological Improvement

## The Problem with Full Scrambling

### Original SCRAMBLED Condition

**Example**:
- **Jabberwocky**: "the prell decided to cleb the bril braz"
- **Old Scrambled**: "the the cleb prell braz bril to decided"

**Issues**:
1. **Imbalanced n**: Only 10/30 usable "to" instances (66.7% filtered)
   - Full scrambling puts "to" in random positions
   - Often followed by punctuation or non-word-start tokens
   - Can't measure VERB mass after "to" when cue is destroyed

2. **Non-comparable cue contexts**:
   - Jabberwocky: "decided to ___" (slot 4, after subject+verb)
   - Scrambled: "to ___" (random position, no consistent context)
   - Not testing same morphosyntactic slot!

3. **Confounded comparison**:
   - Difference could reflect:
     - (a) Syntactic structure (what we want to test), OR
     - (b) Simply that cue isn't present in Scrambled (artifact)

### Reviewer Concerns

> "The scrambled condition has n=10 while other conditions have n=30. How do we know the effect isn't just due to selective sampling? The cue contexts aren't matched—you're comparing different positions in the sentence. This isn't a clean test."

**They're right.** The comparison is methodologically weak.

---

## The Solution: Content-Scrambled Control

### Key Insight

We don't need to scramble **everything**. We only need to disrupt content sequencing while preserving the morphosyntactic cue position.

**Strategy**: Keep function-word skeleton intact, shuffle only content words.

### Content-Scrambled Jabberwocky

**Example**:
- **Jabberwocky**: "the prell decided to cleb the bril braz"
  - Function skeleton: "the ___ decided to ___ the ___ ___"
  - Content words: [prell, cleb, bril, braz]

- **Content-Scrambled**: "the cleb decided to braz the bril prell"
  - Function skeleton: "the ___ decided to ___ the ___ ___" (SAME!)
  - Content words: [cleb, braz, bril, prell] (shuffled)

### What's Preserved

✓ All function words in same positions:
- Determiners: "the", "the"
- Control verb: "decided"
- **Critical cue: "to" (position 3)**

✓ Same number of words (matched length)

✓ Same grammatical slots:
- Slot 1: Subject noun (content)
- Slot 3: "to" (function)
- Slot 4: Predicted verb (content)
- etc.

### What's Disrupted

✗ Content word sequencing:
- "prell...cleb...bril...braz" → "cleb...braz...bril...prell"
- Semantic coherence (if any remained in nonce words)
- Local transitional probabilities between content words

---

## The New Comparison

### 3-Way Design

1. **SENTENCE** (real English):
   - "the scientist decided to study the ancient artifacts"
   - Semantics + Structure

2. **JABBERWOCKY** (matched structure):
   - "the prell decided to cleb the bril braz"
   - Structure only

3. **CONTENT_SCRAMBLED** (matched function skeleton):
   - "the cleb decided to braz the bril prell"
   - Function skeleton only

### Primary Test: JABBERWOCKY vs CONTENT_SCRAMBLED

Both conditions have:
- ✓ **Matched n=30/30** "to" instances
- ✓ **Same cue context**: "to" always at position 3
- ✓ **Same function words**: "the ___ decided to ___"
- ✓ **Only difference**: Content word order

**If JABBERWOCKY > CONTENT_SCRAMBLED**:
- Content **sequencing** matters
- Model tracks linear order of content words
- Predictions depend on "prell...cleb" sequence, not just "the ___ decided to ___"

**If JABBERWOCKY ≈ CONTENT_SCRAMBLED**:
- Content sequencing does **not** matter
- Only function-word **skeleton** drives predictions
- Model only needs "the ___ decided to ___" pattern
- Purely **structural** constraint (not sequential)

---

## Advantages Over Full Scrambling

### Methodological

| Feature | Full Scrambling | Content Scrambling |
|---------|-----------------|-------------------|
| **n after "to"** | 10 (33% retained) | 30 (100% retained) |
| **Cue position** | Random | Fixed (matched) |
| **Function skeleton** | Destroyed | Preserved |
| **What's tested** | Structure vs chaos | Sequencing vs skeleton |
| **Comparison** | Apples vs oranges | Apples vs apples |

### Statistical

- **Matched pairs**: Every sentence set has both Jab and Content-Scram
- **Paired t-test**: More power than independent samples
- **No selective sampling**: All 30 items contribute equally
- **No confounds**: Same cue context, position, length

### Theoretical

This design directly tests:
> "Does morphosyntactic constraint reflect content sequencing or function-word structure?"

Old design (full scrambling) conflates:
- Structure vs no structure
- Present cue vs absent cue
- Matched n vs filtered n

New design (content scrambling) isolates:
- **Pure question**: sequencing vs skeleton
- **Clean answer**: Δ(Jab - Content-Scram)

---

## Implementation

### Files Created

1. **`generate_content_scrambled_stimuli.py`**
   - Identifies function vs content words
   - Shuffles only content positions
   - Deterministic (seeded by set_id)
   - Validates: word count, "to" position

2. **`stimuli_content_scrambled.json`**
   - 30 stimulus sets
   - Each has: sentence, jabberwocky_matched, content_scrambled_jabberwocky
   - Metadata: permutation record, seed

3. **`Morphosyntax_Audit_Content_Scrambled_Colab.ipynb`**
   - Runs 3-condition audit
   - Computes VERB mass after "to"
   - Paired statistical tests
   - Generates plots & CSVs

4. **`COLAB_INSTRUCTIONS_CONTENT_SCRAMBLED.md`**
   - Step-by-step guide
   - Expected outcomes
   - Interpretation guidelines

### Verification

Sanity checks passed:
- ✓ 30 sets generated
- ✓ "to" instances: 30 in Jab, 30 in Content-Scram (matched!)
- ✓ Function words preserved at all positions
- ✓ Content words shuffled (confirmed by permutation records)

---

## For Reviewers

**Old approach (full scrambling)**:
> "Why is n=10 in scrambled vs n=30 in jabberwocky? How do we know this isn't selective sampling? The cue positions don't match."

**New approach (content scrambling)**:
> "Both conditions have n=30 with 'to' at the same position. The only difference is content word order. This is a clean, matched-pairs design that directly tests whether sequencing matters beyond the function-word skeleton."

**Result**: Addresses methodological concerns and provides a cleaner test of the theoretical question.

---

## Next Steps

1. **Run Colab notebook** (15-20 minutes)
   - Upload `stimuli_content_scrambled.json`
   - Run `Morphosyntax_Audit_Content_Scrambled_Colab.ipynb`

2. **Analyze results**
   - Check: JABBERWOCKY vs CONTENT_SCRAMBLED
   - Interpret effect direction and size

3. **Update paper**
   - Replace old scrambled results
   - Use new methodology (cleaner, more convincing)
   - Address reviewer concerns pre-emptively

---

## Summary

**Problem**: Old scrambled control was methodologically weak (imbalanced n, non-comparable contexts)

**Solution**: Content-scrambled control preserves function skeleton, shuffles only content

**Result**: Clean test with matched n=30/30, comparable cue contexts, direct test of sequencing vs skeleton

**Impact**: Stronger evidence, addresses reviewer concerns, cleaner theoretical story
