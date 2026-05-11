"""In-app console tab.

Captures the application's logging output, plus anything written to
``sys.stdout`` / ``sys.stderr``, and renders it inside a Qt widget so the
packaged app can run without a system console window.
"""

from __future__ import annotations

import logging
import sys
from html import escape
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

LEVEL_COLORS = {
    "DEBUG": "#7a7d8e",
    "INFO": "#a9b7c6",
    "WARNING": "#e8b341",
    "ERROR": "#e36161",
    "CRITICAL": "#ff5577",
    "STDOUT": "#9aa8ff",
    "STDERR": "#ff9a76",
}

CONSOLE_STYLESHEET = """
QWidget#ConsoleTab {
    background-color: #1e1e2e;
}
QWidget#ConsoleToolbar {
    background-color: transparent;
}
QWidget#ConsoleToolbar QLabel {
    color: #a9b7c6;
    padding-right: 2px;
}
QWidget#ConsoleToolbar QComboBox {
    min-width: 110px;
    padding: 4px 8px;
}
QWidget#ConsoleToolbar QComboBox::drop-down {
    width: 18px;
    border-left: 1px solid #3B3D48;
}
QWidget#ConsoleToolbar QComboBox QAbstractItemView {
    background-color: #2c2e3c;
    color: #a9b7c6;
    selection-background-color: #717bbc;
    selection-color: #ffffff;
    border: 1px solid #3B3D48;
    padding: 2px;
    outline: 0;
}
QWidget#ConsoleToolbar QCheckBox {
    color: #a9b7c6;
    padding: 0 4px;
}
QWidget#ConsoleToolbar QPushButton {
    min-width: 76px;
    padding: 4px 12px;
}
QPlainTextEdit#ConsoleView {
    background-color: #15151f;
    color: #a9b7c6;
    border: 1px solid #3B3D48;
    border-radius: 6px;
    padding: 6px 8px;
    selection-background-color: #717bbc;
    selection-color: #ffffff;
}
"""

