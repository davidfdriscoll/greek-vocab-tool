import unittest
from unittest.mock import Mock, patch
from vocab.text_processor import TextProcessor
from morph.morph_entry import MorphEntry
from morph.part_of_speech import PartOfSpeech
from morph.features import Feature
from morph.morph_class import MorphClass


class TestTextProcessorDisambiguation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_parser = Mock()
        self.text_processor = TextProcessor(self.mock_parser)
    
    def create_morph_entry(self, lemma, definition, pos=PartOfSpeech.VERB, 
                          features=None, morph_classes=None):
        """Helper to create MorphEntry objects for testing."""
        if features is None:
            features = {Feature.PRESENT, Feature.INDICATIVE, Feature.ACTIVE, Feature.SECOND, Feature.SINGULAR}
        if morph_classes is None:
            morph_classes = {MorphClass.THEMATIC, MorphClass.REGULAR}
            
        return MorphEntry(
            original="test_word",
            part_of_speech=pos,
            lemma=lemma,
            features=features,
            morph_classes=morph_classes,
            short_definition=definition
        )
    
    def test_collapse_redundant_entries_identical_numbered_lemmas(self):
        """Test that identical numbered lemmas are collapsed into one."""
        # Create three identical entries with numbered lemmas (like λέγω1, λέγω2, λέγω3)
        entries = [
            self.create_morph_entry("λέγω1", "to say, tell, speak; epic and arch.: pick, gather"),
            self.create_morph_entry("λέγω2", "to say, tell, speak; epic and arch.: pick, gather"),
            self.create_morph_entry("λέγω3", "to say, tell, speak; epic and arch.: pick, gather"),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should collapse to just one entry
        self.assertEqual(len(result), 1)
        # Should strip the number from the lemma
        self.assertEqual(result[0].lemma, "λέγω")
        self.assertEqual(result[0].short_definition, "to say, tell, speak; epic and arch.: pick, gather")
    
    def test_collapse_redundant_entries_different_definitions(self):
        """Test that entries with different definitions are NOT collapsed."""
        # Create entries like δέω vs δέω2 with different meanings
        entries = [
            self.create_morph_entry("δέω1", "to bind, tie, fetter"),
            self.create_morph_entry("δέω2", "to lack, miss, stand in need of"),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should keep both entries since they have different definitions
        self.assertEqual(len(result), 2)
        # Should strip numbers from lemmas
        lemmas = [entry.lemma for entry in result]
        self.assertIn("δέω", lemmas)
        # Both should have base lemma "δέω" but different definitions
        definitions = [entry.short_definition for entry in result]
        self.assertIn("to bind, tie, fetter", definitions)
        self.assertIn("to lack, miss, stand in need of", definitions)
    
    def test_collapse_redundant_entries_different_features(self):
        """Test that entries with different morphological features ARE collapsed if they have same lemma and definition."""
        entries = [
            self.create_morph_entry("λέγω1", "to say", features={Feature.PRESENT, Feature.INDICATIVE}),
            self.create_morph_entry("λέγω1", "to say", features={Feature.AORIST, Feature.INDICATIVE}),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should collapse both entries since they have same base lemma and definition
        # (different features represent different inflected forms of the same word)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].lemma, "λέγω")
    
    def test_collapse_redundant_entries_different_part_of_speech(self):
        """Test that entries with different parts of speech are NOT collapsed."""
        entries = [
            self.create_morph_entry("καλός1", "beautiful", pos=PartOfSpeech.NOUN),  # Adjectives use NOUN pos
            self.create_morph_entry("καλός1", "beauty", pos=PartOfSpeech.VERB),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should keep both entries since they have different parts of speech
        self.assertEqual(len(result), 2)
    
    def test_collapse_redundant_entries_prefers_unnumbered_lemma(self):
        """Test that when collapsing, unnumbered lemmas are preferred."""
        entries = [
            self.create_morph_entry("λέγω3", "to say"),
            self.create_morph_entry("λέγω", "to say"),  # This one has no number
            self.create_morph_entry("λέγω1", "to say"),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should collapse to just one entry
        self.assertEqual(len(result), 1)
        # Should use the unnumbered form
        self.assertEqual(result[0].lemma, "λέγω")
    
    @patch('builtins.input', return_value='')  # Simulate user pressing Enter (select all)
    def test_disambiguate_entries_redundant_automatically_collapsed(self, mock_input):
        """Test that redundant entries are automatically collapsed without user prompt."""
        # Create redundant entries that should be auto-collapsed
        entries = [
            self.create_morph_entry("λέγω1", "to say, tell, speak; epic and arch.: pick, gather"),
            self.create_morph_entry("λέγω2", "to say, tell, speak; epic and arch.: pick, gather"),
            self.create_morph_entry("λέγω3", "to say, tell, speak; epic and arch.: pick, gather"),
        ]
        
        result = self.text_processor._disambiguate_entries("λέγεις", entries)
        
        # Should automatically collapse without user input since they're truly redundant
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].lemma, "λέγω")
    
    @patch('builtins.print')  # Mock print to avoid output during tests
    @patch('builtins.input', side_effect=['1'])  # User selects first option
    def test_disambiguate_entries_different_definitions_prompt_user(self, mock_input, mock_print):
        """Test that entries with different definitions prompt user for disambiguation."""
        # Create entries with different definitions
        entries = [
            self.create_morph_entry("δέω1", "to bind, tie, fetter"),
            self.create_morph_entry("δέω2", "to lack, miss, stand in need of"),
        ]
        
        result = self.text_processor._disambiguate_entries("δέῃ", entries)
        
        # Should prompt user and return selected entry
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].short_definition, "to bind, tie, fetter")
        
        # Verify that disambiguation prompt was shown
        mock_print.assert_called()
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        self.assertTrue(any("Multiple possibilities" in call for call in print_calls))
    
    @patch('builtins.print')
    @patch('builtins.input', side_effect=['1,2'])  # User selects both options
    def test_disambiguate_entries_select_multiple(self, mock_input, mock_print):
        """Test that user can select multiple entries when disambiguating."""
        entries = [
            self.create_morph_entry("δέω1", "to bind, tie, fetter"),
            self.create_morph_entry("δέω2", "to lack, miss, stand in need of"),
        ]
        
        result = self.text_processor._disambiguate_entries("δέῃ", entries)
        
        # Should return both selected entries
        self.assertEqual(len(result), 2)
        definitions = [entry.short_definition for entry in result]
        self.assertIn("to bind, tie, fetter", definitions)
        self.assertIn("to lack, miss, stand in need of", definitions)
    
    @patch('builtins.print')
    @patch('builtins.input', side_effect=[''])  # User presses Enter (select all)
    def test_disambiguate_entries_select_all(self, mock_input, mock_print):
        """Test that user can select all entries by pressing Enter."""
        entries = [
            self.create_morph_entry("δέω1", "to bind, tie, fetter"),
            self.create_morph_entry("δέω2", "to lack, miss, stand in need of"),
        ]
        
        result = self.text_processor._disambiguate_entries("δέῃ", entries)
        
        # Should return all collapsed entries
        self.assertEqual(len(result), 2)
    
    def test_disambiguate_entries_mixed_redundant_and_different(self):
        """Test disambiguation with a mix of redundant and genuinely different entries."""
        entries = [
            # Three redundant λέγω entries
            self.create_morph_entry("λέγω1", "to say"),
            self.create_morph_entry("λέγω2", "to say"),
            self.create_morph_entry("λέγω3", "to say"),
            # One different word
            self.create_morph_entry("λήγω1", "to cease, stop"),
        ]
        
        # First test the collapse step
        collapsed = self.text_processor._collapse_redundant_entries(entries)
        
        # Should collapse the three λέγω entries into one, keep the λήγω separate
        self.assertEqual(len(collapsed), 2)
        lemmas = [entry.lemma for entry in collapsed]
        self.assertIn("λέγω", lemmas)
        self.assertIn("λήγω", lemmas)

    def test_collapse_redundant_entries_different_morph_classes(self):
        """Test that entries with different morphological classes ARE collapsed if they have same lemma and definition."""
        entries = [
            self.create_morph_entry("λέγω1", "to say", morph_classes={MorphClass.THEMATIC}),
            self.create_morph_entry("λέγω1", "to say", morph_classes={MorphClass.REGULAR}),
        ]
        
        result = self.text_processor._collapse_redundant_entries(entries)
        
        # Should collapse both entries since they have same base lemma and definition
        # (different morph classes can represent the same lexical entry)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].lemma, "λέγω")


if __name__ == '__main__':
    unittest.main() 