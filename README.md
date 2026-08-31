markdown 🇬🇧 English | 🇮🇷 فارسی
# 🧠 Smart Persian Keyboard Corrector – Version 2

**Instantly fix mistyped Persian text** – now with **50 intelligent correction variants**, live preview, pinning, and full clipboard support.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 📌 Table of Contents
- [What’s New in v2](#-whats-new-in-v2)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Installation & Running](#-installation--running)
- [How to Use – Step by Step](#-how-to-use--step-by-step)
- [Use Cases](#-use-cases)
- [Keyboard Shortcuts](#-keyboard-shortcuts)
- [Troubleshooting](#-troubleshooting)
- [Contributing & License](#-contributing--license)

---

## 🆕 What’s New in v2

Version 2 is a **major upgrade** over the basic v1 (which only offered 4 fixed options). Now you get:

- **50 correction variants** (up from 4) – covers almost every possible keyboard‑layout mistake.
- **Live preview** – results update instantly as you type or paste; no “Convert” button needed.
- **Pin your favorites** – keep the most useful corrections at the top of the list.
- **Full keyboard shortcuts** – `Ctrl+C`, `Ctrl+V`, `Ctrl+A`, and `Ctrl+X` work everywhere.
- **Smarter combinations** – automatically mixes Persian and English swap patterns to handle mixed errors.
- **Right‑click context menu** – available on both input and output areas for quick copy/paste.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Live conversion** | As you type (or paste), up to 50 corrected versions appear instantly in the lower panel. |
| **50 intelligent mappings** | Built from **25 Persian‑specific swaps** + **7 English layout swaps** + their smart combinations. |
| **Pinning** | Click the 📌 button on any option to pin it to the top – useful for frequent corrections. |
| **One‑click copy** | Click any result (or press `Ctrl+C` when focused) to copy it to your clipboard. |
| **Full clipboard support** | Use toolbar buttons or standard shortcuts for cut/copy/paste/select‑all. |
| **Right‑click menu** | Works on both the input box and any output label. |
| **Dark theme** | Eye‑friendly, comfortable for extended use. |
| **Mouse wheel scrolling** | Smoothly scroll through the long list of suggestions. |
| **Portable executable** | No Python installation required – just download and run the `.exe`. |

---

## 🧠 How It Works

The program starts with a **base mapping** from English keys to Persian letters (standard Windows layout). Then it builds **50 different correction maps** by applying:

1. **25 Persian‑specific swaps** – e.g., `پ ↔ ب`, `ژ ↔ ف`, `گ ↔ ک`, `ش ↔ س`, `ت ↔ ن`, and many more.
2. **7 English layout swaps** – QWERTY→AZERTY, QWERTY→DVORAK, COLEMAK, shifted left/right, numeric mis‑typing, CapsLock reversal.
3. **Intelligent combinations** – mixes one Persian swap with one English swap, and also combines two Persian swaps, to cover complex mistakes.

When you type or paste text, the app runs **all 50 mappings** on your input and displays each result in a scrollable list.  
Non‑alphabetic characters (spaces, punctuation, digits) are preserved during conversion.

---

## 📥 Installation & Running

### Option 1 – Download the executable (recommended for non‑developers)
- Go to the [Releases page](https://github.com/mahanneman/keyboard-reverse-fixer-en-fa/releases).
- Download `keyboard_reverse_fixer_en_fa_v2.exe` from the v2.0.0 release.
- Double‑click the `.exe` file – no Python or extra libraries needed.

### Option 2 – Run from source (for developers)
- Ensure Python 3.7+ is installed.
- Clone the repository:
  ```bash
  git clone https://github.com/mahanneman/keyboard-reverse-fixer-en-fa.git
  cd keyboard-reverse-fixer-en-fa
Run the script:

bash
python keyboard_reverse_fixer_en_fa_v2.py
🖱️ How to Use – Step by Step
Launch the application.

Type or paste your English‑looking text into the upper text box.
Example: you type ;hgfdlk – this often happens when you intended to type in Persian but forgot to switch the keyboard layout.

Watch the lower area fill with up to 50 different Persian‑corrected versions – they appear in real time.

Find the correct one – usually it will be among the first few options (pinned ones stay on top).

Copy it in any of these ways:

Left‑click on the result text.

Click the 📋 کپی button next to the result.

Click on the result and press Ctrl+C on your keyboard.

Pin any option you frequently use by clicking its 📌 button – pinned items are always shown at the top of the list.

🎯 Use Cases
You typed a sentence in English while intending to type in Persian.
Example: ;hgfdlk → the app suggests سلام as one of the results.

You are using a non‑standard keyboard layout (e.g., AZERTY, Dvorak, Colemak) and want to see the correct Persian output without changing your system settings.

You frequently switch between Persian and English keyboards and often forget which layout is active – this tool saves you from re‑typing.

You are a translator, editor, student, or content creator working with Persian text and need a quick, reliable fix for mis‑typed words.

You want to experiment with different Persian‑keyboard mapping alternatives (e.g., Linux vs Windows layouts) to find the one that matches your typing habits.

⌨️ Keyboard Shortcuts
Shortcut	Action
Ctrl+C	Copy selected text (works on input area and on any output result after clicking on it)
Ctrl+V	Paste text into the input area
Ctrl+A	Select all text in the input area
Ctrl+X	Cut selected text (input area only)
Mouse wheel	Scroll the results list up/down
🛠️ Troubleshooting
Issue	Possible Solution
No results appear	Make sure you have typed at least one character – the app only shows results when there is input.
The correct option is not listed	Try typing a few more characters – the app often needs more context to disambiguate. Also check if your error involves a rare swap not covered; you can suggest additional mappings via GitHub issues.
Copy doesn’t work	Ensure you have clicked on the result first (to give it focus) before pressing Ctrl+C. Alternatively, use the copy button.
The window is too small	Resize the window – the output frame adapts automatically.
The executable doesn’t run	Make sure you have downloaded the correct .exe and that your antivirus isn’t blocking it (it’s a safe Python‑compiled file).
🤝 Contributing & License
Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.

This project is licensed under the MIT License – see the LICENSE file for details.

🙏 Acknowledgements
Developed by MA.AD.GH.
For questions or suggestions, reach out via GitHub.

Enjoy typing in Persian without the headache of wrong keyboard layouts! 🎉

text

---

I hope this comprehensive English README meets your needs.  
If you also want a **Persian (فارسی) version** of this README, just let me know – I’ll translate it for you as well.
