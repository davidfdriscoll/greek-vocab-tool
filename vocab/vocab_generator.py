from typing import List, Set, Dict
from morph import MorphParser
from morph.morph_class import MorphClass
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
                
                # Add logic to prefer better morphological analyses for the same lemma  
                if vocab_entry.lemma not in vocab_dict:
                    # First time seeing this lemma - add it
                    vocab_dict[vocab_entry.lemma] = vocab_entry
                else:
                    # We've seen this lemma before - check if we should replace
                    existing_entry = vocab_dict[vocab_entry.lemma]
                    # Prefer US_EIA_U over US_U morphological class (ἡδύς case: εῖα,ύ vs ὁ)
                    # This handles cases where Morpheus gives both analyses but US_EIA_U is correct
                    if (MorphClass.US_EIA_U in entry.morph_classes and 
                        existing_entry.part_of_speech == "noun" and 
                        existing_entry.morphology == "ὁ"):
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