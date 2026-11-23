# ShadowCipher — Complete Edition

An offline Python/Tkinter laboratory for classical ciphers, steganographic patterns, text encodings, analysis, and Persian text utilities.

This release improves access to the supplied ShadowCipher application without removing any original tools. All **92 original operation buttons**, including duplicate entries, and all six original tabs remain available.

## Preservation guarantee and scope

The source of truth for this release is `keyboard_reverse_fixer_en_fa_v4.py` (ShadowCipher v2.0), not the earlier, separate Smart Text Toolkit script.

- Every original helper function and the complete original `ShadowCipher` class are retained unchanged in `shadowcipher.py`.
- The new `EnhancedShadowCipher` subclass adds usability features and overrides selected UI behavior.
- Original operation definitions and transform semantics are preserved, including legacy limitations.
- The original file is included byte-for-byte as `keyboard_reverse_fixer_en_fa_v4.original.py`.
- The enhanced launcher starts the new subclass; the untouched backup retains the original launcher.
- Tests compare original definitions and button lists, not just operation totals.

Preservation does not mean every legacy algorithm is correct, lossless, reversible, or secure. Known caveats are documented below rather than silently changing your existing results.

## What's improved

- English labels for original tool buttons and the six tabs.
- Search all original tools by English or Persian name.
- Run a search result with Enter, double-click, or **Run selected**.
- Session-only favorites, including separate entries for duplicate buttons.
- Scrollable operation areas in the five previously unscrolled tabs; the original steganography scrollbar remains.
- Open UTF-8 text files and save output as UTF-8.
- Input replacement confirmation for file loading, examples, and transformation chaining.
- Clear-workspace and exit confirmation.
- One-click use of output as input.
- Shared example text to explore extraction and analysis tools.
- Right-click Cut/Copy/Paste and Select all for both editors.
- Larger/smaller editor text controls.
- Optional visual masking of the key.
- An English quick-start guide, compatibility notes, and keyboard shortcuts.

The output editor remains editable, as in the original. English UI labels do not translate underlying data: the original full analysis report, some helper-generated messages, Persian comments, and Persian acrostic cover words remain unchanged.

## Requirements

- Python 3.10 or later is recommended for this distribution.
- Tkinter installed for your Python interpreter.
- A working graphical desktop session.
- No third-party Python packages.

## Run

Download or clone this repository, open a terminal in its directory, and run:

```bash
python shadowcipher.py
```

Depending on your installation:

```bash
python3 shadowcipher.py
# Windows Python launcher:
py shadowcipher.py
```

To check Tkinter availability:

```bash
python -m tkinter
```

If Tkinter is missing, install it using the package manager or Python installer associated with your interpreter. On Debian/Ubuntu, it is commonly provided by `python3-tk`. A server without a graphical display cannot open the desktop UI.

## Quick start

1. Paste text into **Input / Cover text**, or click **Open file**.
2. Choose a tab and click a tool button. It runs immediately; there is no separate global Run button.
3. Read or edit the output.
4. Click **Copy output** or **Save output**.
5. To chain operations, select **Use output as input**, then choose another tool.

For an easy first example, click **Load example**, then find **First letters of lines** or **Full text analysis**.

### Find a tool

Click **Find tool** or press Ctrl+F / Cmd+F. Search English or Persian names, select a result, and press Enter. Double-clicking a result also runs it.

**Toggle favorite** stores a tool in the current session's favorites. It does not remove or replace its tab button. Favorites are not saved after exit.

## Original tabs and tools

| Tab | Included functionality |
| --- | --- |
| Steganography | Word/line initials and endings, paragraph initials, indexed extraction, diagonal reading, book cipher, null patterns, acrostic cover generation, hiding a key in cover text |
| Classical ciphers | Fixed and N-based Caesar shifts, Vigenere encode/decode, Atbash, ROT13, reversal, letter-case transformations |
| Encoding | Base64, hexadecimal/binary character codes, URL encoding, HTML entities, Unicode escape, MD5, SHA-256, SHA-512, CRC32, JSON formatting, text filters |
| Morse and special | Morse encode/decode, NATO phonetic output, Braille substitution, Leet, vowel stripping and uppercase extraction |
| Analysis | Full report, character/word/line counts, character and word frequencies, longest/shortest word |
| Persian and utilities | Digit conversion, Arabic/Persian letter conversion, diacritic/tatweel removal, Persian-range extraction, whitespace normalization, UUID, random password, timestamp, short SHA-256, Unicode codes, local date/time |

### Key and N reference

| Tool | Settings |
| --- | --- |
| Vigenere | Latin-letter key in **Key** |
| Caesar N | **N** is the shift |
| Every Nth character/word | Starts at index 0, then N, 2N, and so on |
| Odd/even positions | Original zero-based indexing: odd = indexes 1, 3, 5; even = indexes 0, 2, 4 |
| Word index key | One-based word positions such as `1 3 5` |
| Book cipher | One-based `line.word.character` triples, e.g. `1.1.1 2.3.2` |
| Character at index N in each line | Uses the zero-based index N after stripping line edges |
| Hide key in cover text | **Input** is the cover; **Key** is the secret; **N** controls candidate positions |

