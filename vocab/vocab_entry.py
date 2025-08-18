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
        return self._greek_sort_key(self.lemma) < self._greek_sort_key(other.lemma)
    
    def _greek_sort_key(self, text: str) -> str:
        """Create a sort key for Greek text that strips diacritics and follows Greek alphabetical order."""
        # Normalize to NFD to separate base characters from diacritics
        normalized = unicodedata.normalize('NFD', text.lower())
        
        # Remove all combining diacritical marks (accents, breathing marks, etc.)
        # These are Unicode categories starting with 'M' (marks)
        stripped = ''.join(char for char in normalized 
                          if not unicodedata.category(char).startswith('M'))
        
        return stripped
    
    def _get_headword(self) -> str:
        """Get the headword portion of the entry (lemma + morphology)."""
        if not self.morphology:
            return self.lemma
            
        # For adverbs (marked with (adv.)), just return the lemma
        if self.morphology == "(adv.)":
            return self.lemma
            
        # For entries with morphology, combine lemma and morphology
        # If morphology is article only (ὁ, ἡ, τό), include it with the lemma
        if self.morphology in ["ὁ", "ἡ", "τό", "ὁ, ἡ", "ὁ/ἡ/τό"]:
            return f"{self.lemma}, {self.morphology}"
            
        # For demonstrative pronouns that include full declension patterns
        if self.morphology and "," in self.morphology and self.lemma in self.morphology.split(",")[0]:
            # For forms like "οὗτος, αὕτη, τοῦτο" where the lemma is part of the morphology
            return f"{self.lemma}, {self.morphology.split(',', 1)[1].strip()}"
            
        # For entries with genitive or adjectival endings
        if self.morphology and ", " in self.morphology and any(gender in self.morphology for gender in ["ὁ", "ἡ", "τό"]):
            try:
                # This has a genitive ending and gender marker
                parts = self.morphology.split(", ")
                if len(parts) == 2:
                    genitive, article = parts
                    # Format: lemma, genitive_ending, article
                    return f"{self.lemma}, {genitive}, {article}"
                else:
                    # If we have more or fewer parts than expected, just use the whole morphology
                    return f"{self.lemma}, {self.morphology}"
            except ValueError:
                # If there's any error in unpacking, fall back to simple format
                return f"{self.lemma}, {self.morphology}"
            
        # For adjective endings or other formatting, use as is
        return f"{self.lemma}, {self.morphology}"
    
    def _get_definition(self) -> str:
        """Get the definition portion of the entry."""
        if self.morphology == "(adv.)":
            return f"(adv.) {self.definition}"
        return self.definition
    
    def format_entry(self) -> str:
        """Format the entry for display in a vocabulary list."""
        return f"{self._get_headword()}: {self._get_definition()}"
    
    def format_latex_entry(self) -> str:
        """Format the entry for LaTeX output."""
        return f"\\vocabentry{{{self._get_headword()}}}{{{self._get_definition()}}}" 