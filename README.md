# voclip-GUI

![voclip-GUI icon](https://raw.githubusercontent.com/iceman1010/voclip-GUI/master/favicon/android-chrome-192x192.png)

**Voice to clipboard — with a modern GUI.**

A GUI frontend for [voclip](https://github.com/iceman1010/voclip) - speaks your words and pastes them at your cursor.

## Features

- **One-Shot Recording** - Press record, speak, and get your words transcribed instantly
- **Listen Mode** - Always-on background mode with wake word detection
- **Wake Words** - Train custom wake words and voice commands
- **Clipboard & Type** - Output to clipboard or type directly into any application
- **System Tray** - Runs quietly in the background with quick access menu
- **Cross-Platform** - Available for Linux, macOS, and Windows

## Quick Start

```bash
# Install
pip install PySide6 toml
git clone https://github.com/iceman1010/voclip-GUI.git
cd voclip-GUI/src

# Run
python main.py
```

## Installation

### Download Pre-built Releases

| Platform | Download |
|----------|----------|
| Linux | [voclip-GUI-linux.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |
| macOS | [voclip-GUI-macos.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |
| Windows | [voclip-GUI-windows.zip](https://github.com/iceman1010/voclip-GUI/releases/latest) |

Extract the archive and run the executable. The voclip binary is included.

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

## System Tray

Right-click the tray icon for quick access:
- Show/Hide Window
- Quick Record
- Start/Stop Listen Mode
- Quit

## Wiki

For more documentation, see the [wiki](https://github.com/iceman1010/voclip-GUI/wiki):
- [Installation](https://github.com/iceman1010/voclip-GUI/wiki/Installation)
- [Quick Start](https://github.com/iceman1010/voclip-GUI/wiki/Quick-Start)
- [Features](https://github.com/iceman1010/voclip-GUI/wiki/Features)
- [Settings](https://github.com/iceman1010/voclip-GUI/wiki/Settings)
- [Troubleshooting](https://github.com/iceman1010/voclip-GUI/wiki/Troubleshooting)

## Requirements

- Python 3.10+
- [voclip](https://github.com/iceman1010/voclip) binary in PATH (or included with GUI)
- PySide6 6.5+
- A working microphone

## License

MIT License
