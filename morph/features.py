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
    
    # Case
    NOMINATIVE = "nom"
    GENITIVE = "gen"
    DATIVE = "dat"
    ACCUSATIVE = "acc"
    VOCATIVE = "voc"
    
    # Tense
    PRESENT = "pres"
    IMPERFECT = "impf"
    IMPERFECT_ALT = "imperf"  # Alternative spelling from Morpheus
    FUTURE = "fut"
    AORIST = "aor"
    PERFECT = "perf"
    PLUPERFECT = "plup"
    
    # Mood
    INDICATIVE = "ind"
    SUBJUNCTIVE = "subj"
    OPTATIVE = "opt"
    IMPERATIVE = "imptv"
    INFINITIVE = "inf"
    PARTICIPLE = "part"
    
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
    
    # Dialect features
    EPIC = "epic"        # For epic dialect forms
    DORIC = "doric"      # For Doric dialect forms
    AEOLIC = "aeolic"    # For Aeolic dialect forms
    ATTIC = "attic"      # For Attic dialect forms
    IONIC = "ionic"      # For Ionic dialect forms
    
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
            # Handle the imperfect alternate spelling
            if feature == "imperf":
                return cls.IMPERFECT_ALT
            # Handle the indeclinable alternate spelling
            if feature == "indecl":
                return cls.INDECLINABLE_ALT
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
 