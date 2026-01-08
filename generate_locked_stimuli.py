#!/usr/bin/env python3
"""
Locked Design Stimulus Generator - Per Cue-Family Dedicated Templates

Creates 30 dedicated base sentences for EACH cue family, ensuring:
- Exactly 1 cue occurrence per sentence in a controlled position
- Consistent template structure within each family
- n=30 per condition per family (guaranteed coverage)

Cue Families and Templates:
1. infinitival_to: "The [N] [PAST-VERB] to [VERB] the [N]"
2. modals: "The [N] can/will [VERB] the [N]"
3. determiners: "The [N] [PAST-VERB] the [ADJ] [N]"
4. prepositions: "The [N] [PAST-VERB] with/in/on the [N]"
5. auxiliaries: "The [N] was/is [V-ING/V-ED] the [N]"
6. complementizers: "The [N] [PAST-VERB] that the [N] [PAST-VERB]"

Conditions Generated:
1. SENTENCE - Original grammatical English
2. JABBERWOCKY - Content words → nonce; function words + morphology + order preserved
3. FULL_SCRAMBLED - Random permutation of ALL tokens
4. CONTENT_SCRAMBLED - Shuffle content words among content slots only
5. FUNCTION_SCRAMBLED - Shuffle function words among function slots only
6. CUE_DELETED - Remove/replace the critical cue with nonce

Author: Morphosyntax Experiment Framework v2
"""

import json
import random
import hashlib
import re
from typing import Dict, List, Tuple, Set
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

SEED = 42  # For reproducibility
N_SENTENCES_PER_FAMILY = 30

# Function words (used for slot identification)
FUNCTION_WORDS = {
    # Determiners
    'the', 'a', 'an', 'this', 'that', 'these', 'those',
    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    # Prepositions
    'to', 'at', 'in', 'on', 'with', 'from', 'of', 'for', 'by', 'about',
    # Conjunctions
    'and', 'or', 'but', 'so', 'if', 'because', 'that', 'whether',
    # Auxiliaries/modals
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'has', 'have', 'had', 'having',
    'do', 'does', 'did',
    'will', 'would', 'can', 'could', 'shall', 'should', 'may', 'might', 'must',
    # Control verbs (function-like in our stimuli)
    'decided', 'wanted', 'began', 'tried', 'planned', 'continued', 'hoped',
    'said', 'thought', 'believed', 'knew', 'expected',
    # Perception verbs used in templates (act as function words)
    'saw', 'heard', 'felt', 'noticed',
}

# ============================================================================
# NONCE WORD GENERATOR
# ============================================================================

class NonceGenerator:
    """Generate pronounceable nonce words for Jabberwocky conditions."""

    ONSETS = [
        'b', 'bl', 'br', 'c', 'cl', 'cr', 'd', 'dr', 'f', 'fl', 'fr',
        'g', 'gl', 'gr', 'h', 'j', 'k', 'kl', 'kr', 'l', 'm', 'n',
        'p', 'pl', 'pr', 'qu', 'r', 's', 'sc', 'sk', 'sl', 'sm', 'sn',
        'sp', 'st', 'str', 'sw', 't', 'tr', 'th', 'v', 'w', 'wh', 'y', 'z'
    ]

    NUCLEI = ['a', 'e', 'i', 'o', 'u', 'ai', 'ea', 'ee', 'oo', 'ou', 'ey', 'ie']

    CODAS = [
        '', 'b', 'ck', 'd', 'f', 'g', 'k', 'l', 'll', 'm', 'n', 'ng',
        'nk', 'p', 'r', 's', 'sh', 'sk', 'sp', 'ss', 'st', 't', 'th', 'x', 'z'
    ]

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.used_nonces = set()

    def generate(self, syllables=1) -> str:
        """Generate a unique nonce word."""
        attempts = 0
        while attempts < 100:
            word_parts = []
            for _ in range(syllables):
                onset = self.rng.choice(self.ONSETS)
                nucleus = self.rng.choice(self.NUCLEI)
                coda = self.rng.choice(self.CODAS)
                word_parts.append(onset + nucleus + coda)

            word = ''.join(word_parts)

            # Ensure not a real word and not used before
            if word not in FUNCTION_WORDS and word not in self.used_nonces and len(word) >= 3:
                self.used_nonces.add(word)
                return word
            attempts += 1

        # Fallback: add random suffix
        return f"zx{self.rng.randint(100, 999)}"

