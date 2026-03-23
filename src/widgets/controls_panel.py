"""Control panel with record/listen buttons."""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


class ControlsPanel(QWidget):
    """Panel with record, listen buttons and output mode selector."""

    record_clicked = Signal(bool)
    listen_clicked = Signal(bool)
    output_mode_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._is_recording = False
        self._is_listening = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        buttons_layout = QHBoxLayout()

        self._record_btn = QPushButton("Record")
        self._record_btn.setCheckable(True)
        self._record_btn.setMinimumWidth(100)
        self._record_btn.clicked.connect(self._on_record_clicked)
        buttons_layout.addWidget(self._record_btn)

        self._listen_btn = QPushButton("Listen")
        self._listen_btn.setCheckable(True)
        self._listen_btn.setMinimumWidth(100)
        self._listen_btn.clicked.connect(self._on_listen_clicked)
        buttons_layout.addWidget(self._listen_btn)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output:"))

        self._clipboard_radio = QRadioButton("Clipboard")
        self._clipboard_radio.setChecked(True)
        self._clipboard_radio.toggled.connect(self._on_output_changed)
        output_layout.addWidget(self._clipboard_radio)

        self._type_radio = QRadioButton("Type")
        self._type_radio.toggled.connect(self._on_output_changed)
        output_layout.addWidget(self._type_radio)

        self._output_group = QButtonGroup(self)
        self._output_group.addButton(self._clipboard_radio, 0)
        self._output_group.addButton(self._type_radio, 1)

        output_layout.addStretch()
        layout.addLayout(output_layout)

    def _on_record_clicked(self, checked: bool) -> None:
        """Handle record button click."""
        if checked and self._is_listening:
            self._listen_btn.setChecked(False)
        self._is_recording = checked
        self._record_btn.setText("Stop" if checked else "Record")
        self.record_clicked.emit(checked)

    def _on_listen_clicked(self, checked: bool) -> None:
        """Handle listen button click."""
        if checked and self._is_recording:
            self._record_btn.setChecked(False)
        self._is_listening = checked
        self._listen_btn.setText("Stop Listening" if checked else "Listen")
        self.listen_clicked.emit(checked)

    def _on_output_changed(self) -> None:
        """Handle output mode change."""
        if self._clipboard_radio.isChecked():
            self.output_mode_changed.emit("clipboard")
        else:
            self.output_mode_changed.emit("type")

    def set_recording(self, recording: bool) -> None:
        """Set recording state externally."""
        self._is_recording = recording
        self._record_btn.setChecked(recording)
        self._record_btn.setText("Stop" if recording else "Record")

    def set_listening(self, listening: bool) -> None:
        """Set listening state externally."""
        self._is_listening = listening
        self._listen_btn.setChecked(listening)
        self._listen_btn.setText("Stop Listening" if listening else "Listen")

    def set_output_mode(self, mode: str) -> None:
        """Set output mode."""
        if mode == "type":
            self._type_radio.setChecked(True)
        else:
            self._clipboard_radio.setChecked(True)

    def get_output_mode(self) -> str:
        """Get current output mode."""
        return "type" if self._type_radio.isChecked() else "clipboard"

    def is_recording(self) -> bool:
        return self._is_recording

    def is_listening(self) -> bool:
        return self._is_listening
