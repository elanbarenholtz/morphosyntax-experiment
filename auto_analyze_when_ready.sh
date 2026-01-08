#!/bin/bash

# Auto-analyze models as they complete

echo "Waiting for experiments to complete..."
echo "Will automatically run entropy analysis when ready."
echo ""

MEDIUM_DONE=false
LARGE_DONE=false

while true; do
  # Check medium
  if [ "$MEDIUM_DONE" = false ] && [ -f "experiment_results_gpt2_medium_scrambled.json" ]; then
    MEDIUM_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_medium_scrambled.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
    if [ "$MEDIUM_COUNT" = "30" ]; then
      echo "[$(date '+%H:%M:%S')] ✓ GPT-2-medium complete! Running entropy analysis..."
      python3 analyze_entropy_effects.py --results experiment_results_gpt2_medium_scrambled.json > entropy_analysis_gpt2_medium.txt 2>&1
      echo "[$(date '+%H:%M:%S')] ✓ GPT-2-medium entropy analysis complete!"
      MEDIUM_DONE=true
    fi
  fi

  # Check large
  if [ "$LARGE_DONE" = false ] && [ -f "experiment_results_gpt2_large_scrambled.json" ]; then
    LARGE_COUNT=$(python3 -c "import json; f=open('experiment_results_gpt2_large_scrambled.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
    if [ "$LARGE_COUNT" = "30" ]; then
      echo "[$(date '+%H:%M:%S')] ✓ GPT-2-large complete! Running entropy analysis..."
      python3 analyze_entropy_effects.py --results experiment_results_gpt2_large_scrambled.json > entropy_analysis_gpt2_large.txt 2>&1
      echo "[$(date '+%H:%M:%S')] ✓ GPT-2-large entropy analysis complete!"
      LARGE_DONE=true
    fi
  fi

  # Check if both done
  if [ "$MEDIUM_DONE" = true ] && [ "$LARGE_DONE" = true ]; then
    echo ""
    echo "================================================================"
    echo "ALL ANALYSES COMPLETE!"
    echo "================================================================"
    echo ""
    echo "Results:"
    echo "  - entropy_analysis_gpt2_medium.txt"
    echo "  - entropy_analysis_gpt2_large.txt"
    echo ""
    echo "Creating scaling comparison plot..."
    python3 create_scaling_plot.py
    echo ""
    echo "Done! Check scaling_analysis_plot.png"
    break
  fi

  sleep 30
done