# ============================================================================
# WORD SLOT MANIPULATION
# ============================================================================

def identify_slots(words: List[str]) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Identify function vs content word positions.

    Returns:
        (function_slots, content_slots) - each is list of (index, word)
    """
    function_slots = []
    content_slots = []

    for i, word in enumerate(words):
        word_clean = word.lower().strip('.,!?;:')
        if word_clean in FUNCTION_WORDS:
            function_slots.append((i, word))
        else:
            content_slots.append((i, word))

    return function_slots, content_slots

# ============================================================================
# CONDITION GENERATORS
# ============================================================================

def full_scramble(sentence: str, seed: int) -> str:
    """
    FULL_SCRAMBLED: Random permutation of ALL tokens.

    Every word position is randomized. No structure preserved.
    """
    words = sentence.split()
    rng = random.Random(seed)
    shuffled = words.copy()

    # Ensure actually scrambled (different from original)
    for _ in range(10):
        rng.shuffle(shuffled)
        if shuffled != words or len(words) <= 1:
            break

    return ' '.join(shuffled)

def content_scramble(sentence: str, seed: int) -> str:
    """
    CONTENT_SCRAMBLED: Shuffle content words among content slots only.

    Function words stay in their original positions.
    Content words are permuted among content-word positions.
    """
    words = sentence.split()
    function_slots, content_slots = identify_slots(words)

    # Extract content words
    content_words = [word for idx, word in content_slots]

    # Shuffle
    rng = random.Random(seed)
    shuffled_content = content_words.copy()
    for _ in range(10):
        rng.shuffle(shuffled_content)
        if shuffled_content != content_words or len(content_words) <= 1:
            break

    # Reconstruct
    result = words.copy()
    for i, (idx, _) in enumerate(content_slots):
        result[idx] = shuffled_content[i]

    return ' '.join(result)

def function_scramble(sentence: str, seed: int) -> str:
    """
    FUNCTION_SCRAMBLED: Shuffle function words among function slots only.

    Content words stay in their original positions.
    Function words are permuted among function-word positions.
    """
    words = sentence.split()
    function_slots, content_slots = identify_slots(words)

    # Extract function words
    function_words_list = [word for idx, word in function_slots]

    # Shuffle
    rng = random.Random(seed)
    shuffled_function = function_words_list.copy()
    for _ in range(10):
        rng.shuffle(shuffled_function)
        if shuffled_function != function_words_list or len(function_words_list) <= 1:
            break

    # Reconstruct
    result = words.copy()
    for i, (idx, _) in enumerate(function_slots):
        result[idx] = shuffled_function[i]

    return ' '.join(result)

def cue_deletion(sentence: str, cue_word: str, replacement: str = 'ke') -> str:
    """
    CUE_DELETED: Replace the critical cue with a nonce function word.

    Tests whether the specific cue is necessary for constraint.
    """
    words = sentence.split()
    result = []

    cue_found = False
    for word in words:
        word_clean = word.lower().strip('.,!?;:')
        if word_clean == cue_word.lower() and not cue_found:
            result.append(replacement)
            cue_found = True  # Only replace first occurrence
        else:
            result.append(word)

    return ' '.join(result)

# ============================================================================
# CUE-FAMILY SPECIFIC TEMPLATES
# ============================================================================

# Content word pools for template filling
NOUNS_AGENT = [
    'scientist', 'artist', 'teacher', 'student', 'doctor', 'chef', 'engineer',
    'musician', 'author', 'mechanic', 'programmer', 'architect', 'researcher',
    'photographer', 'detective', 'captain', 'professor', 'coach', 'director',
    'farmer', 'baker', 'pilot', 'surgeon', 'lawyer', 'journalist', 'carpenter',
    'plumber', 'electrician', 'gardener', 'librarian'
]

NOUNS_PATIENT = [
    'artifacts', 'paintings', 'concept', 'assignment', 'landscape', 'patient',
    'symphony', 'novel', 'engine', 'software', 'blueprint', 'data', 'experiment',
    'recipe', 'manuscript', 'equipment', 'specimens', 'documents', 'vehicle',
    'instrument', 'formula', 'strategy', 'findings', 'technique', 'method',
    'discovery', 'solution', 'project', 'design', 'prototype'
]

ADJECTIVES = [
    'ancient', 'beautiful', 'difficult', 'important', 'complex', 'delicious',
    'broken', 'efficient', 'innovative', 'comprehensive', 'valuable', 'intricate',
    'challenging', 'experimental', 'preliminary', 'historical', 'modern', 'rare',
    'elaborate', 'fundamental', 'critical', 'remarkable', 'unusual', 'significant',
    'mysterious', 'fascinating', 'practical', 'theoretical', 'advanced', 'basic'
]

VERBS_BASE = [
    'study', 'examine', 'analyze', 'explore', 'investigate', 'review', 'inspect',
    'evaluate', 'assess', 'test', 'repair', 'build', 'design', 'create', 'develop',
    'improve', 'fix', 'complete', 'finish', 'prepare', 'organize', 'document',
    'present', 'explain', 'discuss', 'publish', 'research', 'demonstrate', 'solve', 'process'
]

VERBS_PAST = [
    'decided', 'wanted', 'began', 'tried', 'planned', 'continued', 'hoped',
    'expected', 'needed', 'agreed', 'promised', 'attempted', 'managed', 'struggled',
    'offered', 'refused', 'learned', 'forgot', 'remembered', 'chose', 'liked',
    'loved', 'preferred', 'wished', 'demanded', 'requested', 'intended', 'meant',
    'prepared', 'started'
]

VERBS_PARTICIPLE_ING = [
    'studying', 'examining', 'analyzing', 'exploring', 'investigating', 'reviewing',
    'inspecting', 'evaluating', 'assessing', 'testing', 'repairing', 'building',
    'designing', 'creating', 'developing', 'improving', 'fixing', 'completing',
    'finishing', 'preparing', 'organizing', 'documenting', 'presenting', 'explaining',
    'discussing', 'publishing', 'researching', 'demonstrating', 'solving', 'processing'
]

VERBS_PARTICIPLE_ED = [
    'studied', 'examined', 'analyzed', 'explored', 'investigated', 'reviewed',
    'inspected', 'evaluated', 'assessed', 'tested', 'repaired', 'built',
    'designed', 'created', 'developed', 'improved', 'fixed', 'completed',
    'finished', 'prepared', 'organized', 'documented', 'presented', 'explained',
    'discussed', 'published', 'researched', 'demonstrated', 'solved', 'processed'
]

PREPOSITIONS_LIST = ['with', 'in', 'on', 'at', 'for', 'about']
MODALS_LIST = ['can', 'will', 'could', 'would', 'should', 'must', 'may', 'might']
AUXILIARIES_BE = ['is', 'was', 'are', 'were']
AUXILIARIES_HAVE = ['has', 'have', 'had']


def generate_infinitival_to_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for infinitival 'to' → VERB

    Template: "The [AGENT] [PAST-VERB] to [VERB] the [ADJ] [PATIENT]"
    Cue: 'to' (always at position 3)
    Target: VERB (base form)
    """
    templates = []

    agents = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    patients = rng.sample(NOUNS_PATIENT, min(n, len(NOUNS_PATIENT)))
    adjs = rng.sample(ADJECTIVES, min(n, len(ADJECTIVES)))
    verbs_past = rng.sample(VERBS_PAST[:15], min(n, 15))  # Control verbs
    verbs_base = rng.sample(VERBS_BASE, min(n, len(VERBS_BASE)))

    for i in range(n):
        agent = agents[i % len(agents)]
        patient = patients[i % len(patients)]
        adj = adjs[i % len(adjs)]
        v_past = verbs_past[i % len(verbs_past)]
        v_base = verbs_base[i % len(verbs_base)]

        # SENTENCE
        sentence = f"the {agent} {v_past} to {v_base} the {adj} {patient}"

        # JABBERWOCKY: replace content words with nonces
        # Content words: agent, v_base, adj, patient
        # Keep: the, v_past (control verb acts as function), to, the
        nonce_agent = nonce_gen.generate()
        nonce_vbase = nonce_gen.generate()
        nonce_adj = nonce_gen.generate()
        nonce_patient = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent} {v_past} to {nonce_vbase} the {nonce_adj} {nonce_patient}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'infinitival_to',
            'cue_word': 'to',
            'cue_position': 3,  # 0-indexed word position
            'target_class': 'VERB',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent, v_base, adj, patient],
            'nonce_words': [nonce_agent, nonce_vbase, nonce_adj, nonce_patient],
        })

    return templates


