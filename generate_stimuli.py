"""
Generate stimuli for morphosyntax constraint experiment.
Creates 4 conditions: Real sentences, Jabberwocky, Stripped, Random nonwords.
"""

import random
import re
import json

# Consistent nonword roots (phonotactically legal English)
NONWORD_NOUNS = [
    "blicket", "wuggle", "daxen", "plonk", "zorf", "mip", "gleb",
    "snorf", "prock", "flib", "blimp", "trell", "sprock", "grint",
    "flurn", "plib", "skeff", "trock", "verm", "whiff", "yalp", "zink"
]

NONWORD_VERBS = [
    "florp", "tamp", "grent", "borp", "sken", "pliff", "dwel",
    "kreb", "sniv", "trell", "vork", "whisp", "yalm", "zomp",
    "bliv", "kren", "prav", "screll", "teff", "vren"
]

NONWORD_ADJS = [
    "flimp", "grofly", "plonken", "bren", "drell", "geff", "klim",
    "plov", "shill", "tren", "veff", "whill", "yeff", "zell",
    "brell", "cleff", "driv", "fleff", "grell", "keff"
]

NONWORD_ADVS = [
    "grentily", "grofly", "blifly", "klently", "plovly", "snivly",
    "trelly", "vently", "whifly", "yently", "zently", "brenly"
]

# Function word mappings for Stripped condition
FUNCTION_WORD_MAP = {
    "the": "ke", "a": "na", "an": "na",
    "is": "nar", "was": "nar", "are": "nar", "were": "nar",
    "to": "po", "of": "ko", "in": "ne", "on": "ko", "at": "fe",
    "by": "le", "for": "ve", "with": "pe", "from": "mo",
    "through": "so", "that": "ze", "this": "zi", "these": "zi",
    "and": "en", "but": "ba", "or": "ro", "if": "gi", "when": "we",
    "while": "wi", "as": "da", "very": "vo", "so": "so", "too": "tu",
    "not": "no", "have": "ha", "has": "ha", "had": "ha",
    "will": "wi", "would": "wu", "could": "ku", "should": "shu",
    "can": "ka", "may": "ma", "might": "mi"
}

# 30 diverse sentence structures
BASE_SENTENCES = [
    "The teacher was explaining the concept to the students clearly",
    "A small bird landed softly on the wooden fence",
    "The children were playing with their toys in the garden",
    "She has been reading that book very carefully",
    "The scientist discovered a new species in the forest",
    "They will finish the project by tomorrow morning",
    "A gentle breeze was blowing through the open window",
    "The musician played the melody beautifully on stage",
    "He could have solved the problem more easily",
    "The committee is reviewing the proposal thoroughly",
    "A mysterious figure appeared suddenly in the darkness",
    "The students should study the material very seriously",
    "She was walking slowly through the quiet streets",
    "The engineers are designing a better system carefully",
    "A young artist painted the landscape very skillfully",
    "The dog had been barking loudly at the stranger",
    "They were discussing the matter quite intensely",
    "The flowers are blooming beautifully in the spring",
    "A talented chef prepared the meal expertly",
    "The researchers have discovered the answer recently",
    "She will be traveling to the conference tomorrow",
    "The workers were building the structure very carefully",
    "A bright light was shining through the window",
    "The author has written several books successfully",
    "They could see the mountains clearly from here",
    "The machine is processing the data quite rapidly",
    "A skilled doctor examined the patient thoroughly",
    "The team was celebrating the victory enthusiastically",
    "She might have understood the concept more clearly",
    "The investors are evaluating the opportunity very carefully"
]

class NonwordGenerator:
    """Generates consistent nonword replacements."""

    def __init__(self):
        self.noun_map = {}
        self.verb_map = {}
        self.adj_map = {}
        self.adv_map = {}
        self.noun_idx = 0
        self.verb_idx = 0
        self.adj_idx = 0
        self.adv_idx = 0

    def get_nonword_noun(self, word, plural=False):
        """Get nonword for a noun, maintaining consistency."""
        if word not in self.noun_map:
            self.noun_map[word] = NONWORD_NOUNS[self.noun_idx % len(NONWORD_NOUNS)]
            self.noun_idx += 1
        base = self.noun_map[word]
        return base + "s" if plural else base

    def get_nonword_verb(self, word, form="base"):
        """Get nonword for a verb with appropriate morphology."""
        if word not in self.verb_map:
            self.verb_map[word] = NONWORD_VERBS[self.verb_idx % len(NONWORD_VERBS)]
            self.verb_idx += 1
        base = self.verb_map[word]

        if form == "ing":
            return base + "ing"
        elif form == "ed":
            return base + "ed"
        elif form == "s":
            return base + "s"
        return base

    def get_nonword_adj(self, word):
        """Get nonword for an adjective."""
        if word not in self.adj_map:
            self.adj_map[word] = NONWORD_ADJS[self.adj_idx % len(NONWORD_ADJS)]
            self.adj_idx += 1
        return self.adj_map[word]

    def get_nonword_adv(self, word, keep_ly=True):
        """Get nonword for an adverb."""
        if word not in self.adv_map:
            base_adj = NONWORD_ADJS[self.adv_idx % len(NONWORD_ADJS)]
            self.adv_map[word] = base_adj
            self.adv_idx += 1
        base = self.adv_map[word]
        return base + "ly" if keep_ly else base

