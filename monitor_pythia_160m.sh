#!/bin/bash
echo "Monitoring Pythia-160m experiment..."
echo "Started: $(date '+%H:%M:%S')"
echo ""

while true; do
  if [ -f "experiment_results_pythia_160m_final.json" ]; then
    COUNT=$(python3 -c "import json; f=open('experiment_results_pythia_160m_final.json'); d=json.load(f); print(len(d))" 2>/dev/null || echo "0")
  else
    COUNT=0
  fi
  
  PROG=$(python3 -c "print('█' * int($COUNT * 30 / 30) + '░' * (30 - int($COUNT * 30 / 30)))")
  
  clear
  echo "================================================================================"
  echo "PYTHIA-160M EXPERIMENT (Intermediate Data Point)"
  echo "================================================================================"
  echo ""
  printf "  Progress: [%s] %2d/30\n" "$PROG" "$COUNT"
  echo ""
  echo "  Last updated: $(date '+%H:%M:%S')"
  echo "  ETA: ~20 minutes from start"
  echo ""
  
  if [ "$COUNT" = "30" ]; then
    echo "✓ COMPLETE! Running entropy analysis..."
    source venv/bin/activate
    python3 analyze_entropy_effects.py --results experiment_results_pythia_160m_final.json > entropy_analysis_pythia_160m.txt 2>&1
    echo "✓ Entropy analysis complete!"
    echo ""
    echo "Results saved to:"
    echo "  - experiment_results_pythia_160m_final.json"
    echo "  - entropy_analysis_pythia_160m.txt"
    break
  fi
  
  sleep 10
done
