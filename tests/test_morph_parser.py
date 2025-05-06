import unittest
import os
from morph import MorphParser
from morph.part_of_speech import PartOfSpeech, UnknownPartOfSpeechError
from morph.features import Feature, UnknownFeatureError
from morph.morph_class import MorphClass, UnknownMorphClassError

class TestMorphParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Get the project root directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        morpheus_root = os.path.join(current_dir, "morpheus")
        cruncher = os.path.join(morpheus_root, "bin", "cruncher")
        stemlib = os.path.join(morpheus_root, "stemlib")
        
        cls.parser = MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)

    def test_parse_noun(self):
        """Test parsing a basic noun (ἄνθρωπος)"""
        results = self.parser.parse_word("a)/nqrwpos")
        self.assertTrue(len(results) > 0)
        
        # Find the noun entry (there might be multiple interpretations)
        noun_entry = next((entry for entry in results if entry.part_of_speech == PartOfSpeech.NOUN), None)
        self.assertIsNotNone(noun_entry)
        self.assertEqual(noun_entry.lemma, "ἄνθρωπος")
        self.assertIn(Feature.MASCULINE, noun_entry.features)
        self.assertIn(Feature.NOMINATIVE, noun_entry.features)
        self.assertIn(Feature.SINGULAR, noun_entry.features)
        self.assertIn(MorphClass.SECOND_DECLENSION, noun_entry.morph_classes)

    def test_parse_verb(self):
        """Test parsing a verb form (ἔδωκεν)"""
        results = self.parser.parse_word("e)/dwken")
        self.assertTrue(len(results) > 0)
        
        verb_entry = next((entry for entry in results if entry.part_of_speech == PartOfSpeech.VERB), None)
        self.assertIsNotNone(verb_entry)
        self.assertEqual(verb_entry.lemma, "δίδωμι")
        self.assertIn(Feature.AORIST, verb_entry.features)
        self.assertIn(Feature.ACTIVE, verb_entry.features)
        self.assertIn(Feature.INDICATIVE, verb_entry.features)
        self.assertIn(Feature.THIRD, verb_entry.features)
        self.assertIn(Feature.SINGULAR, verb_entry.features)
        self.assertIn(MorphClass.MOVABLE_NU, verb_entry.morph_classes)
        self.assertIn(MorphClass.FIRST_AORIST, verb_entry.morph_classes)

    def test_parse_article(self):
        """Test parsing an article (ὁ)"""
        results = self.parser.parse_word("o(")
        self.assertTrue(len(results) > 0)
        
        article_entry = next((entry for entry in results if entry.part_of_speech == PartOfSpeech.ARTICLE), None)
        self.assertIsNotNone(article_entry)
        self.assertEqual(article_entry.lemma, "ὁ")
        self.assertIn(Feature.MASCULINE, article_entry.features)
        self.assertIn(Feature.NOMINATIVE, article_entry.features)
        self.assertIn(Feature.SINGULAR, article_entry.features)
        self.assertIn(Feature.ARTICLE, article_entry.features)

    def test_parse_adjective(self):
        """Test parsing an adjective (ἀγαθός)"""
        results = self.parser.parse_word("a)gaqo/s")
        self.assertTrue(len(results) > 0)
        
        adj_entry = next((entry for entry in results if entry.part_of_speech == PartOfSpeech.ADJECTIVE), None)
        self.assertIsNotNone(adj_entry)
        self.assertEqual(adj_entry.lemma, "ἀγαθός")
        self.assertIn(Feature.MASCULINE, adj_entry.features)
        self.assertIn(Feature.NOMINATIVE, adj_entry.features)
        self.assertIn(Feature.SINGULAR, adj_entry.features)
        self.assertIn(MorphClass.ADJ_2_1_2, adj_entry.morph_classes)

    def test_parse_conjunction(self):
        """Test parsing a conjunction (καί)"""
        results = self.parser.parse_word("kai/")
        self.assertTrue(len(results) > 0)
        
        conj_entry = next((entry for entry in results if Feature.CONJUNCTION in entry.features), None)
        self.assertIsNotNone(conj_entry)
        self.assertEqual(conj_entry.lemma, "καί")
        self.assertIn(Feature.CONJUNCTION, conj_entry.features)
        self.assertIn(Feature.INDECLINABLE, conj_entry.features)

    def test_parse_contract_verb(self):
        """Test parsing a contract verb (τιμᾷ)"""
        results = self.parser.parse_word("tima=|")
        self.assertTrue(len(results) > 0)
        
        verb_entry = next((entry for entry in results if entry.part_of_speech == PartOfSpeech.VERB), None)
        self.assertIsNotNone(verb_entry)
        self.assertEqual(verb_entry.lemma, "τιμάω")
        self.assertIn(Feature.CONTRACTED, verb_entry.features)
        self.assertIn(Feature.PRESENT, verb_entry.features)
        self.assertIn(MorphClass.AW_PRESENT, verb_entry.morph_classes)
        self.assertIn(MorphClass.AW_DENOM, verb_entry.morph_classes)

    def test_parse_dialect_form(self):
        """Test parsing a form with dialect features (ἦν)"""
        results = self.parser.parse_word("h)=n")
        self.assertTrue(len(results) > 0)
        
        verb_entry = next((entry for entry in results if Feature.AEOLIC in entry.features), None)
        self.assertIsNotNone(verb_entry)
        self.assertEqual(verb_entry.lemma, "εἰμί")
        self.assertIn(Feature.IMPERFECT_ALT, verb_entry.features)
        self.assertIn(Feature.AEOLIC, verb_entry.features)
        self.assertIn(Feature.EPIC, verb_entry.features)
        self.assertIn(MorphClass.IRREGULAR, verb_entry.morph_classes)

    def test_parse_indefinite(self):
        """Test parsing an indefinite pronoun (τις)"""
        results = self.parser.parse_word("tis")
        self.assertTrue(len(results) > 0)
        
        indef_entry = next((entry for entry in results if Feature.INDEFINITE in entry.features), None)
        self.assertIsNotNone(indef_entry)
        self.assertEqual(indef_entry.lemma, "τις")
        self.assertIn(Feature.INDEFINITE, indef_entry.features)
        self.assertIn(Feature.MASC_FEM, indef_entry.features)
        self.assertIn(Feature.ENCLITIC, indef_entry.features)

    def test_parse_article_adjective(self):
        """Test parsing an article-adjective (αὐτός)"""
        results = self.parser.parse_word("au)to/s")
        self.assertTrue(len(results) > 0)
        
        adj_entry = next((entry for entry in results if MorphClass.ARTICLE_ADJECTIVE in entry.morph_classes), None)
        self.assertIsNotNone(adj_entry)
        self.assertEqual(adj_entry.lemma, "αὐτός")
        self.assertIn(Feature.MASCULINE, adj_entry.features)
        self.assertIn(Feature.NOMINATIVE, adj_entry.features)
        self.assertIn(Feature.SINGULAR, adj_entry.features)
        self.assertIn(MorphClass.ARTICLE_ADJECTIVE, adj_entry.morph_classes)

    def test_invalid_word(self):
        """Test parsing an invalid word"""
        results = self.parser.parse_word("xxxxx")
        self.assertEqual(len(results), 0)

    def test_unknown_part_of_speech(self):
        """Test that unknown part of speech codes raise an appropriate exception"""
        with self.assertRaises(UnknownPartOfSpeechError) as context:
            PartOfSpeech.from_str("UNKNOWN")
        self.assertEqual(context.exception.code, "UNKNOWN")

    def test_unknown_feature(self):
        """Test that unknown features raise an appropriate exception"""
        with self.assertRaises(UnknownFeatureError) as context:
            Feature.from_str("UNKNOWN")
        self.assertEqual(context.exception.feature, "UNKNOWN")

    def test_unknown_morph_class(self):
        """Test that unknown morphological classes raise an appropriate exception"""
        with self.assertRaises(UnknownMorphClassError) as context:
            MorphClass.from_str("UNKNOWN")
        self.assertEqual(context.exception.morph_class, "UNKNOWN")

    def test_multiple_morph_classes(self):
        """Test that a word can have multiple morphological classes"""
        classes = MorphClass.from_str("nu_movable aor1")
        self.assertEqual(len(classes), 2)
        self.assertIn(MorphClass.MOVABLE_NU, classes)
        self.assertIn(MorphClass.FIRST_AORIST, classes)

    def test_comma_separated_morph_classes(self):
        """Test that comma-separated morphological classes are handled correctly"""
        classes = MorphClass.from_str("aw_pr,aw_denom")
        self.assertEqual(len(classes), 2)
        self.assertIn(MorphClass.AW_PRESENT, classes)
        self.assertIn(MorphClass.AW_DENOM, classes)

if __name__ == '__main__':
    unittest.main() 