from enum import Enum, auto
from typing import Optional, Set

class UnknownMorphClassError(ValueError):
    """Raised when an unknown morphological class is encountered."""
    def __init__(self, morph_class: str):
        self.morph_class = morph_class
        super().__init__(f"Unknown morphological class: '{morph_class}'")

class MorphClass(Enum):
    """Enumeration of possible morphological classes returned by the morpheus parser."""
    # Noun/Adjective declensions
    FIRST_DECLENSION_A = "a_as"
    FIRST_DECLENSION_H = "h_hs"
    SECOND_DECLENSION = "os_ou"
    THIRD_DECLENSION = "s_os"
    
    # Common adjective patterns
    ADJ_2_1_2 = "os_h_on"  # Like ἀγαθός, -ή, -όν
    ADJ_3_3 = "hs_es"      # Like ἀληθής, -ές
    ADJ_2_2 = "os_on"      # Like βάρβαρος, -ον
    ARTICLE_ADJECTIVE = "art_adj"  # For words like αὐτός that can function as articles or adjectives
    
    # Verb patterns
    THEMATIC = "w_stem"
    ATHEMATIC = "mi_stem"
    CONTRACT = "ew_contract"
    DEPONENT = "dep"
    REGULAR = "reg_conj"    # Regular conjugation pattern
    
    # Contract verb classes
    AW_PRESENT = "aw_pr"      # Alpha contract present stem
    AW_DENOM = "aw_denom"     # Denominative alpha contract
    EW_PRESENT = "ew_pr"      # Epsilon contract present stem
    OW_PRESENT = "ow_pr"      # Omicron contract present stem
    
    # Aorist patterns
    FIRST_AORIST = "aor1"
    SECOND_AORIST = "aor2"
    ROOT_AORIST = "aor_rt"
    
    # Special forms
    MOVABLE_NU = "nu_movable"
    IRREGULAR = "irreg"
    INDECLINABLE = "indecl"
    INDEFINITE = "indef"      # For indefinite pronouns
    
    @classmethod
    def from_str(cls, morph_class: str) -> Set['MorphClass']:
        """Convert a morpheus morphological class string to a set of enum values.
        
        Args:
            morph_class: The morphological class string from morpheus
            
        Returns:
            Set of corresponding MorphClass enum values, empty set if input is empty
            
        Raises:
            UnknownMorphClassError: If any class is not recognized and not empty
        """
        if not morph_class:
            return set()
            
        # Split on whitespace and commas since morpheus can return multiple classes
        classes = set()
        parts = [p.strip() for part in morph_class.split() for p in part.split(',')]
        for part in parts:
            try:
                # Find any enum whose value is contained in this part
                found = False
                for mc in cls:
                    if mc.value in part:
                        classes.add(mc)
                        found = True
                if not found:
                    raise UnknownMorphClassError(part)
            except ValueError:
                raise UnknownMorphClassError(part)
                
        return classes
    
    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return self.name.lower().replace('_', ' ') 