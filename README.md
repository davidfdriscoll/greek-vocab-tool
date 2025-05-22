# Greek Vocabulary Tool

A tool for parsing Ancient Greek words using the Morpheus morphological analysis system.

## Installation

1. Clone this repository with submodules:
```bash
git clone --recursive https://github.com/YOUR_USERNAME/greek-vocab-tool.git
cd greek-vocab-tool
```

2. Build Morpheus:
```bash
cd morpheus/src
make clean
CFLAGS='-std=gnu89 -Wno-return-type -Wno-implicit-function-declaration -Wno-error=incompatible-function-pointer-types' make LOADLIBES='-ll'
make install
cd ../..
```

3. Install Python dependencies (if any):
```bash
pip install -r requirements.txt
```

## Usage

Run the tool with:
```bash
python main.py
```

The script will process a predefined list of Greek words and output their morphological analysis.

### Stop Words

You can provide a list of stop words to exclude from the vocabulary list. Stop words are common words that you want to skip in the analysis. The stop words file should contain one word per line.

Example stop words file (`resources/frogs-stop-words.txt`):
```
ὁ
Ζεύς
καί
διά
ἐγώ
δέ
τις
εἰμί
οὗτος
οὐ
```

To use stop words:
```bash
python main.py input.txt --stop-words resources/frogs-stop-words.txt
```

### LaTeX Output

You can generate LaTeX-formatted vocabulary lists by adding the `--latex` flag:

```bash
python main.py input.txt --latex
```

This will output entries in LaTeX format like:
```
\vocabentry{ἀληθεύω}{to speak truth}
\vocabentry{ἀλύσκω}{to flee from, shun, escape}
\vocabentry{ἄξιος, α, ον}{worthy, deserving}
\vocabentry{ἀοιδή, ἡ}{song}
```

You can combine this with other options:
```bash
python main.py input.txt --stop-words resources/frogs-stop-words.txt --latex
```

## Platform Support

The Morpheus binary needs to be compiled for your specific platform:

- **macOS**: Requires Xcode Command Line Tools (`xcode-select --install`)
- **Linux**: Requires build-essential and flex/lex (`sudo apt-get install build-essential flex`)
- **Windows**: Use WSL (Windows Subsystem for Linux) and follow Linux instructions

## Notes

- The Morpheus binary is compiled from source for your specific platform
- Build warnings about deprecated functions can be safely ignored
- If you get linker errors about `-ll`, you may need to install flex/lex for your platform 