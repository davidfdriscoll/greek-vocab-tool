from enum import Enum, auto
from typing import List, Set

class UnknownFeatureError(ValueError):
    """Raised when an unknown morphological feature is encountered."""
    def __init__(self, feature: str):
        self.feature = feature
        super().__init__(f"Unknown morphological feature: '{feature}'")

class Feature(Enum):
    """Enumeration of possible morphological features returned by the morpheus parser."""
    # Person
    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    
    # Number
    SINGULAR = "sg"
    PLURAL = "pl"
    DUAL = "dual"
    
    # Gender
    MASCULINE = "masc"
    FEMININE = "fem"
    NEUTER = "neut"
    MASC_FEM = "masc/fem"  # Combined gender for pronouns like τίς
    MASC_NEUT = "masc/neut"  # Combined gender for certain forms
    MASC_FEM_NEUT = "masc/fem/neut"  # All genders (for certain pronouns)
    
    # Case
    NOMINATIVE = "nom"
    GENITIVE = "gen"
    DATIVE = "dat"
    ACCUSATIVE = "acc"
    VOCATIVE = "voc"
    NOM_VOC = "nom/voc"  # Combined case
    NOM_ACC = "nom/acc"  # Combined nominative/accusative case
    NOM_VOC_ACC = "nom/voc/acc"  # Combined case for neuter forms
    
    # Tense
    PRESENT = "pres"
    IMPERFECT = "impf"
    IMPERFECT_ALT = "imperf"  # Alternative spelling from Morpheus
    FUTURE = "fut"
    AORIST = "aor"
    AORIST1 = "aor1"  # First aorist
    AORIST2 = "aor2"  # Second aorist
    PERFECT = "perf"
    PLUPERFECT = "plup"
    
    # Mood
    INDICATIVE = "ind"
    SUBJUNCTIVE = "subj"
    OPTATIVE = "opt"
    IMPERATIVE = "imptv"
    INFINITIVE = "inf"
    PARTICIPLE = "part"
    IMPERATIVE_ALT = "imperat"  # Alternative spelling for imperative
    IMPERATIVE_ALT2 = "imperat alt"  # Another alternative spelling
    
    # Voice
    ACTIVE = "act"
    MIDDLE = "mid"
    PASSIVE = "pass"
    MEDIO_PASSIVE = "mp"
    
    # Special features
    ARTICLE = "article"
    PROCLITIC = "proclitic"
    ENCLITIC = "enclitic"
    INDECLINABLE = "indeclform"
    INDECLINABLE_ALT = "indecl"  # Alternative spelling
    CONJUNCTION = "conj"  # For conjunctions like καί
    CONTRACTED = "contr"  # For contracted forms
    INDEFINITE = "indef"  # For indefinite pronouns
    EXCLAMATION = "exclam"  # For interjections like ὦ
    PREPOSITION = "prep"  # For prepositions
    ADVERB = "adverb"  # For adverbs
    ADVERBIAL = "adverbial"  # For adverbial forms (like βαρέως)
    RELATIVE = "relative"  # For relative pronouns like ὅς, ἥ, ὅ
    PRON3 = "pron3"  # For third declension pronouns
    PRON1 = "pron1"  # For first person pronouns
    PARTICLE = "particle"  # For particles like γε, ἄν, etc.
    UNAUGMENTED = "unaugmented"  # For unaugmented verb forms
    DESIDERATIVE = "desiderative"  # For desiderative verb forms
    DIMINUTIVE = "diminutive"  # For diminutive forms (like παιδίον)
    CAUSAL = "causal"  # For causal forms (like κατεδύσαμέν)
    INTERJECTION = "interj"  # For interjections (like ἀπαπαί)
    ADVERBIAL_IKOS = "ikos_adv"  # For adverbs in -ικῶς (like κενταυρικῶς)
    
    # Additional special features from stemtypes.table
    DEMONSTRATIVE = "demonstr"
    CONNECTIVE = "connect"  # For connecting words
    EXPLETIVE = "expletive"  # For expletive particles
    INTERROGATIVE = "interrog"  # For interrogative pronouns
    NUMERAL = "numeral"  # For number words
    PERSONAL_PRONOUN = "pers_pron"  # For personal pronouns
    RELATIVE_PRONOUN = "rel_pron"  # For relative pronouns
    INDEFINITE_RELATIVE = "indef_rel_pron"  # For indefinite relative pronouns
    ALPHABETIC = "alphabetic"  # For alphabetic characters
    
    # Dialect features
    EPIC = "epic"        # For epic dialect forms
    DORIC = "doric"      # For Doric dialect forms
    AEOLIC = "aeolic"    # For Aeolic dialect forms
    ATTIC = "attic"      # For Attic dialect forms
    IONIC = "ionic"
    POETIC = "poetic"    # For poetic forms
    HOMERIC = "homeric"  # For Homeric forms
    SYNCOPE = "syncope"  # For forms with syncope (like Δήμητρα)
    
    # Adding missing feature found in the warnings
    IMPERSONAL = "impersonal"
    
    # Adding missing features from the new warnings
    LATE = "late"           # For late Greek forms
    RARE = "rare"           # For rare forms
    APOCOPE = "apocope"     # For forms with apocope
    PROSE = "prose"         # For prose forms
    
    @classmethod
    def from_str(cls, feature: str) -> 'Feature':
        """Convert a morpheus feature string to the enum value.
        
        Args:
            feature: The feature string from morpheus
            
        Returns:
            The corresponding Feature enum value
            
        Raises:
            UnknownFeatureError: If the feature is not recognized
        """
        try:
            # Handle special cases
            if feature == "imperf":
                return cls.IMPERFECT_ALT
            if feature == "indecl":
                return cls.INDECLINABLE_ALT
            if feature == "imperat":
                return cls.IMPERATIVE_ALT
            if feature == "imperat alt":
                return cls.IMPERATIVE_ALT2
            if feature == "aor1":
                return cls.AORIST1
            if feature == "aor2":
                return cls.AORIST2
            return next(f for f in cls if f.value == feature)
        except StopIteration:
            raise UnknownFeatureError(feature)
    
    @classmethod
    def from_list(cls, features: List[str]) -> Set['Feature']:
        """Convert a list of morpheus feature strings to a set of enum values.
        
        Args:
            features: List of feature strings from morpheus
            
        Returns:
            Set of corresponding Feature enum values
            
        Raises:
            UnknownFeatureError: If any feature is not recognized
        """
        return {cls.from_str(f) for f in features}
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.name.lower().replace('_', ' ')
 