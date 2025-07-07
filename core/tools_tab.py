import logging
import os
import subprocess
import sys
from typing import Dict, List

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.workers.asset_rebuilder_worker import AssetRebuilderWorker
from core.workers.worker_manager import WorkerManager
        # thumbnail_cache imported in utilities.clear_thumbnail_cache_after_rebuild()
from core.tools import (
    BaseWorker,
    WebPConverterWorker,
    ImageResizerWorker,
    FileRenamerWorker,
    FileShortenerWorker,
    PrefixSuffixRemoverWorker,
    DuplicateFinderWorker
)

logger = logging.getLogger(__name__)


class ToolsTab(QWidget):
    """Tools tab for file operations"""

    # Signals
    working_directory_changed = pyqtSignal(str)
    show_info_message = pyqtSignal(str, str)
    show_error_message = pyqtSignal(str, str)
    # Signal emitted when folder structure changes
    folder_structure_changed = pyqtSignal(str)

    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.current_working_directory = None

        # Initialize workers
        self.webp_converter = None
        self.asset_rebuilder = None
        self.image_resizer = None
        self.file_renamer = None
        self.remove_worker = None
        self.duplicate_finder = None

        # Initialize UI
        self._setup_ui()

    def _validate_working_directory(self) -> bool:
        """Common working directory validation"""
        logger.debug(f"Validating working directory: {self.current_working_directory}")
        logger.debug(
            f"Folder exists: {os.path.exists(self.current_working_directory) if self.current_working_directory else False}"
        )

        if not self.current_working_directory or not os.path.exists(
            self.current_working_directory
        ):
            logger.warning(
                f"Working folder is not set or does not exist: {self.current_working_directory}"
            )
            QMessageBox.warning(
                self, "Error", "Working folder is not set or does not exist."
            )
            return False
        return True

    def _handle_worker_lifecycle(self, worker, button, original_text):
        """Unified worker lifecycle handling using WorkerManager"""
        WorkerManager.start_worker_lifecycle(worker, button, original_text, self)

    def _start_operation_with_confirmation(
        self, operation_name: str, description: str, worker_factory
    ):
        """Universal method for starting operations with confirmation using WorkerManager"""
        # Map operation names to button names and class fields
        button_mapping = {
            "webp conversion": ("webp_button", "webp_converter"),
            "asset rebuild": ("rebuild_button", "asset_rebuilder"),
            "image resizing": ("image_resizer_button", "image_resizer"),
            "file name shortening": ("file_renamer_button", "file_renamer"),
            "remove prefix/suffix": ("remove_button", "remove_worker"),
        }

        button_name, worker_attr = button_mapping.get(
            operation_name.lower(), ("webp_button", "webp_converter")
        )
        logger.debug(
            f"Mapping operation '{operation_name}' to button '{button_name}' and field '{worker_attr}'"
        )
        button = getattr(self, button_name)
        
        worker = WorkerManager.create_worker_with_confirmation(
            operation_name, description, worker_factory, self, button
        )
        
        if worker:
            setattr(self, worker_attr, worker)
            self._handle_worker_lifecycle(worker, button, button.text())

    def _setup_ui(self):
        """Setup user interface for tools tab"""
        # Main horizontal layout (2 columns)
        main_layout = QHBoxLayout()

        # Left column - scalable
        left_column = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Files"))

        # Split "Files" column into two list views
        files_layout = QHBoxLayout()

        # Left view - archive files
        self.archive_list = QListWidget()
        self.archive_list.setAlternatingRowColors(True)
        self.archive_list.itemDoubleClicked.connect(self._on_archive_double_clicked)
        files_layout.addWidget(self.archive_list)

        # Right view - preview files
        self.preview_list = QListWidget()
        self.preview_list.setAlternatingRowColors(True)
        self.preview_list.itemDoubleClicked.connect(self._on_preview_double_clicked)
        files_layout.addWidget(self.preview_list)

        left_layout.addLayout(files_layout)
        left_column.setLayout(left_layout)

        # Right column - fixed width 175px
        right_column = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Tools"))

        # Button 1 - convert to WebP
        self.webp_button = QPushButton("Convert to WebP")
        self.webp_button.clicked.connect(self._on_webp_conversion_clicked)
        right_layout.addWidget(self.webp_button)

        # Button 2 - resize images
        self.image_resizer_button = QPushButton("Resize Images")
        self.image_resizer_button.clicked.connect(self._on_image_resizing_clicked)
        right_layout.addWidget(self.image_resizer_button)

        # Button 3 - randomize file names
        self.file_renamer_button = QPushButton("Randomize File Names")
        self.file_renamer_button.clicked.connect(self._on_file_renaming_clicked)
        right_layout.addWidget(self.file_renamer_button)

        # Button 4 - shorten file names
        self.file_shortener_button = QPushButton("Shorten File Names")
        self.file_shortener_button.clicked.connect(self._on_file_shortening_clicked)
        right_layout.addWidget(self.file_shortener_button)

        # Button 5 - remove prefix/suffix from file names
        self.remove_button = QPushButton("Remove prefix/suffix")
        self.remove_button.clicked.connect(self._on_remove_clicked)
        right_layout.addWidget(self.remove_button)

        # Button 6 - find duplicates
        self.find_duplicates_button = QPushButton("Find Duplicates")
        self.find_duplicates_button.clicked.connect(self._on_find_duplicates_clicked)
        right_layout.addWidget(self.find_duplicates_button)

        # Spacer
        right_layout.addSpacerItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        # 5th button at the bottom - rebuild assets
        self.rebuild_button = QPushButton("Rebuild Assets")
        self.rebuild_button.clicked.connect(self._on_rebuild_assets_clicked)
        right_layout.addWidget(self.rebuild_button)
        right_column.setLayout(right_layout)
        right_column.setFixedWidth(175)

        # Add columns to main layout
        main_layout.addWidget(left_column, 1)  # Stretch factor 1 - scalable
        main_layout.addWidget(right_column, 0)  # Stretch factor 0 - fixed width

        self.setLayout(main_layout)
        logger.debug("ToolsTab UI setup completed with 2-column layout")

    def set_working_directory(self, directory_path: str):
        """Sets the working folder and scans files"""
        logger.debug(f"ToolsTab.set_working_directory() called with: {directory_path}")

        if not directory_path or not os.path.exists(directory_path):
            logger.warning(f"Invalid working folder: {directory_path}")
            self.clear_working_directory()
            return

        self.current_working_directory = directory_path
        logger.debug(
            f"Set current_working_directory: {self.current_working_directory}"
        )

        self.scan_working_directory(directory_path)
        self.working_directory_changed.emit(directory_path)
        self._update_button_states()
        logger.info(f"Working folder set: {directory_path}")

    def scan_working_directory(self, directory_path: str):
        """Scans the working folder for archive and preview files"""
        try:
            if not os.path.exists(directory_path):
                logger.error(f"Folder does not exist: {directory_path}")
                return

            # File extensions
            archive_extensions = {
                ".zip",
                ".rar",
                ".7z",
                ".tar",
                ".gz",
                ".bz2",
                ".sbsar",
            }
            preview_extensions = {
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".tiff",
                ".webp",
            }

            # Scan files
            archive_files = []
            preview_files = []

            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in archive_extensions:
                        archive_files.append(item)
                    elif file_ext in preview_extensions:
                        preview_files.append(item)

            # Sort files alphabetically
            archive_files.sort(key=str.lower)
            preview_files.sort(key=str.lower)

            # Update lists
            self._update_archive_list(archive_files)
            self._update_preview_list(preview_files)

            logger.info(
                f"Scan completed: {len(archive_files)} archives, "
                f"{len(preview_files)} previews"
            )

        except Exception as e:
            logger.error(f"Error scanning folder {directory_path}: {e}")
            QMessageBox.warning(self, "Error", f"Cannot scan folder: {e}")

    def _update_archive_list(self, archive_files: list):
        """Updates the list of archive files"""
        self.archive_list.clear()
        for file_name in archive_files:
            item = QListWidgetItem(file_name)
            item.setData(Qt.ItemDataRole.UserRole, file_name)
            self.archive_list.addItem(item)

    def _update_preview_list(self, preview_files: list):
        """Updates the list of preview files"""
        self.preview_list.clear()
        for file_name in preview_files:
            # Get image resolution
            resolution = self._get_image_resolution(file_name)
            display_text = f"{file_name} - res: {resolution}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, file_name)
            self.preview_list.addItem(item)

    def _get_image_resolution(self, file_name: str) -> str:
        """Gets image resolution in 'width x height' format"""
        if not self.current_working_directory:
            return "no data"

        file_path = os.path.join(self.current_working_directory, file_name)

        try:
            # Import Pillow here to avoid global requirement
            from PIL import Image

            with Image.open(file_path) as img:
                width, height = img.size
                return f"{width} x {height}"

        except ImportError:
            logger.warning(
                "Pillow library is not installed - cannot read resolution"
            )
            return "no Pillow"
        except Exception as e:
            logger.debug(f"Cannot read resolution {file_name}: {e}")
            return "read error"

    def clear_lists(self):
        """Clears both lists"""
        self.archive_list.clear()
        self.preview_list.clear()

    def _update_button_states(self):
        """Updates the state of all buttons"""
        has_working_folder = bool(
            self.current_working_directory
            and os.path.exists(self.current_working_directory)
        )

        if self.rebuild_button:
            self.rebuild_button.setEnabled(has_working_folder)
        if self.webp_button:
            self.webp_button.setEnabled(has_working_folder)
        if self.image_resizer_button:
            self.image_resizer_button.setEnabled(has_working_folder)
        if self.file_renamer_button:
            self.file_renamer_button.setEnabled(has_working_folder)
        if self.file_shortener_button:
            self.file_shortener_button.setEnabled(has_working_folder)
        if self.remove_button:
            self.remove_button.setEnabled(has_working_folder)
        if self.find_duplicates_button:
            self.find_duplicates_button.setEnabled(has_working_folder)

    def _handle_worker_progress(
        self, button: QPushButton, current: int, total: int, message: str
    ):
        WorkerManager.handle_progress(button, current, total, message)

    def _handle_worker_finished(
        self, button: QPushButton, message: str, original_text: str
    ):
        # CATEGORICAL CLEARING OF RAM CACHE FOR ASSET REBUILD!!!
        if hasattr(self, "asset_rebuilder") and self.asset_rebuilder and hasattr(button, 'objectName'):
            # Check if it's the asset rebuild button
            if button == getattr(self, 'rebuild_button', None):
                from core.utilities import clear_thumbnail_cache_after_rebuild
                clear_thumbnail_cache_after_rebuild(is_error=False)
        
        WorkerManager.handle_finished(button, message, original_text, self)
        # Add handling for refreshing asset counts in folders
        self._handle_operation_finished(message, original_text)

    def _handle_operation_finished(self, message: str, operation_name: str):
        """# Handles completion of file operations with asset count refresh"""
        try:
            # Check if the operation changed files (does not contain "No files", "Skipped all", "Nothing to")
            operation_modified_files = False
            
            # Check for various messages about no changes
            skip_messages = [
                "No files",
                "Skipped all", 
                "Nothing to",
                "No duplicates found",
                "No archive files",
                "No images found",
                "No files to convert",
                "No files to resize",
                "No files to process"
            ]
            
            # Check for messages about completed changes
            success_messages = [
                "converted",
                "resized", 
                "renamed",
                "moved",
                "removed",
                "shortened",
                "Moved",
                "created",
                "deleted",
                "rebuilt",
                "processed",
                "generated",
                "assets created",
                "files processed",
                "operation completed"
            ]
            
            # Check if the operation did not change files
            if any(skip_msg in message for skip_msg in skip_messages):
                logger.debug(f"Operation '{operation_name}' did not change files: {message}")
                return
            
            # Check if operation changed files
            if any(success_msg in message for success_msg in success_messages):
                operation_modified_files = True
                logger.debug(f"Operation '{operation_name}' changed files: {message}")
            
            # If the operation changed files, emit a refresh signal
            if operation_modified_files and self.current_working_directory:
                self.folder_structure_changed.emit(self.current_working_directory)
                logger.info(f"Emitted folder_structure_changed signal for operation '{operation_name}' in: {self.current_working_directory}")
                
        except Exception as e:
            logger.error(f"Error handling completion of operation '{operation_name}': {e}")

    def _handle_worker_error(
        self, button: QPushButton, error_message: str, original_text: str
    ):
        # CATEGORICAL CLEARING OF RAM CACHE EVEN AFTER ASSET REBUILD ERROR!!!
        if hasattr(self, "asset_rebuilder") and self.asset_rebuilder and hasattr(button, 'objectName'):
            # Check if it's the asset rebuild button
            if button == getattr(self, 'rebuild_button', None):
                from core.utilities import clear_thumbnail_cache_after_rebuild
                clear_thumbnail_cache_after_rebuild(is_error=True)
        
        WorkerManager.handle_error(button, error_message, original_text, self)

    def _reset_button_state(self, button: QPushButton, original_text: str):
        WorkerManager.reset_button_state(button, original_text, self)

    def closeEvent(self, event):
        """Stops all active threads before destruction"""
        try:
            logger.info("ToolsTab: Stopping active threads...")

            # List of all threads to stop
            workers_to_stop = []

            if hasattr(self, "webp_converter") and self.webp_converter:
                workers_to_stop.append(self.webp_converter)
            if hasattr(self, "asset_rebuilder") and self.asset_rebuilder:
                workers_to_stop.append(self.asset_rebuilder)
            if hasattr(self, "image_resizer") and self.image_resizer:
                workers_to_stop.append(self.image_resizer)
            if hasattr(self, "file_renamer") and self.file_renamer:
                workers_to_stop.append(self.file_renamer)
            if hasattr(self, "file_shortener") and self.file_shortener:
                workers_to_stop.append(self.file_shortener)
            if hasattr(self, "remove_worker") and self.remove_worker:
                workers_to_stop.append(self.remove_worker)
            if hasattr(self, "duplicate_finder") and self.duplicate_finder:
                workers_to_stop.append(self.duplicate_finder)

            # Stop all threads
            for worker in workers_to_stop:
                if worker and worker.isRunning():
                    logger.info(f"Stopping worker: {worker.__class__.__name__}")
                    worker.stop()

            logger.info("ToolsTab: All threads have been stopped")

        except Exception as e:
            logger.error(f"Error stopping threads in ToolsTab: {e}")

        # Accept the close event
        event.accept()

    def _on_webp_conversion_clicked(self):
        """Handles WebP conversion button click"""
        logger.debug(
            f"WebP button clicked. Working folder: {self.current_working_directory}"
        )
        logger.debug(f"WebP button enabled: {self.webp_button.isEnabled()}")

        description = (
            "This operation:\n"
            "• Converts JPG, PNG, GIF, BMP, TIFF files to WebP\n"
            "• Skips existing WebP files\n"
            "• Removes original files after successful conversion\n"
            "• Optimizes file size"
        )
        self._start_operation_with_confirmation(
            "WebP conversion",
            description,
            lambda: WebPConverterWorker(self.current_working_directory),
        )

    def _on_rebuild_assets_clicked(self):
        """Handles asset rebuild button click"""
        description = (
            "This operation:\n"
            "• Removes all .asset files\n"
            "• Removes .cache folder\n"
            "• Creates new assets based on archive files"
        )
        self._start_operation_with_confirmation(
            "asset rebuild",
            description,
            lambda: AssetRebuilderWorker(self.current_working_directory),
        )

    def _on_archive_double_clicked(self, item: QListWidgetItem):
        """Handles double-click on an archive file"""
        file_name = item.data(Qt.ItemDataRole.UserRole)
        if not file_name or not self.current_working_directory:
            return

        full_path = os.path.join(self.current_working_directory, file_name)
        if os.path.exists(full_path):
            try:
                # Open archive in default application
                if sys.platform == "win32":
                    os.startfile(full_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", full_path], check=True, timeout=10)
                else:  # Linux
                    subprocess.run(["xdg-open", full_path], check=True, timeout=10)
                logger.info(f"Opened archive: {full_path}")
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout while opening archive: {full_path}")
                QMessageBox.warning(
                    self, "Error", f"Timeout while opening archive"
                )
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Process error while opening archive {full_path}: {e}"
                )
                QMessageBox.warning(
                    self, "Error", f"Process error while opening archive"
                )
            except Exception as e:
                logger.error(f"Error opening archive {full_path}: {e}")
                QMessageBox.warning(self, "Error", f"Cannot open archive: {e}")
        else:
            logger.warning(f"File does not exist: {full_path}")
            QMessageBox.warning(self, "Error", f"File does not exist: {file_name}")

    def _on_preview_double_clicked(self, item: QListWidgetItem):
        """Handles double-click on a preview file"""
        file_name = item.data(Qt.ItemDataRole.UserRole)
        if not file_name or not self.current_working_directory:
            return

        full_path = os.path.join(self.current_working_directory, file_name)
        if os.path.exists(full_path):
            try:
                # Open preview in preview window
                from core.preview_window import PreviewWindow

                # Protection against multiple windows
                if hasattr(self, "preview_window") and self.preview_window:
                    self.preview_window.close()

                self.preview_window = PreviewWindow(full_path, self)
                self.preview_window.show_window()
                logger.info(f"Opened preview: {full_path}")
            except Exception as e:
                logger.error(f"Error opening preview {full_path}: {e}")
                QMessageBox.warning(self, "Error", f"Cannot open preview: {e}")
        else:
            logger.warning(f"File does not exist: {full_path}")
            QMessageBox.warning(self, "Error", f"File does not exist: {file_name}")

    def _on_image_resizing_clicked(self):
        """Handles image resizing button click"""
        logger.debug(
            f"Image Resizer button clicked. Working folder: {self.current_working_directory}"
        )
        logger.debug(
            f"Image Resizer button enabled: {self.image_resizer_button.isEnabled()}"
        )

        description = (
            "This operation:\n"
            "• Resizes images according to specific scaling rules\n"
            "• Skips images that don't need resizing\n"
            "• Optimizes file size"
        )
        self._start_operation_with_confirmation(
            "image resizing",
            description,
            lambda: ImageResizerWorker(self.current_working_directory),
        )

    def _on_file_renaming_clicked(self):
        """Handles file name randomization button click"""
        if not self._validate_working_directory():
            return

        max_name_length, ok = QInputDialog.getInt(
            self,
            "Character Limit",
            "Enter maximum file name length (without extension):",
            16,  # Default limit
            1,  # Minimum limit
            256,  # Maximum limit
            1,  # Step
        )

        if ok:
            self._start_file_renaming(max_name_length)

    def _start_file_renaming(self, max_name_length: int):
        """Starts file name randomization"""
        # Create worker for name randomization
        self.file_renamer = FileRenamerWorker(
            self.current_working_directory, max_name_length
        )

        # Additional signal connection for user confirmation
        self.file_renamer.user_confirmation_needed.connect(self._show_pairs_dialog)

        # Use common worker handling method
        self._handle_worker_lifecycle(
            self.file_renamer, self.file_renamer_button, "Randomize File Names"
        )

    def _on_file_shortening_clicked(self):
        """Handles file name shortening button click"""
        if not self._validate_working_directory():
            return

        max_name_length, ok = QInputDialog.getInt(
            self,
            "Character Limit",
            "Enter maximum file name length (without extension):",
            16,  # Default limit
            1,  # Minimum limit
            256,  # Maximum limit
            1,  # Step
        )

        if ok:
            self._start_file_shortening(max_name_length)

    def _start_file_shortening(self, max_name_length: int):
        """Starts file name shortening"""
        # Create worker for name shortening
        self.file_shortener = FileShortenerWorker(
            self.current_working_directory, max_name_length
        )

        # Additional signal connection for user confirmation
        self.file_shortener.user_confirmation_needed.connect(self._show_pairs_dialog_shortener)

        # Use common worker handling method
        self._handle_worker_lifecycle(
            self.file_shortener, self.file_shortener_button, "Shorten File Names"
        )

    def _on_remove_clicked(self):
        """Handles remove prefix/suffix button click"""
        if not self._validate_working_directory():
            return

        # Create a better dialog for operation and text selection
        dialog = QDialog(self)
        dialog.setWindowTitle("Remove prefixes/suffixes")
        dialog.setModal(True)
        dialog.resize(450, 200)

        layout = QVBoxLayout(dialog)

        # Mode selection section
        mode_label = QLabel("Select operation mode:")
        mode_label.setProperty("class", "mode-label")
        layout.addWidget(mode_label)

        # Radio buttons for mode selection
        mode_layout = QHBoxLayout()

        # Button group (only one can be selected)
        button_group = QButtonGroup()

        prefix_radio = QRadioButton("Remove PREFIX (start of name)")
        suffix_radio = QRadioButton("Remove SUFFIX (end of name)")

        # Add to group (only one can be active)
        button_group.addButton(prefix_radio)
        button_group.addButton(suffix_radio)

        # Default to prefix
        prefix_radio.setChecked(True)

        mode_layout.addWidget(prefix_radio)
        mode_layout.addWidget(suffix_radio)
        layout.addLayout(mode_layout)

        # Text input section
        text_label = QLabel("Text to remove (case sensitive):")
        text_label.setProperty("class", "text-label")
        layout.addWidget(text_label)

        # Larger text field
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(60)
        text_edit.setPlaceholderText("Enter the text to be removed from file names...")
        text_edit.setProperty("class", "tool-text")
        layout.addWidget(text_edit)

        # Examples
        example_label = QLabel(
            "Examples: _8K, _FINAL, temp_, backup_, ' 0' (space+zero)"
        )
        example_label.setProperty("class", "example-label")
        layout.addWidget(example_label)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("REMOVE")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        # Show dialog
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # IMPORTANT: We don't use strip() to preserve spaces!
            text_to_remove = text_edit.toPlainText().rstrip(
                "\n\r"
            )  # Remove only newlines at the end
            if not text_to_remove:
                QMessageBox.warning(
                    self, "Error", "Please enter the text to remove."
                )
                return

            selected_mode = "prefix" if prefix_radio.isChecked() else "suffix"
            self._start_remove(text_to_remove, selected_mode)

    def _start_remove(self, text_to_remove: str, mode: str):  # Starts removing prefix/suffix from file names
        """Starts removing prefix/suffix from file names"""
        try:
            # Disable button during removal
            self.remove_button.setEnabled(False)
            self.remove_button.setText("Removing...")

            # Create worker for removal
            self.remove_worker = PrefixSuffixRemoverWorker(
                self.current_working_directory, text_to_remove, mode
            )

            # Connect signals
            self.remove_worker.progress_updated.connect(
                lambda c, t, m: self._handle_worker_progress(
                    self.remove_button, c, t, m
                )
            )
            self.remove_worker.finished.connect(
                lambda m: self._handle_worker_finished(
                    self.remove_button, m, "Remove prefix/suffix"
                )
            )
            self.remove_worker.error_occurred.connect(
                lambda e: self._handle_worker_error(
                    self.remove_button, e, "Remove prefix/suffix"
                )
            )

            # Uruchom worker
            self.remove_worker.start()

            logger.info(
                f"Started removing {mode} in folder: {self.current_working_directory}"
            )

        except Exception as e:
            logger.error(f"Error starting removal: {e}")
            QMessageBox.critical(self, "Error", f"Cannot start removal: {e}")
            self._reset_button_state(self.remove_button, "Remove prefix/suffix")

    def _on_find_duplicates_clicked(self):
        """Handles find duplicates button click"""
        if not self._validate_working_directory():
            return

        reply = QMessageBox.question(
            self,
            "Confirm Find Duplicates",
            f"Are you sure you want to find duplicates in folder:\n{self.current_working_directory}?\n\n"
            "Function will compare archive files based on SHA-256 and move newer duplicates "
            "along with related files to '__duplicates__' folder.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._start_find_duplicates()

    def _start_find_duplicates(self):
        """Starts finding duplicates"""
        try:
            # Disable button during operation
            self.find_duplicates_button.setEnabled(False)
            self.find_duplicates_button.setText("Searching...")

            # Create worker for finding duplicates
            self.duplicate_finder = DuplicateFinderWorker(self.current_working_directory)

            # Connect signals
            self.duplicate_finder.progress_updated.connect(
                lambda c, t, m: self._handle_worker_progress(
                    self.find_duplicates_button, c, t, m
                )
            )
            self.duplicate_finder.finished.connect(
                lambda m: self._handle_worker_finished(
                    self.find_duplicates_button, m, "Find Duplicates"
                )
            )
            # Additional connection for folder tree refresh
            self.duplicate_finder.finished.connect(
                lambda m: self._handle_duplicates_finished(m)
            )
            self.duplicate_finder.error_occurred.connect(
                lambda e: self._handle_worker_error(
                    self.find_duplicates_button, e, "Find Duplicates"
                )
            )

            # Start worker
            self.duplicate_finder.start()

            logger.info(
                f"Started finding duplicates in folder: {self.current_working_directory}"
            )

        except Exception as e:
            logger.error(f"Error starting duplicate search: {e}")
            QMessageBox.critical(self, "Error", f"Cannot start finding duplicates: {e}")
            self._reset_button_state(self.find_duplicates_button, "Find Duplicates")

    def _handle_duplicates_finished(self, message: str):
        """Handles completion of duplicate finding operation"""
        try:
            # If operation moved files (doesn't contain "No duplicates found" or "No archive files")
            if "Moved" in message and "files to __duplicates__" in message:
                # Emit signal about folder structure change
                self.folder_structure_changed.emit(self.current_working_directory)
                logger.info(f"Emitted folder_structure_changed signal for: {self.current_working_directory}")
        except Exception as e:
            logger.error(f"Error handling duplicate finding completion: {e}")

    def _show_pairs_dialog(self, pairs):
        """Displays a window with a list of pairs to be renamed"""
        if not pairs:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("File pairs to rename")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Header
        header_label = QLabel(f"Found {len(pairs)} file pairs to process:")
        header_label.setProperty("class", "dialog-header")
        layout.addWidget(header_label)

        # List of pairs
        list_widget = QListWidget()
        for archive_path, preview_path in pairs:
            archive_name = os.path.basename(archive_path)
            preview_name = os.path.basename(preview_path)
            item_text = f"📦 {archive_name}\n 🖼️ {preview_name}"
            list_widget.addItem(item_text)

        layout.addWidget(list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Continue")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Show dialog
        result = dialog.exec()

        # If user cancelled, stop worker
        if result == QDialog.DialogCode.Rejected:
            if hasattr(self, "file_renamer") and self.file_renamer:
                self.file_renamer.quit()
                if not self.file_renamer.wait(3000):
                    self.file_renamer.terminate()
                    self.file_renamer.wait(2000)
        else:
            # User confirmed - continue operation
            self.file_renamer.confirm_operation()

    def _show_pairs_dialog_shortener(self, pairs):  # Displays a window with a list of pairs to be shortened
        """Displays a window with a list of pairs to be shortened"""
        if not pairs:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("File pairs to shorten names")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Header
        header_label = QLabel(f"Found {len(pairs)} file pairs to process:")
        header_label.setProperty("class", "dialog-header")
        layout.addWidget(header_label)

        # List of pairs
        list_widget = QListWidget()
        for archive_path, preview_path in pairs:
            archive_name = os.path.basename(archive_path)
            preview_name = os.path.basename(preview_path)
            item_text = f"📦 {archive_name}\n 🖼️ {preview_name}"
            list_widget.addItem(item_text)

        layout.addWidget(list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Continue")
        cancel_button = QPushButton("Cancel")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Show dialog
        result = dialog.exec()

        # If user cancelled, stop worker
        if result == QDialog.DialogCode.Rejected:
            if hasattr(self, "file_shortener") and self.file_shortener:
                self.file_shortener.quit()
                if not self.file_shortener.wait(3000):
                    self.file_shortener.terminate()
                    self.file_shortener.wait(2000)
        else:
            # User confirmed - continue operation
            self.file_shortener.confirm_operation()

    def clear_working_directory(self):
        """Clears working folder, deactivates buttons and clears lists"""
        self.current_working_directory = ""
        self.clear_lists()
        self._update_button_states()
        self.working_directory_changed.emit("")


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ToolsTab()
    w.show()
    sys.exit(app.exec())
