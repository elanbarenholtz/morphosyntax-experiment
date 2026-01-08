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
  echo "IN PROGRESS:"
  
  if [ -f "experiment_results_gpt2_medium_scrambled.json" ]; then
    MEDIUM_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_medium_scrambled.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    MEDIUM_COUNT=0
  fi
  
  if [ -f "experiment_results_gpt2_large_scrambled.json" ]; then
    LARGE_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_large_scrambled.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    LARGE_COUNT=0
  fi
  
  # Progress bars
  MEDIUM_PROG=$(python3 -c "print('█' * int($MEDIUM_COUNT * 30 / 30) + '░' * (30 - int($MEDIUM_COUNT * 30 / 30)))")
  LARGE_PROG=$(python3 -c "print('█' * int($LARGE_COUNT * 30 / 30) + '░' * (30 - int($LARGE_COUNT * 30 / 30)))")
  
  printf "  GPT-2-medium (355M):  [%s] %2d/30\n" "$MEDIUM_PROG" "$MEDIUM_COUNT"
  printf "  GPT-2-large  (774M):  [%s] %2d/30\n" "$LARGE_PROG" "$LARGE_COUNT"
  
  echo ""
  echo "Last updated: $(date '+%H:%M:%S')"
  
  # Check if both complete
  if [ "$MEDIUM_COUNT" = "30" ] && [ "$LARGE_COUNT" = "30" ]; then
    echo ""
    echo "✓ ALL MODELS COMPLETE! Ready for entropy analysis."
    break
  fi
  
  sleep 10
done
