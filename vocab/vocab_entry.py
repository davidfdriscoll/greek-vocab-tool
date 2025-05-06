from dataclasses import dataclass
from typing import Optional
import unicodedata

@dataclass(frozen=True)  # Making the dataclass immutable ensures proper hash behavior
class VocabEntry:
    """A single vocabulary entry with lemma, definition, and morphological information."""
    lemma: str
    definition: str
    part_of_speech: str
    morphology: Optional[str] = None
    
    def __lt__(self, other):
        """Enable sorting by lemma with proper Greek character handling."""
        # Normalize both strings to ensure consistent sorting
        a = unicodedata.normalize('NFD', self.lemma.lower())
        b = unicodedata.normalize('NFD', other.lemma.lower())
        return a < b
    
    def format_entry(self) -> str:
        """Format the entry for display in a vocabulary list."""
        # For entries without morphology, just show lemma: definition
        if not self.morphology:
            return f"{self.lemma}: {self.definition}"
            
        # For adverbs (marked with (adv.)), move the (adv.) after the colon
        if self.morphology == "(adv.)":
            return f"{self.lemma}: (adv.) {self.definition}"
            
        # For entries with morphology, show lemma, morphology: definition
        # If morphology is article only (ὁ, ἡ, τό), put it before the definition
        if self.morphology in ["ὁ", "ἡ", "τό", "ὁ, ἡ", "ὁ/ἡ/τό"]:
            return f"{self.lemma}, {self.morphology}: {self.definition}"
            
        # For demonstrative pronouns that include full declension patterns
        if self.morphology and "," in self.morphology and self.lemma in self.morphology.split(",")[0]:
            # For forms like "οὗτος, αὕτη, τοῦτο" where the lemma is part of the morphology
            return f"{self.lemma}, {self.morphology.split(',', 1)[1].strip()}: {self.definition}"
            
        # For entries with genitive or adjectival endings, add them after the lemma
        if self.morphology and ", " in self.morphology and any(gender in self.morphology for gender in ["ὁ", "ἡ", "τό"]):
            try:
                # This has a genitive ending and gender marker
                parts = self.morphology.split(", ")
                if len(parts) == 2:
                    genitive, article = parts
                    # Format: lemma, genitive_ending, article: definition
                    return f"{self.lemma}, {genitive}, {article}: {self.definition}"
                else:
                    # If we have more or fewer parts than expected, just use the whole morphology
                    return f"{self.lemma}, {self.morphology}: {self.definition}"
            except ValueError:
                # If there's any error in unpacking, fall back to simple format
                return f"{self.lemma}, {self.morphology}: {self.definition}"
            
        # For adjective endings or other formatting, use as is
        return f"{self.lemma}, {self.morphology}: {self.definition}" 