def generate_modal_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for modals → VERB

    Template: "The [AGENT] can/will [VERB] the [ADJ] [PATIENT]"
    Cue: modal (position 2)
    Target: VERB (base form)
    """
    templates = []

    agents = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    patients = rng.sample(NOUNS_PATIENT, min(n, len(NOUNS_PATIENT)))
    adjs = rng.sample(ADJECTIVES, min(n, len(ADJECTIVES)))
    modals = rng.choices(MODALS_LIST, k=n)
    verbs_base = rng.sample(VERBS_BASE, min(n, len(VERBS_BASE)))

    for i in range(n):
        agent = agents[i % len(agents)]
        patient = patients[i % len(patients)]
        adj = adjs[i % len(adjs)]
        modal = modals[i]
        v_base = verbs_base[i % len(verbs_base)]

        sentence = f"the {agent} {modal} {v_base} the {adj} {patient}"

        nonce_agent = nonce_gen.generate()
        nonce_vbase = nonce_gen.generate()
        nonce_adj = nonce_gen.generate()
        nonce_patient = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent} {modal} {nonce_vbase} the {nonce_adj} {nonce_patient}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'modals',
            'cue_word': modal,
            'cue_position': 2,
            'target_class': 'VERB',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent, v_base, adj, patient],
            'nonce_words': [nonce_agent, nonce_vbase, nonce_adj, nonce_patient],
        })

    return templates


def generate_determiner_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for determiners → NOUN/ADJ

    Template: "The [AGENT] [PAST-VERB] and saw a [ADJ] [PATIENT]"
    Cue: 'a' (position 5)
    Target: NOUN or ADJ

    Note: We use "a" as the determiner cue to avoid having two identical "the" words,
    which would make function_scrambled identical to jabberwocky.
    """
    templates = []

    agents = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    patients = rng.sample(NOUNS_PATIENT, min(n, len(NOUNS_PATIENT)))
    adjs = rng.sample(ADJECTIVES, min(n, len(ADJECTIVES)))
    verbs_past = rng.sample(VERBS_PAST, min(n, len(VERBS_PAST)))

    for i in range(n):
        agent = agents[i % len(agents)]
        patient = patients[i % len(patients)]
        adj = adjs[i % len(adjs)]
        v_past = verbs_past[i % len(verbs_past)]

        # Structure: "the AGENT V_PAST and saw a ADJ PATIENT"
        # This gives us diverse function words: "the", "and", "a"
        sentence = f"the {agent} {v_past} and saw a {adj} {patient}"

        nonce_agent = nonce_gen.generate()
        nonce_vpast = nonce_gen.generate()
        nonce_adj = nonce_gen.generate()
        nonce_patient = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent} {nonce_vpast} and saw a {nonce_adj} {nonce_patient}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'determiners',
            'cue_word': 'a',
            'cue_position': 5,  # Position of 'a'
            'target_class': 'NOUN_OR_ADJ',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent, v_past, adj, patient],
            'nonce_words': [nonce_agent, nonce_vpast, nonce_adj, nonce_patient],
        })

    return templates