def manually_transform_sentence(sentence_idx, sentence):
    """
    Manually transform each sentence into Jabberwocky and Stripped forms.
    This ensures accurate grammatical analysis.
    """
    gen = NonwordGenerator()

    # Manual transformations for each sentence
    transformations = {
        0: {  # "The teacher was explaining the concept to the students clearly"
            "jabberwocky": "The blicket was florping the daxen to the wuggles grentily",
            "stripped": "Ke blicket nar florp ke daxen po ke wuggle grenti"
        },
        1: {  # "A small bird landed softly on the wooden fence"
            "jabberwocky": "A flimp zorf tamped grofly on the plonken gleb",
            "stripped": "Na flimp zorf tamp grofl ko ke plonk gleb"
        },
        2: {  # "The children were playing with their toys in the garden"
            "jabberwocky": "The blickets were florping with their daxens in the wuggle",
            "stripped": "Ke blicket nar florp pe zi daxen ne ke wuggle"
        },
        3: {  # "She has been reading that book very carefully"
            "jabberwocky": "She has been florping that daxen very grentily",
            "stripped": "Sho ha nar florp ze daxen vo grenti"
        },
        4: {  # "The scientist discovered a new species in the forest"
            "jabberwocky": "The blicket florped a flimp zorf in the wuggle",
            "stripped": "Ke blicket florp na flimp zorf ne ke wuggle"
        },
        5: {  # "They will finish the project by tomorrow morning"
            "jabberwocky": "They will florp the daxen by plonk gleb",
            "stripped": "Zi wi florp ke daxen le plonk gleb"
        },
        6: {  # "A gentle breeze was blowing through the open window"
            "jabberwocky": "A flimp zorf was florping through the plonken gleb",
            "stripped": "Na flimp zorf nar florp so ke plonk gleb"
        },
        7: {  # "The musician played the melody beautifully on stage"
            "jabberwocky": "The blicket florped the daxen grentily on wuggle",
            "stripped": "Ke blicket florp ke daxen grenti ko wuggle"
        },
        8: {  # "He could have solved the problem more easily"
            "jabberwocky": "He could have florped the daxen more grentily",
            "stripped": "Ho ku ha florp ke daxen mo grenti"
        },
        9: {  # "The committee is reviewing the proposal thoroughly"
            "jabberwocky": "The blicket is florping the daxen grentily",
            "stripped": "Ke blicket nar florp ke daxen grenti"
        },
        10: {  # "A mysterious figure appeared suddenly in the darkness"
            "jabberwocky": "A flimp zorf florped grentily in the wuggle",
            "stripped": "Na flimp zorf florp grenti ne ke wuggle"
        },
        11: {  # "The students should study the material very seriously"
            "jabberwocky": "The blickets should florp the daxen very grentily",
            "stripped": "Ke blicket shu florp ke daxen vo grenti"
        },
        12: {  # "She was walking slowly through the quiet streets"
            "jabberwocky": "She was florping grentily through the flimp wuggles",
            "stripped": "Sho nar florp grenti so ke flimp wuggle"
        },
        13: {  # "The engineers are designing a better system carefully"
            "jabberwocky": "The blickets are florping a flimp zorf grentily",
            "stripped": "Ke blicket nar florp na flimp zorf grenti"
        },
        14: {  # "A young artist painted the landscape very skillfully"
            "jabberwocky": "A flimp blicket florped the daxen very grentily",
            "stripped": "Na flimp blicket florp ke daxen vo grenti"
        },
        15: {  # "The dog had been barking loudly at the stranger"
            "jabberwocky": "The zorf had been florping grentily at the blicket",
            "stripped": "Ke zorf ha nar florp grenti fe ke blicket"
        },
        16: {  # "They were discussing the matter quite intensely"
            "jabberwocky": "They were florping the daxen quite grentily",
            "stripped": "Zi nar florp ke daxen qui grenti"
        },
        17: {  # "The flowers are blooming beautifully in the spring"
            "jabberwocky": "The wuggles are florping grentily in the plonk",
            "stripped": "Ke wuggle nar florp grenti ne ke plonk"
        },
        18: {  # "A talented chef prepared the meal expertly"
            "jabberwocky": "A flimp blicket florped the daxen grentily",
            "stripped": "Na flimp blicket florp ke daxen grenti"
        },
        19: {  # "The researchers have discovered the answer recently"
            "jabberwocky": "The blickets have florped the daxen grentily",
            "stripped": "Ke blicket ha florp ke daxen grenti"
        },
        20: {  # "She will be traveling to the conference tomorrow"
            "jabberwocky": "She will be florping to the wuggle plonk",
            "stripped": "Sho wi nar florp po ke wuggle plonk"
        },
        21: {  # "The workers were building the structure very carefully"
            "jabberwocky": "The blickets were florping the zorf very grentily",
            "stripped": "Ke blicket nar florp ke zorf vo grenti"
        },
        22: {  # "A bright light was shining through the window"
            "jabberwocky": "A flimp daxen was florping through the gleb",
            "stripped": "Na flimp daxen nar florp so ke gleb"
        },
        23: {  # "The author has written several books successfully"
            "jabberwocky": "The blicket has florped flimp wuggles grentily",
            "stripped": "Ke blicket ha florp flimp wuggle grenti"
        },
        24: {  # "They could see the mountains clearly from here"
            "jabberwocky": "They could florp the wuggles grentily from here",
            "stripped": "Zi ku florp ke wuggle grenti mo here"
        },
        25: {  # "The machine is processing the data quite rapidly"
            "jabberwocky": "The zorf is florping the daxen quite grentily",
            "stripped": "Ke zorf nar florp ke daxen qui grenti"
        },
        26: {  # "A skilled doctor examined the patient thoroughly"
            "jabberwocky": "A flimp blicket florped the wuggle grentily",
            "stripped": "Na flimp blicket florp ke wuggle grenti"
        },
        27: {  # "The team was celebrating the victory enthusiastically"
            "jabberwocky": "The blicket was florping the daxen grentily",
            "stripped": "Ke blicket nar florp ke daxen grenti"
        },
        28: {  # "She might have understood the concept more clearly"
            "jabberwocky": "She might have florped the daxen more grentily",
            "stripped": "Sho mi ha florp ke daxen mo grenti"
        },
        29: {  # "The investors are evaluating the opportunity very carefully"
            "jabberwocky": "The blickets are florping the wuggle very grentily",
            "stripped": "Ke blicket nar florp ke wuggle vo grenti"
        }
    }

    return transformations[sentence_idx]

