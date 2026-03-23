"""Main application window for voclip-GUI."""

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config_manager import ConfigManager
from voclip_runner import VoclipRunner
from widgets.controls_panel import ControlsPanel
from widgets.history_panel import HistoryPanel
from widgets.settings_panel import SettingsPanel
from widgets.transcription_panel import TranscriptionPanel
from widgets.wakeword_panel import WakewordPanel


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._config = ConfigManager()
        self._runner = VoclipRunner(self)
        self._setup_ui()
        self._connect_signals()
        self._load_settings()
        self._check_voclip()

    def _setup_ui(self) -> None:
        """Initialize UI components."""
        self.setWindowTitle("voclip")
        self.setMinimumSize(500, 400)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self._transcription_panel = TranscriptionPanel()
        layout.addWidget(self._transcription_panel)

        status_row = QHBoxLayout()
        self._status_label = QLabel("Ready")
        status_row.addWidget(self._status_label)
        status_row.addStretch()
        self._model_label = QLabel()
        status_row.addWidget(self._model_label)
        layout.addLayout(status_row)

        self._controls_panel = ControlsPanel()
        layout.addWidget(self._controls_panel)

        self._tabs = QTabWidget()

        self._history_panel = HistoryPanel()
        self._tabs.addTab(self._history_panel, "History")

        self._wakeword_panel = WakewordPanel()
        self._tabs.addTab(self._wakeword_panel, "Wake Words")

        self._settings_panel = SettingsPanel()
        self._tabs.addTab(self._settings_panel, "Settings")

        layout.addWidget(self._tabs)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

    def _connect_signals(self) -> None:
        """Connect all signals."""
        self._runner.status_changed.connect(self._on_status_changed)
        self._runner.partial_transcript.connect(self._transcription_panel.update_partial)
        self._runner.final_transcript.connect(self._on_final_transcript)
        self._runner.error.connect(self._on_error)
        self._runner.process_finished.connect(self._on_process_finished)
        self._runner.models_listed.connect(self._on_models_listed)
        self._runner.devices_listed.connect(self._on_devices_listed)
        self._runner.wakewords_listed.connect(self._wakeword_panel.set_patterns)

        self._controls_panel.record_clicked.connect(self._on_record_clicked)
        self._controls_panel.listen_clicked.connect(self._on_listen_clicked)
        self._controls_panel.output_mode_changed.connect(self._on_output_mode_changed)

        self._settings_panel.api_key_changed.connect(self._on_api_key_changed)

        self._wakeword_panel.train_wakeword.connect(self._on_train_wakeword)
        self._wakeword_panel.train_command.connect(self._on_train_command)
        self._wakeword_panel.test_wakewords.connect(self._on_test_wakewords)
        self._wakeword_panel.remove_wakeword.connect(self._on_remove_wakeword)

    def _load_settings(self) -> None:
        """Load settings from config."""
        self._runner.list_models()
        self._runner.list_devices()
        self._runner.list_wakewords()

        self._settings_panel.set_timeout(self._config.default_timeout)
        self._settings_panel.set_api_key(self._config.get_api_key())
        self._controls_panel.set_output_mode(self._config.output_mode)

    def _check_voclip(self) -> None:
        """Check if voclip is available."""
        from utils import check_voclip_available

        available, message = check_voclip_available()
        if not available:
            QMessageBox.critical(self, "Error", message)
        else:
            self._status_bar.showMessage(message)

    @Slot(str)
    def _on_status_changed(self, status: str) -> None:
        self._status_label.setText(status)
        self._status_bar.showMessage(status)

    @Slot(str)
    def _on_final_transcript(self, text: str) -> None:
        self._transcription_panel.update_final(text)
        self._history_panel.add_entry(text)
        self._controls_panel.set_recording(False)

    @Slot(str)
    def _on_error(self, error: str) -> None:
        QMessageBox.warning(self, "Error", error)
        self._status_label.setText("Error")

    @Slot(int)
    def _on_process_finished(self, exit_code: int) -> None:
        if self._controls_panel.is_recording():
            self._controls_panel.set_recording(False)
        if self._controls_panel.is_listening():
            if exit_code != 0:
                self._controls_panel.set_listening(False)

    @Slot(list)
    def _on_models_listed(self, models: list[str]) -> None:
        self._settings_panel.set_models(models)
        self._settings_panel.set_current_model(self._config.default_model)
        self._model_label.setText(f"Model: {self._config.default_model}")

    @Slot(list)
    def _on_devices_listed(self, devices: list[dict[str, str]]) -> None:
        self._settings_panel.set_devices(devices)
        if self._config.audio_device:
            self._settings_panel.set_current_device(self._config.audio_device)

    @Slot(bool)
    def _on_record_clicked(self, start: bool) -> None:
        if start:
            self._transcription_panel.clear()
            self._runner.start_recording(
                model=self._settings_panel.get_model(),
                timeout=self._settings_panel.get_timeout(),
                delay=self._settings_panel.get_delay(),
                output_mode=self._controls_panel.get_output_mode(),
                audio_device=self._settings_panel.get_device(),
            )
        else:
            self._runner.stop()

    @Slot(bool)
    def _on_listen_clicked(self, start: bool) -> None:
        if start:
            self._runner.start_listening(
                sensitivity=self._config.wakeword_sensitivity,
                audio_device=self._settings_panel.get_device(),
            )
        else:
            self._runner.stop()

    @Slot(str)
    def _on_output_mode_changed(self, mode: str) -> None:
        self._config.output_mode = mode

    @Slot(str)
    def _on_api_key_changed(self, key: str) -> None:
        self._config.set_api_key(key)
        self._status_bar.showMessage("API key saved")

    @Slot(str, int)
    def _on_train_wakeword(self, name: str, samples: int) -> None:
        self._runner.train_wakeword(name, samples, self._config.wakeword_sensitivity)

    @Slot(str, str, int)
    def _on_train_command(self, name: str, action: str, samples: int) -> None:
        self._runner.train_command(name, action, samples, self._config.wakeword_sensitivity)

    def _on_test_wakewords(self) -> None:
        self._runner.test_wakewords()

    @Slot(str)
    def _on_remove_wakeword(self, name: str) -> None:
        self._runner.remove_wakeword(name)

    def refresh_wakewords(self) -> None:
        self._runner.list_wakewords()

    def closeEvent(self, event) -> None:
        """Handle window close."""
        if self._runner.is_running():
            self._runner.stop()
        event.accept()
