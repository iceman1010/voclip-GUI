"""Wake word management panel."""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class TrainingDialog(QDialog):
    """Dialog for training wake words and command words."""

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

        form_layout = QVBoxLayout()

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(name_label))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g., hey voclip")
        name_row.addWidget(self._name_edit)
        form_layout.addLayout(name_row)

        if show_action:
            action_row = QHBoxLayout()
            action_row.addWidget(QLabel("Key:"))
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
            action_row.addWidget(self._key_combo)
            action_row.addStretch()
            form_layout.addLayout(action_row)
        else:
            self._key_combo = None

        samples_row = QHBoxLayout()
        samples_row.addWidget(QLabel("Samples:"))
        self._samples_spin = QSpinBox()
        self._samples_spin.setRange(4, 20)
        self._samples_spin.setValue(8)
        samples_row.addWidget(self._samples_spin)
        samples_row.addStretch()
        form_layout.addLayout(samples_row)

        layout.addLayout(form_layout)

        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

        self._output_label = QLabel("")
        self._output_label.setWordWrap(True)
        layout.addWidget(self._output_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Start | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._start_btn = buttons.button(QDialogButtonBox.StandardButton.Start)
        self._start_btn.setText("Train")
        layout.addWidget(buttons)

    def get_name(self) -> str:
        return self._name_edit.text().strip()

    def get_action(self) -> str:
        if self._key_combo:
            return f"key:{self._key_combo.currentText()}"
        return "transcribe"

    def get_samples(self) -> int:
        return self._samples_spin.value()

    def set_status(self, text: str) -> None:
        self._status_label.setText(text)

    def append_output(self, text: str) -> None:
        current = self._output_label.text()
        self._output_label.setText(current + "\n" + text if current else text)


class WakewordPanel(QWidget):
    """Panel for managing wake words and command words."""

    train_wakeword = Signal(str, int)
    train_command = Signal(str, str, int)
    test_wakewords = Signal()
    remove_wakeword = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Name", "Type", "Action"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self._table)

        buttons = QHBoxLayout()

        self._train_wake_btn = QPushButton("Train Wake Word")
        self._train_wake_btn.clicked.connect(self._on_train_wakeword)
        buttons.addWidget(self._train_wake_btn)

        self._train_cmd_btn = QPushButton("Train Command Word")
        self._train_cmd_btn.clicked.connect(self._on_train_command)
        buttons.addWidget(self._train_cmd_btn)

        self._test_btn = QPushButton("Test All")
        self._test_btn.clicked.connect(self.test_wakewords.emit)
        buttons.addWidget(self._test_btn)

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
        dialog = TrainingDialog("Train Wake Word", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.get_name()
            samples = dialog.get_samples()
            if name:
                self.train_wakeword.emit(name, samples)

    def _on_train_command(self) -> None:
        dialog = TrainingDialog(
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
                self.train_command.emit(name, action, samples)

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
