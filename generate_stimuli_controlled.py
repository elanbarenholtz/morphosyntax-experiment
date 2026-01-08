"""
Generate CONTROLLED stimuli for morphosyntax experiment.
KEY FIX: Use UNIQUE nonwords for each sentence to avoid repetition confound.
"""

import random
import json

# Large pool of phonotactically legal nonwords
NONWORD_POOL = [
    # Nouns
    "blicket", "wuggle", "daxen", "plonk", "zorf", "mip", "gleb", "snorf",
    "prock", "flib", "blimp", "trell", "sprock", "grint", "flurn", "plib",
    "skeff", "trock", "verm", "whiff", "yalp", "zink", "kreb", "dwel",
    "vork", "whisp", "yalm", "zomp", "bliv", "kren", "prav", "screll",
    "teff", "vren", "brell", "cleff", "driv", "fleff", "grell", "keff",
    "drell", "geff", "klim", "plov", "shill", "tren", "veff", "whill",
    "yeff", "zell", "grof", "klent", "bren", "pliff", "sniv", "grofl",
    "blork", "crell", "daffin", "frell", "glorp", "jexen", "klorn", "lurnip",
    "moxen", "neffin", "plenth", "quorb", "rellick", "sneff", "tembly", "urnix",
    "vellop", "wexin", "yorbel", "zeffin", "blenk", "cromple", "deffin", "flenk",
    "gribble", "heffin", "jembly", "krendle", "leppik", "mornix", "nellick", "pordel",
    "quendle", "reffin", "slenk", "tembril", "ullick", "vemble", "wreffin", "yendle",
    "zemble", "blundle", "crendle", "demble", "fremble", "glendle", "hemble", "jendle",

    # Verbs
    "florp", "tamp", "grent", "borp", "sken", "pliff", "kreb", "sniv",
    "vork", "whisp", "yalm", "zomp", "bliv", "kren", "prav", "screll",
    "teff", "vren", "clorp", "drell", "frell", "gremble", "horp", "jell",
    "klorp", "lemble", "morp", "nemble", "prell", "quemble", "remble", "snell",
    "trell", "urnble", "vemble", "wremble", "yemble", "zemble", "blemble", "cremble",

    # Adjectives
    "flimp", "bren", "drell", "geff", "klim", "plov", "shill", "tren",
    "veff", "whill", "yeff", "zell", "brell", "cleff", "driv", "fleff",
    "grell", "keff", "plenth", "snell", "trell", "vreff", "whell", "yrell",
    "zrell", "blenth", "creff", "drenth", "freff", "grenth", "hreff", "jrenth"
]

# Ensure we have enough
random.shuffle(NONWORD_POOL)

# Function words (preserved in Jabberwocky)
FUNCTION_WORDS = ["the", "a", "was", "is", "were", "to", "in", "on", "at", "by", "with", "from", "through",
                  "that", "very", "has", "been", "will", "could", "should", "have", "are", "their", "her", "his"]

# Base sentences (same as before)
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

class ControlledNonwordGenerator:
    """Generates UNIQUE nonwords for each sentence."""

    def __init__(self):
        self.used_nonwords = set()
        self.nonword_pool = NONWORD_POOL.copy()
        random.shuffle(self.nonword_pool)
        self.pool_index = 0

    def get_unique_nonword(self):
        """Get a nonword that hasn't been used yet."""
        while self.pool_index < len(self.nonword_pool):
            nonword = self.nonword_pool[self.pool_index]
            self.pool_index += 1
            if nonword not in self.used_nonwords:
                self.used_nonwords.add(nonword)
                return nonword
        # If we run out, generate a random one
        import string
        while True:
            # Generate random pronounceable nonword
            consonants = 'bcdfghjklmnprstvwz'
            vowels = 'aeiou'
            length = random.randint(4, 7)
            nonword = ''
            for i in range(length):
                if i % 2 == 0:
                    nonword += random.choice(consonants)
                else:
                    nonword += random.choice(vowels)
            if nonword not in self.used_nonwords:
                self.used_nonwords.add(nonword)
                return nonword

    def add_morphology(self, nonword, form):
        """Add morphological marker."""
        if form == "ing":
            return nonword + "ing"
        elif form == "ed":
            return nonword + "ed"
        elif form == "s":
            return nonword + "s"
        elif form == "ly":
            return nonword + "ly"
        return nonword

