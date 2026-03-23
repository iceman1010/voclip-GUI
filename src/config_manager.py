"""Configuration manager for voclip-GUI."""

import os
from pathlib import Path
from typing import Any

import toml

from utils import CONFIG_DIR, CONFIG_FILE, ENV_FILE, GUI_CONFIG_FILE


class ConfigManager:
    """Manages voclip configuration files."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._gui_config: dict[str, Any] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load all configuration files."""
        self._config = self._load_toml(CONFIG_FILE)
        self._gui_config = self._load_toml(GUI_CONFIG_FILE)

    def _load_toml(self, path: Path) -> dict[str, Any]:
        """Load a TOML file if it exists."""
        if path.exists():
            try:
                with open(path) as f:
                    return toml.load(f)
            except Exception:
                pass
        return {}

    def _save_toml(self, path: Path, data: dict[str, Any]) -> None:
        """Save data to a TOML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            toml.dump(data, f)

    @property
    def default_model(self) -> str:
        return self._config.get("default_model", "u3-rt-pro")

    @default_model.setter
    def default_model(self, value: str) -> None:
        self._config["default_model"] = value
        self._save_toml(CONFIG_FILE, self._config)

    @property
    def default_timeout(self) -> int:
        return self._config.get("default_timeout", 3)

    @default_timeout.setter
    def default_timeout(self, value: int) -> None:
        self._config["default_timeout"] = value
        self._save_toml(CONFIG_FILE, self._config)

    @property
    def audio_device(self) -> str | None:
        return self._config.get("audio_device")

    @audio_device.setter
    def audio_device(self, value: str) -> None:
        self._config["audio_device"] = value
        self._save_toml(CONFIG_FILE, self._config)

    @property
    def wakeword_sensitivity(self) -> str:
        return self._config.get("wakeword_sensitivity", "medium")

    @wakeword_sensitivity.setter
    def wakeword_sensitivity(self, value: str) -> None:
        self._config["wakeword_sensitivity"] = value
        self._save_toml(CONFIG_FILE, self._config)

    def get_api_key(self) -> str | None:
        """Get API key from environment or .env file."""
        key = os.environ.get("ASSEMBLYAI_API_KEY")
        if key:
            return key

        if ENV_FILE.exists():
            try:
                with open(ENV_FILE) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("ASSEMBLYAI_API_KEY="):
                            return line.split("=", 1)[1].strip().strip('"').strip("'")
            except Exception:
                pass
        return None

    def set_api_key(self, key: str) -> None:
        """Save API key to .env file."""
        ENV_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ENV_FILE, "w") as f:
            f.write(f'ASSEMBLYAI_API_KEY="{key}"\n')
        os.chmod(ENV_FILE, 0o600)

    # GUI-specific settings
    @property
    def start_minimized(self) -> bool:
        return self._gui_config.get("start_minimized", False)

    @start_minimized.setter
    def start_minimized(self, value: bool) -> None:
        self._gui_config["start_minimized"] = value
        self._save_toml(GUI_CONFIG_FILE, self._gui_config)

    @property
    def auto_listen(self) -> bool:
        return self._gui_config.get("auto_listen", False)

    @auto_listen.setter
    def auto_listen(self, value: bool) -> None:
        self._gui_config["auto_listen"] = value
        self._save_toml(GUI_CONFIG_FILE, self._gui_config)

    @property
    def output_mode(self) -> str:
        return self._gui_config.get("output_mode", "clipboard")

    @output_mode.setter
    def output_mode(self, value: str) -> None:
        self._gui_config["output_mode"] = value
        self._save_toml(GUI_CONFIG_FILE, self._gui_config)

    def reload(self) -> None:
        """Reload all configurations from disk."""
        self._load_configs()
