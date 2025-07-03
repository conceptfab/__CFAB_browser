import logging
import os
import subprocess
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.amv_models.pairing_model import PairingModel
from core.amv_views.preview_gallery_view import PreviewGalleryView
from core.preview_window import PreviewWindow
from core.workers.asset_rebuilder_worker import AssetRebuilderWorker

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
        self.checkbox.stateChanged.connect(self._on_checkbox_state_changed)
        layout.addWidget(self.checkbox)

        self.label = QLabel(self.file_name)
        layout.addWidget(self.label)
        layout.addStretch(1)

        self.setLayout(layout)

    def contextMenuEvent(self, event):
        """Create context menu for right-click."""
        menu = QMenu(self)
        open_action = QAction("Otwórz w programie domyślnym", self)
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


class PairingTab(QWidget):
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

        self.create_asset_button = QPushButton("Utwórz asset")
        self.create_asset_button.setFixedSize(250, 30)  # Increased width
        self.create_asset_button.clicked.connect(self._on_create_asset_button_clicked)
        button_column_layout.addWidget(self.create_asset_button)

        self.delete_previews_button = QPushButton("Usuń podglądy bez pary")
        self.delete_previews_button.setFixedSize(250, 30)  # Increased width
        self.delete_previews_button.clicked.connect(
            self._on_delete_unpaired_images_clicked
        )
        button_column_layout.addWidget(self.delete_previews_button)

        self.delete_archives_button = QPushButton("Usuń archiwa bez pary")
        self.delete_archives_button.setFixedSize(250, 30)  # Increased width
        self.delete_archives_button.clicked.connect(
            self._on_delete_unpaired_archives_clicked
        )
        button_column_layout.addWidget(self.delete_archives_button)

        self.rebuild_assets_button = QPushButton("Przebuduj assety")
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

        # Sortuj archiwa alfabetycznie
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

        # Walidacja ścieżki work_folder
        if not work_folder or not os.path.exists(work_folder):
            logger.warning(f"Nieprawidłowa ścieżka work_folder: {work_folder}")
            work_folder = ""
        preview_files = self.model.get_unpaired_images()
        logger.info(f"Loaded {len(preview_files)} preview files from model")

        if work_folder:
            # Sortuj podglądy alfabetycznie
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

        self._update_create_asset_button_state()
        self.archive_list_widget.update()
        self.preview_gallery_view.update()

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
        self._update_create_asset_button_state()

    def _on_archive_clicked(self, file_name):
        work_folder = (
            self.model.work_folder if hasattr(self.model, "work_folder") else ""
        )
        if not work_folder:
            print("Error: Could not determine work folder to open archive.")
            return

        full_path = os.path.join(work_folder, file_name)
        print(f"Opening archive: {full_path}")
        if sys.platform == "win32":
            os.startfile(full_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", full_path])
        else:  # linux
            subprocess.Popen(["xdg-open", full_path])
        self.selected_preview = file_name if file_name else None
        self._update_create_asset_button_state()

    def _on_preview_selected(self, file_name: str):
        self.selected_preview = file_name if file_name else None
        self._update_create_asset_button_state()

    def _on_preview_clicked(self, file_path: str):
        print(f"Opening preview: {file_path}")
        self.preview_window = PreviewWindow(file_path)
        self.preview_window.show()

    def _remove_paired_items_from_ui(self, archive_name: str, preview_full_path: str):
        """Usuwa sparowane elementy z UI bez przeładowywania całej listy"""
        # Usuń archiwum z listy archiwów
        for i in range(self.archive_list_widget.count()):
            item = self.archive_list_widget.item(i)
            item_widget = self.archive_list_widget.itemWidget(item)
            if item_widget and item_widget.file_name == archive_name:
                self.archive_list_widget.takeItem(i)
                print(f"Removed archive from UI: {archive_name}")
                break

        # Usuń podgląd z galerii podglądów
        preview_name = os.path.basename(preview_full_path)
        self.preview_gallery_view.remove_preview_by_path(preview_full_path)
        print(f"Removed preview from UI: {preview_name}")

    def _update_create_asset_button_state(self):
        is_archive_selected = (
            hasattr(self, "selected_archive") and self.selected_archive is not None
        )
        is_preview_selected = (
            hasattr(self, "selected_preview") and self.selected_preview is not None
        )
        self.create_asset_button.setEnabled(is_archive_selected and is_preview_selected)

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
            else:
                print("Failed to create asset.")

    def _on_delete_unpaired_images_clicked(self):
        reply = QMessageBox.question(
            self,
            "Potwierdzenie",
            "Czy na pewno chcesz usunąć WSZYSTKIE niesparowane podglądy z listy i z dysku?\nTej operacji nie można cofnąć.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = self.model.delete_unpaired_images()
            if success:
                QMessageBox.information(
                    self, "Sukces", "Pomyślnie usunięto niesparowane podglądy."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Błąd",
                    "Wystąpił błąd podczas usuwania podglądów. Sprawdź logi.",
                )
            self.load_data()

    def _on_delete_unpaired_archives_clicked(self):
        reply = QMessageBox.question(
            self,
            "Potwierdzenie",
            "Czy na pewno chcesz usunąć WSZYSTKIE niesparowane archiwa z listy i z dysku?\nTej operacji nie można cofnąć.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            success = self.model.delete_unpaired_archives()
            if success:
                QMessageBox.information(
                    self, "Sukces", "Pomyślnie usunięto niesparowane archiwa."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Błąd",
                    "Wystąpił błąd podczas usuwania archiwów. Sprawdź logi.",
                )
            self.load_data()

    def _on_rebuild_assets_clicked(self):
        # Użyj folderu roboczego z modelu zamiast folderu z pliku unpair_files.json
        work_folder = (
            self.model.work_folder if hasattr(self.model, "work_folder") else ""
        )

        if not work_folder or not os.path.exists(work_folder):
            QMessageBox.warning(
                self, "Błąd", "Folder roboczy nie jest ustawiony lub nie istnieje."
            )
            return

        reply = QMessageBox.question(
            self,
            "Potwierdzenie",
            f"Czy na pewno chcesz przebudować wszystkie assety w folderze:\n{work_folder}?",
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
                "Proces rozpoczęty",
                f"Rozpoczęto przebudowę assetów w folderze:\n{work_folder}",
            )

    def _on_rebuild_finished(self, message):
        QMessageBox.information(self, "Sukces", message)
        self.load_data()  # Refresh data as assets might have changed

    def _on_rebuild_error(self, error_message):
        QMessageBox.critical(self, "Błąd przebudowy", error_message)
