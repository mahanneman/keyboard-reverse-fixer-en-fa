# Smart Text Toolkit 2.0

An English-language, offline desktop rewrite of the supplied text toolkit.

## Requirements
- Python 3.10 or later.
- Tkinter with a working graphical desktop.
- No third-party Python packages required.

## Start
Open a terminal in this folder and run:

```sh
python smart_text_toolkit.py
```

On systems where Python is named python3:

```sh
python3 smart_text_toolkit.py
```

Windows users can also use `py smart_text_toolkit.py`.

To check whether Tkinter is available, run `python -m tkinter`.
If Tkinter is missing, install the Tkinter package appropriate to your Python
installation. On Debian/Ubuntu this is commonly `sudo apt install python3-tk`.
Use the Python distribution's installer or package manager on other platforms.
A graphical desktop is required to launch the application.

## First use
1. Select Text overview from the tool list.
2. Click Load example, or paste your own text into Input.
3. Click Run tool.
4. Read the output and click Copy output or Save output.
5. Use Search and the category dropdown to discover more tools.

Each tool has a description. Tools with settings display the required fields.
Values are hidden until Show values is selected. For decoding examples, the
application generates matching encoded text where an encoder is available.
Favorites are session-only. No workspace is automatically saved.

## Changes from the supplied version
This is a curated rewrite, not a claim of complete feature parity.
Repeated fixed Caesar shifts and rail counts are consolidated into parameters.
Unsupported or misleading implementations such as the custom two-key stream
cipher, Porta, Bifid, Base58/Base62 and the incomplete ADFGX/Nihilist transforms
are not retained. Morse, Braille, NATO, Pig Latin and Leet are also not included
in this release. No secure-encryption feature is claimed.

The rewrite corrects repeating-key XOR decoding, Beaufort inversion,
columnar transposition padding loss, ROT47 handling of non-ASCII characters,
UTF-8 byte conversions, quoted CSV/TSV conversion and silent invalid UTF-8
replacement. It preserves Persian text support with an English interface.

## Privacy and security
The program has no networking code and does not automatically persist input,
keys, favorites or results. Files you save and clipboard data can be retained
by your operating system and other applications.
Classical ciphers and XOR are educational only. Hashing is not encryption.
MD5 and SHA-1 are labeled as legacy algorithms.

Input is limited to 2,000,000 UTF-8 bytes; output to 8,000,000 UTF-8 bytes.
Decompression reads are output-limited, but the app is not a sandbox: do not
process hostile compressed data. Some operations allocate intermediate data
before the final output limit check. One worker thread runs at a time.
There is no in-process cancellation; closing the application abandons its job.

## Text behavior
- UTF-8 decoding is strict; invalid data produces an actionable error.
- Character counts measure Unicode code points, not grapheme clusters.
- Word counts use Unicode word tokens, including numbers and underscores.
- Most line transformations normalize line endings to LF and omit a final terminator.
- Reading time is an estimate based on 200 word tokens per minute.

## Verification
Run core tests without opening a GUI:

```sh
python smart_text_toolkit.py --self-test
```

List the tools:

```sh
python smart_text_toolkit.py --list-tools
```

The included test report records automated core tests run in the build
environment. The graphical interface was not interactively tested there;
check layout, keyboard shortcuts, clipboard and file dialogs on your OS.
