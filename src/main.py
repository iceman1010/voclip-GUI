"""voclip-GUI entry point."""

import sys
import os
import stat
import shutil
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLockFile, QDir

from main_window import MainWindow


def get_bundle_dir() -> Path:
    """Get the directory where the bundled voclip binary is located."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def ensure_voclip_available() -> bool:
    """Ensure voclip is available in PATH."""
    bundle_dir = get_bundle_dir()

    if sys.platform == "win32":
        voclip_path = bundle_dir / "voclip.exe"
    else:
        voclip_path = bundle_dir / "voclip"

    if voclip_path.exists():
        bundle_path_str = str(voclip_path.parent)
        if bundle_path_str not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bundle_path_str + os.pathsep + os.environ.get("PATH", "")

        if sys.platform != "win32":
            os.chmod(voclip_path, os.stat(voclip_path).st_mode | stat.S_IXUSR)
        return True

    return shutil.which("voclip") is not None


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("voclip")
    app.setApplicationDisplayName("voclip")
    app.setQuitOnLastWindowClosed(False)

    lockfile_path = Path(QDir.tempPath()) / "voclip-gui.lock"
    lockfile = QLockFile(str(lockfile_path))

    if not lockfile.tryLock(100):
        QMessageBox.warning(
            None,
            "voclip-GUI",
            "voclip-GUI is already running.\n\n"
            "If you need to start a new instance, please close the existing one first.",
        )
        return 1

    if not ensure_voclip_available():
        QMessageBox.critical(
            None,
            "voclip-GUI",
            "voclip binary not found!\n\n"
            "Please make sure voclip is installed or the GUI was built correctly.",
        )
        return 1

    window = MainWindow()
    window.show()

    result = app.exec()
    lockfile.unlock()
    return result


if __name__ == "__main__":
    sys.exit(main())
