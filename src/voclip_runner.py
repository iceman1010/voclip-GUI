"""Subprocess manager for voclip binary."""

import re
from typing import Optional

from PySide6.QtCore import QObject, QProcess, Signal, Slot


class VoclipRunner(QObject):
    """Manages voclip subprocess execution and output parsing."""

    status_changed = Signal(str)
    partial_transcript = Signal(str)
    final_transcript = Signal(str)
    error = Signal(str)
    process_finished = Signal(int)
    output_line = Signal(str)
    started = Signal()
    models_listed = Signal(list)
    devices_listed = Signal(list)
    wakewords_listed = Signal(list)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._process: Optional[QProcess] = None
        self._is_running = False
        self._in_session = False
        self._buffer = ""

    def is_running(self) -> bool:
        return self._is_running

    def _start_process(self, args: list[str]) -> bool:
        """Start voclip with given arguments."""
        if self._is_running:
            self.error.emit("A voclip process is already running")
            return False

        self._process = QProcess(self)
        self._process.setProgram("voclip")
        self._process.setArguments(args)
        self._process.readyReadStandardError.connect(self._handle_stderr)
        self._process.readyReadStandardOutput.connect(self._handle_stdout)
        self._process.finished.connect(self._handle_finished)
        self._process.errorOccurred.connect(self._handle_error)

        self._buffer = ""
        self._in_session = False
        self._is_running = True
        self._process.start()
        self.started.emit()
        return True

    def _handle_stderr(self) -> None:
        """Process stderr output from voclip."""
        if not self._process:
            return

        data = self._process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._buffer += data

        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if line:
                self._parse_line(line)

    def _handle_stdout(self) -> None:
        """Process stdout output from voclip."""
        if not self._process:
            return

        data = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        for line in data.strip().split("\n"):
            if line.strip():
                self.output_line.emit(line.strip())

    def _parse_line(self, line: str) -> None:
        """Parse a line of voclip output and emit appropriate signal."""
        self.output_line.emit(line)

        line_lower = line.lower()

        if "authenticating" in line_lower:
            self.status_changed.emit("Authenticating...")
        elif "listening" in line_lower and "speak" in line_lower:
            self._in_session = True
            self.status_changed.emit("Recording...")
        elif "session started" in line_lower:
            self._in_session = True
            self.status_changed.emit("Session active")
        elif "copied to clipboard:" in line_lower:
            match = re.search(r"copied to clipboard:\s*(.+)", line, re.IGNORECASE)
            if match:
                self._in_session = False
                self.final_transcript.emit(match.group(1).strip())
        elif "typed:" in line_lower:
            match = re.search(r"typed:\s*(.+)", line, re.IGNORECASE)
            if match:
                self._in_session = False
                self.final_transcript.emit(match.group(1).strip())
        elif line_lower.startswith("error:") or "error:" in line_lower:
            self.error.emit(line.replace("Error:", "").replace("error:", "").strip())
        elif self._in_session and line and not self._is_status_line(line):
            self.partial_transcript.emit(line)

    def _is_status_line(self, line: str) -> bool:
        """Check if line is a status message, not transcript."""
        status_keywords = [
            "authenticating",
            "listening",
            "session",
            "copied",
            "typed",
            "error",
            "warning",
            "detected",
            "wake",
            "command",
        ]
        line_lower = line.lower()
        return any(kw in line_lower for kw in status_keywords)

    @Slot(int, QProcess.ExitStatus)
    def _handle_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        """Handle process completion."""
        self._is_running = False
        self._in_session = False
        self._process = None
        self.process_finished.emit(exit_code)

    @Slot(QProcess.ProcessError)
    def _handle_error(self, error: QProcess.ProcessError) -> None:
        """Handle process errors."""
        error_messages = {
            QProcess.ProcessError.FailedToStart: "voclip not found. Please install it first.",
            QProcess.ProcessError.Crashed: "voclip crashed unexpectedly.",
            QProcess.ProcessError.TimedOut: "Operation timed out.",
            QProcess.ProcessError.WriteError: "Failed to write to voclip process.",
            QProcess.ProcessError.ReadError: "Failed to read from voclip process.",
            QProcess.ProcessError.UnknownError: "Unknown error occurred.",
        }
        self.error.emit(error_messages.get(error, "Unknown error occurred."))
        self._is_running = False
        self._in_session = False

    def stop(self) -> None:
        """Stop the running process."""
        if self._process and self._is_running:
            self._process.terminate()
            if not self._process.waitForFinished(2000):
                self._process.kill()

    def start_recording(
        self,
        model: str = "u3-rt-pro",
        timeout: int = 3,
        delay: int = 1,
        output_mode: str = "clipboard",
        audio_device: Optional[str] = None,
    ) -> bool:
        """Start one-shot recording session."""
        args = ["--model", model, "--timeout", str(timeout), "--delay", str(delay)]
        if output_mode == "type":
            args.append("--type")
        if audio_device:
            args.extend(["--audio-device", audio_device])
        return self._start_process(args)

    def start_listening(
        self,
        sensitivity: str = "medium",
        audio_device: Optional[str] = None,
    ) -> bool:
        """Start always-on listen mode."""
        args = ["--listen", "--wakeword-sensitivity", sensitivity]
        if audio_device:
            args.extend(["--audio-device", audio_device])
        return self._start_process(args)

    def train_wakeword(
        self,
        name: str,
        samples: int = 8,
        sensitivity: str = "medium",
    ) -> bool:
        """Start wake word training."""
        args = [
            "--train-wakeword",
            "--wakeword-name",
            name,
            "--wakeword-samples",
            str(samples),
            "--wakeword-sensitivity",
            sensitivity,
        ]
        return self._start_process(args)

    def train_command(
        self,
        name: str,
        action: str,
        samples: int = 8,
        sensitivity: str = "medium",
    ) -> bool:
        """Start command word training."""
        args = [
            "--train-command",
            "--command-name",
            name,
            "--command-action",
            action,
            "--wakeword-samples",
            str(samples),
            "--wakeword-sensitivity",
            sensitivity,
        ]
        return self._start_process(args)

    def test_wakewords(self) -> bool:
        """Test wake word detection."""
        return self._start_process(["--test-wakeword"])

    def remove_wakeword(self, name: str) -> bool:
        """Remove a trained voice pattern."""
        return self._start_process(["--remove-wakeword", name])

    def list_models(self) -> None:
        """List available models (async, emits models_listed signal)."""
        self._list_and_parse("--list-models", self._parse_models, self.models_listed)

    def list_devices(self) -> None:
        """List audio devices (async, emits devices_listed signal)."""
        self._list_and_parse("--list-devices", self._parse_devices, self.devices_listed)

    def list_wakewords(self) -> None:
        """List wake words (async, emits wakewords_listed signal)."""
        self._list_and_parse("--list-wakewords", self._parse_wakewords, self.wakewords_listed)

    def _list_and_parse(self, arg: str, parser, signal: Signal) -> None:
        """Run a list command and parse output."""
        import subprocess

        try:
            result = subprocess.run(
                ["voclip", arg],
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout + result.stderr
            items = parser(output)
            signal.emit(items)
        except Exception as e:
            self.error.emit(f"Failed to run {arg}: {e}")

    def _parse_models(self, output: str) -> list[str]:
        """Parse --list-models output."""
        models = []
        for line in output.split("\n"):
            line = line.strip()
            if line and not line.startswith("Available") and not line.startswith("Use"):
                name = line.split()[0] if line.split() else ""
                if name and not name.startswith("("):
                    models.append(name)
        return models

    def _parse_devices(self, output: str) -> list[dict[str, str]]:
        """Parse --list-devices output."""
        devices = []
        for line in output.split("\n"):
            line = line.strip()
            if line and ":" in line and not line.startswith("Audio") and not line.startswith("Use"):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    idx = parts[0].strip()
                    name = parts[1].strip()
                    devices.append({"index": idx, "name": name})
        return devices

    def _parse_wakewords(self, output: str) -> list[dict[str, str]]:
        """Parse --list-wakewords output."""
        patterns = []
        for line in output.split("\n"):
            line = line.strip()
            if line.startswith('"'):
                match = re.match(r'"([^"]+)"\s+(\w+)(?:\s+\((\w+)\))?', line)
                if match:
                    patterns.append(
                        {
                            "name": match.group(1),
                            "type": "Wake word" if match.group(2) == "transcribe" else "Command",
                            "action": match.group(2)
                            + (f" ({match.group(3)})" if match.group(3) else ""),
                        }
                    )
        return patterns

    def send_input(self, text: str) -> None:
        """Send input to the running process."""
        if self._process and self._is_running:
            self._process.write((text + "\n").encode())
