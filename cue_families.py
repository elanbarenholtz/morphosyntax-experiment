#!/usr/bin/env python3
"""
Comprehensive Cue Family Definitions for Morphosyntax Audit

Defines 6 cue families with their cue words and expected word classes.
All matching is word-level (not token-level) using lowercase comparison.

Usage:
    from cue_families import CUE_FAMILIES, WORD_CLASSES
"""

# ============================================================================
# WORD CLASS DEFINITIONS
# ============================================================================

# Family 1: Infinitival TO → VERB
VERB_SET = {
    # Common verbs
    'be', 'have', 'do', 'say', 'go', 'get', 'make', 'know', 'think', 'take',
    'see', 'come', 'want', 'use', 'find', 'give', 'tell', 'work', 'call', 'try',
    'ask', 'need', 'feel', 'become', 'leave', 'put', 'mean', 'keep', 'let', 'begin',
    'seem', 'help', 'show', 'hear', 'play', 'run', 'move', 'like', 'live', 'believe',
    'bring', 'happen', 'write', 'sit', 'stand', 'lose', 'pay', 'meet', 'include', 'continue',
    'set', 'learn', 'change', 'lead', 'understand', 'watch', 'follow', 'stop', 'create', 'speak',
    'read', 'allow', 'add', 'spend', 'grow', 'open', 'walk', 'win', 'teach', 'offer',
    'remember', 'love', 'consider', 'appear', 'buy', 'serve', 'die', 'send', 'build', 'stay',
    'fall', 'cut', 'reach', 'kill', 'raise', 'pass', 'sell', 'decide', 'return', 'explain',
    'hope', 'develop', 'carry', 'break', 'receive', 'agree', 'support', 'hit', 'produce', 'eat',
    # Domain-specific verbs
    'study', 'research', 'investigate', 'examine', 'analyze', 'explore',
    'paint', 'draw', 'design', 'construct',
    'perform', 'practice', 'rehearse',
    'publish', 'edit', 'revise',
    'prepare', 'cook', 'bake',
    'repair', 'fix', 'mend',
    'solve', 'calculate', 'compute',
    'improve', 'enhance', 'upgrade',
    'debug', 'test', 'validate',
    'organize', 'arrange', 'sort',
    'defend', 'protect', 'guard',
    'film', 'record', 'capture',
    'sail', 'navigate', 'steer',
    'discuss', 'debate', 'argue',
    'assemble', 'combine', 'join',
    'refine', 'polish', 'perfect',
    'plan', 'schedule',
    'finish', 'complete', 'conclude',
}

# Family 3: Determiners → NOUN/ADJ
NOUN_SET = {
    # Common nouns
    'time', 'person', 'year', 'way', 'day', 'thing', 'man', 'world', 'life', 'hand',
    'part', 'child', 'eye', 'woman', 'place', 'work', 'week', 'case', 'point', 'government',
    'company', 'number', 'group', 'problem', 'fact', 'house', 'area', 'money', 'story', 'student',
    'word', 'family', 'head', 'water', 'room', 'mother', 'information', 'night', 'home', 'side',
    'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community',
    'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'back', 'parent', 'face',
    'level', 'office', 'door', 'health', 'art', 'war', 'history', 'party', 'result', 'change',
    'morning', 'reason', 'research', 'girl', 'guy', 'moment', 'air', 'teacher', 'force', 'education',
    # Domain-specific nouns
    'scientist', 'artist', 'musician', 'author', 'chef', 'mechanic', 'programmer',
    'engineer', 'architect', 'sailor', 'athlete', 'researcher', 'historian',
    'artifacts', 'paintings', 'symphony', 'novel', 'meal', 'car', 'software',
    'blueprint', 'boat', 'strategy', 'findings', 'documents', 'specimens',
    'composition', 'recipe', 'engine', 'code', 'building', 'vessel', 'data',
    'manuscript', 'dish', 'bug', 'system', 'structure', 'ship', 'experiment',
    'book', 'techniques', 'methods', 'tools', 'equipment', 'materials',
}

ADJECTIVE_SET = {
    # Common adjectives
    'new', 'good', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old',
    'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
    'few', 'public', 'bad', 'same', 'able', 'social', 'national', 'black', 'white', 'political',
    'best', 'full', 'simple', 'left', 'late', 'hard', 'real', 'top', 'whole', 'sure',
    'better', 'free', 'special', 'clear', 'recent', 'beautiful', 'strong', 'particular', 'certain', 'open',
    'red', 'difficult', 'available', 'likely', 'short', 'single', 'medical', 'current', 'wrong', 'private',
    'past', 'foreign', 'fine', 'common', 'poor', 'natural', 'significant', 'similar', 'hot', 'dead',
    'central', 'happy', 'serious', 'ready', 'simple', 'easy', 'effective', 'aware', 'human', 'local',
    # Domain-specific adjectives
    'ancient', 'beautiful', 'complex', 'delicious', 'broken', 'faulty', 'efficient',
    'sturdy', 'seaworthy', 'winning', 'comprehensive', 'historical', 'rare', 'valuable',
    'intricate', 'challenging', 'innovative', 'experimental', 'preliminary', 'final',
}

