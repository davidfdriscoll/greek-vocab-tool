from typing import List, Set, Dict
from morph import MorphParser
from .text_processor import TextProcessor
from .vocab_entry import VocabEntry

class VocabGenerator:
    def __init__(self, morph_parser: MorphParser, stop_words: Set[str] = None, latex_output: bool = False):
        self.text_processor = TextProcessor(morph_parser)
        self.stop_words = stop_words or set()
        self.latex_output = latex_output
        
    def generate_vocab_list(self, text: str, interactive: bool = True) -> List[VocabEntry]:
        """Generate a vocabulary list from the given text."""
        # Extract unique words
        words = self.text_processor.extract_words(text)
        
        # Process each word and create vocab entries
        # Use a dictionary to track unique lemmas
        vocab_dict: Dict[str, VocabEntry] = {}
        for word in words:
            morph_entries = self.text_processor.process_word(word, interactive)
            for entry in morph_entries:
                # Skip if the lemma is in stop words
                if entry.lemma in self.stop_words:
                    continue
                vocab_entry = self.text_processor.vocab_entry_service.create_vocab_entry(entry)
                # Only add if we haven't seen this lemma before
                if vocab_entry.lemma not in vocab_dict:
                    vocab_dict[vocab_entry.lemma] = vocab_entry
        
        # Add proper names that couldn't be parsed
        for proper_name in self.text_processor.PROPER_NAMES:
            # Skip if the proper name is in stop words
            if proper_name in self.stop_words:
                continue
            # Only add if we haven't already added this name
            if proper_name not in vocab_dict:
                vocab_entry = VocabEntry(
                    lemma=proper_name,
                    definition="COULD NOT PARSE, LIKELY PROPER NAME",
                    part_of_speech="noun",
                    morphology="ὁ"  # Assume masculine
                )
                vocab_dict[proper_name] = vocab_entry
        
        # Sort entries alphabetically
        return sorted(vocab_dict.values())
        
    def format_vocab_list(self, entries: List[VocabEntry]) -> str:
        """Format the vocabulary list for display."""
        if self.latex_output:
            return "\n".join(entry.format_latex_entry() for entry in entries)
        return "\n".join(entry.format_entry() for entry in entries) 