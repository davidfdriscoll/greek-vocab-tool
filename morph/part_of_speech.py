from enum import Enum, auto

class UnknownPartOfSpeechError(ValueError):
    """Raised when an unknown part of speech code is encountered."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Unknown part of speech code: '{code}'")

class PartOfSpeech(Enum):
    """Enumeration of possible parts of speech returned by the morpheus parser."""
    NOUN = "N"  # Note: This includes adjectives, which are distinguished by morph_class
    VERB = "V"
    ARTICLE = "N"    # Note: Distinguished from nouns by features
    ADVERB = "Adv"
    PARTICLE = "Part"
    PREPOSITION = "Prep"
    PRONOUN = "Pron"
    CONJUNCTION = "Conj"
    INTERJECTION = "Interj"
    NUMERAL = "Num"
    PARTICIPLE = "P"  # For participles like εἰωθότων
    ETHNIC = "E"  # For ethnic designations and proper names
    
    @classmethod
    def from_str(cls, code: str) -> 'PartOfSpeech':
        """Convert a morpheus part of speech code to the enum value.
        
        Args:
            code: The part of speech code from morpheus
            
        Returns:
            The corresponding PartOfSpeech enum value
            
        Raises:
            UnknownPartOfSpeechError: If the code is not recognized
        """
        # Direct mapping for simple cases
        try:
            return cls(code)
        except ValueError:
            raise UnknownPartOfSpeechError(code)
            
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.name.lower().replace('_', ' ') 