import unittest
import os
import sys
from unittest.mock import Mock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from morph import MorphParser, MorphEntry
from morph.features import Feature
from morph.morph_class import MorphClass
from morph.part_of_speech import PartOfSpeech
from vocab.text_processor import TextProcessor
from vocab.vocab_entry import VocabEntry


class TestTextProcessorMorphology(unittest.TestCase):
    """Test morphological formatting in TextProcessor to ensure adjective patterns don't duplicate masculine forms."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the MorphParser since we're testing formatting logic, not parsing
        self.mock_parser = Mock(spec=MorphParser)
        self.processor = TextProcessor(self.mock_parser)
    
    def create_mock_entry(self, lemma, part_of_speech, features, morph_classes, definition="test definition"):
        """Helper method to create a mock MorphEntry for testing."""
        entry = Mock(spec=MorphEntry)
        entry.lemma = lemma
        entry.part_of_speech = part_of_speech
        entry.features = features
        entry.morph_classes = morph_classes
        entry.short_definition = definition
        return entry
    
    def test_as_asa_an_pattern(self):
        """Test AS_ASA_AN morphological pattern (ἁπαξάπας type)."""
        entry = self.create_mock_entry(
            lemma="ἁπαξάπας",
            part_of_speech=PartOfSpeech.NOUN,
            features={Feature.MASCULINE, Feature.SINGULAR},
            morph_classes={MorphClass.AS_ASA_AN},
            definition="all at once"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ἁπαξάπας")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")  # Should be reclassified as adjective
        self.assertEqual(vocab_entry.morphology, "ασα, αν")  # Should not duplicate masculine
        self.assertEqual(vocab_entry.definition, "all at once")
    
    def test_adj_2_1_2_pattern_alpha_feminine(self):
        """Test ADJ_2_1_2 morphological pattern with alpha feminine (ἀγαθός type)."""
        entry = self.create_mock_entry(
            lemma="ἀγαθός",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE, Feature.FEMININE},
            morph_classes={MorphClass.ADJ_2_1_2},
            definition="good"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ἀγαθός")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ή, όν")  # Should not duplicate masculine (final syllable accented)
        self.assertEqual(vocab_entry.definition, "good")
    
    def test_adj_2_1_2_pattern_default_case(self):
        """Test ADJ_2_1_2 morphological pattern with default alpha feminine case."""
        entry = self.create_mock_entry(
            lemma="μικρός",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE, Feature.FEMININE},
            morph_classes={MorphClass.ADJ_2_1_2},
            definition="small"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "μικρός")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ή, όν")  # Should use eta feminine and not duplicate masculine (final syllable accented)
        self.assertEqual(vocab_entry.definition, "small")
    
    def test_adj_3_3_pattern(self):
        """Test ADJ_3_3 morphological pattern (ἀληθής type)."""
        entry = self.create_mock_entry(
            lemma="ἀληθής",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE},
            morph_classes={MorphClass.ADJ_3_3},
            definition="true"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ἀληθής")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ές")  # Should not duplicate masculine
        self.assertEqual(vocab_entry.definition, "true")
    
    def test_us_eia_u_pattern(self):
        """Test US_EIA_U morphological pattern (γλυκύς type)."""
        entry = self.create_mock_entry(
            lemma="γλυκύς",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE, Feature.FEMININE},
            morph_classes={MorphClass.US_EIA_U},
            definition="sweet"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "γλυκύς")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "εῖα, ύ")  # Should not duplicate masculine
        self.assertEqual(vocab_entry.definition, "sweet")
    
    def test_wn_on_pattern(self):
        """Test WN_ON morphological pattern (σώφρων type) - two-ending adjective."""
        entry = self.create_mock_entry(
            lemma="σώφρων",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE},
            morph_classes={MorphClass.WN_ON},
            definition="of sound mind"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "σώφρων")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ον")  # Two-ending: just neuter
        self.assertEqual(vocab_entry.definition, "of sound mind")
    
    def test_adj_2_2_pattern(self):
        """Test ADJ_2_2 morphological pattern - two-ending adjective."""
        entry = self.create_mock_entry(
            lemma="βάρβαρος",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE},
            morph_classes={MorphClass.ADJ_2_2},
            definition="foreign"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "βάρβαρος")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ον")  # Two-ending: just neuter
        self.assertEqual(vocab_entry.definition, "foreign")
    
    def test_hubris_third_declension_noun(self):
        """Test ὕβρις (hubris) as a third declension noun."""
        entry = self.create_mock_entry(
            lemma="ὕβρις",
            part_of_speech=PartOfSpeech.NOUN,
            features={Feature.FEMININE, Feature.SINGULAR, Feature.NOMINATIVE},
            morph_classes={MorphClass.THIRD_DECLENSION, MorphClass.IS_EWS},  # Third declension with -ις, -εως pattern
            definition="hubris, wanton violence"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ὕβρις")
        self.assertEqual(vocab_entry.part_of_speech, "noun")
        self.assertEqual(vocab_entry.morphology, "εως, ἡ")  # Third declension genitive pattern
        self.assertEqual(vocab_entry.definition, "hubris, wanton violence")
    
    def test_real_word_kalos(self):
        """Test real word καλός with actual morphological data from morpheus."""
        entry = self.create_mock_entry(
            lemma="καλός",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.NOMINATIVE, Feature.SINGULAR, Feature.MASCULINE},
            morph_classes={MorphClass.ADJ_2_1_2},  # Actual morphological class returned by morpheus
            definition="beautiful"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "καλός")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")  # Should be reclassified due to adjective morph class
        self.assertEqual(vocab_entry.morphology, "ή, όν")  # Should not duplicate masculine from lemma (eta feminine because λ ≠ ε,ι,ρ)
        self.assertEqual(vocab_entry.definition, "beautiful")
    
    def test_real_word_eugenes(self):
        """Test real word εὐγενής with actual morphological data from morpheus."""
        entry = self.create_mock_entry(
            lemma="εὐγενής",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASC_FEM, Feature.SINGULAR, Feature.NOMINATIVE},
            morph_classes={MorphClass.ADJ_3_3},  # Actual morphological class returned by morpheus
            definition="well-born, of noble race, of high descent"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "εὐγενής")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")  # Should be reclassified due to adjective morph class
        self.assertEqual(vocab_entry.morphology, "ές")  # Should not duplicate masculine from lemma
        self.assertEqual(vocab_entry.definition, "well-born, of noble race, of high descent")
    
    def test_real_word_tachus(self):
        """Test real word ταχύς with actual morphological data from morpheus."""
        entry = self.create_mock_entry(
            lemma="ταχύς",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.SINGULAR, Feature.MASCULINE, Feature.NOMINATIVE},
            morph_classes={MorphClass.US_EIA_U},  # Actual morphological class returned by morpheus
            definition="quick, swift, fleet"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ταχύς")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")  # Should be reclassified due to adjective morph class
        self.assertEqual(vocab_entry.morphology, "εῖα, ύ")  # Should not duplicate masculine from lemma
        self.assertEqual(vocab_entry.definition, "quick, swift, fleet")
    
    def test_fallback_pattern_wn_ending(self):
        """Test fallback patterns for -ων endings."""
        entry = self.create_mock_entry(
            lemma="χαρίεις",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE},
            morph_classes={MorphClass.AS_ASA_AN},  # Should use fallback patterns
            definition="graceful"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "χαρίεις")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "ασα, αν")  # Should use fallback
        self.assertEqual(vocab_entry.definition, "graceful")
    
    def test_irregular_adjectives_preserved(self):
        """Test that irregular adjectives preserve their special patterns."""
        entry = self.create_mock_entry(
            lemma="πολύς",
            part_of_speech=PartOfSpeech.NOUN,  # Adjectives are classified as NOUN in morpheus
            features={Feature.MASCULINE},
            morph_classes={MorphClass.US_EIA_U},  # Would normally use regular pattern
            definition="much, many"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "πολύς")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")
        self.assertEqual(vocab_entry.morphology, "πολύς, πολλή, πολύ")  # Should use irregular pattern
        self.assertEqual(vocab_entry.definition, "much, many")
    
    def test_non_adjective_unaffected(self):
        """Test that non-adjectives are not affected by the formatting changes."""
        entry = self.create_mock_entry(
            lemma="ἀνήρ",
            part_of_speech=PartOfSpeech.NOUN,
            features={Feature.MASCULINE, Feature.SINGULAR, Feature.NOMINATIVE},
            morph_classes={MorphClass.THIRD_DECLENSION},  # Not an adjective class
            definition="man"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "ἀνήρ")
        self.assertEqual(vocab_entry.part_of_speech, "noun")
        self.assertEqual(vocab_entry.morphology, "ἀνδρός, ὁ")  # Should use noun pattern
        self.assertEqual(vocab_entry.definition, "man")
    
    def test_adverb_formatting(self):
        """Test that adverbs get the correct (adv.) marker."""
        entry = self.create_mock_entry(
            lemma="καλῶς",
            part_of_speech=PartOfSpeech.ADVERB,
            features={Feature.ADVERB},
            morph_classes=set(),
            definition="well"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "καλῶς")
        self.assertEqual(vocab_entry.part_of_speech, "adverb")
        self.assertEqual(vocab_entry.morphology, "(adv.)")
        self.assertEqual(vocab_entry.definition, "well")
    
    def test_adjective_reclassification(self):
        """Test that morphological adjective classes override the part_of_speech classification."""
        entry = self.create_mock_entry(
            lemma="κακός",
            part_of_speech=PartOfSpeech.NOUN,  # Morpheus often classifies adjectives as NOUN
            features={Feature.MASCULINE},
            morph_classes={MorphClass.ADJ_2_1_2},  # But morph class indicates it's an adjective
            definition="bad"
        )
        
        vocab_entry = self.processor.vocab_entry_service.create_vocab_entry(entry)
        
        self.assertEqual(vocab_entry.lemma, "κακός")
        self.assertEqual(vocab_entry.part_of_speech, "adjective")  # Should be reclassified
        self.assertEqual(vocab_entry.morphology, "ή, όν")  # Should use adjective pattern (eta feminine because κ ≠ ε,ι,ρ)
        self.assertEqual(vocab_entry.definition, "bad")


if __name__ == '__main__':
    unittest.main() 