# Family 4: Prepositions → NP start (NOUN or ADJ or DET)
# NP_START combines nouns, adjectives, and determiners
NP_START_SET = NOUN_SET | ADJECTIVE_SET | {
    'the', 'a', 'an', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her',
    'its', 'our', 'their', 'some', 'any', 'each', 'every', 'all', 'both', 'many',
    'few', 'several', 'other', 'another', 'such', 'no',
}

# Family 5: Auxiliaries → V-participle/V-ing/predicate
# This is complex - includes past participles, present participles, and adjectives
PARTICIPLE_SET = {
    # Past participles (common verbs)
    'been', 'had', 'done', 'said', 'gone', 'gotten', 'made', 'known', 'thought', 'taken',
    'seen', 'come', 'wanted', 'used', 'found', 'given', 'told', 'worked', 'called', 'tried',
    'asked', 'needed', 'felt', 'become', 'left', 'put', 'meant', 'kept', 'let', 'begun',
    'seemed', 'helped', 'shown', 'heard', 'played', 'run', 'moved', 'liked', 'lived', 'believed',
    'brought', 'happened', 'written', 'sat', 'stood', 'lost', 'paid', 'met', 'included', 'continued',
    'set', 'learned', 'changed', 'led', 'understood', 'watched', 'followed', 'stopped', 'created', 'spoken',
    'read', 'allowed', 'added', 'spent', 'grown', 'opened', 'walked', 'won', 'taught', 'offered',
    'remembered', 'loved', 'considered', 'appeared', 'bought', 'served', 'died', 'sent', 'built', 'stayed',
    'fallen', 'cut', 'reached', 'killed', 'raised', 'passed', 'sold', 'decided', 'returned', 'explained',
    # Present participles / -ing forms (will be generated programmatically)
    'being', 'having', 'doing', 'saying', 'going', 'getting', 'making', 'knowing', 'thinking', 'taking',
    'seeing', 'coming', 'wanting', 'using', 'finding', 'giving', 'telling', 'working', 'calling', 'trying',
    'asking', 'needing', 'feeling', 'becoming', 'leaving', 'putting', 'meaning', 'keeping', 'letting', 'beginning',
    'seeming', 'helping', 'showing', 'hearing', 'playing', 'running', 'moving', 'liking', 'living', 'believing',
    'bringing', 'happening', 'writing', 'sitting', 'standing', 'losing', 'paying', 'meeting', 'including', 'continuing',
    'setting', 'learning', 'changing', 'leading', 'understanding', 'watching', 'following', 'stopping', 'creating', 'speaking',
    'reading', 'allowing', 'adding', 'spending', 'growing', 'opening', 'walking', 'winning', 'teaching', 'offering',
    'remembering', 'loving', 'considering', 'appearing', 'buying', 'serving', 'dying', 'sending', 'building', 'staying',
    'falling', 'cutting', 'reaching', 'killing', 'raising', 'passing', 'selling', 'deciding', 'returning', 'explaining',
}

# Predicates can also be adjectives
PREDICATE_SET = PARTICIPLE_SET | ADJECTIVE_SET

# Family 6: Complementizers / Wh-words → clause-like continuations
# This expects pronouns, determiners, or nouns (subject of embedded clause)
CLAUSE_START_SET = {
    # Pronouns
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those', 'who', 'what', 'which', 'where', 'when', 'why', 'how',
    # Determiners
    'the', 'a', 'an', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
    'some', 'any', 'all', 'both', 'each', 'every', 'no',
} | NOUN_SET  # Also allow nouns as clause subjects

# ============================================================================
# CUE FAMILIES
# ============================================================================

