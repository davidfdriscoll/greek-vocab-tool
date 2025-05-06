from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)  # Making the dataclass immutable ensures proper hash behavior
class VocabEntry:
    """A single vocabulary entry with lemma, definition, and morphological information."""
    lemma: str
    definition: str
    part_of_speech: str
    morphology: Optional[str] = None
    
    def __lt__(self, other):
        """Enable sorting by lemma."""
        return self.lemma < other.lemma
    
    def format_entry(self) -> str:
        """Format the entry for display in a vocabulary list."""
        # For entries without morphology, just show lemma: definition
        if not self.morphology:
            return f"{self.lemma}: {self.definition}"
            
        # For entries with morphology, show lemma, morphology: definition
        # If morphology is article only (ὁ, ἡ, τό), put it before the definition
        if self.morphology in ["ὁ", "ἡ", "τό", "ὁ, ἡ", "ὁ/ἡ/τό"]:
            return f"{self.lemma}, {self.morphology}: {self.definition}"
        # If morphology starts with a parenthesis (like "(adv.)"), put it before the definition
        elif self.morphology.startswith("("):
            return f"{self.lemma} {self.morphology}: {self.definition}"
        # For entries with genitive or adjectival endings, embed them in the entry
        else:
            return f"{self.lemma}, {self.morphology}: {self.definition}" 