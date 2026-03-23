# voclip GUI — Implementation Plan

## Overview

A cross-platform graphical user interface for [voclip](https://github.com/iceman1010/voclip), a CLI tool that captures voice from the microphone, streams it to AssemblyAI for real-time transcription, and copies the result to the clipboard or types it via keyboard simulation. The GUI wraps the `voclip` binary as a subprocess, providing a visual interface for all features.

**Technology:** Python 3 + PySide6 (Qt 6)
**Platforms:** Linux, Windows, macOS
**Reference:** [voclip wiki](https://github.com/iceman1010/voclip/wiki)

---

## voclip CLI Reference

### Modes of Operation

1. **One-shot mode** (default) — Run `voclip`, speak, wait for silence timeout, transcript goes to clipboard. Audio feedback: rising beep = recording started, falling beep = done.
2. **Keyboard typing mode** (`--type`) — Same as one-shot but types text at cursor instead of clipboard.
3. **Always-on listen mode** (`--listen`) — Continuously listens for wake words and command words. Wake word triggers transcription + typing. Command word triggers key press. ~2% CPU. Runs until Ctrl+C.

### Configuration

- **Config file:** `~/.config/voclip/config.toml`
- **Config format:**
  ```toml
  default_model = "u3-rt-pro"
  default_timeout = 5
  wakeword_sensitivity = "medium"

  [[voice_pattern]]
  name = "Computer"
  action = "transcribe"

  [[voice_pattern]]
  name = "press enter"
  action = "key:Return"
  ```
- **Settings priority:** CLI flags > config file > built-in defaults
- **API key locations:** Environment variable `ASSEMBLYAI_API_KEY`, or `~/.config/voclip/.env`
- **Voice patterns:** Stored as `.rpw` files in `~/.config/voclip/voice_patterns/`

### Wake Word System

- Uses **rustpotter** — local detection, no cloud needed
- Training: Record N samples (default 8), speak clearly, vary tone between samples
- **Sensitivity presets:**
  - `low` (0.55) — fewer false positives
  - `medium` (0.40) — balanced default
  - `high` (0.30) — more detections, possible false triggers
  - Custom float (0.0–1.0) — lower = more sensitive
- **Supported command keys:** Return, BackSpace, Tab, Escape, Space, Delete, arrow keys, pagination keys
- Detection uses Dynamic Time Warping on MFCC features, <1ms per 30ms frame, <100KB per model

### Speech Models

Available: `u3-rt-pro`, `english`, `multilingual`, `whisper-rt`

### Platform Dependencies

| Platform | Audio | Clipboard | Keyboard Typing |
|----------|-------|-----------|-----------------|
| Linux (X11) | ALSA | xclip/xsel | xdotool/enigo |
| Linux (Wayland) | ALSA | wl-clipboard | wtype/ydotool/enigo |
| macOS | CoreAudio | pbcopy | enigo |
| Windows | WASAPI | Native API | enigo |

- voclip uses PID lock files to prevent multiple simultaneous instances
- Warns at startup if clipboard/keyboard tools are missing
- Auto-detects X11 vs Wayland via `WAYLAND_DISPLAY` / `DISPLAY` env vars

---

## Architecture

### Core Design Principles

- **Subprocess wrapper** — The GUI invokes `voclip` as a child process, parsing its stderr output for status updates and partial transcripts. No modification to the voclip binary is needed.
- **Non-blocking UI** — All voclip invocations run in background threads (via `QThread` or `QProcess`) so the GUI never freezes.
- **System tray integration** — The app can minimize to the system tray for always-on listen mode.
- **Config file aware** — Reads and writes `~/.config/voclip/config.toml` for persistent settings, same as the CLI.

### Project Structure

```
voclip-GUI/
├── PLAN.md
├── requirements.txt              # PySide6, toml
├── setup.py / pyproject.toml     # Packaging config
├── src/
│   ├── main.py                   # Entry point, app initialization
│   ├── main_window.py            # Main application window
│   ├── voclip_runner.py          # Subprocess manager for voclip
│   ├── config_manager.py         # Read/write voclip config.toml
│   ├── widgets/
│   │   ├── transcription_panel.py  # Live transcription display
│   │   ├── controls_panel.py       # Record button, mode selector
│   │   ├── settings_panel.py       # Model, timeout, device, API key
│   │   ├── wakeword_panel.py       # Wake word / command word management
│   │   └── history_panel.py        # Transcription history
│   ├── system_tray.py            # System tray icon and menu
│   ├── resources/                # Icons, assets
│   │   ├── icon.png
│   │   ├── mic_on.png
│   │   └── mic_off.png
│   └── utils.py                  # Helpers (platform detection, etc.)
├── packaging/
│   ├── build_linux.sh            # PyInstaller / AppImage script
│   ├── build_macos.sh            # PyInstaller / .app bundle script
│   └── build_windows.bat         # PyInstaller .exe script
└── tests/
    ├── test_config_manager.py
    └── test_voclip_runner.py
```

---

## GUI Layout

### Main Window

```
┌─────────────────────────────────────────────────────────┐
│  voclip                                        [_][□][X]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │          Live Transcription Area                   │  │
│  │                                                   │  │
│  │  "Hello, this is a test of voice to clipboard."   │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Status: Ready  |  Model: u3-rt-pro  | Timeout: 3│  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│       ┌──────────┐   ┌────────────┐  ┌──────────┐      │
│       │  ● Record │   │ ◉ Listen   │  │ ⚙ Settings│     │
│       └──────────┘   └────────────┘  └──────────┘      │
│                                                         │
│  Output: ( ) Clipboard  (●) Type                        │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  History  │  Wake Words  │  Settings                    │
├───────────┴──────────────┴──────────────────────────────┤
│  (Tab content area — see below)                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Tab: History

A scrollable list of past transcriptions from the current session:
- Timestamp
- Transcribed text
- Click to copy to clipboard
- Clear history button

### Tab: Wake Words

Manage trained voice patterns:

```
┌─────────────────────────────────────────────────────────┐
│  Wake Words & Commands                                  │
├─────────────────────────────────────────────────────────┤
│  Name              │ Type     │ Action       │          │
│  ─────────────────────────────────────────────────────  │
│  hey voclip        │ Wake     │ Transcribe   │ [Remove] │
│  press enter       │ Command  │ key:Return   │ [Remove] │
│  go back           │ Command  │ key:BackSpace│ [Remove] │
├─────────────────────────────────────────────────────────┤
│  [Train Wake Word]    [Train Command Word]   [Test All] │
│                                                         │
│  Sensitivity: [low | ●medium | high]   Samples: [8]     │
└─────────────────────────────────────────────────────────┘
```

- **Train Wake Word** button: Opens a dialog asking for the name, then runs `voclip --train-wakeword --wakeword-name "<name>" --wakeword-samples <N>` and displays the training progress from stderr.
- **Train Command Word** button: Opens a dialog for name + action (key picker dropdown with: Return, BackSpace, Tab, Escape, Space, Delete, Up, Down, Left, Right, PageUp, PageDown), then runs `voclip --train-command --command-name "<name>" --command-action "key:<key>"`.
- **Test All** button: Runs `voclip --test-wakeword` and streams output in a dialog showing detection type, name, and confidence score in real time.
- **Remove** button: Runs `voclip --remove-wakeword "<name>"` with confirmation dialog.
- List populated by running `voclip --list-wakewords` and parsing the output.
- **Training dialog flow:** Shows instructions ("Speak clearly, vary your tone between samples"), a progress indicator (sample N of M), and real-time feedback from voclip stderr. User presses Enter in the dialog to start each sample (maps to Enter keypress that voclip expects on stdin).

### Tab: Settings

```
┌─────────────────────────────────────────────────────────┐
│  Settings                                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Speech Model:    [ u3-rt-pro      ▼ ]  [Set Default]   │
│                                                         │
│  Silence Timeout: [ 3        ] sec      [Set Default]   │
│                                                         │
│  Delay:           [ 1        ] sec                      │
│                                                         │
│  Audio Device:    [ Default        ▼ ]                  │
│                   (populated from --list-devices)        │
│                                                         │
│  API Key:         [ ●●●●●●●●●●●●●●●● ] [Show] [Save]  │
│                   (reads/writes ASSEMBLYAI_API_KEY)      │
│                                                         │
│  ☐ Start minimized to tray                              │
│  ☐ Start listen mode on launch                          │
│                                                         │
│  voclip version: 1.x.x          [Check for Updates]    │
└─────────────────────────────────────────────────────────┘
```

- **Speech Model dropdown**: Populated by running `voclip --list-models` at startup.
- **Audio Device dropdown**: Populated by running `voclip --list-devices` at startup.
- **Set Default buttons**: Run `voclip --set-default-model <model>` and `voclip --set-default-timeout <sec>`.
- **API Key**: Read from environment / `.env` file. Save writes to `~/.config/voclip/.env`.
- **Check for Updates**: Runs `voclip --update`.

---

## Component Details

### 1. `voclip_runner.py` — Subprocess Manager

The heart of the GUI. Manages all interaction with the voclip binary.

**Responsibilities:**
- Start voclip with the appropriate arguments as a subprocess
- Capture stderr line-by-line in real time (voclip writes status and transcripts to stderr)
- Parse output to detect: authentication status, recording started, partial transcripts, final transcript, errors
- Emit Qt signals for each event so the UI can react
- Support cancellation (send SIGTERM / terminate process)
- Track whether a process is currently running

**Key signals (Qt):**
- `status_changed(str)` — "Authenticating...", "Listening...", "Session started.", etc.
- `partial_transcript(str)` — Real-time partial text as user speaks
- `final_transcript(str)` — Completed transcription text
- `error(str)` — Error messages
- `process_finished(int)` — Exit code when voclip exits
- `output_line(str)` — Raw output line (for training/testing modes)

**Methods:**
- `start_recording(model, timeout, delay, output_mode)` — One-shot transcription
- `start_listening(sensitivity)` — Always-on listen mode
- `train_wakeword(name, samples, sensitivity)` — Wake word training
- `train_command(name, action, samples, sensitivity)` — Command word training
- `test_wakewords()` — Test detection
- `list_wakewords()` → `str` — Get list of patterns
- `list_models()` → `list[str]` — Get available models
- `list_devices()` → `list[str]` — Get audio devices
- `check_update()` — Run self-update
- `stop()` — Kill running process

### 2. `config_manager.py` — Configuration

**Responsibilities:**
- Read `~/.config/voclip/config.toml` (using Python `toml` library)
- Provide current defaults (model, timeout, device, etc.)
- Read API key from environment or `.env` file
- Save API key to `~/.config/voclip/.env`
- Store GUI-specific settings (start minimized, auto-listen) in a separate `~/.config/voclip/gui_config.toml`

### 3. `main_window.py` — Main Window

**Responsibilities:**
- Compose all panels/tabs into the main layout
- Connect signals from `voclip_runner` to UI updates
- Handle window close → minimize to tray (if configured)
- Keyboard shortcut for quick record (e.g., Ctrl+R)

### 4. `system_tray.py` — System Tray

**Menu items:**
- Show/Hide window
- Quick Record (one-shot)
- Start/Stop Listen mode
- Quit

**Tray icon states:**
- Idle (default icon)
- Recording (red/active icon)
- Listening (pulsing/different color icon)

### 5. Widget Panels

Each panel is a self-contained QWidget:

- **`transcription_panel.py`** — QTextEdit (read-only) showing live and final transcripts. Clears between sessions. Copy button.
- **`controls_panel.py`** — Record button (toggle), Listen button (toggle), output mode radio buttons (clipboard/type).
- **`settings_panel.py`** — Form layout with dropdowns, spinboxes, and the API key field.
- **`wakeword_panel.py`** — Table of patterns + training buttons. Training dialogs show real-time subprocess output.
- **`history_panel.py`** — QListWidget of past transcriptions. Click to copy.

---

## Implementation Phases

### Phase 1: Foundation
1. Set up project structure, `pyproject.toml`, `requirements.txt`
2. Implement `voclip_runner.py` — subprocess execution with signal-based output parsing
3. Implement `config_manager.py` — read config and API key
4. Create `main_window.py` skeleton with placeholder panels
5. Basic one-shot recording: Record button → run voclip → display transcript

### Phase 2: Core UI
6. Implement `transcription_panel.py` with live partial transcript updates
7. Implement `controls_panel.py` with Record/Stop button and output mode selector
8. Implement `settings_panel.py` — model dropdown (from `--list-models`), timeout spinner, device dropdown (from `--list-devices`), delay spinner
9. Implement status bar showing current state
10. Add session history panel

### Phase 3: Wake Words
11. Implement `wakeword_panel.py` — list patterns from `--list-wakewords`
12. Train wake word dialog — runs `--train-wakeword` and streams progress
13. Train command word dialog — name + key picker + runs `--train-command`
14. Test all button — runs `--test-wakeword` and streams output
15. Remove button — runs `--remove-wakeword`

### Phase 4: Listen Mode & System Tray
16. Listen mode toggle — runs `voclip --listen` as long-running subprocess
17. System tray icon with menu (show/hide, quick record, listen toggle, quit)
18. Minimize to tray on close (configurable)
19. Tray icon state changes (idle/recording/listening)

### Phase 5: Settings & Polish
20. API key management (show/hide, save to .env)
21. Set default model/timeout buttons
22. Check for updates button
23. GUI-specific settings (start minimized, auto-listen)
24. Keyboard shortcuts (Ctrl+R to record)
25. Error handling and user-friendly error dialogs
26. Application icon

### Phase 6: Packaging
27. PyInstaller spec files for Linux, macOS, Windows
28. Test on each platform
29. AppImage for Linux (optional)
30. .dmg for macOS (optional)
31. Installer for Windows (optional)

---

## Dependencies

```
PySide6>=6.5        # Qt 6 bindings (LGPL)
toml>=0.10          # Config file parsing
```

No other Python dependencies needed. The `voclip` binary must be installed and in `$PATH`.

---

## Subprocess Output Parsing

voclip writes all UI output to stderr. Key patterns to parse:

| stderr output | GUI event |
|---|---|
| `Authenticating...` | Status: authenticating |
| `Listening... (speak, then wait Xs silence to finish, or Ctrl+C)` | Status: recording |
| `Session started.` | Status: session active |
| Lines that aren't status messages (during session) | Partial transcript updates |
| `Copied to clipboard: <text>` | Final transcript → clipboard mode |
| Lines after session ends | Final transcript |
| `Error: ...` / `error: ...` | Error event |
| `voclip X.Y.Z` (from --version) | Version display |

The exact parsing logic will need refinement based on testing, but the general approach is line-by-line stderr reading with pattern matching.

---

## Platform Considerations

- **Linux**: PySide6 works on X11 and Wayland. System tray may need `libappindicator` on some desktops.
- **macOS**: PySide6 provides native macOS look. App may need to be signed for distribution.
- **Windows**: PySide6 works natively. System tray fully supported.
- **voclip binary**: Must be installed separately. The GUI should show a helpful error if `voclip` is not found in `$PATH`, with a link to installation instructions.
- **PID lock files**: voclip uses lock files to prevent multiple instances. The GUI should be aware of this — only one recording/listen session at a time. If a stale lock is detected, inform the user.
- **Startup checks**: On launch, verify voclip is in PATH, check for missing platform tools (clipboard/keyboard), and display warnings if needed.

---

## Verification & Testing

1. **Unit tests**: `test_config_manager.py` (config reading/writing), `test_voclip_runner.py` (output parsing logic with mock subprocess)
2. **Manual testing**:
   - One-shot record → verify transcript appears in GUI and clipboard
   - Switch output mode to "type" → verify text is typed
   - Change model/timeout → verify passed to voclip correctly
   - Train a wake word → verify dialog shows training progress
   - List/remove wake words → verify table updates
   - Listen mode → verify long-running process, tray icon changes
   - System tray → verify minimize/restore, quick actions
   - Close and reopen → verify settings persist
3. **Cross-platform**: Test on Linux (X11 + Wayland), macOS, Windows
