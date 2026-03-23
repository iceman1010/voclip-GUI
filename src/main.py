"""voclip-GUI entry point."""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QLockFile, QDir

from main_window import MainWindow


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

    window = MainWindow()
    window.show()

    result = app.exec()
    lockfile.unlock()
    return result


if __name__ == "__main__":
    sys.exit(main())
