import os
import pytest
from morph import MorphParser
from vocab.vocab_generator import VocabGenerator
from vocab.text_processor import TextProcessor
from morph.part_of_speech import PartOfSpeech
from morph.features import Feature
from morph.morph_class import MorphClass

@pytest.fixture
def morph_parser():
    """Create a MorphParser instance for testing."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    morpheus_root = os.path.join(current_dir, "morpheus")
    cruncher = os.path.join(morpheus_root, "bin", "cruncher")
    stemlib = os.path.join(morpheus_root, "stemlib")
    return MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)

@pytest.fixture
def text_processor(morph_parser):
    """Create a TextProcessor instance for testing."""
    return TextProcessor(morph_parser)

@pytest.fixture
def vocab_generator(morph_parser):
    """Create a VocabGenerator instance for testing."""
    return VocabGenerator(morph_parser, latex_output=True)

class TestAdjectiveFormatting:
    """Test cases for adjective morphological formatting."""
    
    def test_two_ending_adjective_os_on_pattern(self, vocab_generator):
        """Test that two-ending adjectives with -ος/-ον pattern show only neuter ending."""
        # Test ἐπίορκος (perjured) - should be "ἐπίορκος, ον" not "ἐπίορκος, ος, ον"
        entries = vocab_generator.generate_vocab_list('ἐπίορκος', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology == "ον"
        assert entry.format_latex_entry() == "\\vocabentry{ἐπίορκος, ον}{sworn falsely, perjured}"

    def test_two_ending_adjective_wn_on_pattern(self, vocab_generator):
        """Test that two-ending adjectives with -ων/-ον pattern show only neuter ending."""
        # Test εὐδαίμων (fortunate) - should be "εὐδαίμων, ον" not "εὐδαίμων, ων, ον"
        entries = vocab_generator.generate_vocab_list('εὐδαίμων', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology == "ον"
        assert entry.format_latex_entry() == "\\vocabentry{εὐδαίμων, ον}{fortunate, wealthy, happy}"

    def test_three_ending_adjective_os_h_on_pattern(self, vocab_generator):
        """Test that three-ending adjectives show all endings."""
        # Test ἀγαθός (good) - should show "ος, ή, όν" pattern
        entries = vocab_generator.generate_vocab_list('ἀγαθός', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology in ["ος, ή, όν", "ός, ά, όν"]  # Allow both variants
        assert "ἀγαθός," in entry.format_latex_entry()
        assert ("ος, ή, όν" in entry.format_latex_entry() or 
                "ός, ά, όν" in entry.format_latex_entry())

    def test_three_ending_adjective_hs_es_pattern(self, vocab_generator):
        """Test that three-ending adjectives with -ης/-ες pattern show both endings."""
        # Test ἀληθής (true) - should show "ής, ές" pattern
        entries = vocab_generator.generate_vocab_list('ἀληθής', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology == "ής, ές"
        assert entry.format_latex_entry() == "\\vocabentry{ἀληθής, ής, ές}{unconcealed, true}"

    def test_irregular_adjective_polys(self, vocab_generator):
        """Test that irregular adjectives use the predefined patterns."""
        # Test πολύς (much, many) - should use irregular pattern
        entries = vocab_generator.generate_vocab_list('πολύς', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology == "πολύς, πολλή, πολύ"
        assert entry.format_latex_entry() == "\\vocabentry{πολύς, πολλή, πολύ}{much, many}"

    def test_irregular_adjective_megas(self, vocab_generator):
        """Test that irregular adjectives use the predefined patterns."""
        # Test μέγας (great, large) - should use irregular pattern
        entries = vocab_generator.generate_vocab_list('μέγας', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "adjective"
        assert entry.morphology == "μέγας, μεγάλη, μέγα"
        assert entry.format_latex_entry() == "\\vocabentry{μέγας, μεγάλη, μέγα}{big, great}"

class TestMorphologicalClassDetection:
    """Test cases for proper detection of morphological classes."""
    
    def test_adj_2_2_class_detection(self, text_processor):
        """Test that ADJ_2_2 morphological class is properly detected and formatted."""
        # Parse ἐπίορκος directly to check morphological classes
        morph_entries = text_processor.morph_parser.parse_word('ἐπίορκος')
        assert len(morph_entries) > 0
        
        entry = morph_entries[0]
        assert MorphClass.ADJ_2_2 in entry.morph_classes
        assert MorphClass.is_adjective(entry.morph_classes)
        
        # Test the formatting logic
        morphology = text_processor._format_adjective_morphology(entry)
        assert morphology == "ον"

    def test_wn_on_class_detection(self, text_processor):
        """Test that WN_ON morphological class is properly detected and formatted."""
        # Parse εὐδαίμων directly to check morphological classes
        morph_entries = text_processor.morph_parser.parse_word('εὐδαίμων')
        assert len(morph_entries) > 0
        
        entry = morph_entries[0]
        assert MorphClass.WN_ON in entry.morph_classes
        assert MorphClass.is_adjective(entry.morph_classes)
        
        # Test the formatting logic
        morphology = text_processor._format_adjective_morphology(entry)
        assert morphology == "ον"

    def test_adj_2_1_2_class_detection(self, text_processor):
        """Test that ADJ_2_1_2 morphological class is properly detected and formatted."""
        # Parse ἀγαθός directly to check morphological classes
        morph_entries = text_processor.morph_parser.parse_word('ἀγαθός')
        assert len(morph_entries) > 0
        
        # Find the adjective entry
        adj_entry = next((entry for entry in morph_entries 
                         if MorphClass.is_adjective(entry.morph_classes)), None)
        assert adj_entry is not None
        assert MorphClass.ADJ_2_1_2 in adj_entry.morph_classes
        
        # Test the formatting logic
        morphology = text_processor._format_adjective_morphology(adj_entry)
        assert morphology in ["ος, ή, όν", "ός, ά, όν"]

class TestNounFormatting:
    """Test cases to ensure noun formatting wasn't broken by adjective fixes."""
    
    def test_basic_noun_formatting(self, vocab_generator):
        """Test that basic nouns still format correctly."""
        # Test ἄνθρωπος (human) - should show genitive and article
        entries = vocab_generator.generate_vocab_list('ἄνθρωπος', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "noun"
        assert "ὁ" in entry.morphology  # Should have masculine article
        assert "ἄνθρωπος," in entry.format_latex_entry()

    def test_feminine_noun_formatting(self, vocab_generator):
        """Test that feminine nouns format correctly."""
        # Test πόλις (city) - should show genitive and feminine article
        entries = vocab_generator.generate_vocab_list('πόλις', interactive=False)
        assert len(entries) == 1
        entry = entries[0]
        
        assert entry.part_of_speech == "noun"
        assert "ἡ" in entry.morphology  # Should have feminine article
        assert "πόλις," in entry.format_latex_entry()

class TestComparisonWithOldBehavior:
    """Test cases that verify the specific fixes for the reported issues."""
    
    def test_epiorkon_before_and_after_fix(self, vocab_generator):
        """Test that ἐπίορκος formatting matches expected output."""
        entries = vocab_generator.generate_vocab_list('ἐπίορκος', interactive=False)
        latex_output = entries[0].format_latex_entry()
        
        # Should NOT be the old incorrect format
        assert latex_output != "\\vocabentry{ἐπίορκος, ος, ον}{sworn falsely, perjured}"
        
        # Should be the new correct format
        assert latex_output == "\\vocabentry{ἐπίορκος, ον}{sworn falsely, perjured}"

    def test_eudaimon_before_and_after_fix(self, vocab_generator):
        """Test that εὐδαίμων formatting matches expected output."""
        entries = vocab_generator.generate_vocab_list('εὐδαίμων', interactive=False)
        latex_output = entries[0].format_latex_entry()
        
        # Should NOT be the old incorrect format
        assert latex_output != "\\vocabentry{εὐδαίμων, ων, ον}{fortunate, wealthy, happy}"
        
        # Should be the new correct format
        assert latex_output == "\\vocabentry{εὐδαίμων, ον}{fortunate, wealthy, happy}"

class TestEdgeCases:
    """Test edge cases and potential regressions."""
    
    def test_adjective_fallback_formatting(self, text_processor):
        """Test that adjectives without recognized morphological classes fall back correctly."""
        # Create a mock MorphEntry with unknown morphological class but adjective ending
        from morph.morph_entry import MorphEntry
        
        mock_entry = MorphEntry(
            original="τεστος",
            part_of_speech=PartOfSpeech.NOUN,  # Marked as noun but will be detected as adjective
            lemma="τεστος",
            features={Feature.MASCULINE, Feature.NOMINATIVE, Feature.SINGULAR},
            morph_classes={MorphClass.ADJ_2_2}  # This should trigger adjective detection
        )
        
        # Should be detected as adjective and formatted accordingly
        vocab_entry = text_processor.create_vocab_entry(mock_entry)
        assert vocab_entry.part_of_speech == "adjective"
        assert vocab_entry.morphology == "ον"

    def test_mixed_morphological_classes(self, text_processor):
        """Test behavior when an entry has multiple morphological classes."""
        # This tests the robustness of the is_adjective detection
        from morph.morph_entry import MorphEntry
        
        mock_entry = MorphEntry(
            original="τεστος",
            part_of_speech=PartOfSpeech.NOUN,
            lemma="τεστος",
            features={Feature.MASCULINE, Feature.NOMINATIVE, Feature.SINGULAR},
            morph_classes={MorphClass.ADJ_2_2, MorphClass.SECOND_DECLENSION}  # Mixed classes
        )
        
        # Should still be detected as adjective due to ADJ_2_2
        vocab_entry = text_processor.create_vocab_entry(mock_entry)
        assert vocab_entry.part_of_speech == "adjective"
        assert vocab_entry.morphology == "ον" 