The original N parser is unchanged: invalid input falls back to 2, and numeric values are clamped to at least 1. The spinner's displayed range does not prevent manually entered larger values.

## Keyboard shortcuts

| Action | Shortcut |
| --- | --- |
| Open input file | Ctrl+O / Cmd+O |
| Save output | Ctrl+S / Cmd+S |
| Find tool | Ctrl+F / Cmd+F |
| Copy output | Ctrl+Shift+C / Cmd+Shift+C |
| Select all in focused editor | Ctrl+A / Cmd+A |
| Larger editor text | Ctrl/Cmd + Plus or Equal |
| Smaller editor text | Ctrl/Cmd + Minus |
| Help | F1 |
| Run selected finder result | Enter |
| Close finder | Escape |

Shortcut behavior can vary by operating system and Tk installation. Menu and button alternatives are available.

## Compatibility and known limitations

No existing transformation has been silently replaced by a new algorithm.

- **Morse:** original encoding can lose spaces and unsupported characters; decoding does not reliably reconstruct original word boundaries.
- **Vigenere:** a nonempty key containing no Latin letters retains the original fallback to `a` rather than producing an error.
- **Base64:** the original decoder uses replacement characters for invalid UTF-8 and permissive Base64 parsing.
- **Hex and binary:** represent Unicode code points. The binary format uses a minimum width of eight bits; these tools do not represent UTF-8 bytes.
- **Cover hiding:** only eligible alphabetic positions are changed. A short or unsuitable cover can silently truncate the secret. The generic every-N extractor may also read remaining cover characters; verify results yourself.
- **Acrostic cover generation:** uses the original limited Persian word list and falls back to a character followed by `xx` when no word matches.
- **Persian extraction:** uses the original Unicode-range regular expression, not linguistic word segmentation.
- **Vowel/consonant tools:** retain the original simple character heuristic; they are not Persian phonetic analysis.
- **Counts:** count Unicode code points or original whitespace-separated tokens, not grapheme clusters or linguistic words.
- **Responsiveness:** operations still execute synchronously. Large files or expensive transformations can pause the interface. No worker cancellation, resource sandbox, or new input-size limit is implemented.
- **Scrolling:** original steganography wheel behavior is retained; scrollbar dragging is available. Cross-platform wheel refinements are not claimed.

## Privacy and security

The application adds no networking, telemetry, or automatic workspace/history saving. Files you explicitly save and operating-system clipboard history may retain text. Favorites are session-only.

The key remains visible by default for compatibility. Use **Tools → Hide key** for visual masking; this is not encrypted key storage.

Classical ciphers and steganographic patterns are educational, not secure encryption. Base64, NATO, Braille, and Leet do not provide confidentiality. MD5 is a legacy digest. Plain hashes are not complete password-storage systems. Do not use this application as a substitute for reviewed security software.

## Tests

Run from the repository directory:

```bash
python -m unittest -v test_shadowcipher.py
```

The tests verify:

1. Every original helper/class definition is unchanged.
2. The original source prefix is retained verbatim.
3. Representative helper outputs match the untouched original.
4. Caesar transformations round-trip.
5. Vigenere matches a known vector.
6. Every original operation-button entry remains, in order, including duplicates.

These tests do not prove every original tool is correct or reversible. They check preservation and selected existing behavior. They do not launch or interactively validate the GUI. If Tkinter is missing, the helper-only test loader omits GUI imports and uses a non-GUI base-class placeholder; this does not test GUI functionality.

See `TEST_REPORT.txt` for the actual build-environment results. The graphical interface still needs manual testing on your operating system.

## Repository layout

```text
shadowcipher/
├── shadowcipher.py                              # Enhanced app, with original definitions retained
├── keyboard_reverse_fixer_en_fa_v4.original.py   # Untouched source backup
├── test_shadowcipher.py                         # Headless preservation tests
├── README.md                                    # Documentation
└── TEST_REPORT.txt                              # Build-time verification
```

## Troubleshooting

### Python is not found
Try `python3` or Windows `py`, or install Python and verify your command-line configuration.

### Tkinter cannot be imported
Install Tkinter for the interpreter actually running the application. A different Python installation may have different Tk support.

### A file cannot be opened
The file must decode as UTF-8; an initial UTF-8 BOM is accepted. Files saved in other encodings must be converted first.

### A tool gives unexpected output
Check the original semantics above, the Key field, and N. Some transformations are lossy by design or retain known legacy behavior. Use a small, non-sensitive example to investigate.

### A button is hard to find
Use **Find tool** to search across every tab. The finder includes all original operation entries.

### The window pauses
Tools run on the GUI thread. Avoid very large input. Save important output before trying expensive transformations.

## Contributing

Preserving existing tools is a requirement for this branch. Do not delete, rename away, or silently change an existing operation. Prefer additive UI changes or separately named corrected tools. Document deliberate behavior changes and add tests.

When reporting bugs, include your operating system, Python version, tool name, N/key settings when safe, and a minimal reproducible input. Never post private documents, real passwords, or secret keys.

## License

No license is assumed or granted by this README. Before publishing, the repository owner should choose an appropriate license and add a `LICENSE` file after confirming rights to the supplied source.
