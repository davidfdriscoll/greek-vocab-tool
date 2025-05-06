import re
from typing import List, Set
from morph import MorphParser, MorphEntry
from .vocab_entry import VocabEntry
from morph.features import Feature
from morph.morph_class import MorphClass
from morph.part_of_speech import PartOfSpeech

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
        """Format morphological information based on part of speech and features."""
        # For adverbs, mark them with (adv.)
        if Feature.ADVERB in entry.features or Feature.ADVERBIAL in entry.features:
            return "(adv.)"
            
        # Handle nouns
        if entry.part_of_speech == PartOfSpeech.NOUN:
            return self._format_noun_morphology(entry)
        # Handle adjectives
        elif entry.part_of_speech == PartOfSpeech.ADJECTIVE:
            return self._format_adjective_morphology(entry)
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
        
        # Check if it's a 3rd declension noun
        is_third_decl = (MorphClass.THIRD_DECLENSION in entry.morph_classes or 
                         MorphClass.IRREGULAR_DECL3 in entry.morph_classes or
                         MorphClass.S_DOS_STEM in entry.morph_classes or
                         MorphClass.IS_IDOS_STEM in entry.morph_classes or
                         MorphClass.HS_EOS_STEM in entry.morph_classes or
                         MorphClass.MA_MATOS in entry.morph_classes or
                         MorphClass.N_NOS in entry.morph_classes or
                         MorphClass.HR_EROS in entry.morph_classes)
                         
        lemma = entry.lemma
        
        if is_third_decl:
            # For words ending in -ις, add gen. -εως
            if lemma.endswith("ις") and MorphClass.IS_EWS in entry.morph_classes:
                gen_ending = ", εως"
            # For words ending in -μα, add gen. -ματος
            elif lemma.endswith("μα") and MorphClass.MA_MATOS in entry.morph_classes:
                gen_ending = ", ματος"
            # For words ending in -ηρ, add gen. -ερος
            elif lemma.endswith("ηρ") and MorphClass.HR_EROS in entry.morph_classes:
                gen_ending = ", ερος"
            # For words ending in -ις, add gen. -ιδος
            elif lemma.endswith("ις") and MorphClass.IS_IDOS_STEM in entry.morph_classes:
                gen_ending = ", ιδος"
            # For words ending in -ων, add gen. -οντος
            elif lemma.endswith("ων"):
                gen_ending = ", οντος"
            # For words ending in -ης, add gen. -ους
            elif lemma.endswith("ης") and MorphClass.HS_EOS_STEM in entry.morph_classes:
                gen_ending = ", ους"
            # For words ending in consonant, add gen. -ος
            elif not lemma.endswith(("α", "η", "ος", "ον")):
                gen_ending = ", ος"
            # Default 3rd declension ending
            else:
                gen_ending = ", ος"
        
        # Return formatted string
        if gen_ending:
            return f"{lemma}{gen_ending}, {gender_article}"
        else:
            return gender_article
    
    def _format_adjective_morphology(self, entry: MorphEntry) -> str:
        """Format adjective morphology information."""
        lemma = entry.lemma
        
        # Common endings for adjectives
        if lemma.endswith("ος"):
            # Adjectives with three endings (masc, fem, neut)
            if Feature.FEMININE in entry.features:
                return "ος, ή, όν" if "ή," in str(entry.features) else "ός, ά, όν"
            # Adjectives with two endings (masc/fem, neut)
            else:
                return "ος, ον"
        elif lemma.endswith("ης"):
            return "ής, ές"  # Third declension adjectives like ἀληθής
        elif lemma.endswith("υς"):
            return "ύς, εῖα, ύ"  # Adjectives like γλυκύς
        elif lemma.endswith("ων"):
            return "ων, ον"  # Adjectives like σώφρων
        
        # Default format for other adjectives
        return None 