LEVEL_ORDER = {
    "DEBUG": 10,
    "STDOUT": 15,
    "INFO": 20,
    "STDERR": 25,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ---------------------------------------------------------------------------
# Early log buffer — installed before the UI exists so startup logs are kept.
# ---------------------------------------------------------------------------

_early_records: List[Tuple[str, str]] = []


class _EarlyLogBuffer(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            _early_records.append((record.levelname, self.format(record)))
        except Exception:
            pass


_early_handler: Optional[_EarlyLogBuffer] = None


def install_early_log_buffer() -> None:
    """Capture log records before the ConsoleTab exists. Idempotent."""
    global _early_handler
    if _early_handler is not None:
        return
    handler = _EarlyLogBuffer()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger().addHandler(handler)
    _early_handler = handler


def _drain_early_records() -> List[Tuple[str, str]]:
    """Return buffered records and uninstall the early handler."""
    global _early_handler
    records = list(_early_records)
    _early_records.clear()
    if _early_handler is not None:
        try:
            logging.getLogger().removeHandler(_early_handler)
        except Exception:
            pass
        _early_handler = None
    return records


# ---------------------------------------------------------------------------
# Early stdio buffer — captures print() calls during module imports.
#
# Many modules (scanner, image tools, hash utils) emit `RUST ...: Using LOCAL
# version ...` lines via ``print()`` at import time. That happens before the
# ConsoleTab can install its stdio redirectors, so those prints would otherwise
# only appear on the system console. Tee them through this lightweight buffer
# and drain them when the ConsoleTab comes up.
# ---------------------------------------------------------------------------

_early_stdio_records: List[Tuple[str, str]] = []


class _EarlyStdioCapture:
    """File-like wrapper that buffers writes for later replay."""

    def __init__(self, level_label: str, original) -> None:
        self._level_label = level_label
        self._original = original
        self._buffer = ""

    def write(self, text) -> int:
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return 0

        if self._original is not None:
            try:
                self._original.write(text)
            except Exception:
                pass

        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line:
                _early_stdio_records.append((self._level_label, line))
        return len(text)

    def flush(self) -> None:
        if self._original is not None:
            try:
                self._original.flush()
            except Exception:
                pass
        if self._buffer:
            _early_stdio_records.append((self._level_label, self._buffer))
            self._buffer = ""

    def isatty(self) -> bool:
        return False

    def fileno(self) -> int:
        if self._original is not None and hasattr(self._original, "fileno"):
            return self._original.fileno()
        raise OSError("Early stdio capture has no fileno")

    @property
    def original(self):
        return self._original


_early_stdout_capture: Optional[_EarlyStdioCapture] = None
_early_stderr_capture: Optional[_EarlyStdioCapture] = None


def install_early_stdio_buffer() -> None:
    """Capture stdout/stderr writes before the ConsoleTab exists. Idempotent."""
    global _early_stdout_capture, _early_stderr_capture
    if _early_stdout_capture is None:
        _early_stdout_capture = _EarlyStdioCapture("STDOUT", sys.stdout)
        sys.stdout = _early_stdout_capture
    if _early_stderr_capture is None:
        _early_stderr_capture = _EarlyStdioCapture("STDERR", sys.stderr)
        sys.stderr = _early_stderr_capture


def _drain_early_stdio_records() -> List[Tuple[str, str]]:
    """Return buffered stdio records (kept verbatim for replay)."""
    records = list(_early_stdio_records)
    _early_stdio_records.clear()
    return records


def _uninstall_early_stdio_buffer() -> Tuple[object, object]:
    """Restore the original stdio streams that were active before capture.

    Returns the original (stdout, stderr) so the caller can chain them into
    its own redirectors.
    """
    global _early_stdout_capture, _early_stderr_capture
    original_stdout = _early_stdout_capture.original if _early_stdout_capture else sys.stdout
    original_stderr = _early_stderr_capture.original if _early_stderr_capture else sys.stderr

    if _early_stdout_capture is not None and sys.stdout is _early_stdout_capture:
        sys.stdout = original_stdout
    if _early_stderr_capture is not None and sys.stderr is _early_stderr_capture:
        sys.stderr = original_stderr

    _early_stdout_capture = None
    _early_stderr_capture = None
    return original_stdout, original_stderr


# ---------------------------------------------------------------------------
# Bridges
# ---------------------------------------------------------------------------


class _QtLogHandler(logging.Handler):
    """Routes log records into the ConsoleTab via its Qt signal."""

    def __init__(self, console_tab: "ConsoleTab") -> None:
        super().__init__()
        self._console_tab = console_tab

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._console_tab.append_log_signal.emit(record.levelname, msg)
        except Exception:
            pass


class _StreamRedirector:
    """File-like wrapper mirroring writes into the console tab.

    The original stream (typically the real stdout/stderr) is preserved so
    developers running from a terminal still see output there. When the
    original stream is ``None`` (e.g. ``pythonw.exe`` or a macOS ``.app``
    bundle) writes simply land in the in-app console.
    """

    def __init__(
        self,
        console_tab: "ConsoleTab",
        level_label: str,
        original=None,
    ) -> None:
        self._console_tab = console_tab
        self._level_label = level_label
        self._original = original
        self._buffer = ""

    def write(self, text) -> int:
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return 0

        if self._original is not None:
            try:
                self._original.write(text)
            except Exception:
                pass

        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line:
                self._console_tab.append_log_signal.emit(self._level_label, line)
        return len(text)

    def flush(self) -> None:
        if self._original is not None:
            try:
                self._original.flush()
            except Exception:
                pass
        if self._buffer:
            self._console_tab.append_log_signal.emit(self._level_label, self._buffer)
            self._buffer = ""

    def isatty(self) -> bool:
        return False

    def fileno(self) -> int:
        if self._original is not None and hasattr(self._original, "fileno"):
            return self._original.fileno()
        raise OSError("ConsoleTab redirector has no fileno")

    @property
    def original(self):
        return self._original


# ---------------------------------------------------------------------------
# ConsoleTab widget
# ---------------------------------------------------------------------------


class ConsoleTab(QWidget):
    """Tab that displays application logs and captured stdio."""

    append_log_signal = pyqtSignal(str, str)  # level, message

    MAX_BLOCKS = 5000

    def __init__(self) -> None:
        super().__init__()

        self._minimum_level = logging.DEBUG
        original_stdout, original_stderr = _uninstall_early_stdio_buffer()
        self._original_stdout = original_stdout
        self._original_stderr = original_stderr
        self._stdout_redirector: Optional[_StreamRedirector] = None
        self._stderr_redirector: Optional[_StreamRedirector] = None
        self._log_handler: Optional[_QtLogHandler] = None

        self._setup_ui()
        self.append_log_signal.connect(self._on_append_log)

        self._install_logging_handler()
        self._install_stdio_redirectors()
        self._flush_early_records()
        self._flush_early_stdio_records()

    # -- setup ------------------------------------------------------------

    def _setup_ui(self) -> None:
        self.setObjectName("ConsoleTab")
        self.setStyleSheet(CONSOLE_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        toolbar_widget = QWidget(self)
        toolbar_widget.setObjectName("ConsoleToolbar")
        toolbar = QHBoxLayout(toolbar_widget)
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setSpacing(10)

        toolbar.addWidget(QLabel("Level:"))
        self.level_combo = QComboBox()
        for label in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            self.level_combo.addItem(label, getattr(logging, label))
        self.level_combo.setCurrentText("DEBUG")
        self.level_combo.setMinimumHeight(28)
        self.level_combo.currentIndexChanged.connect(self._on_level_changed)
        toolbar.addWidget(self.level_combo)

        self.autoscroll_checkbox = QCheckBox("Auto-scroll")
        self.autoscroll_checkbox.setChecked(True)
        toolbar.addWidget(self.autoscroll_checkbox)

        toolbar.addStretch(1)

        self.copy_button = QPushButton("Copy all")
        self.copy_button.setMinimumHeight(28)
        self.copy_button.clicked.connect(self.copy_all)
        toolbar.addWidget(self.copy_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setMinimumHeight(28)
        self.clear_button.clicked.connect(self.clear)
        toolbar.addWidget(self.clear_button)

        layout.addWidget(toolbar_widget)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setObjectName("ConsoleView")
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumBlockCount(self.MAX_BLOCKS)
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        font = QFont()
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setFamilies(["Menlo", "Consolas", "DejaVu Sans Mono", "monospace"])
        font.setPointSize(11)
        self.text_edit.setFont(font)

        layout.addWidget(self.text_edit, 1)

    # -- handlers ---------------------------------------------------------

    def _install_logging_handler(self) -> None:
        handler = _QtLogHandler(self)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(handler)
        self._log_handler = handler

    def _install_stdio_redirectors(self) -> None:
        # Preserve the *real* underlying stream (resolved before any early
        # capture wrapper) so we still tee to a real terminal when the app is
        # launched from one.
        self._stdout_redirector = _StreamRedirector(self, "STDOUT", self._original_stdout)
        self._stderr_redirector = _StreamRedirector(self, "STDERR", self._original_stderr)
        sys.stdout = self._stdout_redirector
        sys.stderr = self._stderr_redirector

    def _flush_early_records(self) -> None:
        for level, msg in _drain_early_records():
            self.append_log_signal.emit(level, msg)

    def _flush_early_stdio_records(self) -> None:
        for level, msg in _drain_early_stdio_records():
            self.append_log_signal.emit(level, msg)

    # -- events -----------------------------------------------------------

    def _on_level_changed(self, _index: int) -> None:
        level_value = self.level_combo.currentData()
        if isinstance(level_value, int):
            self._minimum_level = level_value

    def _on_append_log(self, level: str, message: str) -> None:
        if LEVEL_ORDER.get(level, 100) < self._minimum_level:
            return
        color = LEVEL_COLORS.get(level, "#dddddd")
        html = f'<span style="color:{color};white-space:pre">{escape(message)}</span>'
        self.text_edit.appendHtml(html)
        if self.autoscroll_checkbox.isChecked():
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    # -- public API -------------------------------------------------------

    def clear(self) -> None:
        self.text_edit.clear()

    def copy_all(self) -> None:
        cursor = self.text_edit.textCursor()
        self.text_edit.selectAll()
        self.text_edit.copy()
        self.text_edit.setTextCursor(cursor)

    def shutdown(self) -> None:
        """Restore stdio and detach handlers. Safe to call multiple times."""
        if self._log_handler is not None:
            try:
                logging.getLogger().removeHandler(self._log_handler)
            except Exception:
                pass
            self._log_handler = None

        if isinstance(sys.stdout, _StreamRedirector) and sys.stdout is self._stdout_redirector:
            sys.stdout = self._original_stdout
        if isinstance(sys.stderr, _StreamRedirector) and sys.stderr is self._stderr_redirector:
            sys.stderr = self._original_stderr

        self._stdout_redirector = None
        self._stderr_redirector = None
