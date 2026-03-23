"""Small status window for listen mode."""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ListenStatusWidget(QWidget):
    """Compact widget showing listen mode status."""

    stop_clicked = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.setFixedSize(280, 80)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        header = QHBoxLayout()

        self._status_indicator = QLabel("●")
        self._status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
        header.addWidget(self._status_indicator)

        self._status_label = QLabel("Listening for wake words...")
        self._status_label.setStyleSheet("font-weight: bold;")
        header.addWidget(self._status_label, 1)

        layout.addLayout(header)

        self._detection_label = QLabel("")
        self._detection_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self._detection_label)

        self._stop_btn = QPushButton("Stop Listen Mode")
        self._stop_btn.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(self._stop_btn)

        self.setWindowFlags(self.windowFlags() | 0x00000800)
        self.setWindowTitle("voclip - Listen Mode")

    def set_detecting(self, is_detecting: bool) -> None:
        if is_detecting:
            self._status_indicator.setStyleSheet("color: #FF9800; font-size: 16px;")
            self._status_label.setText("Transcribing...")
        else:
            self._status_indicator.setStyleSheet("color: #4CAF50; font-size: 16px;")
            self._status_label.setText("Listening for wake words...")

    def set_detection_text(self, text: str) -> None:
        self._detection_label.setText(text)
