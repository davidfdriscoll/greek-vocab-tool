from morph import MorphParser
import os
import beta_code

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
morpheus_root = os.path.join(current_dir, "morpheus")
cruncher = os.path.join(morpheus_root, "bin", "cruncher")
stemlib = os.path.join(morpheus_root, "stemlib")

parser = MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)

# Unicode Greek words
words = [
    "ἄνθρωπος", "γυνή", "ὁ", "καί", "λόγος", "τιμᾷ", "ἔδωκεν",
    "ἦν", "εἶναι", "ἀγαθός", "καλός", "μή", "τίς", "αὐτός", "λέγει"
]

for word in words:
    print(f"\nProcessing: {word}")
    # Convert Unicode to Beta Code for Morpheus
    beta_word = beta_code.greek_to_beta_code(word)
    results = parser.parse_word(beta_word)
    for entry in results:
        print(entry)
