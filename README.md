
markdown
[🇬🇧 English](README.md) | [🇮🇷 فارسی](README.fa.md)

# 🎤 Vosk Voice Typing – Speech-to-Text Keyboard

**Version 3** · Real‑time speech recognition that types directly into any application.  
Works offline, supports 20+ languages, floats above all windows, and includes smart timers, voice commands, and a built‑in model manager.

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green)](https://pypi.org/project/PyQt5/)
[![Vosk](https://img.shields.io/badge/Vosk-0.3.45-orange)](https://alphacephei.com/vosk/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Table of Contents
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation & Setup](#-installation--setup)
- [How to Use](#-how-to-use)
- [Global Hotkeys](#-global-hotkeys)
- [Voice Commands](#-voice-commands)
- [Building Executable](#-building-an-executable-optional)
- [Linux‑Specific Notes](#-linuxspecific-notes)
- [Folder Structure](#-folder-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing & License](#-contributing--license)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Real‑time recognition** | Uses the Vosk engine – no internet required, works entirely offline. |
| **20+ languages** | Supports Persian, English, Russian, German, French, Spanish, Italian, Chinese, and many more. |
| **Floating window** | Always‑on‑top, draggable, semi‑transparent, stays out of your way. |
| **Smart timer** | Automatically start or stop recording after a countdown (two modes: `Off` and `On`). |
| **Global hotkeys** | Control recording from anywhere: `Ctrl+Shift+S` (start), `Ctrl+Shift+X` (stop), `Ctrl+Shift+L` (switch language). |
| **Voice commands** | Hands‑free control: `copy`, `paste`, `enter`, `delete all`, `undo`, and language switching. |
| **Built‑in model manager** | Download models from the Vosk server, add your own local models, or delete unwanted ones – all from the GUI. |
| **Bilingual UI** | Switch between Persian and English instantly. |
| **System tray icon** | Run in the background with a tray menu for quick access. |
| **Dark theme** | Modern, eye‑friendly interface with rounded corners and transparency. |

---

## 📸 Screenshots

*(Add your own screenshots and update the file paths)*

![Main window](screenshot_main.png)  
*Floating window showing status, timer, and language selector*

![Model manager](screenshot_models.png)  
*Download models, add local ones, or delete installed models*

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.7 or higher**
- Required Python libraries (see `requirements.txt`)

### Steps

#### 1. Clone the repository
```bash
git clone https://github.com/mahanneman/vosk-voice-typing.git
cd vosk-voice-typing
2. Install dependencies
bash
pip install -r requirements.txt
Linux users: You may need to install portaudio and libportaudio2 first:

bash
sudo apt install portaudio19-dev python3-pyaudio
3. Run the application
bash
python Vosk_SpeechToText_v3.py
🧭 How to Use
First Run
The app scans for existing models in the models/ folder.

If no model is found, you'll see: "No model found. Please download a model."

Click the "📥 Manage Models" button to open the model manager.

Managing Models
In the model manager you can:

Download official Vosk models from the list (requires internet).

Add a local model by selecting its folder and entering the language code (e.g., fa for Persian).

Delete unwanted models (only those inside the models/ folder can be removed).

After adding a model, select it from the language dropdown in the main window.

Start Recording
Click the "🎤 Start" button or press Ctrl+Shift+S.

Recognised text is typed automatically into the currently focused application.

If typing fails (e.g., in restricted environments), the text is copied to the clipboard instead.

Stop Recording
Click "⏹ Stop" or press Ctrl+Shift+X.

Switch Language
Use the language dropdown in the main window, or press Ctrl+Shift+L to cycle through installed languages.

You can also say "change to English" (when in Persian mode) or "persian" (when in English mode).

Smart Timer
Set a countdown (up to 99:59) using the + and − buttons.

Off mode – when the timer expires, recording stops.

On mode – when the timer expires, recording starts.

The timer runs in the background and its status is shown in the status bar.

⌨️ Global Hotkeys
Hotkey	Action
Ctrl+Shift+S	Start recording
Ctrl+Shift+X	Stop recording
Ctrl+Shift+L	Cycle through available languages
These hotkeys work globally – the app does not need to be in focus.

🗣️ Voice Commands
While recording, say any of these phrases to execute the corresponding action:

Command (English)	Action
copy	Copy selected text
paste	Paste from clipboard
enter / new line	Press Enter
delete all / clear	Clear all text in the active field
undo / ctrl z	Undo the last action
change to English (when in Persian)	Switch to English
persian (when in English)	Switch to Persian
📦 Building an Executable (Optional)
You can create a standalone executable (Windows, Linux, macOS) with PyInstaller:

bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico Vosk_SpeechToText_v3.py
You can use the built‑in microphone icon from the code, or provide your own .ico file.

🐧 Linux‑Specific Notes
To access the microphone, ensure your user is in the audio group:

bash
sudo usermod -a -G audio $USER
Some distributions may require additional packages:

bash
sudo apt install python3-pyqt5 python3-pyqt5.qtsvg
If audio is not captured, check your default input device in system settings or use pavucontrol.

📂 Folder Structure
text
vosk-voice-typing/
├── Vosk_SpeechToText_v3.py   # Main application
├── models/                   # Downloaded models (created automatically)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
🛠️ Troubleshooting
Issue	Possible Solution
No models found	Go to Manage Models and download at least one model for your language.
Microphone not working	Check your system audio input settings. On Linux, ensure you are in the audio group.
Recognition is inaccurate	Try a larger model (e.g., vosk-model-en-us-0.22 instead of small). Also speak clearly and close to the mic.
App doesn't type the text	Make sure the target application has focus. If typing fails, the text is copied to the clipboard – just paste it manually.
Hotkeys not responding	Some applications may intercept global hotkeys. Try running the app as administrator (Windows) or check your system's shortcut settings.
Executable doesn't run	Ensure you have downloaded the correct .exe and that your antivirus isn't blocking it (it's a safe Python‑compiled file).
🤝 Contributing & License
Contributions are welcome! Feel free to open issues or submit pull requests on GitHub.

This project is licensed under the MIT License – see the LICENSE file for details.

👤 Author
MA.AD.GH
GitHub | Telegram

🙏 Acknowledgements
The Vosk team for their excellent speech recognition engine

PyQt5, sounddevice, keyboard, and requests libraries

