import os
import subprocess
import re
import beta_code
from typing import List, Set
from .morph_entry import MorphEntry
from .part_of_speech import PartOfSpeech, UnknownPartOfSpeechError
from .features import Feature, UnknownFeatureError
from .morph_class import MorphClass, UnknownMorphClassError
from .definition_loader import DefinitionLoader

class MorphParser:
    def __init__(self, cruncher_path: str, stemlib_path: str, debug=False):
        self.cruncher_path = cruncher_path
        self.env = os.environ.copy()
        self.env["MORPHLIB"] = stemlib_path
        self.definition_loader = DefinitionLoader()
        self.debug = debug

    def _get_attic_lemma(self, lemma: str) -> str:
        """Extract the Attic form from a lemma string.
        When multiple forms are present (separated by comma), 
        the Attic form is typically the second one."""
        if ',' in lemma:
            forms = lemma.split(',')
            # Convert Beta Code lemma to Unicode
            return beta_code.beta_code_to_greek(forms[1].strip())
        return beta_code.beta_code_to_greek(lemma)

    def _determine_part_of_speech(self, code: str, features: Set[Feature], morph_classes: Set[MorphClass]) -> PartOfSpeech:
        """Determine the part of speech, handling special cases where the code alone is insufficient.
        
        Args:
            code: The raw part of speech code from morpheus
            features: Set of morphological features
            morph_classes: Set of morphological classes
            
        Returns:
            The determined PartOfSpeech enum value
            
        Raises:
            UnknownPartOfSpeechError: If the code is not recognized
        """
        try:
            pos = PartOfSpeech.from_str(code)
            
            # Handle special cases where multiple parts of speech share the same code
            if pos == PartOfSpeech.NOUN:
                if Feature.ARTICLE in features:
                    return PartOfSpeech.ARTICLE
                else:
                    return PartOfSpeech.NOUN
                    
            return pos
            
        except UnknownPartOfSpeechError as e:
            print(f"Warning: {e} in word with features {features} and morph_classes {morph_classes}")
            raise

    def _handle_special_words(self, original_word: str) -> List[MorphEntry]:
        """Handle special words that Morpheus doesn't parse correctly.
        
        Args:
            original_word: The original word (in Unicode or Beta Code)
            
        Returns:
            List of MorphEntry objects for special words, empty list if not a special word
        """
        # Normalize the word to check against our special cases
        word_normalized = original_word.strip()
        
        # Handle 'ἢ' (or/than) - check both Unicode and Beta Code forms
        if word_normalized in ['ἢ', 'h)\\']:
            # Use hardcoded definition since morpheus/definition_loader returns wrong info
            lemma = 'ἤ'  # Standard lemma form
            short_definition = "or, than"
            
            return [MorphEntry(
                original=original_word,
                part_of_speech=PartOfSpeech.CONJUNCTION,
                lemma=lemma,
                features=set(),  # Conjunctions typically have no morphological features
                morph_classes=set(),  # Conjunctions typically have no morphological classes
                short_definition=short_definition
            )]
        
        return []

    def parse_word(self, word: str, verbose=False, ignore_case=False, ignore_accent=False) -> List[MorphEntry]:
        # Start with normal Morpheus parsing
        morpheus_results = self._parse_with_morpheus(word, verbose, ignore_case, ignore_accent)
        
        # Check for special words and add additional entries
        special_entries = self._handle_special_words(word)
        
        # Combine results - special entries are added to morpheus results
        all_results = morpheus_results + special_entries
        
        if verbose or self.debug:
            if special_entries:
                print(f"DEBUG: Added {len(special_entries)} special entries for '{word}'")
        
        return all_results

    def _parse_with_morpheus(self, word: str, verbose=False, ignore_case=False, ignore_accent=False) -> List[MorphEntry]:
        """Run the normal Morpheus parsing logic."""
        try:
            # Check for various apostrophe characters that might appear in Unicode text
            apostrophe_chars = ["'", "ʼ", "'", "᾽", "᾿", "ʻ", "`"]
            has_initial_apostrophe = any(word.startswith(a) for a in apostrophe_chars)
            
            # Store the original word for later reference
            original_word = word
            
            # Ensure word is in Beta Code format for Morpheus
            # More comprehensive check for Beta Code markers
            beta_code_markers = set("/*\\()=|<>_^")
            is_beta_code = any(c in word for c in beta_code_markers)
            
            if not is_beta_code:
                try:
                    # If word has an initial apostrophe in Unicode, we need to preserve it
                    if has_initial_apostrophe:
                        # Remove apostrophe temporarily, convert to Beta Code, then add it back
                        apostrophe = "'"  # Use standard apostrophe for beta code
                        word_without_apostrophe = word[1:]
                        word = apostrophe + beta_code.greek_to_beta_code(word_without_apostrophe)
                    else:
                        word = beta_code.greek_to_beta_code(word)
                except Exception as e:
                    print(f"Warning: Failed to convert '{word}' to Beta Code: {e}")
                    return []
            
            # Prepare cruncher command with flags
            cmd = [self.cruncher_path]
            if ignore_case:
                cmd.append("-S")
            if ignore_accent:
                cmd.append("-n")
                
            if verbose or self.debug:
                print(f"\nDEBUG: Sending to morpheus: '{word}'")
                
            result = subprocess.run(
                cmd,
                input=word,
                text=True,
                capture_output=True,
                env=self.env,
                check=True
            )
            
            if verbose or self.debug:
                print(f"\nDEBUG: Raw morpheus output for '{word}':")
                print(result.stdout)
                
            # For words with initial apostrophes, we need to preserve the original apostrophe
            # in the results, so we pass the original word to _parse_output
            return self._parse_output(original_word if has_initial_apostrophe else word, 
                                    result.stdout, verbose)
        except subprocess.CalledProcessError as e:
            print(f"Error processing word '{word}': {e}")
            print(f"stderr: {e.stderr}")
            return []

    def _parse_output(self, original: str, raw_output: str, verbose=False) -> List[MorphEntry]:
        entries = []
        matches = re.findall(r"<NL>(.*?)</NL>", raw_output, re.DOTALL)
        
        if verbose or self.debug:
            print(f"DEBUG: Found {len(matches)} matches in morpheus output for '{original}'")
        
        for line in matches:
            parts = line.strip().split()
            if not parts or len(parts) < 3:
                if verbose or self.debug:
                    print(f"DEBUG: Skipping match, insufficient parts: '{line}'")
                continue

            raw_pos_code = parts[0]
            raw_lemma = parts[1].rstrip(",")
            lemma = self._get_attic_lemma(raw_lemma)

            split_index = next((i for i, part in enumerate(parts[2:], 2) if "_" in part or "," in part), len(parts))
            raw_features = parts[2:split_index]
            raw_morph_class = " ".join(parts[split_index:])
            
            if verbose or self.debug:
                print(f"DEBUG: Processing match:")
                print(f"  - POS code: {raw_pos_code}")
                print(f"  - Lemma: {raw_lemma} -> {lemma}")
                print(f"  - Features: {raw_features}")
                print(f"  - Morph class: {raw_morph_class}")

            try:
                # Convert raw strings to enum values
                features = Feature.from_list(raw_features)
                morph_classes = MorphClass.from_str(raw_morph_class)
                part_of_speech = self._determine_part_of_speech(raw_pos_code, features, morph_classes)
                
                # For words that came in as Unicode (not Beta Code), ensure we return them in Unicode
                if not any(c in original for c in "/*\\()=|"):
                    # Handle apostrophe preservation for Unicode input
                    apostrophe_chars = ["'", "ʼ", "'", "᾽", "᾿", "ʻ", "`"]
                    if any(original.startswith(a) for a in apostrophe_chars):
                        # Keep the original apostrophe character
                        apostrophe = original[0]
                        # Use the original Unicode word that was passed in
                        processed_original = original
                    else:
                        processed_original = original
                else:
                    # For Beta Code input, convert to Unicode
                    # If the original has an initial apostrophe, preserve it
                    if original.startswith("'"):
                        original_without_apostrophe = original[1:]
                        processed_original = "'" + beta_code.beta_code_to_greek(original_without_apostrophe)
                    else:
                        processed_original = beta_code.beta_code_to_greek(original)
                
                # Get the short definition for the lemma
                short_definition = self.definition_loader.get_definition(lemma)
                
                entries.append(MorphEntry(
                    original=processed_original,
                    part_of_speech=part_of_speech,
                    lemma=lemma,
                    features=features,
                    morph_classes=morph_classes,
                    short_definition=short_definition
                ))
            except (UnknownPartOfSpeechError, UnknownFeatureError, UnknownMorphClassError) as e:
                # Log the error but continue processing other entries
                print(f"Warning while processing '{original}': {e}")
                if verbose or self.debug:
                    print(f"DEBUG: Exception details: {type(e).__name__}: {str(e)}")
                continue

        if len(entries) == 0 and (verbose or self.debug):
            print(f"DEBUG: No valid entries found for '{original}'")
            
        return entries
