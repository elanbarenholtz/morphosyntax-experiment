#!/bin/bash
#
# Cross-Model Replication Script for Comprehensive Morphosyntax Audit
#
# Runs comprehensive audit across 5 models:
# - GPT-2 (124M)
# - GPT-2-medium (355M)
# - GPT-2-large (774M)
# - Pythia-160m (160M)
# - Pythia-410m (410M)
#

set -e  # Exit on error

echo "================================================================================"
echo "COMPREHENSIVE MORPHOSYNTAX AUDIT: CROSS-MODEL REPLICATION"
echo "================================================================================"
echo ""
echo "This will run comprehensive audit on 5 models."
echo "Expected runtime: ~5-10 hours total (depending on hardware)"
echo ""

# Activate environment
source venv/bin/activate

# Models to test
MODELS=(
    "gpt2"
    "gpt2-medium"
    "gpt2-large"
    "EleutherAI/pythia-160m"
    "EleutherAI/pythia-410m"
)

# Check if stimuli exists
if [ ! -f "stimuli_comprehensive.json" ]; then
    echo "ERROR: stimuli_comprehensive.json not found!"
    echo "Please run: python3 generate_comprehensive_stimuli.py"
    exit 1
fi

echo "✓ Found stimuli_comprehensive.json"
echo ""

# Run each model
for MODEL in "${MODELS[@]}"; do
    # Create safe filename
    MODEL_SLUG=$(echo "$MODEL" | tr '/' '_')
    OUTPUT_FILE="comprehensive_audit_${MODEL_SLUG}.json"

    echo "================================================================================"
    echo "MODEL: $MODEL"
    echo "================================================================================"
    echo "Output: $OUTPUT_FILE"
    echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # Check if already complete
    if [ -f "$OUTPUT_FILE" ]; then
        echo "⚠ Output file already exists. Skipping."
        echo "   (Delete $OUTPUT_FILE to re-run)"
        echo ""
        continue
    fi

    # Run audit
    python3 run_comprehensive_audit.py \
        --model "$MODEL" \
        --stimuli stimuli_comprehensive.json \
        --output "$OUTPUT_FILE" \
        --method lexicon \
        --top-k 1000

    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        echo ""
        echo "✓ $MODEL complete!"
        echo "  Results saved to: $OUTPUT_FILE"
        echo "  Completed: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
    else
        echo ""
        echo "✗ $MODEL failed with exit code $EXIT_CODE"
        echo ""
        exit $EXIT_CODE
    fi

    # Brief pause between models
    sleep 5
done

echo "================================================================================"
echo "ALL MODELS COMPLETE!"
echo "================================================================================"
echo ""
echo "Results saved:"
for MODEL in "${MODELS[@]}"; do
    MODEL_SLUG=$(echo "$MODEL" | tr '/' '_')
    OUTPUT_FILE="comprehensive_audit_${MODEL_SLUG}.json"
    if [ -f "$OUTPUT_FILE" ]; then
        echo "  ✓ $OUTPUT_FILE"
    else
        echo "  ✗ $OUTPUT_FILE (MISSING)"
    fi
done

echo ""
echo "================================================================================"
echo "NEXT STEP: ANALYZE RESULTS"
echo "================================================================================"
echo ""
echo "Run statistical analysis for each model:"
echo ""

for MODEL in "${MODELS[@]}"; do
    MODEL_SLUG=$(echo "$MODEL" | tr '/' '_')
    OUTPUT_FILE="comprehensive_audit_${MODEL_SLUG}.json"
    if [ -f "$OUTPUT_FILE" ]; then
        echo "  python3 analyze_comprehensive_results.py $OUTPUT_FILE"
    fi
done

echo ""
echo "This will generate comparison tables and plots for each model."
echo ""
