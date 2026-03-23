"""Main application window for voclip-GUI."""

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QApplication,
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
from system_tray import SystemTray
from voclip_runner import VoclipRunner
from widgets.controls_panel import ControlsPanel
from widgets.history_panel import HistoryPanel
from widgets.listen_status import ListenStatusWidget
from widgets.settings_panel import SettingsPanel
from widgets.transcription_panel import TranscriptionPanel
from widgets.wakeword_panel import TestWakewordsDialog, TrainingProgressDialog, WakewordPanel


class MainWindow(QMainWindow):
    """Main application window - focused on one-shot recording."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._config = ConfigManager()
        self._runner = VoclipRunner(self)
        self._is_listening = False
        self._setup_ui()
        self._connect_signals()
        self._setup_tray()
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

    def _setup_tray(self) -> None:
        """Set up system tray."""
        self._tray = SystemTray(self)
        self._tray.show_window_requested.connect(self.show)
        self._tray.quick_record_requested.connect(self._on_quick_record)
        self._tray.toggle_listen_requested.connect(self._toggle_listen_mode)
        self._tray.quit_requested.connect(self._on_quit)
        self._tray.show()

        self._listen_widget = ListenStatusWidget()
        self._listen_widget.stop_clicked.connect(self._stop_listen_mode)

        self._runner.output_line.connect(self._on_listen_output)

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
        self._controls_panel.listen_clicked.connect(self._toggle_listen_mode)
        self._controls_panel.output_mode_changed.connect(self._on_output_mode_changed)

        self._settings_panel.api_key_changed.connect(self._on_api_key_changed)

        self._wakeword_panel.train_wakeword_requested.connect(self._on_train_wakeword_requested)
        self._wakeword_panel.train_command_requested.connect(self._on_train_command_requested)
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
            self._status_label.setText(message)

    @Slot(str)
    def _on_status_changed(self, status: str) -> None:
        self._status_label.setText(status)

    @Slot(str)
    def _on_final_transcript(self, text: str) -> None:
        self._transcription_panel.update_final(text)
        self._history_panel.add_entry(text)
        self._controls_panel.set_recording(False)
        self._tray.set_recording(False)

    @Slot(str)
    def _on_error(self, error: str) -> None:
        QMessageBox.warning(self, "Error", error)
        self._status_label.setText("Error")

    @Slot(int)
    def _on_process_finished(self, exit_code: int) -> None:
        self._tray.set_recording(False)
        if self._is_listening:
            if exit_code != 0:
                self._stop_listen_mode()
                QMessageBox.warning(
                    self, "Error", f"Listen mode stopped unexpectedly (exit code: {exit_code})"
                )
            else:
                self._listen_widget.set_detecting(False)

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
            self._tray.set_recording(True)
        else:
            self._runner.stop()
            self._tray.set_recording(False)

    def _on_quick_record(self) -> None:
        """Handle quick record from tray."""
        if self._is_listening:
            return
        if self._runner.is_running():
            self._runner.stop()
            self._controls_panel.set_recording(False)
            self._tray.set_recording(False)
        else:
            self._transcription_panel.clear()
            self._controls_panel.set_recording(True)
            self._runner.start_recording(
                model=self._settings_panel.get_model(),
                timeout=self._settings_panel.get_timeout(),
                delay=self._settings_panel.get_delay(),
                output_mode=self._controls_panel.get_output_mode(),
                audio_device=self._settings_panel.get_device(),
            )
            self._tray.set_recording(True)

    def _toggle_listen_mode(self) -> None:
        """Toggle listen mode from tray."""
        if self._is_listening:
            self._stop_listen_mode()
        else:
            self._start_listen_mode()

    def _start_listen_mode(self) -> None:
        """Start listen mode."""
        self._is_listening = True
        self._runner.start_listening(
            sensitivity=self._config.wakeword_sensitivity,
            audio_device=self._settings_panel.get_device(),
        )
        self._tray.set_listening(True)
        self._controls_panel.set_listening(True)
        self._listen_widget.set_detecting(False)
        self._listen_widget.show()
        self.hide()

    def _stop_listen_mode(self) -> None:
        """Stop listen mode."""
        self._is_listening = False
        self._runner.stop()
        self._tray.set_listening(False)
        self._controls_panel.set_listening(False)
        self._listen_widget.hide()

    @Slot(str)
    def _on_listen_output(self, line: str) -> None:
        """Process output during listen mode."""
        if not self._is_listening:
            return

        line_lower = line.lower()
        if "wake word detected" in line_lower or "command detected" in line_lower:
            self._listen_widget.set_detecting(True)
            self._listen_widget.set_detection_text(line)
        elif "typed:" in line_lower or "key:" in line_lower:
            self._listen_widget.set_detecting(False)

    @Slot(str)
    def _on_output_mode_changed(self, mode: str) -> None:
        self._config.output_mode = mode

    @Slot(str)
    def _on_api_key_changed(self, key: str) -> None:
        self._config.set_api_key(key)
        self._status_label.setText("API key saved")

    def _on_train_wakeword_requested(self, name: str, samples: int) -> None:
        self._training_dialog = TrainingProgressDialog(name, samples, is_command=False, parent=self)
        self._training_dialog.send_input.connect(self._runner.send_input)
        self._runner.output_line.connect(self._training_dialog.append_output)
        self._runner.process_finished.connect(self._on_training_finished)

        if self._runner.train_wakeword(name, samples, self._config.wakeword_sensitivity):
            self._training_dialog.exec()
        else:
            self._training_dialog.deleteLater()
            self._training_dialog = None

        self._runner.output_line.disconnect(self._training_dialog.append_output)
        self._runner.process_finished.disconnect(self._on_training_finished)
        self._training_dialog.deleteLater()
        self._training_dialog = None
        self._runner.list_wakewords()

    def _on_train_command_requested(self, name: str, action: str, samples: int) -> None:
        self._training_dialog = TrainingProgressDialog(name, samples, is_command=True, parent=self)
        self._training_dialog.send_input.connect(self._runner.send_input)
        self._runner.output_line.connect(self._training_dialog.append_output)
        self._runner.process_finished.connect(self._on_training_finished)

        if self._runner.train_command(name, action, samples, self._config.wakeword_sensitivity):
            self._training_dialog.exec()
        else:
            self._training_dialog.deleteLater()
            self._training_dialog = None

        self._runner.output_line.disconnect(self._training_dialog.append_output)
        self._runner.process_finished.disconnect(self._on_training_finished)
        self._training_dialog.deleteLater()
        self._training_dialog = None
        self._runner.list_wakewords()

    def _on_training_finished(self, exit_code: int) -> None:
        if hasattr(self, "_training_dialog") and self._training_dialog:
            self._training_dialog.set_status(
                "Training complete!"
                if exit_code == 0
                else f"Training failed (exit code: {exit_code})"
            )

    def _on_test_wakewords(self) -> None:
        self._test_dialog = TestWakewordsDialog(self)
        self._runner.output_line.connect(self._test_dialog.append_output)
        self._runner.process_finished.connect(self._on_test_finished)

        if self._runner.test_wakewords():
            self._test_dialog.exec()
        else:
            self._test_dialog.deleteLater()
            self._test_dialog = None

        self._runner.output_line.disconnect(self._test_dialog.append_output)
        self._runner.process_finished.disconnect(self._on_test_finished)
        self._test_dialog.deleteLater()
        self._test_dialog = None

    def _on_test_finished(self, exit_code: int) -> None:
        if hasattr(self, "_test_dialog") and self._test_dialog:
            pass

    @Slot(str)
    def _on_remove_wakeword(self, name: str) -> None:
        self._runner.remove_wakeword(name)
        self._runner.list_wakewords()

    def refresh_wakewords(self) -> None:
        self._runner.list_wakewords()

    def _on_quit(self) -> None:
        """Handle quit from tray."""
        if self._runner.is_running():
            self._runner.stop()
        self._listen_widget.close()
        self._tray.hide()
        QApplication.quit()

    def closeEvent(self, event) -> None:
        """Handle window close - minimize to tray instead of quitting."""
        event.ignore()
        self.hide()