def generate_random_nonwords(num_words):
    """Generate random nonword string for Condition 4."""
    nonwords = NONWORD_NOUNS + NONWORD_VERBS + NONWORD_ADJS
    # Strip morphology from adverbs
    base_advs = [adv.replace("ly", "") for adv in NONWORD_ADVS]
    all_nonwords = nonwords + base_advs

    selected = random.sample(all_nonwords * 3, min(num_words, len(all_nonwords) * 3))
    return " ".join(selected[:num_words])

def generate_all_stimuli():
    """Generate all 30 stimulus sets with 4 conditions each."""
    stimuli = []

    for idx, sentence in enumerate(BASE_SENTENCES):
        # Get transformations
        transforms = manually_transform_sentence(idx, sentence)

        # Count words for matched random condition
        num_words = len(sentence.split())

        # Generate random nonwords
        random_nonwords = generate_random_nonwords(num_words)

        stimulus_set = {
            "set_id": idx + 1,
            "sentence": sentence,
            "jabberwocky": transforms["jabberwocky"],
            "stripped": transforms["stripped"],
            "nonwords": random_nonwords,
            "num_words": num_words
        }

        stimuli.append(stimulus_set)

    return stimuli

if __name__ == "__main__":
    stimuli = generate_all_stimuli()

    # Save to JSON
    with open("stimuli.json", "w") as f:
        json.dump(stimuli, f, indent=2)

    # Print first 3 sets as examples
    print("Generated 30 stimulus sets. First 3 examples:\n")
    for stim in stimuli[:3]:
        print(f"Set {stim['set_id']}:")
        print(f"  Sentence:    {stim['sentence']}")
        print(f"  Jabberwocky: {stim['jabberwocky']}")
        print(f"  Stripped:    {stim['stripped']}")
        print(f"  Nonwords:    {stim['nonwords']}")
        print(f"  Words: {stim['num_words']}\n")

    print(f"Saved to stimuli.json")
