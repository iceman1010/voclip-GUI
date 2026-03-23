# voclip-GUI

<img src="src/icon.png" width="48" height="48" align="left" />

A modern GUI frontend for [voclip](https://github.com/iceman1010/voclip) - a voice-to-clipboard tool that transcribes your speech and copies the text to your clipboard or types it directly.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **One-Shot Recording** - Press record, speak, and get your words transcribed instantly
- **Listen Mode** - Always-on background mode with wake word detection
- **Wake Words** - Train custom wake words and voice commands
- **Clipboard & Type** - Output to clipboard or type directly into any application
- **System Tray** - Runs quietly in the background with quick access menu
- **Cross-Platform** - Available for Linux, macOS, and Windows
- **Multiple Models** - Support for various Whisper models
- **Audio Device Selection** - Choose your preferred microphone

## Installation

### Download Pre-built Releases

| Platform | Download |
|----------|----------|
| Linux | [voclip-GUI-linux.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |
| macOS | [voclip-GUI-macos.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |
| Windows | [voclip-GUI-windows.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |

Extract the archive and run the executable. The voclip binary is included.

### Install from Source

```bash
pip install PySide6 toml
git clone https://github.com/iceman1010/voclip-GUI.git
cd voclip-GUI/src
python main.py
```

## Usage

### One-Shot Recording

1. Click the **Record** button
2. Speak your message
3. The transcription is automatically copied to your clipboard

### Listen Mode

1. Click **Start Listen Mode** or right-click the tray icon
2. Say your wake word
3. Speak your command - it will be transcribed and copied

### Wake Words

Train custom wake words and commands:
1. Go to the **Wake Words** tab
2. Click **Train Wake Word** or **Train Command**
3. Follow the prompts to record samples
4. Test your new wake word

### Output Modes

- **Clipboard** - Copies transcription to clipboard
- **Type** - Types text directly into the active application

## System Tray

Right-click the tray icon for quick access:
- Show/Hide Window
- Quick Record
- Start/Stop Listen Mode
- Quit

## Settings

| Setting | Description |
|---------|-------------|
| Model | Whisper model to use (default: u3-rt-pro) |
| Timeout | Silence timeout in seconds |
| Delay | Recording delay after pressing record |
| Audio Device | Select your microphone |
| API Key | OpenAI API key for enhanced transcription |

## Requirements

- Python 3.10+
- [voclip](https://github.com/iceman1010/voclip) binary in PATH (or included with GUI)
- PySide6 6.5+
- A working microphone

## Development

```bash
# Clone the repository
git clone https://github.com/iceman1010/voclip-GUI.git
cd voclip-GUI

# Install dependencies
pip install PySide6 toml

# Run from source
cd src
python main.py

# Run tests
python -m pytest tests/

# Type check
python -m mypy src/
```

## Architecture

```
src/
├── main.py              # Entry point, single-instance lock
├── main_window.py       # Main application window
├── system_tray.py       # System tray icon and menu
├── voclip_runner.py     # Subprocess manager for voclip
├── config_manager.py    # Configuration file handling
└── widgets/
    ├── controls_panel.py      # Record button, listen mode toggle
    ├── transcription_panel.py  # Live transcription display
    ├── history_panel.py       # Transcription history
    ├── settings_panel.py      # Configuration UI
    ├── listen_status.py       # Listen mode status window
    └── wakeword_panel.py      # Wake word training UI
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [voclip-GUI Repository](https://github.com/iceman1010/voclip-GUI)
- [voclip](https://github.com/iceman1010/voclip) - The underlying voice-to-clipboard tool
- [Issues](https://github.com/iceman1010/voclip-GUI/issues) - Report bugs or request features
