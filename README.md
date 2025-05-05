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

## Platform Support

The Morpheus binary needs to be compiled for your specific platform:

- **macOS**: Requires Xcode Command Line Tools (`xcode-select --install`)
- **Linux**: Requires build-essential and flex/lex (`sudo apt-get install build-essential flex`)
- **Windows**: Use WSL (Windows Subsystem for Linux) and follow Linux instructions

## Notes

- The Morpheus binary is compiled from source for your specific platform
- Build warnings about deprecated functions can be safely ignored
- If you get linker errors about `-ll`, you may need to install flex/lex for your platform 