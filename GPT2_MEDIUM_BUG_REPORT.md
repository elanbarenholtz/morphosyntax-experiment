# GPT-2-Medium NaN Bug Report

## Summary

GPT-2-medium consistently produces NaN/Inf values in logits during forward pass on this system, making it unusable for the entropy validation experiment. This issue does NOT occur with gpt2 (base), gpt2-large, or gpt2-xl on the same system.

## System Configuration

- Platform: macOS (Darwin 23.3.0)
- CPU: Apple Silicon
- Python: 3.13.3
- PyTorch: 2.9.1
- Transformers: 4.57.3
- Device: CPU (no CUDA available)

## Debugging Steps Performed

### 1. Initial Discovery
- GPT-2-medium forward pass produces:
  ```
  Logits: Min=nan, Max=nan, Mean=nan
  Has Inf: True
  Has NaN: True
  ```
- Same code works perfectly for gpt2-large:
  ```
  Logits: Min=-24.09, Max=5.60, Mean=-3.18
  Has Inf: False
  Has NaN: False
  ```

### 2. Cache Corruption Hypothesis
- **Action**: Cleared HuggingFace cache: `rm -rf ~/.cache/huggingface/hub/models--gpt2-medium`
- **Result**: Fresh download still produces NaN
- **Conclusion**: Not a corrupted download

### 3. Model Weights Inspection
- **Action**: Checked all model parameters for NaN
- **Result**: No NaN found in model weights
- **Conclusion**: NaN generated during forward pass, not from corrupted weights

### 4. Precision/dtype Testing
- **Default loading (float32)**: NaN ✗
- **Explicit float32**: NaN ✗
- **Float16**: No NaN but suspicious uniform values (-83 to -61)
- **Conclusion**: float16 avoids NaN but produces incorrect logits

### 5. Forward Pass Configuration
- **Tested**:
  - With/without attention masks
  - `use_cache=False`
  - `return_dict=True`
  - Different input texts
- **Result**: NaN persists in all configurations
- **Conclusion**: Issue is model-specific, not input or config dependent

## Why Only GPT-2-Medium?

| Model | Size | Status |
|-------|------|--------|
| gpt2 (base) | 124M | ✓ Works |
| **gpt2-medium** | **355M** | **✗ NaN** |
| gpt2-large | 774M | ✓ Works |
| gpt2-xl | 1.5B | ✓ Works (tested) |
| pythia-410m | 410M | ✓ Works |

This pattern suggests a specific numerical instability in the 355M parameter configuration when running on Apple Silicon CPU with this software stack.

## Potential Root Causes

1. **PyTorch 2.9.1 + Apple Silicon**: Known numerical instability with certain model sizes
2. **Transformers 4.57.3 regression**: Recent version may have introduced bug
3. **Model architecture interaction**: Specific combination of:
   - 24 layers
   - 16 attention heads
   - 1024 hidden size
   - Running on CPU (no CUDA)

   May trigger overflow/underflow in intermediate computations

## Proposed Solutions

### Option 1: Use Alternative Mid-Size Model
Replace gpt2-medium (355M) with a working alternative:
- **EleutherAI/pythia-160m** (162M params) - Already tested, works
- **EleutherAI/pythia-1b** (1B params) - Would provide 4th data point
- **distilgpt2** (82M params) - Smaller but proven to work

**Scaling series would be**:
- gpt2 (124M): Δ Entropy = -0.427 bits
- pythia-160m (162M): [NEW]
- pythia-410m (410M): Δ Entropy = -0.270 bits
- gpt2-large (774M): Δ Entropy = -0.116 bits
- [Optional] pythia-1b (1B): [NEW]

### Option 2: Try Different Software Stack
- Downgrade transformers to 4.35.x (known stable version)
- Downgrade PyTorch to 2.0.x
- Use Python 3.10 instead of 3.13

### Option 3: Use GPU/Different Hardware
- Run on system with CUDA GPU
- Try on x86_64 Linux system
- Use Google Colab with GPU runtime

### Option 4: Use openai-gpt2-medium
- Try loading from openai-community organization:
  ```python
  model = AutoModelForCausalLM.from_pretrained('openai-community/gpt2-medium')
  ```

## Recommendation

**Immediate action**: Use **pythia-160m** as the intermediate data point.

**Rationale**:
1. Same architecture family as pythia-410m (already validated)
2. Size (162M) fills the gap between gpt2-base (124M) and pythia-410m (410M)
3. Proven to work on this system
4. Can run immediately without debugging delays
5. Provides 4 solid data points for scaling trend analysis

**Alternative**: If user wants to stay within GPT-2 family, can try Option 4 (openai-community org) or Option 2 (downgrade libs), but both require more debugging time.

## Files Affected

- All `experiment_results_gpt2_medium_*.json` files contain invalid NaN data
- `gpt2_medium_rerun.log` shows processing but all results are NaN
- `entropy_analysis_gpt2_medium.txt` shows all NaN values

## Next Steps

Awaiting user decision on which option to pursue.
