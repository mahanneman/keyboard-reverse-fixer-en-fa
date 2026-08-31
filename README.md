
markdown
[🇬🇧 English](README.md) | [🇮🇷 فارسی](README.fa.md)

# 🧠 Smart Persian Keyboard Corrector

**Instantly fix mistyped Persian text** – with **two versions** to suit your needs:  
- **V1** – Simple, 4 fixed correction options.  
- **V2** – Intelligent, **50 live suggestions**, pinning, and full clipboard support.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 📌 Table of Contents
- [Which Version to Choose?](#-which-version-to-choose)
- [Features Comparison](#-features-comparison)
- [Screenshots](#-screenshots)
- [Installation & Running](#-installation--running)
- [How to Use – V2 (Recommended)](#-how-to-use--v2-recommended)
- [How to Use – V1 (Basic)](#-how-to-use--v1-basic)
- [Keyboard Shortcuts (V2)](#-keyboard-shortcuts-v2)
- [Troubleshooting](#-troubleshooting)
- [Contributing & License](#-contributing--license)

---

## 🎯 Which Version to Choose?

| Version | Best For |
|---------|----------|
| **V1** | Quick, occasional use – just 4 fixed options, no live preview. |
| **V2** | Frequent use – 50 intelligent variants, live preview, pinning, and full keyboard shortcuts. |

> **Recommendation:** Use **V2** for the best experience.

---

## ✨ Features Comparison

| Feature | V1 | V2 |
|---------|:---:|:---:|
| Number of correction options | 4 | **50** |
| Live preview as you type | ❌ | ✅ |
| Pin favorites to top | ❌ | ✅ |
| Keyboard shortcuts (Ctrl+C/V/A/X) | ❌ | ✅ |
| Right‑click context menu | Partial | Full |
| Scrollable results | ✅ | ✅ |
| Dark theme | ✅ | ✅ |
| Portable executable | ✅ | ✅ |
| No Python required | ✅ | ✅ |

---

## 📸 Screenshots

*(Add your own screenshots and update the file paths)*

![V2 Main Window](screenshot_v2.png)  
*V2 – Live preview with 50 suggestions, pinning, and copy buttons*

![V1 Main Window](screenshot_v1.png)  
*V1 – Simple interface with 4 fixed options*

---

## 🚀 Installation & Running

### Option 1 – Download the executable (recommended)
- Go to the [Releases page](https://github.com/mahanneman/keyboard-reverse-fixer-en-fa/releases).
- Download the version you want:
  - `keyboard_reverse_fixer_en_fa_v1.exe` – Basic version
  - `keyboard_reverse_fixer_en_fa_v2.exe` – Smart version
- Double‑click the `.exe` – no Python or extra libraries needed.

### Option 2 – Run from source (for developers)
- Ensure Python 3.7+ is installed.
- Clone the repository:
  ```bash
  git clone https://github.com/mahanneman/keyboard-reverse-fixer-en-fa.git
  cd keyboard-reverse-fixer-en-fa
Run the desired script:

bash
# For V1
python keyboard_reverse_fixer_en_fa_v1.py

# For V2
python keyboard_reverse_fixer_en_fa_v2.py
🖱️ How to Use – V2 (Recommended)
Launch the application.

Type or paste your English‑looking text into the upper box.
Example: ;hgfdlk → you meant سلام but forgot to switch keyboard layout.

Watch the lower area fill with up to 50 Persian‑corrected versions – they appear in real time.

Find the correct one – usually among the first few options (pinned ones stay on top).

Copy it in any of these ways:

Left‑click on the result text.

Click the 📋 کپی button next to the result.

Click the result and press Ctrl+C.

Pin any option you frequently use by clicking its 📌 button – pinned items always appear at the top.

🖱️ How to Use – V1 (Basic)
Launch the application.

Type or paste your English‑looking text into the upper box.

Click the "تبدیل / نمایش گزینه‌ها" button.

Choose one of the 4 corrected versions shown below.

Click on any result (or use the copy button) to copy it to your clipboard.

⌨️ Keyboard Shortcuts (V2)
Shortcut	Action
Ctrl+C	Copy selected text (works on input and any output result after clicking on it)
Ctrl+V	Paste text into the input area
Ctrl+A	Select all text in the input area
Ctrl+X	Cut selected text (input area only)
Mouse wheel	Scroll the results list up/down
Note: V1 does not support keyboard shortcuts.

🛠️ Troubleshooting
Issue	Possible Solution
No results appear (V2)	Make sure you have typed at least one character – results appear instantly as you type.
The correct option is not listed	Try typing a few more characters – more context helps. You can suggest additional mappings via GitHub issues.
Copy doesn’t work	Ensure you have clicked on the result first (to give it focus) before pressing Ctrl+C. Alternatively, use the copy button.
The window is too small	Resize the window – the output area adapts automatically.
The executable doesn’t run	Make sure you have downloaded the correct .exe and that your antivirus isn’t blocking it (it’s a safe Python‑compiled file).
🤝 Contributing & License
Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.

This project is licensed under the MIT License – see the LICENSE file for details.

👤 Author
MA.AD.GH
GitHub | Telegram

🙏 Acknowledgements
Built with Python's built‑in Tkinter – no external dependencies.

Special thanks to all users who provided feedback and suggested new swap patterns.

Tip: For a more advanced experience, always use V2. V1 is kept for simplicity and legacy support.

Enjoy typing in Persian without the headache of wrong keyboard layouts! 🎉
