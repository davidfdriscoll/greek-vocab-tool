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
        parts = [self.lemma]
        if self.morphology:
            parts.append(self.morphology)
        parts.append(self.definition)
        return ": ".join([", ".join(parts[:-1]), parts[-1]]) 