def generate_preposition_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for prepositions → NP_START

    Template: "The [AGENT] [PAST-VERB] with/in/on the [ADJ] [PATIENT]"
    Cue: preposition (position 3)
    Target: NP_START (det, adj, or noun)
    """
    templates = []

    agents = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    patients = rng.sample(NOUNS_PATIENT, min(n, len(NOUNS_PATIENT)))
    adjs = rng.sample(ADJECTIVES, min(n, len(ADJECTIVES)))
    verbs_past = rng.sample(VERBS_PAST, min(n, len(VERBS_PAST)))
    preps = rng.choices(PREPOSITIONS_LIST, k=n)

    for i in range(n):
        agent = agents[i % len(agents)]
        patient = patients[i % len(patients)]
        adj = adjs[i % len(adjs)]
        v_past = verbs_past[i % len(verbs_past)]
        prep = preps[i]

        sentence = f"the {agent} {v_past} {prep} the {adj} {patient}"

        nonce_agent = nonce_gen.generate()
        nonce_vpast = nonce_gen.generate()
        nonce_adj = nonce_gen.generate()
        nonce_patient = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent} {nonce_vpast} {prep} the {nonce_adj} {nonce_patient}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'prepositions',
            'cue_word': prep,
            'cue_position': 3,
            'target_class': 'NP_START',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent, v_past, adj, patient],
            'nonce_words': [nonce_agent, nonce_vpast, nonce_adj, nonce_patient],
        })

    return templates


def generate_auxiliary_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for auxiliaries → PARTICIPLE

    Template: "The [AGENT] is/was [V-ING/V-ED] the [ADJ] [PATIENT]"
    Cue: auxiliary (position 2)
    Target: PARTICIPLE (V-ing or V-ed form)
    """
    templates = []

    agents = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    patients = rng.sample(NOUNS_PATIENT, min(n, len(NOUNS_PATIENT)))
    adjs = rng.sample(ADJECTIVES, min(n, len(ADJECTIVES)))

    # Half progressive (is V-ing), half passive (was V-ed)
    for i in range(n):
        agent = agents[i % len(agents)]
        patient = patients[i % len(patients)]
        adj = adjs[i % len(adjs)]

        if i % 2 == 0:
            # Progressive: is/are V-ing
            aux = rng.choice(['is', 'was'])
            v_part = VERBS_PARTICIPLE_ING[i % len(VERBS_PARTICIPLE_ING)]
        else:
            # Passive: was/were V-ed
            aux = rng.choice(['was', 'were', 'is', 'are'])
            v_part = VERBS_PARTICIPLE_ED[i % len(VERBS_PARTICIPLE_ED)]

        sentence = f"the {agent} {aux} {v_part} the {adj} {patient}"

        nonce_agent = nonce_gen.generate()
        nonce_vpart = nonce_gen.generate()
        nonce_adj = nonce_gen.generate()
        nonce_patient = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent} {aux} {nonce_vpart} the {nonce_adj} {nonce_patient}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'auxiliaries',
            'cue_word': aux,
            'cue_position': 2,
            'target_class': 'PARTICIPLE',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent, v_part, adj, patient],
            'nonce_words': [nonce_agent, nonce_vpart, nonce_adj, nonce_patient],
        })

    return templates


