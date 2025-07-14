import re
from typing import List, Set, Dict
from morph import MorphParser, MorphEntry
from .vocab_entry_service import VocabEntryService
from morph.features import Feature
from morph.morph_class import MorphClass
from morph.part_of_speech import PartOfSpeech

class TextProcessor:
    # Track proper names we've seen but couldn't parse
    PROPER_NAMES: Set[str] = set()
    
    def __init__(self, morph_parser: MorphParser):
        self.morph_parser = morph_parser
        self.vocab_entry_service = VocabEntryService()
        
    def extract_words(self, text: str) -> List[str]:
        """Extract individual Greek words from text, preserving elision apostrophes."""
        # Split on whitespace first to get each potential word
        potential_words = text.split()
        words = []
        
        # Define apostrophe characters that can indicate elision
        apostrophe_chars = ["'", "ʼ", "'", "᾽", "᾿", "ʻ", "`"]
        
        for word in potential_words:
            # Check if it's a beta code word with an apostrophe
            if word.startswith("'") and any(c in word for c in "/*\\()=|'<>_^"):
                words.append(word)
            # Check if it's a beta code word without apostrophe
            elif any(c in word for c in "/*\\()=|'<>_^"):
                words.append(word)
            # Otherwise extract Greek Unicode characters
            else:
                # Check for Unicode words with initial apostrophes
                if word.startswith("'") and any(0x0370 <= ord(c) <= 0x03FF or 0x1F00 <= ord(c) <= 0x1FFF for c in word[1:]):
                    words.append(word)
                else:
                    # Extract Greek Unicode characters, preserving trailing elision apostrophes
                    # First, find all Greek character sequences
                    greek_matches = list(re.finditer(r'[\u0370-\u03FF\u1F00-\u1FFF]+', word))
                    
                    for match in greek_matches:
                        greek_word = match.group()
                        start_pos = match.start()
                        end_pos = match.end()
                        
                        # Check if there's an elision apostrophe immediately after this Greek word
                        if end_pos < len(word) and word[end_pos] in apostrophe_chars:
                            # Include the apostrophe as part of the word
                            greek_word += word[end_pos]
                        
                        words.append(greek_word)
                    
        return list(set(words))  # Remove duplicates
        
    def process_word(self, word: str, interactive: bool = True) -> List[MorphEntry]:
        """Process a single word, optionally asking for user disambiguation."""
        original_word = word
        
        # Normalize apostrophe characters that cause beta code conversion issues
        # The modifier letter apostrophe (ʼ) gets converted to ')' instead of "'"
        # So convert it to Greek koronis (᾽) which converts correctly to a single apostrophe
        apostrophe_mapping = {
            'ʼ': '᾽',  # modifier letter apostrophe → Greek koronis
            'ʻ': '᾽',  # modifier letter turned comma → Greek koronis  
            '`': '᾽',  # grave accent → Greek koronis
            chr(0x2019): '᾽',  # right single quotation mark → Greek koronis
        }
        
        for bad_apos, good_apos in apostrophe_mapping.items():
            word = word.replace(bad_apos, good_apos)
        
        # Preprocess words with initial apostrophes (elided forms)
        apostrophe_chars = ["'", "ʼ", "'", "᾽", "᾿", "ʻ", "`"]
        if any(word.startswith(a) for a in apostrophe_chars):
            # Try parsing as is - the parser will handle the elided form
            pass
        
        # First try to parse all words normally
        entries = self.morph_parser.parse_word(word)
        if entries:
            # Always collapse redundant entries regardless of interactive mode
            entries = self._collapse_redundant_entries(entries)
            if len(entries) > 1 and interactive:
                # Check if there are still multiple unique options after collapsing
                unique_entries = {}
                for entry in entries:
                    base_lemma = re.sub(r'\d+$', '', entry.lemma)
                    key = (base_lemma, entry.short_definition or "(no definition)")
                    if key not in unique_entries:
                        unique_entries[key] = entry
                
                if len(unique_entries) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 1: Try with -S flag to ignore case
        entries = self.morph_parser.parse_word(word, ignore_case=True)
        if entries:
            # Always collapse redundant entries regardless of interactive mode
            entries = self._collapse_redundant_entries(entries)
            if len(entries) > 1 and interactive:
                # Check if there are still multiple unique options after collapsing
                unique_entries = {}
                for entry in entries:
                    base_lemma = re.sub(r'\d+$', '', entry.lemma)
                    key = (base_lemma, entry.short_definition or "(no definition)")
                    if key not in unique_entries:
                        unique_entries[key] = entry
                
                if len(unique_entries) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 2: Try with -S -n flags to ignore case and accent
        entries = self.morph_parser.parse_word(word, ignore_case=True, ignore_accent=True)
        if entries:
            # Always collapse redundant entries regardless of interactive mode
            entries = self._collapse_redundant_entries(entries)
            if len(entries) > 1 and interactive:
                # Check if there are still multiple unique options after collapsing
                unique_entries = {}
                for entry in entries:
                    base_lemma = re.sub(r'\d+$', '', entry.lemma)
                    key = (base_lemma, entry.short_definition or "(no definition)")
                    if key not in unique_entries:
                        unique_entries[key] = entry
                
                if len(unique_entries) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 3: Try capitalizing first letter with ignore case and accent flags
        if word.islower() and len(word) > 0:
            capitalized = word[0].upper() + word[1:] if len(word) > 1 else word[0].upper()
            entries = self.morph_parser.parse_word(capitalized, ignore_case=True, ignore_accent=True)
            if entries:
                # Always collapse redundant entries regardless of interactive mode
                entries = self._collapse_redundant_entries(entries)
                if len(entries) > 1 and interactive:
                    # Check if there are still multiple unique options after collapsing
                    unique_entries = {}
                    for entry in entries:
                        base_lemma = re.sub(r'\d+$', '', entry.lemma)
                        key = (base_lemma, entry.short_definition or "(no definition)")
                        if key not in unique_entries:
                            unique_entries[key] = entry
                    
                    if len(unique_entries) > 1:
                        entries = self._disambiguate_entries(word, entries)
                return entries
        
        # Fallback 4: Try parsing root word without prefixes (if we have an expanded form)
        if word != original_word and word.startswith('ἐξ'):
            root_word = word[2:]  # Remove the ἐξ prefix
            root_entries = self.morph_parser.parse_word(root_word)
            
            if root_entries:
                # Always collapse redundant entries regardless of interactive mode
                root_entries = self._collapse_redundant_entries(root_entries)
                if len(root_entries) > 1 and interactive:
                    # Check if there are still multiple unique options after collapsing
                    unique_entries = {}
                    for entry in root_entries:
                        base_lemma = re.sub(r'\d+$', '', entry.lemma)
                        key = (base_lemma, entry.short_definition or "(no definition)")
                        if key not in unique_entries:
                            unique_entries[key] = entry
                    
                    if len(unique_entries) > 1:
                        root_entries = self._disambiguate_entries(word, root_entries)
                
                # We found entries for the root word, create entries for the prefix + root
                for entry in root_entries:
                    # Create a new entry with the lemma prefixed with ἐξ
                    if not entry.lemma.startswith('ἐξ'):
                        entry.lemma = 'ἐξ' + entry.lemma
                return root_entries

        # If all parsing attempts failed
        if word and word[0].isupper() and word.isalpha():
            # Record it as a proper name and print warning
            print(f"Warning: COULD NOT PARSE '{word}', LIKELY PROPER NAME")
            self.PROPER_NAMES.add(word)
        else:
            print(f"Warning: Could not parse word '{word}'")
        return []
        
    def _disambiguate_entries(self, word: str, entries: List[MorphEntry]) -> List[MorphEntry]:
        """Ask user to disambiguate multiple possible parses."""
        # First, collapse truly redundant entries (same base lemma, definition, features, and morph classes)
        collapsed_entries = self._collapse_redundant_entries(entries)
        
        # Group entries by base lemma and definition to avoid duplicates in display
        unique_entries = {}
        for entry in collapsed_entries:
            # Strip trailing numbers from lemma for grouping
            base_lemma = re.sub(r'\d+$', '', entry.lemma)
            key = (base_lemma, entry.short_definition or "(no definition)")
            if key not in unique_entries:
                unique_entries[key] = entry
        
        # If after grouping we only have one entry, return the collapsed entries
        if len(unique_entries) == 1:
            return collapsed_entries
            
        print(f"\nMultiple possibilities for '{word}':")
        display_entries = list(unique_entries.values())
        for i, entry in enumerate(display_entries, 1):
            base_lemma = re.sub(r'\d+$', '', entry.lemma)
            print(f"{i}. {base_lemma}: {entry.short_definition or '(no definition)'}")
        
        while True:
            choice = input("Enter number(s) of correct parse(s) (comma-separated) or press Enter for all: ").strip()
            if not choice:
                return collapsed_entries
                
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_entries = []
                
                for i, idx in enumerate(indices):
                    if 0 <= idx < len(display_entries):
                        # Use the specific entry from display_entries, not just base lemma matching
                        selected_entry = display_entries[idx]
                        # Find all entries from collapsed list that match both base lemma AND definition
                        selected_base_lemma = re.sub(r'\d+$', '', selected_entry.lemma)
                        selected_definition = selected_entry.short_definition
                        
                        matching_entries = [e for e in collapsed_entries 
                                          if (re.sub(r'\d+$', '', e.lemma) == selected_base_lemma and 
                                              e.short_definition == selected_definition)]
                        selected_entries.extend(matching_entries)
                
                return selected_entries
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
                
    def _collapse_redundant_entries(self, entries: List[MorphEntry]) -> List[MorphEntry]:
        """Collapse entries that are truly redundant (same base lemma and definition)."""
        # Group entries by their "signature" - base lemma, definition, and part of speech
        groups = {}
        for entry in entries:
            base_lemma = re.sub(r'\d+$', '', entry.lemma)
            # Create a signature based on base lemma, definition, and part of speech only
            # We don't include features and morph_classes because those represent different
            # inflected forms of the same lexical entry, not different words
            signature = (
                base_lemma,
                entry.short_definition or "",
                entry.part_of_speech
            )
            if signature not in groups:
                groups[signature] = []
            groups[signature].append(entry)
        
        # For each group, keep only one representative entry (prefer the one without numbers)
        collapsed = []
        for signature, group_entries in groups.items():
            # Sort by lemma to prefer entries without numbers, then by lemma
            sorted_entries = sorted(group_entries, key=lambda e: (re.search(r'\d+$', e.lemma) is not None, e.lemma))
            representative = sorted_entries[0]
            # Strip the number from the representative's lemma for cleaner display
            representative.lemma = re.sub(r'\d+$', '', representative.lemma)
            collapsed.append(representative)
        
        return collapsed
 