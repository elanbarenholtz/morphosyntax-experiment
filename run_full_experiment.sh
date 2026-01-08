#!/bin/bash

# Full experiment runner for morphosyntax constraint testing
# This script runs all three steps of the experiment

set -e  # Exit on error

echo "======================================================================"
echo "MORPHOSYNTAX CONSTRAINT EXPERIMENT"
echo "======================================================================"
echo ""

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "Loading API key from .env file..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "ERROR: OPENAI_API_KEY not set!"
        echo ""
        echo "Please either:"
        echo "  1. Set environment variable: export OPENAI_API_KEY='your-key'"
        echo "  2. Create .env file: cp .env.template .env (then edit)"
        echo ""
        exit 1
    fi
fi

# Check for required packages
echo "Checking dependencies..."
python3 -c "import openai, numpy, scipy, pandas, matplotlib, seaborn" 2>/dev/null || {
    echo "Missing dependencies! Installing..."
    pip3 install -r requirements.txt
}

echo ""
echo "======================================================================"
echo "STEP 1: Generating stimuli"
echo "======================================================================"
echo ""
python3 generate_stimuli.py

echo ""
echo "======================================================================"
echo "STEP 2: Running experiment (this may take 5-10 minutes)"
echo "======================================================================"
echo ""
python3 run_experiment.py

echo ""
echo "======================================================================"
echo "STEP 3: Analyzing results"
echo "======================================================================"
echo ""
python3 analyze_results.py

echo ""
echo "======================================================================"
echo "EXPERIMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "Check the following files:"
echo "  - analysis_summary.txt (summary report)"
echo "  - visualizations/ (plots)"
echo "  - experiment_data.csv (raw data)"
echo "  - statistical_tests.csv (test results)"
echo ""
