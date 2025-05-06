import os
from morph import MorphParser
from vocab.vocab_generator import VocabGenerator

def main():
    # Initialize the morphological parser
    current_dir = os.path.dirname(os.path.abspath(__file__))
    morpheus_root = os.path.join(current_dir, "morpheus")
    cruncher = os.path.join(morpheus_root, "bin", "cruncher")
    stemlib = os.path.join(morpheus_root, "stemlib")
    
    parser = MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)
    generator = VocabGenerator(parser)
    
    # Get text input from user
    print("Enter Greek text (press Ctrl+D or Ctrl+Z when finished):")
    try:
        text = ""
        while True:
            line = input()
            text += line + "\n"
    except (EOFError, KeyboardInterrupt):
        if not text.strip():
            print("No text entered. Exiting.")
            return
    
    # Generate and display vocabulary list
    entries = generator.generate_vocab_list(text)
    print("\nVocabulary List:")
    print("================")
    print(generator.format_vocab_list(entries))

if __name__ == "__main__":
    main()
