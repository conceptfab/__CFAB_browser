import logging
import os
import sys

from PyQt6.QtCore import QSize, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QSizePolicy,
    QSplitter,
)

from core.amv_models.pairing_model import PairingModel
from core.amv_views.preview_gallery_view import PreviewGalleryView
from core.preview_window import PreviewWindow
from core.workers.asset_rebuilder_worker import AssetRebuilderWorker
# thumbnail_cache imported w utilities.clear_thumbnail_cache_after_rebuild()

logger = logging.getLogger(__name__)


class ArchiveListItem(QWidget):
    # Signal emitted when checkbox state changes
    checked = pyqtSignal(str, bool)
    # Signal emitted when file name is clicked
    clicked = pyqtSignal(str)

    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("AssetTileCheckBox")
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        self.label = QLabel(self.file_name)
        layout.addWidget(self.label)
        layout.addStretch(1)

        self.setLayout(layout)

    def contextMenuEvent(self, event):
        """Create context menu for right-click."""
        menu = QMenu(self)
        open_action = QAction("Open in default program", self)
        open_action.triggered.connect(self._handle_open)
        menu.addAction(open_action)
        menu.exec(event.globalPos())

    def _on_checkbox_state_changed(self, state):
        self.checked.emit(self.file_name, state == Qt.CheckState.Checked.value)

    def _handle_open(self):
        """Handle the open action from the context menu."""
        self.clicked.emit(self.file_name)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)

    def sizeHint(self):
        """Returns row height increased by 30%"""
        base_size = super().sizeHint()
        # Increase height by 30%
        increased_height = int(base_size.height() * 1.5)
        return QSize(base_size.width(), increased_height)


