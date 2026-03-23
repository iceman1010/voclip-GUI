"""System tray icon for voclip-GUI."""

from typing import Optional

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class SystemTray(QSystemTrayIcon):
    """System tray icon with menu."""

    def __init__(self, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize tray icon and menu."""
        self._menu = QMenu()

        self._show_action = self._menu.addAction("Show Window")
        self._show_action.triggered.connect(self._on_show)

        self._menu.addSeparator()

        self._record_action = self._menu.addAction("Quick Record")
        self._record_action.triggered.connect(self._on_record)

        self._listen_action = self._menu.addAction("Start Listen Mode")
        self._listen_action.triggered.connect(self._on_listen)

        self._menu.addSeparator()

        self._quit_action = self._menu.addAction("Quit")
        self._quit_action.triggered.connect(self._on_quit)

        self.setContextMenu(self._menu)
        self.setToolTip("voclip")

        self.activated.connect(self._on_activated)

    def _on_show(self) -> None:
        from PySide6.QtCore import Signal

        self.show_window_requested = True

    def _on_record(self) -> None:
        self.quick_record_requested = True

    def _on_listen(self) -> None:
        self.toggle_listen_requested = True

    def _on_quit(self) -> None:
        self.quit_requested = True

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window_requested = True

    def set_recording(self, recording: bool) -> None:
        """Update tray state for recording."""
        if recording:
            self._record_action.setText("Stop Recording")
        else:
            self._record_action.setText("Quick Record")

    def set_listening(self, listening: bool) -> None:
        """Update tray state for listen mode."""
        if listening:
            self._listen_action.setText("Stop Listen Mode")
        else:
            self._listen_action.setText("Start Listen Mode")

    show_window_requested = False
    quick_record_requested = False
    toggle_listen_requested = False
    quit_requested = False
