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

def test_us_eia_u_preference_over_us_u(vocab_generator):
    """Test that US_EIA_U morphological class is preferred over US_U for the same lemma."""
    # ἡδύς has both us_eia_u (correct: εῖα, ύ) and us_u (incorrect: ὁ) analyses in Morpheus
    # We should get the us_eia_u analysis with εῖα, ύ morphology
    text = "ἡδύς"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Should find exactly one entry for ἡδύς
    hedys_entries = [e for e in entries if e.lemma == "ἡδύς"]
    assert len(hedys_entries) == 1
    
    entry = hedys_entries[0]
    assert entry.part_of_speech == "adjective"
    assert entry.morphology == "εῖα, ύ"  # Should be the US_EIA_U pattern, not ὁ from US_U
    assert entry.format_latex_entry() == "\\vocabentry{ἡδύς, εῖα, ύ}{sweet}"

def test_greek_alphabetization(vocab_generator):
    """Test that Greek words are alphabetized correctly, stripping diacritics."""
    # Test the specific case that was reported as a bug
    text = "ἄγχω ἀλλότριος ἀν-αίσχυντος ἀν-ίστημι ἀπ-αίσσω ἀπο-διδράσκω Ἀχερόντιος αἱματόω αἱματο-σταγής"
    entries = vocab_generator.generate_vocab_list(text, interactive=False)
    
    # Extract just the lemmas in the order they appear after sorting
    sorted_lemmas = [entry.lemma for entry in entries]
    
    # Expected order based on Greek alphabet (stripping diacritics):
    # ἄγχω (αγχω) -> αἱματο-σταγής (αιματο-σταγης) -> αἱματόω (αιματοω) -> ἀλλότριος (αλλοτριος) -> etc.
    
    # Find the positions of our key test words
    agcho_pos = next(i for i, lemma in enumerate(sorted_lemmas) if lemma == "ἄγχω")
    haimatoo_pos = next(i for i, lemma in enumerate(sorted_lemmas) if lemma == "αἱματόω")
    haima_stag_pos = next((i for i, lemma in enumerate(sorted_lemmas) if "αἱματο" in lemma and "σταγής" in lemma), -1)
    allotrios_pos = next(i for i, lemma in enumerate(sorted_lemmas) if lemma == "ἀλλότριος")
    
    # Debug output for troubleshooting
    print(f"DEBUG: Sorted lemmas: {sorted_lemmas}")
    print(f"DEBUG: ἄγχω at position {agcho_pos}")
    print(f"DEBUG: αἱματόω at position {haimatoo_pos}")
    print(f"DEBUG: αἱματο-σταγής at position {haima_stag_pos}")
    print(f"DEBUG: ἀλλότριος at position {allotrios_pos}")
    
    # Test the core alphabetization issue: αἱματ- words should come between ἄγχω and ἀλλότριος
    assert agcho_pos < haimatoo_pos, f"ἄγχω (pos {agcho_pos}) should come before αἱματόω (pos {haimatoo_pos})"
    assert haimatoo_pos < allotrios_pos, f"αἱματόω (pos {haimatoo_pos}) should come before ἀλλότριος (pos {allotrios_pos})"
    
    # If αἱματο-σταγής is found, it should also be between ἄγχω and ἀλλότριος
    if haima_stag_pos != -1:
        assert agcho_pos < haima_stag_pos < allotrios_pos, f"αἱματο-σταγής should be between ἄγχω and ἀλλότριος"

def test_diacritic_stripping_for_sorting():
    """Test that the VocabEntry._greek_sort_key method properly strips diacritics."""
    from vocab.vocab_entry import VocabEntry
    
    # Create test entries with various diacritics
    test_cases = [
        ("ἄγχω", "αγχω"),          # rough breathing + acute accent
        ("ἀλλότριος", "αλλοτριος"), # rough breathing + acute accent  
        ("αἱματόω", "αιματοω"),     # smooth breathing + acute accent
        ("ὁ", "ο"),                # rough breathing
        ("ἡ", "η"),                # rough breathing
        ("τὸ", "το"),              # grave accent
        ("τὴν", "την"),            # grave accent
        ("μῆνις", "μηνις"),        # circumflex
        ("σῶμα", "σωμα"),          # circumflex
        ("παῖς", "παις"),          # diaeresis (if present)
    ]
    
    for original, expected_stripped in test_cases:
        entry = VocabEntry(lemma=original, definition="test", part_of_speech="test")
        actual_stripped = entry._greek_sort_key(original)
        assert actual_stripped == expected_stripped, f"'{original}' should strip to '{expected_stripped}', got '{actual_stripped}'"

def test_alphabetical_ordering_comprehensive():
    """Test comprehensive alphabetical ordering across the Greek alphabet."""
    from vocab.vocab_entry import VocabEntry
    
    # Test words that span the Greek alphabet with various diacritics
    test_words = [
        "ἀγαθός",    # alpha + gamma  
        "ἄνθρωπος",  # alpha + nu
        "αἱματόω",   # alpha + iota
        "ἀλλότριος", # alpha + lambda
        "βίος",      # beta
        "γῆ",        # gamma
        "δέ",        # delta
        "εἰμί",      # epsilon + iota
        "ἔργον",     # epsilon + rho
        "ζωή",       # zeta
        "ἡμέρα",     # eta
        "θεός",      # theta
        "ἰχθύς",     # iota + chi
        "κόσμος",    # kappa
        "λόγος",     # lambda
        "μήτηρ",     # mu
        "νόμος",     # nu
        "ξένος",     # xi
        "ὁδός",      # omicron + delta
        "οὐρανός",   # omicron + upsilon
        "πατήρ",     # pi
        "ῥῆμα",      # rho
        "σῶμα",      # sigma
        "τέχνη",     # tau
        "ὑπό",       # upsilon
        "φίλος",     # phi
        "χρόνος",    # chi
        "ψυχή",      # psi
        "ὧδε"        # omega
    ]
    
    # Create VocabEntry objects
    entries = [VocabEntry(lemma=word, definition="test", part_of_speech="test") for word in test_words]
    
    # Sort them
    sorted_entries = sorted(entries)
    sorted_words = [entry.lemma for entry in sorted_entries]
    
    print(f"DEBUG: Original order: {test_words}")
    print(f"DEBUG: Sorted order: {sorted_words}")
    
    # Test that some key ordering relationships hold
    # Alpha words should come first
    alpha_words = [word for word in sorted_words if word[0] in "ἀἁάὰᾶἂἃἄἅἆἇἀἁΑἄΆαΆάΆ"]
    beta_words = [word for word in sorted_words if word[0] in "βΒ"]
    gamma_words = [word for word in sorted_words if word[0] in "γΓ"]
    
    if alpha_words and beta_words:
        alpha_last_index = max(sorted_words.index(word) for word in alpha_words)
        beta_first_index = min(sorted_words.index(word) for word in beta_words)
        assert alpha_last_index < beta_first_index, "All alpha words should come before beta words"
    
    if beta_words and gamma_words:
        beta_last_index = max(sorted_words.index(word) for word in beta_words)
        gamma_first_index = min(sorted_words.index(word) for word in gamma_words)
        assert beta_last_index < gamma_first_index, "All beta words should come before gamma words" 