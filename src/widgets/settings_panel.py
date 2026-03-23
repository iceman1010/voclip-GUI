"""Settings panel for model, timeout, device, and API key configuration."""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SettingsPanel(QWidget):
    """Panel for voclip settings configuration."""

    model_changed = Signal(str)
    timeout_changed = Signal(int)
    device_changed = Signal(str)
    api_key_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Settings")
        group_layout = QVBoxLayout(group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Model:"))
        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(150)
        self._model_combo.currentTextChanged.connect(self.model_changed.emit)
        row1.addWidget(self._model_combo)
        row1.addStretch()
        group_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Timeout:"))
        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(1, 30)
        self._timeout_spin.setValue(3)
        self._timeout_spin.setSuffix(" sec")
        self._timeout_spin.valueChanged.connect(lambda v: self.timeout_changed.emit(v))
        row2.addWidget(self._timeout_spin)
        row2.addStretch()
        group_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Delay:"))
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(0, 10)
        self._delay_spin.setValue(1)
        self._delay_spin.setSuffix(" sec")
        row3.addWidget(self._delay_spin)
        row3.addStretch()
        group_layout.addLayout(row3)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Audio Device:"))
        self._device_combo = QComboBox()
        self._device_combo.setMinimumWidth(200)
        self._device_combo.currentTextChanged.connect(self.device_changed.emit)
        row4.addWidget(self._device_combo)
        row4.addStretch()
        group_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("API Key:"))
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("AssemblyAI API Key")
        row5.addWidget(self._api_key_edit)

        self._show_key_btn = QPushButton("Show")
        self._show_key_btn.setCheckable(True)
        self._show_key_btn.toggled.connect(self._toggle_key_visibility)
        row5.addWidget(self._show_key_btn)

        self._save_key_btn = QPushButton("Save")
        self._save_key_btn.clicked.connect(self._save_api_key)
        row5.addWidget(self._save_key_btn)
        group_layout.addLayout(row5)

        layout.addWidget(group)
        layout.addStretch()

    def _toggle_key_visibility(self, show: bool) -> None:
        """Toggle API key visibility."""
        self._api_key_edit.setEchoMode(
            QLineEdit.EchoMode.Normal if show else QLineEdit.EchoMode.Password
        )
        self._show_key_btn.setText("Hide" if show else "Show")

    def _save_api_key(self) -> None:
        """Emit API key save signal."""
        self.api_key_changed.emit(self._api_key_edit.text())

    def set_models(self, models: list[str]) -> None:
        """Set available models."""
        self._model_combo.clear()
        self._model_combo.addItems(models)

    def set_current_model(self, model: str) -> None:
        """Set current model selection."""
        idx = self._model_combo.findText(model)
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)

    def set_devices(self, devices: list[dict[str, str]]) -> None:
        """Set available audio devices."""
        self._device_combo.clear()
        self._device_combo.addItem("Default", "")
        for device in devices:
            self._device_combo.addItem(device["name"], device["name"])

    def set_current_device(self, device: Optional[str]) -> None:
        """Set current device selection."""
        if device:
            idx = self._device_combo.findText(device)
            if idx >= 0:
                self._device_combo.setCurrentIndex(idx)

    def set_timeout(self, timeout: int) -> None:
        self._timeout_spin.setValue(timeout)

    def set_delay(self, delay: int) -> None:
        self._delay_spin.setValue(delay)

    def set_api_key(self, key: Optional[str]) -> None:
        if key:
            self._api_key_edit.setText(key)

    def get_model(self) -> str:
        return self._model_combo.currentText()

    def get_timeout(self) -> int:
        return self._timeout_spin.value()

    def get_delay(self) -> int:
        return self._delay_spin.value()

    def get_device(self) -> Optional[str]:
        device = self._device_combo.currentData()
        return device if device else None
