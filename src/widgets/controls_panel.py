"""Control panel with record button and output mode selector."""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QWidget,
)


class ControlsPanel(QWidget):
    """Panel with record button and output mode selector (one-shot mode only)."""

    record_clicked = Signal(bool)
    listen_clicked = Signal()
    output_mode_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._is_recording = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        layout.addStretch()

        self._record_btn = QPushButton("Record")
        self._record_btn.setCheckable(True)
        self._record_btn.setMinimumWidth(140)
        self._record_btn.setMinimumHeight(44)
        self._record_btn.clicked.connect(self._on_record_clicked)
        layout.addWidget(self._record_btn)

        self._listen_btn = QPushButton("Start Listen Mode")
        self._listen_btn.setMinimumWidth(140)
        self._listen_btn.setMinimumHeight(44)
        self._listen_btn.clicked.connect(self._on_listen_clicked)
        layout.addWidget(self._listen_btn)

        layout.addSpacing(24)

        layout.addWidget(QLabel("Output:"))

        self._clipboard_radio = QRadioButton("Clipboard")
        self._clipboard_radio.setChecked(True)
        self._clipboard_radio.toggled.connect(self._on_output_changed)
        layout.addWidget(self._clipboard_radio)

        self._type_radio = QRadioButton("Type")
        self._type_radio.toggled.connect(self._on_output_changed)
        layout.addWidget(self._type_radio)

        self._output_group = QButtonGroup(self)
        self._output_group.addButton(self._clipboard_radio, 0)
        self._output_group.addButton(self._type_radio, 1)

        layout.addStretch()

    def _on_record_clicked(self, checked: bool) -> None:
        """Handle record button click."""
        self._is_recording = checked
        self._record_btn.setText("Stop" if checked else "Record")
        self.record_clicked.emit(checked)

    def _on_listen_clicked(self) -> None:
        """Handle listen button click."""
        self.listen_clicked.emit()

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
        self._listen_btn.setText("Stop Listen Mode" if listening else "Start Listen Mode")

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
