# AGENTS.md

Guidelines for AI coding agents working in the voclip-GUI codebase.

## Project

GUI frontend for [voclip](https://github.com/iceman1010/voclip) — wraps the `voclip` binary as a subprocess. See [PLAN.md](PLAN.md) for full architecture, CLI reference, and component details.

**Stack:** Python 3 + PySide6 (Qt 6)

## Commands

```bash
python src/main.py                              # Run the app
python -m pytest tests/                         # Run all tests
python -m pytest tests/test_voclip_runner.py -v # Single test file
python -m pytest tests/test_voclip_runner.py::test_start_recording -v  # Single test
python -m mypy src/                             # Type checking
python -m ruff check src/                       # Linting
```

## Code Style

- 4 spaces, max 100 chars line length
- Type hints on all functions
- Google-style docstrings
- snake_case for functions/variables, PascalCase for classes
- Imports: stdlib → third-party → local (alphabetical within each group)

## Architecture

- All voclip calls go through `voclip_runner.py` — never spawn subprocess directly from UI
- Use Qt signals for async operations
- Config files in `~/.config/voclip/`

## Key Points

1. Never block the UI thread
2. Only one voclip instance at a time (uses PID lock files)
3. Parse voclip stderr for status/transcripts
4. Check voclip is in PATH at startup
