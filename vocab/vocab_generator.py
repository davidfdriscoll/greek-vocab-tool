from typing import List, Set, Dict
from morph import MorphParser
from .text_processor import TextProcessor
from .vocab_entry import VocabEntry

class VocabGenerator:
    def __init__(self, morph_parser: MorphParser):
        self.text_processor = TextProcessor(morph_parser)
        
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
                vocab_entry = self.text_processor.create_vocab_entry(entry)
                # Only add if we haven't seen this lemma before
                if vocab_entry.lemma not in vocab_dict:
                    vocab_dict[vocab_entry.lemma] = vocab_entry
        
        # Sort entries alphabetically
        return sorted(vocab_dict.values())
        
    def format_vocab_list(self, entries: List[VocabEntry]) -> str:
        """Format the vocabulary list for display."""
        return "\n".join(entry.format_entry() for entry in entries) 