#!/bin/bash
echo "Monitoring GPT-2-medium rerun..."
echo "Started: $(date '+%H:%M:%S')"
echo ""

while true; do
  if [ -f "experiment_results_gpt2_medium_final.json" ]; then
    COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_medium_final.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    COUNT=0
  fi
  
  PROG=$(python3 -c "print('█' * int($COUNT * 30 / 30) + '░' * (30 - int($COUNT * 30 / 30)))")
  
  clear
  echo "================================================================================"
  echo "GPT-2-MEDIUM RERUN (Corrected Pipeline)"
  echo "================================================================================"
  echo ""
  printf "  Progress: [%s] %2d/30\n" "$PROG" "$COUNT"
  echo ""
  echo "  Last updated: $(date '+%H:%M:%S')"
  echo "  ETA: ~30 minutes from start"
  echo ""
  
  if [ "$COUNT" = "30" ]; then
    echo "✓ COMPLETE! Running entropy analysis..."
    python3 analyze_entropy_effects.py --results experiment_results_gpt2_medium_final.json > entropy_analysis_gpt2_medium.txt 2>&1
    echo "✓ Entropy analysis complete!"
    echo ""
    echo "Results saved to:"
    echo "  - experiment_results_gpt2_medium_final.json"
    echo "  - entropy_analysis_gpt2_medium.txt"
    break
  fi
  
  sleep 10
done
