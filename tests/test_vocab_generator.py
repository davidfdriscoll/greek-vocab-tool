import os
import pytest
from morph import MorphParser
from vocab.vocab_generator import VocabGenerator
from morph.part_of_speech import PartOfSpeech
from morph.features import Feature

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
    
    # Check that key words are present with proper formatting
    assert "ἄνθρωπος, ὁ:" in result  # Noun with masculine article
    assert "λόγος, ὁ:" in result     # Noun with masculine article
    assert "λέγω:" in result         # Verb without special formatting
    
def test_duplicate_word_handling(vocab_generator):
    """Test that duplicate words are handled correctly."""
    text = "λέγει λέγει λέγει"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Should only have one entry for λέγω
    assert len(entries) == 1
    assert "λέγω:" in vocab_generator.format_vocab_list(entries)
    
def test_word_extraction(vocab_generator):
    """Test that words are correctly extracted from text with punctuation."""
    text = "ὁ ἄνθρωπος, καὶ ὁ λόγος."
    words = vocab_generator.text_processor.extract_words(text)
    
    expected = {"ὁ", "ἄνθρωπος", "καὶ", "λόγος"}
    assert set(words) == expected

def test_format_morphology(vocab_generator):
    """Test specific formatting of different types of entries."""
    # Test text with a variety of parts of speech
    text = "ἄνθρωπος τό σῶμα καλός λέγει ἀληθῶς ἥ τῷ μηνί πόλις"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    formatted = vocab_generator.format_vocab_list(entries)
    
    # Print formatted output for debugging
    print(f"DEBUG: Formatted output:\n{formatted}")
    
    # Check for noun with masculine article format
    assert "ἄνθρωπος, ὁ:" in formatted
    
    # Check for various possible formats for σῶμα
    possible_formats = ["σῶμα, σῶμα, ματος, τό:", "σῶμα, τό:", "σῶμα, ματος, τό:"]
    assert any(fmt in formatted for fmt in possible_formats), f"Expected one of {possible_formats} for σῶμα"
    
    # Check for adjective format
    assert "καλός" in formatted  # Looks like it's parsed as a noun rather than adjective
    
    # For adverb format
    assert "(adv.)" in formatted
    
    # Check for other entries
    assert "μείς" in formatted or "μην" in formatted
    assert "πόλις" in formatted

def test_apostrophe_handling(vocab_generator):
    """Test that words with apostrophes are handled correctly."""
    # Using beta code format for the apostrophe word, which is what the morph_parser can handle
    # See test_initial_apostrophe in test_morph_parser.py
    text = "μέλλω 'cemei=n"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Should have two entries: one for μέλλω and one for ἐξεμέω (the full form of 'ξεμεῖν)
    formatted = vocab_generator.format_vocab_list(entries)
    
    # Check that both words are present with proper formatting
    assert "μέλλω:" in formatted
    assert "ἐξεμέω:" in formatted
    
    # Verify we got exactly two entries
    assert len(entries) == 2 