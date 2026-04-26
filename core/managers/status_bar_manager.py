import logging
from PyQt6.QtWidgets import QStatusBar, QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class StatusBarManager:
    """
    Manages the application status bar, including messages, progress bar, 
    and selection stats.
    """
    def __init__(self, parent, logger):
        self.logger = logger
        self.status_bar = QStatusBar(parent)
        parent.setStatusBar(self.status_bar)

        # Container with three columns
        status_container = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)

        # Left column: messages
        self.status_message_label = QLabel("")
        self.status_message_label.setMinimumWidth(200)
        self.status_message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.status_message_label, 2)

        # Center: centered progress bar
        center_widget = QWidget()
        center_layout = QHBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.addStretch(1)
        self.status_progress_bar = QProgressBar()
        self.status_progress_bar.setFixedHeight(12)
        self.status_progress_bar.setMinimumWidth(300)
        self.status_progress_bar.setMaximumWidth(360)
        self.status_progress_bar.setValue(0)
        self.status_progress_bar.setVisible(True)
        center_layout.addWidget(self.status_progress_bar)
        center_layout.addStretch(1)
        center_widget.setLayout(center_layout)
        status_layout.addWidget(center_widget, 1)

        # Right column: number of selected tiles
        self.selected_label = QLabel("Selected: 0")
        self.selected_label.setMinimumWidth(100)
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status_layout.addWidget(self.selected_label, 2)

        status_container.setLayout(status_layout)
        self.status_bar.addWidget(status_container, 1)
        self.logger.debug("Status bar created successfully (StatusBarManager)")

    def update_status(self, message, timeout=5000):
        try:
            if self.status_message_label:
                self.status_message_label.setText(message)
                self.logger.debug(f"Status updated: {message}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")

    def show_log_info(self, log_level, message):
        try:
            level_mapping = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍",
                "CRITICAL": "🚨",
            }
            icon = level_mapping.get(log_level.upper(), "ℹ️")
            if len(message) > 100:
                message = message[:97] + "..."
            status_message = f"{icon} {message}"
            self.update_status(status_message)
        except Exception as e:
            self.logger.error(f"Error showing log info: {e}")

    def update_working_directory_status(self, directory_path):
        try:
            if directory_path:
                if len(directory_path) > 80:
                    sep = "\\" if "\\" in directory_path else "/"
                    parts = directory_path.split(sep)
                    if len(parts) > 3:
                        tail = sep.join(parts[-3:])
                        short_path = f"...{sep}{tail}"
                    else:
                        short_path = directory_path
                else:
                    short_path = directory_path
                status_message = f"📁 Working directory: {short_path}"
                self.update_status(status_message, timeout=0)
                self.logger.debug(f"Working directory status updated: {directory_path}")
        except Exception as e:
            self.logger.error(f"Error updating working directory status: {e}")

    def update_selection_status(self, status_text: str):
        if self.selected_label:
            self.selected_label.setText(status_text)
            self.logger.debug(f"Updated status bar: {status_text}")