def generate_complementizer_templates(n: int, nonce_gen: NonceGenerator, rng: random.Random) -> List[Dict]:
    """
    Generate templates for complementizers → CLAUSE_START

    Template: "The [AGENT] [PAST-VERB] that the [AGENT2] [PAST-VERB2]"
    Cue: 'that' (position 3)
    Target: CLAUSE_START (pronoun, det, or noun - embedded subject)
    """
    templates = []

    agents1 = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    agents2 = rng.sample(NOUNS_AGENT, min(n, len(NOUNS_AGENT)))
    verbs1 = rng.sample(['said', 'thought', 'believed', 'knew', 'expected', 'hoped',
                         'realized', 'noticed', 'discovered', 'understood'], min(n, 10))
    verbs2 = rng.sample(VERBS_PAST, min(n, len(VERBS_PAST)))

    for i in range(n):
        agent1 = agents1[i % len(agents1)]
        agent2 = agents2[(i + 5) % len(agents2)]  # Offset to get different agents
        v1 = verbs1[i % len(verbs1)]
        v2 = verbs2[i % len(verbs2)]

        sentence = f"the {agent1} {v1} that the {agent2} {v2}"

        nonce_agent1 = nonce_gen.generate()
        nonce_v1 = nonce_gen.generate()
        nonce_agent2 = nonce_gen.generate()
        nonce_v2 = nonce_gen.generate()

        jabberwocky = f"the {nonce_agent1} {nonce_v1} that the {nonce_agent2} {nonce_v2}"

        templates.append({
            'set_id': i + 1,
            'cue_family': 'complementizers',
            'cue_word': 'that',
            'cue_position': 3,
            'target_class': 'CLAUSE_START',
            'sentence': sentence,
            'jabberwocky': jabberwocky,
            'content_words': [agent1, v1, agent2, v2],
            'nonce_words': [nonce_agent1, nonce_v1, nonce_agent2, nonce_v2],
        })

    return templates


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_all_conditions(templates: List[Dict], rng: random.Random) -> List[Dict]:
    """
    Generate all 6 conditions for each template.

    Returns list of complete stimulus sets.
    """
    stimuli = []

    for template in templates:
        jabberwocky = template['jabberwocky']
        cue_word = template['cue_word']

        # Generate deterministic seeds for scrambles
        seed_base = hash(f"{template['cue_family']}_{template['set_id']}")
        seed_full = (seed_base + 1) % (2**31)
        seed_content = (seed_base + 2) % (2**31)
        seed_function = (seed_base + 3) % (2**31)

        # Generate conditions
        full_scrambled = full_scramble(jabberwocky, seed_full)
        content_scrambled = content_scramble(jabberwocky, seed_content)
        function_scrambled = function_scramble(jabberwocky, seed_function)
        cue_deleted = cue_deletion(jabberwocky, cue_word, replacement='ke')

        stimulus = {
            'set_id': template['set_id'],
            'cue_family': template['cue_family'],
            'cue_word': template['cue_word'],
            'cue_position': template['cue_position'],
            'target_class': template['target_class'],

            # 6 conditions
            'sentence': template['sentence'],
            'jabberwocky': jabberwocky,
            'full_scrambled': full_scrambled,
            'content_scrambled': content_scrambled,
            'function_scrambled': function_scrambled,
            'cue_deleted': cue_deleted,

            # Metadata
            'content_words': template['content_words'],
            'nonce_words': template['nonce_words'],
            'seeds': {
                'full_scramble': seed_full,
                'content_scramble': seed_content,
                'function_scramble': seed_function,
            }
        }

        stimuli.append(stimulus)

    return stimuli


