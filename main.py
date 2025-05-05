from morph import MorphParser
import os

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
morpheus_root = os.path.join(current_dir, "morpheus")
cruncher = os.path.join(morpheus_root, "bin", "cruncher")
stemlib = os.path.join(morpheus_root, "stemlib")

parser = MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)

words = [
    "a)/nqrwpos", "gunh/", "o(", "kai/", "lo/gos", "tima=", "e)/dwken",
    "h)=n", "ei)=nai", "a)gaqo/s", "kalo/s", "mh/", "ti/s", "au)to/s", "le/gei"
]

for word in words:
    print(f"\nProcessing: {word}")
    results = parser.parse_word(word)
    for entry in results:
        print(entry)
