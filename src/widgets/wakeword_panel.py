"""Wake word management panel."""

import re
from typing import Optional

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TrainingConfigDialog(QDialog):
    """Dialog to configure training parameters before starting."""

    def __init__(
        self,
        title: str,
        name_label: str = "Name:",
        show_action: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self._setup_ui(name_label, show_action)

    def _setup_ui(self, name_label: str, show_action: bool) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(8)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g., hey voclip")
        form.addRow(name_label, self._name_edit)

        if show_action:
            self._key_combo = QComboBox()
            self._key_combo.addItems(
                [
                    "Return",
                    "BackSpace",
                    "Tab",
                    "Escape",
                    "Space",
                    "Delete",
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "PageUp",
                    "PageDown",
                ]
            )
            form.addRow("Key:", self._key_combo)
        else:
            self._key_combo = None

        self._samples_spin = QSpinBox()
        self._samples_spin.setRange(4, 20)
        self._samples_spin.setValue(8)
        form.addRow("Samples:", self._samples_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self) -> str:
        return self._name_edit.text().strip()

    def get_action(self) -> str:
        if self._key_combo:
            return f"key:{self._key_combo.currentText()}"
        return "transcribe"

    def get_samples(self) -> int:
        return self._samples_spin.value()


class TrainingProgressDialog(QDialog):
    """Dialog showing real-time training progress with Enter-to-continue."""

    send_input = Signal(str)

    def __init__(
        self,
        name: str,
        samples: int,
        is_command: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._name = name
        self._total_samples = samples
        self._is_command = is_command
        self._completed = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle(f"Training: {self._name}")
        self.setMinimumSize(500, 350)

        layout = QVBoxLayout(self)

        self._instruction_label = QLabel(
            "Speak clearly and vary your tone between samples.\n"
            "Press 'Record Sample' or Enter when ready to record each sample."
        )
        self._instruction_label.setWordWrap(True)
        layout.addWidget(self._instruction_label)

        self._progress_label = QLabel(f"Progress: 0 / {self._total_samples} samples")
        self._progress_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self._progress_label)

        self._status_label = QLabel("Starting training...")
        layout.addWidget(self._status_label)

        self._output_text = QPlainTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setMaximumBlockCount(100)
        layout.addWidget(self._output_text)

        btn_layout = QHBoxLayout()

        self._record_btn = QPushButton("Record Sample")
        self._record_btn.setDefault(True)
        self._record_btn.clicked.connect(self._on_record_clicked)
        btn_layout.addWidget(self._record_btn)

        self._cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self._cancel_btn)
        self._cancel_btn.clicked.connect(self.reject)

        layout.addLayout(btn_layout)

    def keyPressEvent(self, event) -> None:
        if event.key() == 0x01000005 or event.key() == 0x01000004:
            if not self._completed:
                self._on_record_clicked()
            return
        super().keyPressEvent(event)

    def _on_record_clicked(self) -> None:
        if not self._completed:
            self.send_input.emit("\n")
            self._record_btn.setEnabled(False)
            QTimer.singleShot(500, lambda: self._record_btn.setEnabled(True))

    def append_output(self, line: str) -> None:
        self._output_text.appendPlainText(line)
        self._update_progress_from_output(line)

    def _update_progress_from_output(self, line: str) -> None:
        line_lower = line.lower()
        if "sample" in line_lower:
            match = re.search(r"sample\s*(\d+)", line_lower)
            if match:
                current = int(match.group(1))
                self._progress_label.setText(f"Progress: {current} / {self._total_samples} samples")
        if "complete" in line_lower or "saved" in line_lower or "done" in line_lower:
            self._completed = True
            self._status_label.setText("Training complete!")
            self._record_btn.setText("Close")
            self._record_btn.clicked.disconnect()
            self._record_btn.clicked.connect(self.accept)

    def set_status(self, status: str) -> None:
        self._status_label.setText(status)


class TestWakewordsDialog(QDialog):
    """Dialog showing real-time wake word detection testing."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("Test Wake Words")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)

        self._instruction_label = QLabel(
            "Speak your trained wake words or command words.\nDetected patterns will appear below."
        )
        self._instruction_label.setWordWrap(True)
        layout.addWidget(self._instruction_label)

        self._output_text = QPlainTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setMaximumBlockCount(100)
        layout.addWidget(self._output_text)

        self._close_btn = QPushButton("Close")
        self._close_btn.clicked.connect(self.reject)
        layout.addWidget(self._close_btn)

    def append_output(self, line: str) -> None:
        self._output_text.appendPlainText(line)


class WakewordPanel(QWidget):
    """Panel for managing wake words and command words."""

    train_wakeword_requested = Signal(str, int)
    train_command_requested = Signal(str, str, int)
    test_wakewords = Signal()
    remove_wakeword = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 4)
        layout.setSpacing(6)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Name", "Type", "Action"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._table)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)

        self._train_wake_btn = QPushButton("Train Wake Word")
        self._train_wake_btn.clicked.connect(self._on_train_wakeword)
        buttons.addWidget(self._train_wake_btn)

        self._train_cmd_btn = QPushButton("Train Command Word")
        self._train_cmd_btn.clicked.connect(self._on_train_command)
        buttons.addWidget(self._train_cmd_btn)

        self._test_btn = QPushButton("Test All")
        self._test_btn.clicked.connect(self.test_wakewords.emit)
        buttons.addWidget(self._test_btn)

        buttons.addStretch()

        self._remove_btn = QPushButton("Remove")
        self._remove_btn.clicked.connect(self._on_remove)
        buttons.addWidget(self._remove_btn)

        layout.addLayout(buttons)

    def set_patterns(self, patterns: list[dict[str, str]]) -> None:
        """Update the table with voice patterns."""
        self._table.setRowCount(len(patterns))
        for i, pattern in enumerate(patterns):
            self._table.setItem(i, 0, QTableWidgetItem(pattern.get("name", "")))
            self._table.setItem(i, 1, QTableWidgetItem(pattern.get("type", "")))
            self._table.setItem(i, 2, QTableWidgetItem(pattern.get("action", "")))

    def _on_train_wakeword(self) -> None:
        dialog = TrainingConfigDialog("Train Wake Word", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            samples = dialog.get_samples()
            if name:
                self.train_wakeword_requested.emit(name, samples)

    def _on_train_command(self) -> None:
        dialog = TrainingConfigDialog(
            "Train Command Word",
            name_label="Command Name:",
            show_action=True,
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            action = dialog.get_action()
            samples = dialog.get_samples()
            if name:
                self.train_command_requested.emit(name, action, samples)

    def _on_remove(self) -> None:
        selected = self._table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        name_item = self._table.item(row, 0)
        if not name_item:
            return

        name = name_item.text()
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove voice pattern '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.remove_wakeword.emit(name)
