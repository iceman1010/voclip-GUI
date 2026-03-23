"""Transcription history panel."""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HistoryPanel(QWidget):
    """Panel showing transcription history."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._history: list[tuple[str, str]] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.addWidget(QLabel("History"))
        header.addStretch()

        copy_btn = QPushButton("Copy Selected")
        copy_btn.clicked.connect(self._copy_selected)
        header.addWidget(copy_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_history)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._copy_item)
        layout.addWidget(self._list)

    @Slot(str)
    def add_entry(self, text: str) -> None:
        """Add a transcription to history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._history.append((timestamp, text))
        item = QListWidgetItem(f"[{timestamp}] {text[:100]}{'...' if len(text) > 100 else ''}")
        item.setData(1, text)
        self._list.insertItem(0, item)

    def _copy_item(self, item: QListWidgetItem) -> None:
        """Copy item text to clipboard on double-click."""
        text = item.data(1)
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def _copy_selected(self) -> None:
        """Copy selected item to clipboard."""
        current = self._list.currentItem()
        if current:
            self._copy_item(current)

    def clear_history(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._list.clear()
