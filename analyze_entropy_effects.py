"""
Proper analysis of syntactic constraint effects using ENTROPY.

Key insight: Syntax might constrain predictions (reduce entropy) without
helping predict nonce identity (surprisal stays high).

Three analyses:
1. Entropy comparison: Δ(Jabberwocky - Scrambled)
2. Function-word vs content-word split
3. Confident-wrong diagnostic: entropy vs surprisal gap
"""

import json
import numpy as np
from collections import defaultdict

# Function words for splitting analysis
FUNCTION_WORDS = {
    'the', 'a', 'an', 'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with',
    'from', 'as', 'is', 'was', 'were', 'are', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
    'could', 'may', 'might', 'must', 'can', 'shall', 'that', 'this',
    'these', 'those', 'it', 'its', 'they', 'them', 'their', 'he', 'she',
    'him', 'her', 'his', 'hers', 'we', 'us', 'our', 'ours', 'you', 'your',
    'yours', 'i', 'me', 'my', 'mine', 'and', 'or', 'but', 'if', 'when',
    'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
}

def analyze_entropy_effects(results_file):
    """
    Analyze entropy effects with three key comparisons.
    """
    print("=" * 80)
    print("ENTROPY ANALYSIS: Testing Syntactic Constraint")
    print("=" * 80)

    with open(results_file, 'r') as f:
        results = json.load(f)

    # ========================================================================
    # ANALYSIS 1: Entropy Comparison (Main Test)
    # ========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 1: ENTROPY COMPARISON")
    print("=" * 80)
    print("\nQuestion: Does syntax constrain predictions (reduce entropy)?")
    print("Test: Δ(Jabberwocky - Scrambled Jabberwocky)\n")

    # Collect entropy values
    jab_entropy = []
    scram_entropy = []
    jab_surprisal = []
    scram_surprisal = []

    for item in results:
        if 'jabberwocky_matched' in item['conditions'] and 'scrambled_jabberwocky' in item['conditions']:
            jab_entropy.append(item['conditions']['jabberwocky_matched']['mean_word_entropy'])
            scram_entropy.append(item['conditions']['scrambled_jabberwocky']['mean_word_entropy'])
            jab_surprisal.append(item['conditions']['jabberwocky_matched']['mean_word_surprisal'])
            scram_surprisal.append(item['conditions']['scrambled_jabberwocky']['mean_word_surprisal'])

    # Compute statistics
    jab_ent_mean = np.mean(jab_entropy)
    jab_ent_se = np.std(jab_entropy) / np.sqrt(len(jab_entropy))
    scram_ent_mean = np.mean(scram_entropy)
    scram_ent_se = np.std(scram_entropy) / np.sqrt(len(scram_entropy))

    jab_surp_mean = np.mean(jab_surprisal)
    jab_surp_se = np.std(jab_surprisal) / np.sqrt(len(jab_surprisal))
    scram_surp_mean = np.mean(scram_surprisal)
    scram_surp_se = np.std(scram_surprisal) / np.sqrt(len(scram_surprisal))

    delta_entropy = jab_ent_mean - scram_ent_mean
    delta_surprisal = jab_surp_mean - scram_surp_mean

    print(f"Jabberwocky (Syntax):          {jab_ent_mean:.3f} ± {jab_ent_se:.3f} bits (entropy)")
    print(f"Scrambled (No Structure):      {scram_ent_mean:.3f} ± {scram_ent_se:.3f} bits (entropy)")
    print(f"Δ Entropy (Syntax - Scrambled): {delta_entropy:.3f} bits")
    print(f"\nInterpretation: {'Syntax REDUCES entropy (increases constraint)' if delta_entropy < 0 else 'Syntax INCREASES entropy (reduces constraint)'}")

    print(f"\nFor comparison:")
    print(f"Jabberwocky surprisal:         {jab_surp_mean:.3f} ± {jab_surp_se:.3f} bits")
    print(f"Scrambled surprisal:           {scram_surp_mean:.3f} ± {scram_surp_se:.3f} bits")
    print(f"Δ Surprisal:                   {delta_surprisal:.3f} bits")

    # Compute effect size (Cohen's d)
    pooled_std_ent = np.sqrt((np.std(jab_entropy)**2 + np.std(scram_entropy)**2) / 2)
    cohens_d_ent = delta_entropy / pooled_std_ent if pooled_std_ent > 0 else 0

    pooled_std_surp = np.sqrt((np.std(jab_surprisal)**2 + np.std(scram_surprisal)**2) / 2)
    cohens_d_surp = delta_surprisal / pooled_std_surp if pooled_std_surp > 0 else 0

    print(f"\nEffect sizes (Cohen's d):")
    print(f"  Entropy:   d = {cohens_d_ent:.3f}")
    print(f"  Surprisal: d = {cohens_d_surp:.3f}")

    # ========================================================================
    # ANALYSIS 2: Function-word vs Content-word Split
    # ========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 2: FUNCTION-WORD vs CONTENT-WORD SPLIT")
    print("=" * 80)
    print("\nQuestion: Does structure matter more for function-word targets?")
    print("Prediction: Structure should constrain function words more than content words\n")

    # Split by position type
    fw_jab_ent = []
    fw_scram_ent = []
    fw_jab_surp = []
    fw_scram_surp = []

    cw_jab_ent = []
    cw_scram_ent = []
    cw_jab_surp = []
    cw_scram_surp = []

    for item in results:
        if 'jabberwocky_matched' in item['conditions'] and 'scrambled_jabberwocky' in item['conditions']:
            jab_text = item['conditions']['jabberwocky_matched']['text']
            jab_words = jab_text.split()

            jab_word_ents = item['conditions']['jabberwocky_matched'].get('word_entropies', [])
            scram_word_ents = item['conditions']['scrambled_jabberwocky'].get('word_entropies', [])
            jab_word_surps = item['conditions']['jabberwocky_matched'].get('word_surprisals', [])
            scram_word_surps = item['conditions']['scrambled_jabberwocky'].get('word_surprisals', [])

            # Classify each position
            for i, word in enumerate(jab_words):
                if i < len(jab_word_ents) and i < len(scram_word_ents):
                    if word.lower() in FUNCTION_WORDS:
                        # Function word position
                        fw_jab_ent.append(jab_word_ents[i])
                        fw_scram_ent.append(scram_word_ents[i])
                        if i < len(jab_word_surps):
                            fw_jab_surp.append(jab_word_surps[i])
                            fw_scram_surp.append(scram_word_surps[i])
                    else:
                        # Content word position
                        cw_jab_ent.append(jab_word_ents[i])
                        cw_scram_ent.append(scram_word_ents[i])
                        if i < len(jab_word_surps):
                            cw_jab_surp.append(jab_word_surps[i])
                            cw_scram_surp.append(scram_word_surps[i])

    # Function words
    print("Function-word positions:")
    if fw_jab_ent:
        fw_jab_ent_m = np.mean(fw_jab_ent)
        fw_scram_ent_m = np.mean(fw_scram_ent)
        fw_delta_ent = fw_jab_ent_m - fw_scram_ent_m

        fw_jab_surp_m = np.mean(fw_jab_surp) if fw_jab_surp else 0
        fw_scram_surp_m = np.mean(fw_scram_surp) if fw_scram_surp else 0
        fw_delta_surp = fw_jab_surp_m - fw_scram_surp_m

        print(f"  Entropy:   Jab {fw_jab_ent_m:.3f} vs Scram {fw_scram_ent_m:.3f} → Δ = {fw_delta_ent:.3f} bits")
        print(f"  Surprisal: Jab {fw_jab_surp_m:.3f} vs Scram {fw_scram_surp_m:.3f} → Δ = {fw_delta_surp:.3f} bits")

    # Content words
    print("\nContent-word positions:")
    if cw_jab_ent:
        cw_jab_ent_m = np.mean(cw_jab_ent)
        cw_scram_ent_m = np.mean(cw_scram_ent)
        cw_delta_ent = cw_jab_ent_m - cw_scram_ent_m

        cw_jab_surp_m = np.mean(cw_jab_surp) if cw_jab_surp else 0
        cw_scram_surp_m = np.mean(cw_scram_surp) if cw_scram_surp else 0
        cw_delta_surp = cw_jab_surp_m - cw_scram_surp_m

        print(f"  Entropy:   Jab {cw_jab_ent_m:.3f} vs Scram {cw_scram_ent_m:.3f} → Δ = {cw_delta_ent:.3f} bits")
        print(f"  Surprisal: Jab {cw_jab_surp_m:.3f} vs Scram {cw_scram_surp_m:.3f} → Δ = {cw_delta_surp:.3f} bits")

    # ========================================================================
    # ANALYSIS 3: Confident-Wrong Diagnostic
    # ========================================================================
    print("\n" + "=" * 80)
    print("ANALYSIS 3: CONFIDENT-WRONG DIAGNOSTIC")
    print("=" * 80)
    print("\nQuestion: Does structure make models confident but wrong?")
    print("Signature: Lower entropy (more committed) but similar/higher surprisal (still wrong)\n")

    # For each condition, compute entropy, surprisal, and gap
    conditions = ['sentence', 'jabberwocky_matched', 'scrambled_jabberwocky',
                  'word_list_nonce_2tok']

    print(f"{'Condition':30s} | {'Entropy':>8s} | {'Surprisal':>10s} | {'Gap (S-E)':>10s}")
    print("-" * 70)

    for condition in conditions:
        entropies = []
        surprisals = []

        for item in results:
            if condition in item['conditions']:
                entropies.append(item['conditions'][condition]['mean_word_entropy'])
                surprisals.append(item['conditions'][condition]['mean_word_surprisal'])

        if entropies:
            ent_mean = np.mean(entropies)
            surp_mean = np.mean(surprisals)
            gap_mean = surp_mean - ent_mean

            print(f"{condition:30s} | {ent_mean:8.3f} | {surp_mean:10.3f} | {gap_mean:10.3f}")

    print("\nInterpretation:")
    print("  Entropy: Model's uncertainty (bits). Lower = more committed.")
    print("  Surprisal: Model's error (bits). Higher = worse prediction.")
    print("  Gap (S-E): 'Confident-wrong' index. Positive = confident but wrong.")
    print("\nIf Jabberwocky has:")
    print("  - Lower entropy than Scrambled → structure increases commitment")
    print("  - Similar/higher surprisal → but doesn't help with nonce identity")
    print("  → Structure engages prediction without improving lexical accuracy")

    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\nKey Result 1: Δ Entropy (Jabberwocky - Scrambled) = {delta_entropy:.3f} bits")
    if delta_entropy < -0.1:
        print("  → Syntax REDUCES entropy (increases constraint) ✓")
    elif delta_entropy > 0.1:
        print("  → Syntax INCREASES entropy (reduces constraint)")
    else:
        print("  → Syntax has MINIMAL effect on entropy")

    print(f"\nKey Result 2: Δ Surprisal (Jabberwocky - Scrambled) = {delta_surprisal:.3f} bits")
    if abs(delta_surprisal) < 0.3:
        print("  → Syntax does NOT help predict nonce identity")

    print("\nConclusion:")
    if delta_entropy < -0.1 and abs(delta_surprisal) < 0.3:
        print("  Syntax constrains predictions (↓ entropy) without improving")
        print("  nonce accuracy (~ surprisal). This is the 'confident-wrong'")
        print("  signature: structure engages prediction but can't overcome")
        print("  the fundamental unpredictability of novel lexical items.")
    elif abs(delta_entropy) < 0.1 and abs(delta_surprisal) < 0.3:
        print("  Syntax provides minimal constraint in absence of semantics.")
        print("  Both entropy and surprisal are unaffected by structure.")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze entropy effects')
    parser.add_argument('--results', type=str, required=True,
                       help='Results file to analyze')

    args = parser.parse_args()

    analyze_entropy_effects(args.results)
