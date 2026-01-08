#!/bin/bash
# =============================================================================
# Locked Design Morphosyntax Audit - Full Pipeline
# =============================================================================
#
# This script runs the complete experiment pipeline:
# 1. Generate locked stimuli (if not present)
# 2. Run audit with context ablation
# 3. Analyze results
# 4. Generate publication-ready figures
#
# Usage:
#   ./run_locked_pipeline.sh                    # Run with GPT-2
#   ./run_locked_pipeline.sh gpt2-medium        # Run with GPT-2 Medium
#   ./run_locked_pipeline.sh EleutherAI/pythia-410m  # Run with Pythia
#
# =============================================================================

set -e  # Exit on error

# Default model
MODEL=${1:-gpt2}
MODEL_SLUG=$(echo "$MODEL" | sed 's/\//_/g')

echo "=============================================="
echo "LOCKED DESIGN MORPHOSYNTAX AUDIT PIPELINE"
echo "=============================================="
echo ""
echo "Model: $MODEL"
echo "Model slug: $MODEL_SLUG"
echo ""

# Activate virtual environment
source venv/bin/activate

# Step 1: Generate stimuli (if needed)
if [ ! -f "stimuli_locked.json" ]; then
    echo "[Step 1/4] Generating locked stimuli..."
    python3 generate_locked_stimuli.py
    echo ""
else
    echo "[Step 1/4] Stimuli already exist: stimuli_locked.json"
    echo ""
fi

# Step 2: Run audit with context ablation
AUDIT_FILE="locked_audit_${MODEL_SLUG}.json"
if [ ! -f "$AUDIT_FILE" ]; then
    echo "[Step 2/4] Running audit with context ablation..."
    python3 run_locked_audit.py \
        --model "$MODEL" \
        --stimuli stimuli_locked.json \
        --output "$AUDIT_FILE" \
        --context-lengths 1,2,4,8,-1 \
        --top-k 1000
    echo ""
else
    echo "[Step 2/4] Audit already exists: $AUDIT_FILE"
    echo ""
fi

# Step 3: Analyze results
echo "[Step 3/4] Analyzing results..."
python3 analyze_locked_results.py "$AUDIT_FILE" --output-prefix "locked_audit_${MODEL_SLUG}"
echo ""

# Step 4: Generate figures
echo "[Step 4/4] Generating figures..."
mkdir -p figures
python3 generate_locked_figures.py "$AUDIT_FILE" --output-dir figures
echo ""

echo "=============================================="
echo "PIPELINE COMPLETE"
echo "=============================================="
echo ""
echo "Output files:"
echo "  Stimuli:    stimuli_locked.json"
echo "  Audit:      $AUDIT_FILE"
echo "  Summary:    locked_audit_${MODEL_SLUG}_summary.csv"
echo "  Contrasts:  locked_audit_${MODEL_SLUG}_contrasts.csv"
echo "  Ablation:   locked_audit_${MODEL_SLUG}_ablation.csv"
echo "  Figures:    figures/"
echo ""
echo "Sanity check log: stimuli_locked_sanity_check.log"
