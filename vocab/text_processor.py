import re
from typing import List, Set
from morph import MorphParser, MorphEntry
from .vocab_entry import VocabEntry

class TextProcessor:
    def __init__(self, morph_parser: MorphParser):
        self.morph_parser = morph_parser
        
    def extract_words(self, text: str) -> List[str]:
        """Extract individual Greek words from text, ignoring punctuation."""
        # Split on whitespace and strip punctuation
        words = re.findall(r'[\u0370-\u03FF\u1F00-\u1FFF]+', text)
        return list(set(words))  # Remove duplicates
        
    def process_word(self, word: str, interactive: bool = True) -> List[MorphEntry]:
        """Process a single word, optionally asking for user disambiguation."""
        entries = self.morph_parser.parse_word(word)
        
        if not entries:
            print(f"Warning: Could not parse word '{word}'")
            return []
            
        if len(entries) > 1 and interactive:
            return self._disambiguate_entries(word, entries)
        
        return entries
        
    def _disambiguate_entries(self, word: str, entries: List[MorphEntry]) -> List[MorphEntry]:
        """Ask user to disambiguate multiple possible parses."""
        print(f"\nMultiple possibilities for '{word}':")
        for i, entry in enumerate(entries, 1):
            print(f"{i}. {entry}")
        
        while True:
            choice = input("Enter number(s) of correct parse(s) (comma-separated) or press Enter for all: ").strip()
            if not choice:
                return entries
                
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                return [entries[i] for i in indices if 0 <= i < len(entries)]
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
                
    def create_vocab_entry(self, morph_entry: MorphEntry) -> VocabEntry:
        """Convert a MorphEntry to a VocabEntry."""
        # Strip any trailing numbers from the lemma
        lemma = re.sub(r'\d+$', '', morph_entry.lemma)
        
        # Format morphological information based on part of speech
        morph_info = self._format_morphology(morph_entry)
        
        return VocabEntry(
            lemma=lemma,
            definition=morph_entry.short_definition or "",
            part_of_speech=str(morph_entry.part_of_speech),
            morphology=morph_info
        )
        
    def _format_morphology(self, entry: MorphEntry) -> str:
        """Format morphological information based on part of speech."""
        # This is a simplified version - expand based on requirements
        pos_str = str(entry.part_of_speech)
        if pos_str == "NOUN":
            return "ὁ" if "MASCULINE" in str(entry.features) else "ἡ" if "FEMININE" in str(entry.features) else "τό"
        elif pos_str == "ADJECTIVE":
            return "ή, όν" if "FEMININE" in str(entry.features) else "ός, ά, όν"
        return None 