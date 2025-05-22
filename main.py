import os
import sys
import argparse
from morph import MorphParser
from vocab.vocab_generator import VocabGenerator

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Greek vocabulary tool')
    parser.add_argument('input_file', nargs='?', help='Input file containing Greek text')
    parser.add_argument('--non-interactive', '-n', action='store_true', 
                        help='Run in non-interactive mode (no prompts)')
    parser.add_argument('--stop-words', '-s', help='File containing stop words (one per line)')
    parser.add_argument('--latex', '-l', action='store_true', help='Output in LaTeX format')
    args = parser.parse_args()
    
    # Initialize the morphological parser
    current_dir = os.path.dirname(os.path.abspath(__file__))
    morpheus_root = os.path.join(current_dir, "morpheus")
    cruncher = os.path.join(morpheus_root, "bin", "cruncher")
    stemlib = os.path.join(morpheus_root, "stemlib")
    
    morph_parser = MorphParser(cruncher_path=cruncher, stemlib_path=stemlib)
    
    # Load stop words if provided
    stop_words = set()
    if args.stop_words:
        try:
            with open(args.stop_words, 'r', encoding='utf-8') as f:
                stop_words = {line.strip() for line in f if line.strip()}
        except FileNotFoundError:
            print(f"Warning: Stop words file {args.stop_words} not found. Continuing without stop words.")
        except Exception as e:
            print(f"Warning: Error reading stop words file: {e}. Continuing without stop words.")
    
    generator = VocabGenerator(morph_parser, stop_words=stop_words, latex_output=args.latex)
    
    # Determine if we should run in interactive mode
    interactive = not args.non_interactive
    
    # Check if a file path was provided
    if args.input_file:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            # Generate and display vocabulary list
            entries = generator.generate_vocab_list(text, interactive=interactive)
            print("\nVocabulary List:")
            print("================")
            print(generator.format_vocab_list(entries))
            return
        except FileNotFoundError:
            print(f"Error: File {args.input_file} not found.")
            return
        except Exception as e:
            print(f"Error processing file: {e}")
            return
    
    # If no file provided, get input from console
    print("Enter Greek text (enter three empty lines in a row to finish):")
    text = ""
    empty_lines = 0
    
    try:
        while empty_lines < 3:
            line = input()
            if not line.strip():
                empty_lines += 1
            else:
                empty_lines = 0
            
            if empty_lines < 3:  # Only add lines that aren't part of the exit sequence
                text += line + "\n"
    except EOFError:
        # Handle case where input is from a pipe/file
        pass
    
    if not text.strip():
        print("No text entered. Exiting.")
        return
    
    # Generate and display vocabulary list
    entries = generator.generate_vocab_list(text, interactive=interactive)
    print("\nVocabulary List:")
    print("================")
    print(generator.format_vocab_list(entries))

if __name__ == "__main__":
    main()
