import os
import pytest
from morph import MorphParser
from vocab.vocab_generator import VocabGenerator

@pytest.fixture
def morph_parser():
    """Create a MorphParser instance for testing."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    morpheus_root = os.path.join(current_dir, "morpheus")
    cruncher = os.path.join(morpheus_root, "bin", "cruncher")
    stemlib = os.path.join(morpheus_root, "stemlib")
    return MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)

@pytest.fixture
def vocab_generator(morph_parser):
    """Create a VocabGenerator instance for testing."""
    return VocabGenerator(morph_parser)

def test_basic_vocab_generation(vocab_generator):
    """Test basic vocabulary list generation with a simple text."""
    text = "ὁ ἄνθρωπος τὸν λόγον λέγει"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Convert to formatted string for easier comparison
    result = vocab_generator.format_vocab_list(entries)
    
    # Check that key words are present
    assert "ἄνθρωπος" in result
    assert "λόγος" in result
    assert "λέγω" in result  # Should get dictionary form
    
def test_duplicate_word_handling(vocab_generator):
    """Test that duplicate words are handled correctly."""
    text = "λέγει λέγει λέγει"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Should only have one entry for λέγω
    assert len(entries) == 1
    assert "λέγω" in vocab_generator.format_vocab_list(entries)
    
def test_word_extraction(vocab_generator):
    """Test that words are correctly extracted from text with punctuation."""
    text = "ὁ ἄνθρωπος, καὶ ὁ λόγος."
    words = vocab_generator.text_processor.extract_words(text)
    
    expected = {"ὁ", "ἄνθρωπος", "καὶ", "λόγος"}
    assert set(words) == expected 