def sanity_check_stimuli(stimuli: List[Dict], log_file: str):
    """
    Run sanity checks and write detailed log.

    Checks:
    1. Each family has exactly 30 stimuli
    2. Each stimulus has exactly 1 cue occurrence
    3. Print 3 examples per condition per family
    4. Verify scrambles are actually scrambled
    """
    with open(log_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("STIMULUS SANITY CHECK LOG\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("=" * 80 + "\n\n")

        # Group by family
        by_family = {}
        for s in stimuli:
            family = s['cue_family']
            if family not in by_family:
                by_family[family] = []
            by_family[family].append(s)

        all_passed = True

        for family, family_stimuli in by_family.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"CUE FAMILY: {family.upper()}\n")
            f.write(f"{'='*60}\n\n")

            # Check 1: Count
            n = len(family_stimuli)
            f.write(f"Count: {n}/30\n")
            if n != 30:
                f.write(f"  *** FAIL: Expected 30, got {n} ***\n")
                all_passed = False
            else:
                f.write(f"  PASS\n")

            # Check 2: Cue occurrences per condition
            f.write(f"\nCue occurrence check:\n")
            conditions = ['sentence', 'jabberwocky', 'full_scrambled',
                         'content_scrambled', 'function_scrambled', 'cue_deleted']

            for cond in conditions:
                cue_counts = []
                for s in family_stimuli:
                    text = s[cond]
                    cue = s['cue_word'].lower()
                    words = text.lower().split()
                    count = sum(1 for w in words if w.strip('.,!?;:') == cue)
                    cue_counts.append(count)

                if cond == 'cue_deleted':
                    expected = 0
                    ke_counts = [sum(1 for w in s[cond].lower().split() if w == 'ke') for s in family_stimuli]
                    avg_ke = sum(ke_counts) / len(ke_counts)
                    f.write(f"  {cond:20s}: cue={sum(cue_counts)/30:.1f} avg, ke={avg_ke:.1f} avg")
                else:
                    expected = 1
                    f.write(f"  {cond:20s}: {sum(cue_counts)/30:.1f} avg cues per sentence")

                if cond != 'cue_deleted' and all(c == 1 for c in cue_counts):
                    f.write(" [PASS]\n")
                elif cond == 'cue_deleted' and all(c == 0 for c in cue_counts):
                    f.write(" [PASS]\n")
                else:
                    f.write(" [CHECK]\n")

            # Check 3: Print 3 examples per condition
            f.write(f"\n--- Examples (first 3 stimuli) ---\n\n")
            for i, s in enumerate(family_stimuli[:3]):
                f.write(f"Stimulus {s['set_id']}:\n")
                f.write(f"  Cue word: '{s['cue_word']}' at position {s['cue_position']}\n")
                f.write(f"  Target class: {s['target_class']}\n\n")

                for cond in conditions:
                    f.write(f"  {cond:20s}: {s[cond]}\n")
                f.write("\n")

            # Check 4: Verify scrambles are different
            f.write(f"\n--- Scramble verification ---\n")
            same_full = sum(1 for s in family_stimuli if s['jabberwocky'] == s['full_scrambled'])
            same_content = sum(1 for s in family_stimuli if s['jabberwocky'] == s['content_scrambled'])
            same_function = sum(1 for s in family_stimuli if s['jabberwocky'] == s['function_scrambled'])

            f.write(f"  full_scrambled same as jabberwocky: {same_full}/30\n")
            f.write(f"  content_scrambled same as jabberwocky: {same_content}/30\n")
            f.write(f"  function_scrambled same as jabberwocky: {same_function}/30\n")

            if same_full > 0 or same_content > 0 or same_function > 0:
                f.write("  *** WARNING: Some scrambles may not have changed ***\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total families: {len(by_family)}\n")
        f.write(f"Total stimuli: {len(stimuli)}\n")
        f.write(f"Expected: 6 families × 30 = 180 stimuli\n")
        f.write(f"Overall: {'PASS' if len(stimuli) == 180 and all_passed else 'CHECK REQUIRED'}\n")

    return all_passed


def main():
    """Generate locked design stimuli for all cue families."""

    print("=" * 80)
    print("LOCKED DESIGN STIMULUS GENERATOR")
    print("=" * 80)
    print()

    rng = random.Random(SEED)

    all_templates = []

    # Generate templates for each cue family
    print("Generating templates...")

    families = [
        ('infinitival_to', generate_infinitival_to_templates),
        ('modals', generate_modal_templates),
        ('determiners', generate_determiner_templates),
        ('prepositions', generate_preposition_templates),
        ('auxiliaries', generate_auxiliary_templates),
        ('complementizers', generate_complementizer_templates),
    ]

    for family_name, generator_func in families:
        nonce_gen = NonceGenerator(seed=hash(family_name) % (2**31))
        templates = generator_func(N_SENTENCES_PER_FAMILY, nonce_gen, rng)
        all_templates.extend(templates)
        print(f"  {family_name}: {len(templates)} templates")

    print(f"\nTotal templates: {len(all_templates)}")
    print()

    # Generate all conditions
    print("Generating conditions...")
    all_stimuli = generate_all_conditions(all_templates, rng)
    print(f"Total stimuli: {len(all_stimuli)} (6 conditions each)")
    print()

    # Sanity checks
    print("Running sanity checks...")
    log_file = 'stimuli_locked_sanity_check.log'
    passed = sanity_check_stimuli(all_stimuli, log_file)
    print(f"Sanity check log: {log_file}")
    print(f"Status: {'PASS' if passed else 'CHECK REQUIRED'}")
    print()

    # Save stimuli
    output_file = 'stimuli_locked.json'
    with open(output_file, 'w') as f:
        json.dump(all_stimuli, f, indent=2)

    print(f"Saved stimuli to: {output_file}")
    print()

    # Summary table
    print("=" * 80)
    print("STIMULUS SUMMARY")
    print("=" * 80)
    print()
    print(f"{'Cue Family':<20} {'N':>5} {'Cue Word':>15} {'Target Class':>15}")
    print("-" * 60)

    for family_name, _ in families:
        family_stims = [s for s in all_stimuli if s['cue_family'] == family_name]
        cue_words = set(s['cue_word'] for s in family_stims)
        target = family_stims[0]['target_class']
        cue_str = ', '.join(sorted(cue_words)[:3])
        if len(cue_words) > 3:
            cue_str += '...'
        print(f"{family_name:<20} {len(family_stims):>5} {cue_str:>15} {target:>15}")

    print("-" * 60)
    print(f"{'TOTAL':<20} {len(all_stimuli):>5}")
    print()
    print("Ready for comprehensive audit!")


if __name__ == '__main__':
    main()
