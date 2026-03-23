"""System tray icon for voclip-GUI."""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class SystemTray(QSystemTrayIcon):
    """System tray icon with menu."""

    show_window_requested = Signal()
    quick_record_requested = Signal()
    toggle_listen_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: Optional[object] = None) -> None:
        super().__init__(parent)
        self._is_listening = False
        self._is_recording = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize tray icon and menu."""
        self._menu = QMenu()

        self._show_action = self._menu.addAction("Show Window")
        self._show_action.triggered.connect(lambda: self.show_window_requested.emit())

        self._menu.addSeparator()

        self._record_action = self._menu.addAction("Quick Record")
        self._record_action.triggered.connect(lambda: self.quick_record_requested.emit())

        self._listen_action = self._menu.addAction("Start Listen Mode")
        self._listen_action.triggered.connect(lambda: self.toggle_listen_requested.emit())

        self._menu.addSeparator()

        self._quit_action = self._menu.addAction("Quit")
        self._quit_action.triggered.connect(lambda: self.quit_requested.emit())

        self.setContextMenu(self._menu)
        self.setToolTip("voclip")

        try:
            from PySide6.QtGui import QIcon
            from PySide6.QtWidgets import QStyle, QApplication

            app = QApplication.instance()
            if app:
                self.setIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        except Exception:
            pass

        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window_requested.emit()

    def set_recording(self, recording: bool) -> None:
        """Update tray state for recording."""
        self._is_recording = recording
        if recording:
            self._record_action.setText("Stop Recording")
            self.setToolTip("voclip - Recording...")
        else:
            self._record_action.setText("Quick Record")
            self._update_tooltip()

    def set_listening(self, listening: bool) -> None:
        """Update tray state for listen mode."""
        self._is_listening = listening
        if listening:
            self._listen_action.setText("Stop Listen Mode")
            self.setToolTip("voclip - Listening for wake words...")
        else:
            self._listen_action.setText("Start Listen Mode")
            self._update_tooltip()

    def _update_tooltip(self) -> None:
        """Update tooltip based on current state."""
        if self._is_listening:
            self.setToolTip("voclip - Listening for wake words...")
        elif self._is_recording:
            self.setToolTip("voclip - Recording...")
        else:
            self.setToolTip("voclip")

    def is_listening(self) -> bool:
        return self._is_listening
