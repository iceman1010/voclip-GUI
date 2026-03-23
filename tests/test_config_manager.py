"""Tests for config_manager module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import os

from config_manager import ConfigManager


@pytest.fixture
def temp_config_dir(tmp_path):
    return tmp_path


@pytest.fixture
def config_manager(temp_config_dir, monkeypatch):
    monkeypatch.setattr("config_manager.CONFIG_DIR", temp_config_dir)
    monkeypatch.setattr("config_manager.CONFIG_FILE", temp_config_dir / "config.toml")
    monkeypatch.setattr("config_manager.ENV_FILE", temp_config_dir / ".env")
    monkeypatch.setattr("config_manager.GUI_CONFIG_FILE", temp_config_dir / "gui_config.toml")
    monkeypatch.delenv("ASSEMBLYAI_API_KEY", raising=False)
    return ConfigManager()


def test_default_model(config_manager):
    assert config_manager.default_model == "u3-rt-pro"


def test_default_timeout(config_manager):
    assert config_manager.default_timeout == 3


def test_set_default_model(config_manager):
    config_manager.default_model = "english"
    assert config_manager.default_model == "english"


def test_set_default_timeout(config_manager):
    config_manager.default_timeout = 5
    assert config_manager.default_timeout == 5


def test_output_mode_default(config_manager):
    assert config_manager.output_mode == "clipboard"


def test_set_output_mode(config_manager):
    config_manager.output_mode = "type"
    assert config_manager.output_mode == "type"


def test_api_key_not_set(config_manager, monkeypatch):
    monkeypatch.delenv("ASSEMBLYAI_API_KEY", raising=False)
    assert config_manager.get_api_key() is None


def test_set_api_key(config_manager):
    config_manager.set_api_key("test-key-123")
    assert config_manager.get_api_key() == "test-key-123"


def test_gui_settings(config_manager):
    assert config_manager.start_minimized is False
    assert config_manager.auto_listen is False

    config_manager.start_minimized = True
    config_manager.auto_listen = True

    assert config_manager.start_minimized is True
    assert config_manager.auto_listen is True


def test_reload(config_manager):
    config_manager.default_model = "english"
    config_manager.reload()
    assert config_manager.default_model == "english"
