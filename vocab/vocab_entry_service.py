import re
from typing import Dict
from morph import MorphEntry
from .vocab_entry import VocabEntry
from morph.features import Feature
from morph.morph_class import MorphClass
from morph.part_of_speech import PartOfSpeech


class VocabEntryService:
    """Service for creating and formatting vocabulary entries from morphological data."""
    
    # Dictionary of irregular adjectives with their full declension patterns
    IRREGULAR_ADJECTIVES: Dict[str, str] = {
        "πολύς": "πολύς, πολλή, πολύ",
        "μέγας": "μέγας, μεγάλη, μέγα",
        "πᾶς": "πᾶς, πᾶσα, πᾶν",
        "ἄλλος": "ἄλλη, ἄλλο",
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
                        # Apply the same accentuation rule for pronouns
                        final_accented = self._is_final_syllable_accented(entry.lemma)
                        # Check if the letter before -ος is ε, ι, or ρ (alpha feminine rule)
                        if len(entry.lemma) >= 2 and entry.lemma[-2] in "ειρ":
                            return "ά, όν" if final_accented else "α, ον"  # Always alpha after ε, ι, ρ
                        else:
                            return "ή, όν" if final_accented else "α, ον"
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
        
        # For indeclinable forms, just return the gender article without genitive
        if Feature.INDECLINABLE in entry.features:
            return gender_article
        
        # Add genitive ending for 3rd declension nouns or irregular 1st/2nd declension
        gen_ending = ""
        
        # Special case handling for specific words
        if entry.lemma == "ἀνήρ":
            return "ἀνδρός, ὁ"
        
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
            if entry.lemma.endswith("ις") and MorphClass.IS_EWS in entry.morph_classes:
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
    
    def _is_final_syllable_accented(self, word: str) -> bool:
        """Check if the final syllable of a Greek word is accented.
        
        Args:
            word: Greek word (in Unicode)
            
        Returns:
            True if the final syllable has an accent, False otherwise
        """
        if not word:
            return False
            
        # Greek accent marks: acute (΄), grave (`), circumflex (῀)
        # Also check for combined characters with accents
        accent_chars = set(['ά', 'έ', 'ή', 'ί', 'ό', 'ύ', 'ώ', 'ὰ', 'ὲ', 'ὴ', 'ὶ', 'ὸ', 'ὺ', 'ὼ', 
                           'ᾶ', 'ῆ', 'ῖ', 'ῦ', 'ῶ', 'ᾷ', 'ῇ', 'ῷ'])
        
        # Find vowels in the word (including diphthongs)
        vowels = []
        i = 0
        while i < len(word):
            char = word[i]
            # Check for diphthongs first
            if i < len(word) - 1:
                diphthong = word[i:i+2]
                if diphthong in ['αι', 'ει', 'οι', 'υι', 'αυ', 'ευ', 'ου', 'ηυ']:
                    # Check if either part of diphthong is accented
                    has_accent = any(c in accent_chars for c in diphthong)
                    vowels.append((diphthong, has_accent))
                    i += 2
                    continue
            
            # Single vowel
            if char in 'αεηιουωάέήίόύώὰὲὴὶὸὺὼᾶῆῖῦῶᾷῇῷ':
                has_accent = char in accent_chars
                vowels.append((char, has_accent))
            i += 1
        
        if not vowels:
            return False
            
        # Check if the final vowel/syllable is accented
        return vowels[-1][1]

    def _format_adjective_morphology(self, entry: MorphEntry) -> str:
        """Format adjective morphology information."""
        lemma = entry.lemma
        
        # Check for irregular adjectives
        if lemma in self.IRREGULAR_ADJECTIVES:
            return self.IRREGULAR_ADJECTIVES[lemma]
            
        # Check if final syllable is accented to determine fem/neut accent pattern
        final_accented = self._is_final_syllable_accented(lemma)
        
        # Handle adjective patterns based on morphological classes
        if MorphClass.ADJ_2_1_2 in entry.morph_classes:
            # Check if the letter before -ος is ε, ι, or ρ (alpha feminine rule)
            if len(lemma) >= 2 and lemma[-2] in "ειρ":
                return "ά, όν" if final_accented else "α, ον"  # Always alpha after ε, ι, ρ
            else:
                return "ή, όν" if final_accented else "α, ον"  # Apply accentuation rule
        elif MorphClass.ADJ_2_2 in entry.morph_classes:
            return "όν" if final_accented else "ον"  # Two-ending adjective: apply accentuation rule
        elif MorphClass.ADJ_3_3 in entry.morph_classes:
            return "ές"  # Third declension adjectives typically keep their pattern
        elif MorphClass.US_EIA_U in entry.morph_classes:
            return "εῖα, ύ"  # These patterns typically maintain their accents
        elif MorphClass.AS_ASA_AN in entry.morph_classes:
            return "ασα, αν"  # These are typically unaccented
        elif MorphClass.WN_ON in entry.morph_classes or MorphClass.WN_ON_COMP in entry.morph_classes:
            return "όν" if final_accented else "ον"  # Apply accentuation rule
        
        # Fallback to endings if morphological class doesn't provide format
        elif lemma.endswith("ος"):
            # Adjectives with three endings (masc, fem, neut)
            if Feature.FEMININE in entry.features:
                # Check if the letter before -ος is ε, ι, or ρ (alpha feminine rule)
                if len(lemma) >= 2 and lemma[-2] in "ειρ":
                    return "ά, όν" if final_accented else "α, ον"  # Always alpha after ε, ι, ρ
                else:
                    return "ή, όν" if final_accented else "α, ον"  # Apply accentuation rule
            # Adjectives with two endings (masc/fem, neut) - just show neuter
            else:
                return "όν" if final_accented else "ον"  # Apply accentuation rule
        elif lemma.endswith("ης"):
            return "ές"  # Third declension pattern
        elif lemma.endswith("υς"):
            return "εῖα, ύ"  # This pattern typically maintains accents
        elif lemma.endswith("ων"):
            return "όν" if final_accented else "ον"  # Apply accentuation rule
        
        # Default format for other adjectives
        return None 