CUE_FAMILIES = {
    'infinitival_to': {
        'name': 'Infinitival TO',
        'description': 'Infinitival particle "to" expects base-form VERB',
        'cue_words': {'to'},  # Only infinitival to (distinguish from prepositional)
        'expected_classes': {
            'VERB': VERB_SET,
        },
        'primary_class': 'VERB',
        'notes': 'Distinguish infinitival from prepositional "to" using context (e.g., after control verbs)',
    },

    'modals': {
        'name': 'Modal Auxiliaries',
        'description': 'Modal auxiliaries expect base-form VERB',
        'cue_words': {
            'can', 'could', 'will', 'would', 'shall', 'should',
            'may', 'might', 'must', 'ought',
        },
        'expected_classes': {
            'VERB': VERB_SET,
        },
        'primary_class': 'VERB',
        'notes': 'Modals always take bare infinitive (base form)',
    },

    'determiners': {
        'name': 'Determiners',
        'description': 'Determiners expect NOUN or ADJECTIVE',
        'cue_words': {
            'the', 'a', 'an', 'this', 'that', 'these', 'those',
            'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'some', 'any', 'each', 'every', 'all', 'both', 'many',
            'few', 'several', 'other', 'another', 'such', 'no',
        },
        'expected_classes': {
            'NOUN': NOUN_SET,
            'ADJECTIVE': ADJECTIVE_SET,
        },
        'primary_class': 'NOUN',  # Most common
        'notes': 'Determiners introduce noun phrases; may be followed by adjective then noun',
    },

    'prepositions': {
        'name': 'Prepositions',
        'description': 'Prepositions expect NP start (DET, ADJ, or NOUN)',
        'cue_words': {
            'of', 'in', 'on', 'at', 'with', 'from', 'by', 'about',
            'as', 'into', 'through', 'during', 'before', 'after', 'above',
            'below', 'between', 'under', 'over', 'for', 'against', 'among',
            'within', 'without', 'toward', 'towards', 'throughout', 'beside',
            'besides', 'behind', 'beyond', 'across', 'along', 'around',
        },
        'expected_classes': {
            'NP_START': NP_START_SET,
        },
        'primary_class': 'NP_START',
        'notes': 'Prepositions take noun phrase complements',
    },

    'auxiliaries': {
        'name': 'Auxiliary Verbs',
        'description': 'Auxiliaries (be/have) expect participles or predicates',
        'cue_words': {
            'is', 'are', 'was', 'were', 'be', 'been', 'being',  # BE forms
            'has', 'have', 'had', 'having',  # HAVE forms
        },
        'expected_classes': {
            'PARTICIPLE': PARTICIPLE_SET,
            'PREDICATE': PREDICATE_SET,  # For copular BE
        },
        'primary_class': 'PARTICIPLE',
        'notes': 'BE takes -ing (progressive) or -ed (passive) or adjective (copular); HAVE takes -ed (perfect)',
    },

    'complementizers': {
        'name': 'Complementizers and Wh-words',
        'description': 'Complementizers and wh-words expect clause start (pronoun, DET, NOUN)',
        'cue_words': {
            'that',  # Complementizer
            'whether', 'if',  # Interrogative complementizers
            'who', 'what', 'which', 'where', 'when', 'why', 'how',  # Wh-words
        },
        'expected_classes': {
            'CLAUSE_START': CLAUSE_START_SET,
        },
        'primary_class': 'CLAUSE_START',
        'notes': 'Introduces embedded clause; expects subject (pronoun, DET+N, or bare noun)',
    },
}

# ============================================================================
# WORD CLASS LOOKUP
# ============================================================================

WORD_CLASSES = {
    'VERB': VERB_SET,
    'NOUN': NOUN_SET,
    'ADJECTIVE': ADJECTIVE_SET,
    'NP_START': NP_START_SET,
    'PARTICIPLE': PARTICIPLE_SET,
    'PREDICATE': PREDICATE_SET,
    'CLAUSE_START': CLAUSE_START_SET,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_cue_family(family_name):
    """
    Get cue family definition by name.

    Args:
        family_name: One of ['infinitival_to', 'modals', 'determiners',
                     'prepositions', 'auxiliaries', 'complementizers']

    Returns:
        Dictionary with cue family specification
    """
    if family_name not in CUE_FAMILIES:
        raise ValueError(f"Unknown cue family: {family_name}. "
                        f"Available: {list(CUE_FAMILIES.keys())}")
    return CUE_FAMILIES[family_name]

def is_cue_word(word, family_name):
    """
    Check if word is a cue in the specified family.

    Args:
        word: Word string (will be lowercased)
        family_name: Cue family name

    Returns:
        Boolean
    """
    family = get_cue_family(family_name)
    return word.lower().strip('.,!?;:') in family['cue_words']

def get_expected_classes(family_name):
    """
    Get expected word classes for a cue family.

    Args:
        family_name: Cue family name

    Returns:
        Dictionary mapping class names to word sets
    """
    family = get_cue_family(family_name)
    return family['expected_classes']

def get_primary_class(family_name):
    """
    Get primary expected class for a cue family.

    Args:
        family_name: Cue family name

    Returns:
        String (class name)
    """
    family = get_cue_family(family_name)
    return family['primary_class']

# ============================================================================
# VERIFICATION
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("CUE FAMILY DEFINITIONS")
    print("=" * 80)
    print()

    for family_id, family_spec in CUE_FAMILIES.items():
        print(f"{family_spec['name']} ({family_id})")
        print(f"  Description: {family_spec['description']}")
        print(f"  Cue words ({len(family_spec['cue_words'])}): {sorted(family_spec['cue_words'])[:10]}...")
        print(f"  Expected classes: {list(family_spec['expected_classes'].keys())}")
        print(f"  Primary class: {family_spec['primary_class']}")

        # Show class sizes
        for class_name, word_set in family_spec['expected_classes'].items():
            print(f"    - {class_name}: {len(word_set)} words")

        print()

    print("=" * 80)
    print("WORD CLASS SUMMARY")
    print("=" * 80)
    print()

    for class_name, word_set in WORD_CLASSES.items():
        print(f"{class_name}: {len(word_set)} words")

    print()
    print("✓ Cue families defined")
