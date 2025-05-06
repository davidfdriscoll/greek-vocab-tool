import os
import subprocess
import re
import beta_code
from typing import List, Set
from .morph_entry import MorphEntry
from .part_of_speech import PartOfSpeech, UnknownPartOfSpeechError
from .features import Feature, UnknownFeatureError
from .morph_class import MorphClass, UnknownMorphClassError

class MorphParser:
    def __init__(self, cruncher_path: str, stemlib_path: str):
        self.cruncher_path = cruncher_path
        self.env = os.environ.copy()
        self.env["MORPHLIB"] = stemlib_path

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
                elif MorphClass.ADJ_2_1_2 in morph_classes:
                    return PartOfSpeech.ADJECTIVE
                else:
                    return PartOfSpeech.NOUN
                    
            return pos
            
        except UnknownPartOfSpeechError as e:
            print(f"Warning: {e} in word with features {features} and morph_classes {morph_classes}")
            raise

    def parse_word(self, word: str) -> List[MorphEntry]:
        try:
            # Ensure word is in Beta Code format for Morpheus
            if not any(c in word for c in "/*\\()=|"):  # Simple check for Beta Code markers
                word = beta_code.greek_to_beta_code(word)
                
            result = subprocess.run(
                [self.cruncher_path],
                input=word,
                text=True,
                capture_output=True,
                env=self.env,
                check=True
            )
            return self._parse_output(word, result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error processing word '{word}': {e}")
            return []

    def _parse_output(self, original: str, raw_output: str) -> List[MorphEntry]:
        entries = []
        matches = re.findall(r"<NL>(.*?)</NL>", raw_output, re.DOTALL)
        for line in matches:
            parts = line.strip().split()
            if not parts or len(parts) < 3:
                continue

            raw_pos_code = parts[0]
            raw_lemma = parts[1].rstrip(",")
            lemma = self._get_attic_lemma(raw_lemma)

            split_index = next((i for i, part in enumerate(parts[2:], 2) if "_" in part or "," in part), len(parts))
            raw_features = parts[2:split_index]
            raw_morph_class = " ".join(parts[split_index:])

            try:
                # Convert raw strings to enum values
                features = Feature.from_list(raw_features)
                morph_classes = MorphClass.from_str(raw_morph_class)
                part_of_speech = self._determine_part_of_speech(raw_pos_code, features, morph_classes)
                
                # Convert original word from Beta Code to Unicode if it's in Beta Code
                if any(c in original for c in "/*\\()=|"):
                    original = beta_code.beta_code_to_greek(original)
                
                entries.append(MorphEntry(
                    original=original,
                    part_of_speech=part_of_speech,
                    lemma=lemma,
                    features=features,
                    morph_classes=morph_classes
                ))
            except (UnknownPartOfSpeechError, UnknownFeatureError, UnknownMorphClassError) as e:
                # Log the error but continue processing other entries
                print(f"Warning while processing '{original}': {e}")
                continue

        return entries
