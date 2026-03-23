"""Transcription display panel."""

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TranscriptionPanel(QWidget):
    """Panel for displaying live and final transcripts."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_transcript = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(4)

        header = QHBoxLayout()
        label = QLabel("Transcription")
        font = label.font()
        font.setBold(True)
        label.setFont(font)
        header.addWidget(label)
        header.addStretch()

        self._copy_btn = QPushButton("Copy")
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        header.addWidget(self._copy_btn)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self.clear)
        header.addWidget(self._clear_btn)

        layout.addLayout(header)

        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setPlaceholderText("Transcription will appear here...")
        self._text_edit.setMinimumHeight(80)
        self._text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self._text_edit)

    @Slot(str)
    def update_partial(self, text: str) -> None:
        """Update with partial transcript."""
        self._current_transcript = text
        self._text_edit.setPlainText(text)

    @Slot(str)
    def update_final(self, text: str) -> None:
        """Update with final transcript."""
        self._current_transcript = text
        self._text_edit.setPlainText(text)

    def clear(self) -> None:
        """Clear the transcription."""
        self._current_transcript = ""
        self._text_edit.clear()

    def _copy_to_clipboard(self) -> None:
        """Copy current transcript to clipboard."""
        if self._current_transcript:
            clipboard = QApplication.clipboard()
            clipboard.setText(self._current_transcript)
