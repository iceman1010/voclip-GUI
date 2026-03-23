"""Settings panel for model, timeout, device, and API key configuration."""

from typing import Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSizePolicy,
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
        layout.setContentsMargins(4, 4, 4, 4)

        group = QGroupBox("Settings")
        form = QFormLayout(group)
        form.setSpacing(8)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.DontWrapRows)

        self._model_combo = QComboBox()
        self._model_combo.setMinimumWidth(200)
        self._model_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._model_combo.currentTextChanged.connect(self.model_changed.emit)
        form.addRow("Model:", self._model_combo)

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(1, 30)
        self._timeout_spin.setValue(3)
        self._timeout_spin.setSuffix(" sec")
        self._timeout_spin.valueChanged.connect(lambda v: self.timeout_changed.emit(v))
        form.addRow("Timeout:", self._timeout_spin)

        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(0, 10)
        self._delay_spin.setValue(1)
        self._delay_spin.setSuffix(" sec")
        form.addRow("Delay:", self._delay_spin)

        self._device_combo = QComboBox()
        self._device_combo.setMinimumWidth(200)
        self._device_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._device_combo.currentTextChanged.connect(self.device_changed.emit)
        form.addRow("Audio Device:", self._device_combo)

        api_key_row = QHBoxLayout()
        api_key_row.setContentsMargins(0, 0, 0, 0)
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("AssemblyAI API Key")
        api_key_row.addWidget(self._api_key_edit)

        self._show_key_btn = QPushButton("Show")
        self._show_key_btn.setCheckable(True)
        self._show_key_btn.toggled.connect(self._toggle_key_visibility)
        api_key_row.addWidget(self._show_key_btn)

        self._save_key_btn = QPushButton("Save")
        self._save_key_btn.clicked.connect(self._save_api_key)
        api_key_row.addWidget(self._save_key_btn)
        form.addRow("API Key:", api_key_row)

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
