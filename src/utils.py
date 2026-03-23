"""Utilities for voclip-GUI."""

import os
import platform
import shutil
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "voclip"
CONFIG_FILE = CONFIG_DIR / "config.toml"
ENV_FILE = CONFIG_DIR / ".env"
GUI_CONFIG_FILE = CONFIG_DIR / "gui_config.toml"


def get_platform() -> str:
    """Detect the current platform."""
    system = platform.system()
    if system == "Linux":
        return "wayland" if is_wayland() else "x11"
    return system.lower()


def is_wayland() -> bool:
    """Check if running on Wayland."""
    return "WAYLAND_DISPLAY" in os.environ


def find_voclip() -> str | None:
    """Find voclip binary in PATH."""
    return shutil.which("voclip")


def check_voclip_available() -> tuple[bool, str]:
    """Check if voclip is available and return (available, version_or_error)."""
    voclip_path = find_voclip()
    if not voclip_path:
        return False, "voclip not found in PATH. Please install it first."

    import subprocess

    try:
        result = subprocess.run(
            [voclip_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            return True, version
        return False, f"voclip found but returned error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "voclip --version timed out"
    except Exception as e:
        return False, f"Error running voclip: {e}"
