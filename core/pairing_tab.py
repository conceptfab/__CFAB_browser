import os
import subprocess
import sys

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.amv_models.pairing_model import PairingModel
from core.amv_views.preview_gallery_view import PreviewGalleryView
from core.preview_window import PreviewWindow


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
        self.label.linkActivated.connect(self._on_label_clicked)
        # Make label clickable
        self.label.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        layout.addWidget(self.label)
        layout.addStretch(1)

        self.setLayout(layout)

    def _on_checkbox_state_changed(self, state):
        self.checked.emit(self.file_name, state == Qt.CheckState.Checked.value)

    def _on_label_clicked(self):
        self.clicked.emit(self.file_name)

    def is_checked(self):
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        self.checkbox.setChecked(checked)


class PairingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.model = PairingModel()
        self.init_ui()
        # self.load_data() # Data will be loaded on directory change

    def on_working_directory_changed(self, path: str):
        """Slot to be connected to the controller's signal."""
        print(f"PairingTab: Received new working directory: {path}")
        self.model.set_work_folder(path)
        self.load_data()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Left Column: Archive Files List (200px)
        self.archive_list_widget = QListWidget()
        self.archive_list_widget.setFixedWidth(200)
        main_layout.addWidget(self.archive_list_widget)

        # Middle Column: Buttons (75px)
        button_column_layout = QVBoxLayout()
        button_column_layout.setContentsMargins(0, 0, 0, 0)
        button_column_layout.setSpacing(5)
        button_column_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.create_asset_button = QPushButton("Utwórz asset")
        self.create_asset_button.setFixedSize(75, 30)
        self.create_asset_button.clicked.connect(self._on_create_asset_button_clicked)
        button_column_layout.addWidget(self.create_asset_button)

        self.button2 = QPushButton("Przycisk 2")
        self.button2.setFixedSize(75, 30)
        button_column_layout.addWidget(self.button2)

        self.button3 = QPushButton("Przycisk 3")
        self.button3.setFixedSize(75, 30)
        button_column_layout.addWidget(self.button3)

        # Add a spacer to push buttons to the top
        button_column_layout.addStretch(1)

        main_layout.addLayout(button_column_layout)

        # Right Column: Preview Gallery (remaining space)
        self.preview_gallery_view = PreviewGalleryView()
        self.preview_gallery_view.preview_selected.connect(self._on_preview_selected)
        self.preview_gallery_view.preview_clicked.connect(self._on_preview_clicked)
        main_layout.addWidget(self.preview_gallery_view)

        self.setLayout(main_layout)
        self._update_create_asset_button_state()

    def load_data(self):
        self.archive_list_widget.clear()
        # Clear selection state
        self.selected_archive = None
        self.selected_preview = None

        for archive_file in self.model.get_unpaired_archives():
            item_widget = ArchiveListItem(archive_file)
            item_widget.checked.connect(self._on_archive_checked)
            item_widget.clicked.connect(self._on_archive_clicked)
            list_item = QListWidgetItem(self.archive_list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.archive_list_widget.addItem(list_item)
            self.archive_list_widget.setItemWidget(list_item, item_widget)

        # Construct full paths for previews before sending them to the gallery view
        work_folder = (
            os.path.dirname(self.model.unpair_files_path)
            if self.model.unpair_files_path
            else ""
        )
        preview_files = self.model.get_unpaired_previews()

        if work_folder:
            full_preview_paths = [os.path.join(work_folder, f) for f in preview_files]
            self.preview_gallery_view.set_previews(full_preview_paths)
        else:
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
            os.path.dirname(self.model.unpair_files_path)
            if self.model.unpair_files_path
            else ""
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

            work_folder = os.path.dirname(self.model.unpair_files_path)
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
                print("Asset created successfully. Refreshing data...")
                self.load_data()
            else:
                print("Failed to create asset.")
