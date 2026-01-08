# Morphosyntax Constraint Experiment

This experiment tests whether morphosyntactic tokens (function words and morphological markers) constrain next-token predictions in language models, even when surrounded by nonsense content words.

## Hypothesis

"Syntax" is an epiphenomenon of distributional learning over high-leverage tokens (function words like THE, WAS, TO and morphological markers like -ING, -ED, -LY) rather than a separate rule-governed system.

## Experimental Design

### Four Conditions

1. **Real Sentences**: Grammatical English sentences with real content words
2. **Jabberwocky**: Function words + morphology intact, content words → phonotactically legal nonwords
3. **Stripped**: All nonwords, no function words, no morphological markers
4. **Random Nonwords**: Completely random nonwords (floor condition)

### Example Stimulus Set

```
Sentence:    "The teacher was explaining the concept to the students clearly"
Jabberwocky: "The blicket was florping the daxen to the wuggles grentily"
Stripped:    "Ke blicket nar florp ke daxen po ke wuggle grenti"
Nonwords:    "Ke blicket nar florp daxen po wuggle grenti borp"
```

### Predictions

If function words and morphology constrain predictions distributionally:
- **Entropy**: Sentences < Jabberwocky < Stripped ≈ Nonwords
- The **Jabberwocky vs Stripped** comparison is critical
- Within Jabberwocky, entropy should be lower after function words

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with pip3:
```bash
pip3 install -r requirements.txt
```

### 2. Configure OpenAI API Key

**Option A: Environment variable**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Option B: .env file** (recommended)
```bash
cp .env.template .env
# Edit .env and add your actual API key
```

## Running the Experiment

### Step 1: Generate Stimuli

```bash
python3 generate_stimuli.py
```

This creates `stimuli.json` with 30 matched stimulus sets (120 items total).

### Step 2: Run Experiment

```bash
python3 run_experiment.py
```

This:
- Sends each stimulus to the OpenAI API
- Collects token-by-token logprobs
- Calculates entropy metrics
- Saves results to `experiment_results.json`

**Note**: This will make ~120 API calls and may take 5-10 minutes with rate limiting.

### Step 3: Analyze Results

```bash
python3 analyze_results.py
```

This generates:
- `experiment_data.csv` - Raw data table
- `statistical_tests.csv` - Paired t-tests and effect sizes
- `analysis_summary.txt` - Interpretable summary report
- `visualizations/` directory with plots:
  - Mean entropy by condition (bar plot)
  - Entropy by token position (line plot)
  - Distribution comparison (violin plot)
  - Paired comparisons (scatter plots)

## Measurements

For each stimulus:

1. **Token-by-token entropy**: H = -Σ p(token) × log₂(p(token))
2. **Top-1 probability**: Probability of most likely next token
3. **Mean entropy**: Average across all token positions
4. **Sequence perplexity**: exp(mean negative log likelihood)

## Statistical Analysis

### Key Comparisons

1. **Jabberwocky vs Stripped** - Tests function word contribution
2. **Jabberwocky vs Nonwords** - Tests total morphosyntactic contribution
3. **Sentence vs Jabberwocky** - Tests content word contribution

### Methods

- Paired t-tests (parametric)
- Wilcoxon signed-rank tests (non-parametric)
- Cohen's d effect sizes
- Position-level analysis

## Project Structure

```
morphosyntax-experiment/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.template                # API key template
├── generate_stimuli.py          # Stimulus generation
├── run_experiment.py            # Main experiment script
├── analyze_results.py           # Analysis and visualization
├── stimuli.json                 # Generated stimuli (created)
├── experiment_results.json      # Raw results (created)
├── experiment_data.csv          # Processed data (created)
├── statistical_tests.csv        # Test results (created)
├── analysis_summary.txt         # Summary report (created)
└── visualizations/              # Plots (created)
    ├── mean_entropy_by_condition.png
    ├── entropy_by_position.png
    ├── entropy_distribution.png
    └── paired_comparisons.png
```

## Expected Results

If the hypothesis is correct:

1. Jabberwocky should show **lower entropy** than Stripped (function words constrain predictions)
2. Effect size (Cohen's d) should be **moderate to large** (d > 0.5)
3. Position analysis should show **entropy dips** after function words in Jabberwocky
4. Stripped ≈ Nonwords (no structure without morphosyntax)

## Cost Estimate

- **Model**: GPT-3.5-turbo
- **API calls**: ~120 requests
- **Tokens per call**: ~50-100 tokens
- **Estimated cost**: $0.10 - $0.20 USD

## Troubleshooting

**No logprobs returned**: Ensure you're using a model that supports logprobs (GPT-3.5-turbo or GPT-4)

**Rate limit errors**: The script includes 0.5s delays between requests. Increase if needed.

**Import errors**: Install missing packages with `pip install <package>`

## Citation

If you use this experiment in research, please cite:

```
Morphosyntax Constraint Experiment (2025)
Testing distributional learning of syntactic constraints in language models
```
