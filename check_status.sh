#!/bin/bash
# Quick Status Checker for Morphosyntax Experiment
# Run this anytime to see what's completed and what's running

cd /Users/elanbarenholtz/morphosyntax-experiment

echo "================================================================================"
echo "MORPHOSYNTAX EXPERIMENT - STATUS CHECK"
echo "================================================================================"
echo ""
echo "Location: $(pwd)"
echo "Date: $(date)"
echo ""

# ============================================================================
# COMPREHENSIVE FRAMEWORK FILES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. COMPREHENSIVE FRAMEWORK (Main Analysis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Core Scripts:"
for file in cue_families.py word_level_analysis.py run_comprehensive_audit.py analyze_comprehensive_results.py; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

echo "Stimulus Files:"
for file in stimuli_comprehensive.json generate_comprehensive_stimuli.py; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "  ✓ $file ($size)"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

echo "Context Ablation Scripts:"
for file in run_context_ablation.py analyze_context_ablation.py; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

echo "Documentation:"
for file in COMPREHENSIVE_INVESTIGATION_README.md CONTEXT_ABLATION_README.md Comprehensive_Morphosyntax_Audit_Colab.ipynb PROJECT_SUMMARY.md; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
    fi
done
echo ""

# ============================================================================
# COMPREHENSIVE AUDIT RESULTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. COMPREHENSIVE AUDIT RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

MODELS=(
    "gpt2:GPT-2 (124M)"
    "gpt2-medium:GPT-2-medium (355M)"
    "gpt2-large:GPT-2-large (774M)"
    "EleutherAI_pythia-160m:Pythia-160m"
    "EleutherAI_pythia-410m:Pythia-410m"
)

for model_info in "${MODELS[@]}"; do
    model="${model_info%%:*}"
    name="${model_info##*:}"

    result_file="comprehensive_audit_${model}.json"
    csv_file="comprehensive_audit_${model}_comparisons.csv"

    if [ -f "$result_file" ]; then
        size=$(ls -lh "$result_file" | awk '{print $5}')
        echo "  ✓ $name"
        echo "    - Results: $result_file ($size)"

        if [ -f "$csv_file" ]; then
            echo "    - Analysis: $csv_file"
        fi

        # Count plots
        plot_count=$(ls comprehensive_audit_${model}_*.png 2>/dev/null | wc -l)
        if [ "$plot_count" -gt 0 ]; then
            echo "    - Plots: $plot_count files"
        fi
    else
        echo "  ✗ $name (not run)"
    fi
done
echo ""

# ============================================================================
# CONTEXT ABLATION RESULTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. CONTEXT ABLATION RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for model_info in "${MODELS[@]}"; do
    model="${model_info%%:*}"
    name="${model_info##*:}"

    ablation_file="context_ablation_${model}.csv"

    if [ -f "$ablation_file" ]; then
        size=$(ls -lh "$ablation_file" | awk '{print $5}')
        echo "  ✓ $name"
        echo "    - Data: $ablation_file ($size)"

        # Check for summary files
        for family in infinitival_to determiners; do
            summary="context_ablation_${model}_${family}_summary.csv"
            plot="context_ablation_${model}_${family}_ablation_plot.png"

            if [ -f "$summary" ]; then
                echo "    - ${family}: summary + plot"
            fi
        done
    else
        echo "  ✗ $name (not run)"
    fi
done
echo ""

# ============================================================================
# LEGACY EXPERIMENT RESULTS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. LEGACY EXPERIMENT RESULTS (Earlier Work)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Experiment Result Files:"
ls -lh experiment_results_*.json 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  (none found)"
echo ""

echo "Entropy Analysis Files:"
ls -lh entropy_analysis_*.txt 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  (none found)"
echo ""

echo "Output Logs:"
ls -lh *_output.log 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}' || echo "  (none found)"
echo ""

# ============================================================================
# BACKGROUND PROCESSES
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. RUNNING PROCESSES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python_procs=$(ps aux | grep -E "python3.*run_" | grep -v grep | wc -l)
if [ "$python_procs" -gt 0 ]; then
    echo "Active Python processes: $python_procs"
    echo ""
    ps aux | grep -E "python3.*run_" | grep -v grep | awk '{print "  PID " $2 ": " $11 " " $12 " " $13}'
else
    echo "No active Python experiment processes detected."
fi
echo ""

# ============================================================================
# ENVIRONMENT
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. ENVIRONMENT STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -d "venv" ]; then
    echo "  ✓ Virtual environment: venv/"

    if [ -n "$VIRTUAL_ENV" ]; then
        echo "  ✓ Currently activated: $VIRTUAL_ENV"
    else
        echo "  ⚠ Not activated (run: source venv/bin/activate)"
    fi
else
    echo "  ✗ Virtual environment not found"
fi
echo ""

# ============================================================================
# QUICK ACTIONS
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. QUICK ACTIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To run comprehensive audit (single model test):"
echo "  source venv/bin/activate"
echo "  python3 run_comprehensive_audit.py --model gpt2"
echo ""
echo "To analyze existing results:"
echo "  python3 analyze_comprehensive_results.py comprehensive_audit_gpt2.json"
echo ""
echo "To run all 5 models:"
echo "  ./run_cross_model_replication.sh"
echo ""
echo "To check this status again:"
echo "  ./check_status.sh"
echo ""
echo "For full documentation:"
echo "  cat PROJECT_SUMMARY.md"
echo ""
echo "================================================================================"
