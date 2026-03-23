"""Tests for voclip_runner module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from voclip_runner import VoclipRunner


@pytest.fixture
def runner():
    runner = VoclipRunner()
    return runner


def test_is_running_initial(runner):
    assert not runner.is_running()


def test_parse_authenticating_line(runner):
    runner._in_session = False
    runner._parse_line("Authenticating...")
    assert runner._in_session is False


def test_parse_listening_line(runner):
    runner._in_session = False
    runner._parse_line("Listening... (speak, then wait 3s silence to finish, or Ctrl+C)")
    assert runner._in_session is True


def test_parse_session_started(runner):
    runner._in_session = False
    runner._parse_line("Session started.")
    assert runner._in_session is True


def test_parse_copied_to_clipboard(runner):
    signals = []
    runner.final_transcript.connect(lambda t: signals.append(t))
    runner._in_session = True
    runner._parse_line("Copied to clipboard: Hello world")
    assert signals == ["Hello world"]
    assert runner._in_session is False


def test_parse_error_line(runner):
    signals = []
    runner.error.connect(lambda e: signals.append(e))
    runner._parse_line("Error: Something went wrong")
    assert "Something went wrong" in signals[0]


def test_parse_models_output(runner):
    output = """Available speech models:

  u3-rt-pro          Latest model, best quality (default)
  english            English only

Use --model <name> to select for one run."""
    models = runner._parse_models(output)
    assert "u3-rt-pro" in models
    assert "english" in models


def test_parse_devices_output(runner):
    output = """Audio input devices:

  1: default
  2: pulse
  3: hw:CARD=Card0

Use --audio-device <name> to select one."""
    devices = runner._parse_devices(output)
    assert len(devices) == 3
    assert devices[0]["name"] == "default"


def test_parse_wakewords_output(runner):
    output = """Voice patterns:

  Wake word:
    "Hey Computer"       transcribe (trained)

  Command words:
    "press enter"        key:Return"""
    patterns = runner._parse_wakewords(output)
    assert len(patterns) >= 1
    assert patterns[0]["name"] == "Hey Computer"