class PairingTab(QWidget):
    """Tab for pairing archives and previews, asset creation, and cleanup operations"""
    
    # Signal emitted when pairing changes (files paired/unpaired)
    pairing_changed = pyqtSignal(str)  # folder_path

    def __init__(self):
        super().__init__()
        self.model = PairingModel()
        self.rebuild_thread = None
        self.init_ui()
        # self.load_data() # Data will be loaded on directory change

    def on_working_directory_changed(self, path: str):
        """Slot to be connected to the controller's signal."""
        print(f"PairingTab: Received new working directory: {path}")
        self.model.set_work_folder(path)
        self.load_data()
        self._update_button_states()

    def init_ui(self):
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Horizontal layout for the three columns
        columns_layout = QHBoxLayout()
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setSpacing(5)

        # Left Column: Archive Files List (350px)
        self.archive_list_widget = QListWidget()
        self.archive_list_widget.setFixedWidth(350)  # Increased width
        columns_layout.addWidget(self.archive_list_widget)

        # Middle Column: Buttons (150px)
        button_column_layout = QVBoxLayout()
        button_column_layout.setContentsMargins(0, 0, 0, 0)
        button_column_layout.setSpacing(5)
        button_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.create_asset_button = QPushButton("Create asset")
        self.create_asset_button.setFixedSize(250, 30)  # Increased width
        self.create_asset_button.clicked.connect(self._on_create_asset_button_clicked)
        button_column_layout.addWidget(self.create_asset_button)

        self.delete_previews_button = QPushButton("Delete unpaired previews")
        self.delete_previews_button.setFixedSize(250, 30)  # Increased width
        self.delete_previews_button.clicked.connect(
            self._on_delete_unpaired_images_clicked
        )
        button_column_layout.addWidget(self.delete_previews_button)

        self.delete_archives_button = QPushButton("Delete unpaired archives")
        self.delete_archives_button.setFixedSize(250, 30)  # Increased width
        self.delete_archives_button.clicked.connect(
            self._on_delete_unpaired_archives_clicked
        )
        button_column_layout.addWidget(self.delete_archives_button)

        self.rebuild_assets_button = QPushButton("Rebuild assets")
        self.rebuild_assets_button.setFixedSize(250, 30)  # Increased width
        self.rebuild_assets_button.clicked.connect(self._on_rebuild_assets_clicked)
        button_column_layout.addWidget(self.rebuild_assets_button)

        button_column_layout.addStretch(1)
        columns_layout.addLayout(button_column_layout)

        # Right Column: Preview Gallery and Slider
        right_column_layout = QVBoxLayout()
        self.preview_gallery_view = PreviewGalleryView()
        self.preview_gallery_view.preview_selected.connect(self._on_preview_selected)
        self.preview_gallery_view.preview_clicked.connect(self._on_preview_clicked)
        right_column_layout.addWidget(self.preview_gallery_view)

        # Slider for thumbnail size below the gallery
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(64)
        self.size_slider.setMaximum(256)
        self.size_slider.setValue(128)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(32)
        self.size_slider.valueChanged.connect(
            self.preview_gallery_view.on_slider_value_changed
        )
        right_column_layout.addWidget(self.size_slider)

        columns_layout.addLayout(right_column_layout)

        # Add columns layout to main layout
        main_layout.addLayout(columns_layout)

        self.setLayout(main_layout)
        self._update_create_asset_button_state()

    def load_data(self):
        self.archive_list_widget.clear()
        # Clear selection state
        self.selected_archive = None
        self.selected_preview = None

        # Sort archives alphabetically
        sorted_archives = sorted(self.model.get_unpaired_archives(), key=str.lower)
        for archive_file in sorted_archives:
            item_widget = ArchiveListItem(archive_file)
            item_widget.checked.connect(self._on_archive_checked)
            item_widget.clicked.connect(self._on_archive_clicked)
            list_item = QListWidgetItem(self.archive_list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.archive_list_widget.addItem(list_item)
            self.archive_list_widget.setItemWidget(list_item, item_widget)

        # Construct full paths for previews before sending them to the gallery view
        work_folder = (
            self.model.work_folder if hasattr(self.model, "work_folder") else ""
        )

        # Validate work_folder path
        if not work_folder or not os.path.exists(work_folder):
            logger.warning(f"Invalid work_folder path: {work_folder}")
            work_folder = ""
        preview_files = self.model.get_unpaired_images()
        logger.info(f"Loaded {len(preview_files)} preview files from model")

        if work_folder:
            # Sort previews alphabetically
            sorted_preview_files = sorted(preview_files, key=str.lower)
            full_preview_paths = [
                os.path.join(work_folder, f) for f in sorted_preview_files
            ]
            logger.info(f"Created {len(full_preview_paths)} full preview paths")
            logger.debug(f"First 5 preview paths: {full_preview_paths[:5]}")
            self.preview_gallery_view.set_previews(full_preview_paths)
        else:
            logger.warning("No work folder available, clearing previews")
            self.preview_gallery_view.set_previews(
                []
            )  # Clear previews if no folder is set

        self._update_button_states()
        self.archive_list_widget.update()
        self.preview_gallery_view.update()
        
        # Notify about data change to update tab indicator
        self._notify_pairing_changed()

    def _on_archive_checked(self, file_name, checked):
        if checked:
            # Uncheck all other archives
            for i in range(self.archive_list_widget.count()):
                item = self.archive_list_widget.item(i)
                item_widget = self.archive_list_widget.itemWidget(item)
                if item_widget.file_name != file_name and item_widget.is_checked():
                    item_widget.set_checked(False)
            self.selected_archive = file_name
        else:
            if hasattr(self, "selected_archive") and self.selected_archive == file_name:
                self.selected_archive = None
        self._update_button_states()

    def _on_archive_clicked(self, file_name):
        work_folder = (
            self.model.work_folder if hasattr(self.model, "work_folder") else ""
        )
        if not work_folder:
            print("Error: Could not determine work folder to open archive.")
            return

        full_path = os.path.join(work_folder, file_name)
        print(f"Opening archive: {full_path}")
        
        # Path validation
        if not os.path.exists(full_path):
            logger.error(f"File does not exist: {full_path}")
            return
            
        try:
            if sys.platform == "win32":
                os.startfile(full_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", full_path], check=True, timeout=10)
            else:  # linux
                subprocess.run(["xdg-open", full_path], check=True, timeout=10)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while opening file: {full_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Process error while opening file {full_path}: {e}")
        except Exception as e:
            logger.error(f"Error while opening file {full_path}: {e}")
        self.selected_preview = file_name if file_name else None
        self._update_button_states()

    def _on_preview_selected(self, file_name: str):
        self.selected_preview = file_name if file_name else None
        self._update_button_states()

    def _on_preview_clicked(self, file_path: str):
        print(f"Opening preview: {file_path}")
        # Zabezpieczenie przed wieloma oknami
        if hasattr(self, "preview_window") and self.preview_window:
            self.preview_window.close()

        self.preview_window = PreviewWindow(file_path)
        self.preview_window.show_window()

    def _remove_paired_items_from_ui(self, archive_name: str, preview_full_path: str):
        """Removes paired items from UI without reloading the entire list"""
        # Remove archive from archives list
        for i in range(self.archive_list_widget.count()):
            item = self.archive_list_widget.item(i)
            item_widget = self.archive_list_widget.itemWidget(item)
            if item_widget and item_widget.file_name == archive_name:
                self.archive_list_widget.takeItem(i)
                print(f"Removed archive from UI: {archive_name}")
                break

        # Remove preview from preview gallery
        preview_name = os.path.basename(preview_full_path)
        self.preview_gallery_view.remove_preview_by_path(preview_full_path)
        print(f"Removed preview from UI: {preview_name}")

    def _update_button_states(self):
        """Updates the state of all buttons based on the working folder"""
        working_folder_valid = self._validate_working_folder()
        selection_state = self._get_selection_state()
        
        self._update_basic_buttons(working_folder_valid)
        self._update_create_asset_button(working_folder_valid, selection_state)

    def _update_create_asset_button_state(self):
        """Updates the state of the 'Create asset' button - now uses _update_button_states()"""
        self._update_button_states()

    def _on_create_asset_button_clicked(self):
        if (
            hasattr(self, "selected_archive")
            and self.selected_archive
            and hasattr(self, "selected_preview")
            and self.selected_preview
        ):

            work_folder = (
                self.model.work_folder if hasattr(self.model, "work_folder") else ""
            )
            if not work_folder:
                print("Error: Could not determine work folder to create asset.")
                return

            archive_full_path = os.path.join(work_folder, self.selected_archive)
            # self.selected_preview is already a full path from the gallery
            preview_full_path = self.selected_preview

            # Double-check that paths exist before proceeding
            if not os.path.exists(archive_full_path):
                print(f"FATAL ERROR: Archive path does not exist: {archive_full_path}")
                return
            if not os.path.exists(preview_full_path):
                print(f"FATAL ERROR: Preview path does not exist: {preview_full_path}")
                return

            success = self.model.create_asset_from_pair(
                archive_full_path, preview_full_path
            )
            if success:
                print("Asset created successfully. Removing items from lists...")
                self._remove_paired_items_from_ui(
                    self.selected_archive, preview_full_path
                )
                # Reset selection
                self.selected_archive = None
                self.selected_preview = None
                self._update_create_asset_button_state()
                # Notify about pairing change
                self._notify_pairing_changed()
            else:
                print("Failed to create asset.")

    def _on_delete_unpaired_images_clicked(self):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to delete ALL unpaired previews from the list and disk?\nThis operation cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = self.model.delete_unpaired_images()
            if success:
                QMessageBox.information(
                    self, "Success", "Successfully deleted unpaired previews."
                )
                # Notify about pairing change
                self._notify_pairing_changed()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "An error occurred while deleting previews. Check the logs.",
                )
            self.load_data()

    def _on_delete_unpaired_archives_clicked(self):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to delete ALL unpaired archives from the list and disk?\nThis operation cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = self.model.delete_unpaired_archives()
            if success:
                QMessageBox.information(
                    self, "Success", "Successfully deleted unpaired archives."
                )
                # Notify about pairing change
                self._notify_pairing_changed()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "An error occurred while deleting archives. Check the logs.",
                )
            self.load_data()

    def _on_rebuild_assets_clicked(self):
        # Use the working folder from the model instead of the folder from the unpair_files.json file
        work_folder = (
            self.model.work_folder if hasattr(self.model, "work_folder") else ""
        )

        if not work_folder or not os.path.exists(work_folder):
            QMessageBox.warning(
                self, "Error", "The working folder is not set or does not exist."
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to rebuild all assets in the folder:\n{work_folder}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.rebuild_thread = AssetRebuilderWorker(work_folder)
            self.rebuild_thread.finished.connect(self._on_rebuild_finished)
            self.rebuild_thread.error_occurred.connect(self._on_rebuild_error)
            # We can also connect progress_updated if we add a progress bar
            self.rebuild_thread.start()
            QMessageBox.information(
                self,
                "Process started",
                f"Asset rebuild started in folder:\n{work_folder}",
            )

    def _on_rebuild_finished(self, message):
        # ABSOLUTE CLEARING OF RAM CACHE AFTER REBUILDING ASSETS!!!
        from core.utilities import clear_thumbnail_cache_after_rebuild
        clear_thumbnail_cache_after_rebuild(is_error=False)
        
        QMessageBox.information(self, "Success", message)
        self.load_data()  # Refresh data as assets might have changed

    def _on_rebuild_error(self, error_message):
        # CATEGORICAL CLEARING OF RAM CACHE EVEN AFTER REBUILD ERROR!!!
        from core.utilities import clear_thumbnail_cache_after_rebuild
        clear_thumbnail_cache_after_rebuild(is_error=True)
        
        QMessageBox.critical(self, "Rebuild error", error_message)

    # ===============================================
    # HELPER FUNCTIONS FOR _update_button_states
    # ===============================================
    
    def _validate_working_folder(self) -> bool:
        """Validate if working folder exists and is accessible"""
        return bool(
            hasattr(self.model, "work_folder")
            and self.model.work_folder
            and os.path.exists(self.model.work_folder)
        )
    
    def _get_selection_state(self) -> dict:
        """Get current selection state for archive and preview"""
        return {
            "archive_selected": (
                hasattr(self, "selected_archive") and self.selected_archive is not None
            ),
            "preview_selected": (
                hasattr(self, "selected_preview") and self.selected_preview is not None
            )
        }
    
    def _update_basic_buttons(self, enabled: bool):
        """Update states of basic operation buttons"""
        if hasattr(self, "delete_previews_button"):
            self.delete_previews_button.setEnabled(enabled)
        if hasattr(self, "delete_archives_button"):
            self.delete_archives_button.setEnabled(enabled)
        if hasattr(self, "rebuild_assets_button"):
            self.rebuild_assets_button.setEnabled(enabled)
    
    def _update_create_asset_button(self, folder_valid: bool, selection: dict):
        """Update create asset button based on folder and selection state"""
        if hasattr(self, "create_asset_button"):
            can_create = (
                folder_valid 
                and selection["archive_selected"] 
                and selection["preview_selected"]
            )
            self.create_asset_button.setEnabled(can_create)

    def _notify_pairing_changed(self):
        """Emit signal that pairing has changed to update tab indicator"""
        try:
            if hasattr(self.model, 'work_folder') and self.model.work_folder:
                self.pairing_changed.emit(self.model.work_folder)
                logger.debug(f"Emitted pairing_changed signal for: {self.model.work_folder}")
        except Exception as e:
            logger.error(f"Error emitting pairing_changed signal: {e}")
