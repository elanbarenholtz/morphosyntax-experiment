#!/bin/bash
while true; do
  clear
  echo "================================================================================"
  echo "ENTROPY VALIDATION: Model Scaling Analysis"
  echo "================================================================================"
  echo ""
  
  # Check completed models
  echo "COMPLETED (with entropy analysis):"
  echo "  ✓ GPT-2 base (124M)     - Δ Entropy: -0.427 bits (d=-0.557)"
  echo "  ✓ Pythia-410m (410M)    - Δ Entropy: -0.270 bits (d=-0.382)"
  echo ""
  
  # Check in-progress models
  echo "IN PROGRESS (all 7 conditions):"
  
  if [ -f "experiment_results_gpt2_medium_final.json" ]; then
    MEDIUM_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_medium_final.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    MEDIUM_COUNT=0
  fi
  
  if [ -f "experiment_results_gpt2_large_final.json" ]; then
    LARGE_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_large_final.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    LARGE_COUNT=0
  fi
  
  # Progress bars
  MEDIUM_PROG=$(python3 -c "print('█' * int($MEDIUM_COUNT * 30 / 30) + '░' * (30 - int($MEDIUM_COUNT * 30 / 30)))")
  LARGE_PROG=$(python3 -c "print('█' * int($LARGE_COUNT * 30 / 30) + '░' * (30 - int($LARGE_COUNT * 30 / 30)))")
  
  printf "  GPT-2-medium (355M):  [%s] %2d/30\n" "$MEDIUM_PROG" "$MEDIUM_COUNT"
  printf "  GPT-2-large  (774M):  [%s] %2d/30\n" "$LARGE_PROG" "$LARGE_COUNT"
  
  echo ""
  echo "Estimated time: ~6 min (medium), ~15 min (large)"
  echo "Last updated: $(date '+%H:%M:%S')"
  
  # Check if both complete
  if [ "$MEDIUM_COUNT" = "30" ] && [ "$LARGE_COUNT" = "30" ]; then
    echo ""
    echo "✓ ALL MODELS COMPLETE! Running entropy analysis..."
    break
  fi
  
  sleep 10
done

# Auto-run entropy analysis when complete
if [ "$MEDIUM_COUNT" = "30" ]; then
  echo "Analyzing GPT-2-medium..."
  python3 analyze_entropy_effects.py --results experiment_results_gpt2_medium_final.json > entropy_analysis_gpt2_medium.txt 2>&1
  echo "✓ GPT-2-medium analysis complete!"
fi

if [ "$LARGE_COUNT" = "30" ]; then
  echo "Analyzing GPT-2-large..."
  python3 analyze_entropy_effects.py --results experiment_results_gpt2_large_final.json > entropy_analysis_gpt2_large.txt 2>&1
  echo "✓ GPT-2-large analysis complete!"
fi

echo ""
echo "Creating scaling comparison plot..."
python3 create_scaling_plot.py
echo "✓ Done! Check scaling_analysis_plot.png"
