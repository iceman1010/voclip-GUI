# CLAUDE.md

## Project Overview

GUI frontend for [voclip](https://github.com/iceman1010/voclip) — a voice-to-clipboard CLI tool that transcribes speech via AssemblyAI. The GUI wraps the `voclip` binary as a subprocess, parsing its stderr for status updates and transcripts. No modifications to the voclip binary are needed.

**Stack:** Python 3 + PySide6 (Qt 6)
**Platforms:** Linux (X11/Wayland), Windows, macOS

## Commands

```bash
# Run the app
python src/main.py

# Install dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest tests/

# Run a single test
python -m pytest tests/test_voclip_runner.py -v

# Package (PyInstaller)
pyinstaller --onefile --windowed src/main.py
```

## Architecture

This is a **subprocess wrapper GUI** — it does not import or link against voclip. All interaction happens by spawning `voclip` with CLI flags and reading its stderr output line-by-line.

### Key architectural boundaries

- **`voclip_runner.py`** — The only module that spawns voclip subprocesses. All other code communicates through Qt signals emitted by this module (`status_changed`, `partial_transcript`, `final_transcript`, `error`, `process_finished`, `output_line`). Long-running operations (recording, listen mode, training) use `QProcess` or `QThread` to keep the UI responsive.

- **`config_manager.py`** — Reads/writes voclip's own config at `~/.config/voclip/config.toml` and API key from `~/.config/voclip/.env`. GUI-specific settings go in a separate `~/.config/voclip/gui_config.toml`. Uses the `toml` library.

- **`widgets/`** — Each panel is a self-contained `QWidget` that receives data via signals. Panels do not call voclip directly.

- **`system_tray.py`** — Tray icon with quick actions (record, listen, quit). Icon state reflects app state (idle/recording/listening).

### How voclip output is parsed

voclip writes everything to stderr. The runner parses lines matching these patterns:

| stderr pattern | Meaning |
|---|---|
| `Authenticating...` | Auth in progress |
| `Listening... (speak, then wait Xs silence...)` | Recording started |
| `Session started.` | WebSocket session active |
| `Copied to clipboard: <text>` | Final transcript (clipboard mode) |
| `Error: ...` | Error |
| Other lines during active session | Partial transcript updates |

### voclip subprocess interaction

- **One-shot:** `voclip [--model X] [--timeout N] [--delay N] [--type]` — runs and exits
- **Listen mode:** `voclip --listen` — long-running, terminated via SIGTERM
- **Training:** `voclip --train-wakeword --wakeword-name "X" --wakeword-samples N` — interactive, expects Enter keypresses on stdin between samples
- **Queries:** `--list-models`, `--list-devices`, `--list-wakewords`, `--version` — run, capture stdout/stderr, exit

## voclip CLI reference

voclip must be installed and in `$PATH`. Key flags:

- `--timeout <N>` — silence timeout seconds (default 3)
- `--model <MODEL>` — u3-rt-pro, english, multilingual, whisper-rt
- `--delay <N>` — pre-recording delay (default 1)
- `--type` — type at cursor instead of clipboard
- `--listen` — always-on wake word detection mode
- `--train-wakeword / --train-command` — interactive training
- `--wakeword-sensitivity` — low (0.55), medium (0.40), high (0.30), or custom float
- `--list-models / --list-devices / --list-wakewords` — query commands
- `--set-default-model / --set-default-timeout` — persist defaults
- `--audio-device <NAME>` — substring match for input device
- `--update` — self-update

Config file: `~/.config/voclip/config.toml`. API key: env var `ASSEMBLYAI_API_KEY` or `~/.config/voclip/.env`.

## Platform notes

- voclip uses PID lock files — only one recording/listen session at a time
- Linux system tray may need `libappindicator` on some desktops
- Training dialogs must send Enter keypress to voclip's stdin to advance between samples