def create_jabberwocky(sentence, generator):
    """Create Jabberwocky version with UNIQUE nonwords."""
    words = sentence.split()
    result = []

    for word in words:
        lower_word = word.lower().strip('.,!?;:')

        # Preserve function words
        if lower_word in FUNCTION_WORDS:
            result.append(word)
        # Check for morphological patterns
        elif lower_word.endswith('ing'):
            nonword = generator.get_unique_nonword()
            result.append(generator.add_morphology(nonword, 'ing'))
        elif lower_word.endswith('ed'):
            nonword = generator.get_unique_nonword()
            result.append(generator.add_morphology(nonword, 'ed'))
        elif lower_word.endswith('ly'):
            nonword = generator.get_unique_nonword()
            result.append(generator.add_morphology(nonword, 'ly'))
        elif lower_word.endswith('s') and len(lower_word) > 3:
            nonword = generator.get_unique_nonword()
            result.append(generator.add_morphology(nonword, 's'))
        else:
            # Replace with unique nonword
            result.append(generator.get_unique_nonword())

    return " ".join(result)

def create_stripped(jabberwocky, generator):
    """Create stripped version - remove function words and morphology."""
    words = jabberwocky.split()
    result = []

    # Unique function word replacements for this sentence
    func_replacements = {}

    for word in words:
        lower_word = word.lower().strip('.,!?;:')

        # Replace function words with unique nonwords
        if lower_word in FUNCTION_WORDS:
            if lower_word not in func_replacements:
                func_replacements[lower_word] = generator.get_unique_nonword()
            result.append(func_replacements[lower_word])
        # Strip morphology
        elif word.endswith('ing'):
            result.append(word[:-3])
        elif word.endswith('ed'):
            result.append(word[:-2])
        elif word.endswith('ly'):
            result.append(word[:-2])
        elif word.endswith('s') and len(word) > 3:
            result.append(word[:-1])
        else:
            result.append(word)

    return " ".join(result)

def create_random_nonwords(length, generator):
    """Create random nonword string with UNIQUE nonwords."""
    return " ".join([generator.get_unique_nonword() for _ in range(length)])

def generate_all_stimuli():
    """Generate all 30 controlled stimulus sets."""
    stimuli = []

    for idx, sentence in enumerate(BASE_SENTENCES):
        # Create NEW generator for each set to ensure uniqueness within set
        generator = ControlledNonwordGenerator()

        # Generate conditions
        jabberwocky = create_jabberwocky(sentence, generator)
        stripped = create_stripped(jabberwocky, generator)
        num_words = len(sentence.split())
        random_nonwords = create_random_nonwords(num_words, generator)

        stimulus_set = {
            "set_id": idx + 1,
            "sentence": sentence,
            "jabberwocky": jabberwocky,
            "stripped": stripped,
            "nonwords": random_nonwords,
            "num_words": num_words
        }

        stimuli.append(stimulus_set)

    return stimuli

if __name__ == "__main__":
    stimuli = generate_all_stimuli()

    # Save to JSON
    with open("stimuli_controlled.json", "w") as f:
        json.dump(stimuli, f, indent=2)

    # Print first 3 sets
    print("Generated 30 CONTROLLED stimulus sets. First 3 examples:\n")
    for stim in stimuli[:3]:
        print(f"Set {stim['set_id']}:")
        print(f"  Sentence:    {stim['sentence']}")
        print(f"  Jabberwocky: {stim['jabberwocky']}")
        print(f"  Stripped:    {stim['stripped']}")
        print(f"  Nonwords:    {stim['nonwords']}")
        print(f"  Words: {stim['num_words']}\n")

    print(f"Saved to stimuli_controlled.json")

    # Quick vocabulary check
    print("\n" + "="*80)
    print("VOCABULARY CHECK (to verify no repetition)")
    print("="*80)

    for condition in ['jabberwocky', 'stripped', 'nonwords']:
        all_words = []
        for stim in stimuli:
            words = stim[condition].lower().split()
            all_words.extend(words)

        from collections import Counter
        word_counts = Counter(all_words)
        unique_words = len(word_counts)
        total_words = len(all_words)

        print(f"\n{condition.upper()}:")
        print(f"  Total tokens: {total_words}")
        print(f"  Unique words: {unique_words}")
        print(f"  Type-token ratio: {unique_words/total_words:.3f}")
        print(f"  Top 5 most common: {word_counts.most_common(5)}")
