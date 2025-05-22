import re
from typing import List, Set, Dict
from morph import MorphParser, MorphEntry
from .vocab_entry import VocabEntry
from morph.features import Feature
from morph.morph_class import MorphClass
from morph.part_of_speech import PartOfSpeech

class TextProcessor:
    # Dictionary of irregular adjectives with their full declension patterns
    IRREGULAR_ADJECTIVES: Dict[str, str] = {
        "πολύς": "πολύς, πολλή, πολύ",
        "μέγας": "μέγας, μεγάλη, μέγα",
        "πᾶς": "πᾶς, πᾶσα, πᾶν",
        # Include more irregular adjectives as needed
    }
    
    # Dictionary of irregular pronouns and special forms
    IRREGULAR_PRONOUNS: Dict[str, str] = {
        "τίς": "τίς, τί",  # interrogative pronoun
        "τις": "τις, τι",   # indefinite pronoun
        "ὅστις": "ὅστις, ἥτις, ὅτι",
        "οὗτος": "οὗτος, αὕτη, τοῦτο",
        "ἐκεῖνος": "ἐκεῖνος, ἐκείνη, ἐκεῖνο",
        "ὅδε": "ὅδε, ἥδε, τόδε", 
        "αὐτός": "αὐτός, αὐτή, αὐτό",
        "ὅς": "ὅς, ἥ, ὅ"  # relative pronoun
    }
    
    # Track proper names we've seen but couldn't parse
    PROPER_NAMES: Set[str] = set()
    
    def __init__(self, morph_parser: MorphParser, stop_words: Set[str] = None):
        self.morph_parser = morph_parser
        self.stop_words = stop_words or set()
        
    def extract_words(self, text: str) -> List[str]:
        """Extract individual Greek words from text, ignoring punctuation."""
        # Split on whitespace first to get each potential word
        potential_words = text.split()
        words = []
        
        for word in potential_words:
            # Check if it's a beta code word with an apostrophe
            if word.startswith("'") and any(c in word for c in "/*\\()=|'<>_^"):
                words.append(word)
            # Check if it's a beta code word without apostrophe
            elif any(c in word for c in "/*\\()=|'<>_^"):
                words.append(word)
            # Otherwise extract Greek Unicode characters
            else:
                # Check for Unicode words with apostrophes
                if word.startswith("'") and any(0x0370 <= ord(c) <= 0x03FF or 0x1F00 <= ord(c) <= 0x1FFF for c in word[1:]):
                    words.append(word)
                # Extract Greek Unicode characters
                greek_word_match = re.findall(r'[\u0370-\u03FF\u1F00-\u1FFF]+', word)
                if greek_word_match:
                    words.extend(greek_word_match)
                    
        return list(set(words))  # Remove duplicates
        
    def process_word(self, word: str, interactive: bool = True) -> List[MorphEntry]:
        """Process a single word, optionally asking for user disambiguation."""
        original_word = word
        
        # Preprocess words with initial apostrophes (elided forms)
        apostrophe_chars = ["'", "ʼ", "'", "᾽", "᾿", "ʻ", "`"]
        if any(word.startswith(a) for a in apostrophe_chars):
            # Try parsing as is - the parser will handle the elided form
            pass
        
        # First try to parse all words normally
        entries = self.morph_parser.parse_word(word)
        if entries:
            if len(entries) > 1 and interactive:
                # Check if there are multiple lemmas - only then ask for disambiguation
                unique_lemmas = set(entry.lemma for entry in entries)
                if len(unique_lemmas) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 1: Try with -S flag to ignore case
        entries = self.morph_parser.parse_word(word, ignore_case=True)
        if entries:
            if len(entries) > 1 and interactive:
                # Check if there are multiple lemmas - only then ask for disambiguation
                unique_lemmas = set(entry.lemma for entry in entries)
                if len(unique_lemmas) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 2: Try with -S -n flags to ignore case and accent
        entries = self.morph_parser.parse_word(word, ignore_case=True, ignore_accent=True)
        if entries:
            if len(entries) > 1 and interactive:
                # Check if there are multiple lemmas - only then ask for disambiguation
                unique_lemmas = set(entry.lemma for entry in entries)
                if len(unique_lemmas) > 1:
                    entries = self._disambiguate_entries(word, entries)
            return entries
            
        # Fallback 3: Try capitalizing first letter with ignore case and accent flags
        if word.islower() and len(word) > 0:
            capitalized = word[0].upper() + word[1:] if len(word) > 1 else word[0].upper()
            entries = self.morph_parser.parse_word(capitalized, ignore_case=True, ignore_accent=True)
            if entries:
                if len(entries) > 1 and interactive:
                    # Check if there are multiple lemmas - only then ask for disambiguation
                    unique_lemmas = set(entry.lemma for entry in entries)
                    if len(unique_lemmas) > 1:
                        entries = self._disambiguate_entries(word, entries)
                return entries
        
        # Fallback 4: Try parsing root word without prefixes (if we have an expanded form)
        if word != original_word and word.startswith('ἐξ'):
            root_word = word[2:]  # Remove the ἐξ prefix
            root_entries = self.morph_parser.parse_word(root_word)
            
            if root_entries:
                if len(root_entries) > 1 and interactive:
                    # Check if there are multiple lemmas - only then ask for disambiguation
                    unique_lemmas = set(entry.lemma for entry in root_entries)
                    if len(unique_lemmas) > 1:
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
        # Group entries by lemma and definition to avoid duplicates
        unique_entries = {}
        for entry in entries:
            key = (entry.lemma, entry.short_definition or "(no definition)")
            if key not in unique_entries:
                unique_entries[key] = entry
        
        # If after grouping we only have one entry, return the original entries
        if len(unique_entries) == 1:
            # Check if the single lemma is in stop words
            if entries[0].lemma in self.stop_words:
                return []
            return entries
            
        print(f"\nMultiple possibilities for '{word}':")
        display_entries = list(unique_entries.values())
        for i, entry in enumerate(display_entries, 1):
            print(f"{i}. {entry.lemma}: {entry.short_definition or '(no definition)'}")
        
        while True:
            choice = input("Enter number(s) of correct parse(s) (comma-separated) or press Enter for all: ").strip()
            if not choice:
                # Check if any of the lemmas are in stop words
                if any(entry.lemma in self.stop_words for entry in entries):
                    return []
                return entries
                
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                selected_entries = []
                
                for i, idx in enumerate(indices):
                    if 0 <= idx < len(display_entries):
                        selected_lemma = display_entries[idx].lemma
                        # Add all entries from original list that match the selected lemma
                        selected_entries.extend([e for e in entries if e.lemma == selected_lemma])
                
                # Check if any of the selected lemmas are in stop words
                if any(entry.lemma in self.stop_words for entry in selected_entries):
                    return []
                return selected_entries
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")
                
    def create_vocab_entry(self, morph_entry: MorphEntry) -> VocabEntry:
        """Convert a MorphEntry to a VocabEntry."""
        # Strip any trailing numbers from the lemma
        lemma = re.sub(r'\d+$', '', morph_entry.lemma)
        
        # Special case handling for certain words regardless of part of speech
        # This ensures they get the right format even if morphological analysis is incomplete
        if lemma == "πολύς":
            return VocabEntry(
                lemma=lemma,
                definition=morph_entry.short_definition or "",
                part_of_speech="adjective" if MorphClass.is_adjective(morph_entry.morph_classes) else str(morph_entry.part_of_speech),
                morphology=self.IRREGULAR_ADJECTIVES[lemma]
            )
        elif lemma in ["τίς", "τις"]:
            return VocabEntry(
                lemma=lemma,
                definition=morph_entry.short_definition or "",
                part_of_speech=str(morph_entry.part_of_speech),
                morphology=self.IRREGULAR_PRONOUNS[lemma]
            )
            
        # Format morphological information based on part of speech
        morph_info = self._format_morphology(morph_entry)
        
        # Determine correct part of speech
        part_of_speech = str(morph_entry.part_of_speech)
        if MorphClass.is_adjective(morph_entry.morph_classes):
            part_of_speech = "adjective"
            
        return VocabEntry(
            lemma=lemma,
            definition=morph_entry.short_definition or "",
            part_of_speech=part_of_speech,
            morphology=morph_info
        )
        
    def _format_morphology(self, entry: MorphEntry) -> str:
        """Format morphological information based on part of speech and features."""
        # For adverbs, mark them with (adv.)
        if Feature.ADVERB in entry.features or Feature.ADVERBIAL in entry.features:
            return "(adv.)"
            
        # Handle demonstratives, pronouns, and similar words
        if (Feature.DEMONSTRATIVE in entry.features or 
            MorphClass.PRON_ADJ1 in entry.morph_classes or 
            MorphClass.PRON_ADJ3 in entry.morph_classes or
            Feature.RELATIVE_PRONOUN in entry.features or
            Feature.PERSONAL_PRONOUN in entry.features or
            Feature.INDEFINITE_RELATIVE in entry.features or
            entry.lemma in self.IRREGULAR_PRONOUNS):
            
            # Use our dictionary for irregular pronouns
            if entry.lemma in self.IRREGULAR_PRONOUNS:
                return self.IRREGULAR_PRONOUNS[entry.lemma]
                
            # For other pronouns, use a generalized format
            else:
                # If we have a masculine form, create a pronoun trio
                if Feature.MASCULINE in entry.features:
                    if entry.lemma.endswith("ος"):
                        return f"{entry.lemma}, ή, όν" if "ή," in str(entry.features) else f"{entry.lemma}, ά, όν"
                    elif Feature.MASC_FEM in entry.features:
                        return f"{entry.lemma}, τό"
                    elif Feature.MASC_FEM_NEUT in entry.features:
                        return f"{entry.lemma}"
                
                # Otherwise return simple gender marker
                return None
            
        # Check if this is an adjective using morphological classes
        if MorphClass.is_adjective(entry.morph_classes):
            return self._format_adjective_morphology(entry)
        # Handle nouns
        elif entry.part_of_speech == PartOfSpeech.NOUN and not MorphClass.is_adjective(entry.morph_classes):
            return self._format_noun_morphology(entry)
        # Handle articles
        elif Feature.ARTICLE in entry.features:
            return "ὁ/ἡ/τό"
        # Handle particles, conjunctions, etc.
        elif entry.part_of_speech in [PartOfSpeech.PARTICLE, PartOfSpeech.CONJUNCTION, 
                                      PartOfSpeech.PREPOSITION, PartOfSpeech.INTERJECTION]:
            return None
            
        return None
        
    def _format_noun_morphology(self, entry: MorphEntry) -> str:
        """Format noun morphology information."""
        # Determine the gender and article
        gender_article = ""
        if Feature.MASCULINE in entry.features:
            gender_article = "ὁ"
        elif Feature.FEMININE in entry.features:
            gender_article = "ἡ"
        elif Feature.NEUTER in entry.features:
            gender_article = "τό"
        elif Feature.MASC_FEM in entry.features:
            gender_article = "ὁ, ἡ"
        
        # Add genitive ending for 3rd declension nouns or irregular 1st/2nd declension
        gen_ending = ""
        
        # Special case handling for specific words
        if entry.lemma == "ὕβρις":
            return "εως, ἡ"
        
        # Check if it's a 3rd declension noun
        is_third_decl = (MorphClass.THIRD_DECLENSION in entry.morph_classes or 
                         MorphClass.IRREGULAR_DECL3 in entry.morph_classes or
                         MorphClass.S_DOS_STEM in entry.morph_classes or
                         MorphClass.IS_IDOS_STEM in entry.morph_classes or
                         MorphClass.HS_EOS_STEM in entry.morph_classes or
                         MorphClass.MA_MATOS in entry.morph_classes or
                         MorphClass.N_NOS in entry.morph_classes or
                         MorphClass.HR_EROS in entry.morph_classes)
                         
        # For words ending in -ις, add gen. -εως
        if is_third_decl:
            # Special case for ὕβρις
            if entry.lemma == "ὕβρις":
                gen_ending = "εως"
            elif entry.lemma.endswith("ις") and MorphClass.IS_EWS in entry.morph_classes:
                gen_ending = "εως"
            # For words ending in -μα, add gen. -ματος
            elif entry.lemma.endswith("μα") and MorphClass.MA_MATOS in entry.morph_classes:
                gen_ending = "ματος"
            # For words ending in -ηρ, add gen. -ερος
            elif entry.lemma.endswith("ηρ") and MorphClass.HR_EROS in entry.morph_classes:
                gen_ending = "ερος"
            # For words ending in -ις, add gen. -ιδος
            elif entry.lemma.endswith("ις") and MorphClass.IS_IDOS_STEM in entry.morph_classes:
                gen_ending = "ιδος"
            # For words ending in -ων, add gen. -οντος
            elif entry.lemma.endswith("ων"):
                gen_ending = "οντος"
            # For words ending in -ης, add gen. -ους
            elif entry.lemma.endswith("ης") and MorphClass.HS_EOS_STEM in entry.morph_classes:
                gen_ending = "ους"
            # For words ending in -ος (like σκεῦος), add gen. -εος or -ους
            elif entry.lemma.endswith("ος") and (MorphClass.HS_EOS_STEM in entry.morph_classes or 
                                           "neut" in str(entry.features) and "sg" in str(entry.features)):
                gen_ending = "εος"
            # For words ending in consonant, add gen. -ος
            elif not entry.lemma.endswith(("α", "η", "ος", "ον")):
                gen_ending = "ος"
            # Default 3rd declension ending
            else:
                gen_ending = "ος"
        
        # Return formatted string with genitive ending and article
        if gen_ending:
            return f"{gen_ending}, {gender_article}"
        else:
            return gender_article
    
    def _format_adjective_morphology(self, entry: MorphEntry) -> str:
        """Format adjective morphology information."""
        lemma = entry.lemma
        
        # Check for irregular adjectives
        if lemma in self.IRREGULAR_ADJECTIVES:
            return self.IRREGULAR_ADJECTIVES[lemma]
            
        # Handle adjective patterns based on morphological classes
        if MorphClass.ADJ_2_1_2 in entry.morph_classes:
            return "ος, ή, όν" if "ή," in str(entry.features) else "ός, ά, όν"
        elif MorphClass.ADJ_2_2 in entry.morph_classes:
            return "ος, ον"
        elif MorphClass.ADJ_3_3 in entry.morph_classes:
            return "ής, ές"
        elif MorphClass.US_EIA_U in entry.morph_classes:
            return "ύς, εῖα, ύ"
        elif MorphClass.WN_ON in entry.morph_classes or MorphClass.WN_ON_COMP in entry.morph_classes:
            return "ων, ον"
        
        # Fallback to endings if morphological class doesn't provide format
        elif lemma.endswith("ος"):
            # Adjectives with three endings (masc, fem, neut)
            if Feature.FEMININE in entry.features:
                return "ος, ή, όν" if "ή," in str(entry.features) else "ός, ά, όν"
            # Adjectives with two endings (masc/fem, neut)
            else:
                return "ος, ον"
        elif lemma.endswith("ης"):
            return "ής, ές"
        elif lemma.endswith("υς"):
            return "ύς, εῖα, ύ"
        elif lemma.endswith("ων"):
            return "ων, ον"
        
        # Default format for other adjectives
        return None 