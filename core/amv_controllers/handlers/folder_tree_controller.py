import logging

from PyQt6.QtCore import QObject, Qt

logger = logging.getLogger(__name__)


class FolderTreeController(QObject):
    def __init__(self, model, view, controller):
        super().__init__()
        self.model = model
        self.view = view
        self.controller = controller

    def setup(self):
        tree_model = self.model.folder_system_model.get_tree_model()
        self.view.folder_tree_view.setModel(tree_model)
        self.view.folder_tree_view.clicked.connect(self.on_tree_item_clicked)
        self.view.folder_tree_view.expanded.connect(self.on_tree_item_expanded)
        self.view.folder_tree_view.collapsed.connect(self.on_tree_item_collapsed)

        if hasattr(self.view.folder_tree_view, "set_models"):
            self.view.folder_tree_view.set_models(
                self.model.drag_drop_model,
                self.model.file_operations_model,
                self.model.asset_grid_model.get_current_folder,
                self.model.asset_grid_model,
            )

        if hasattr(self.view.folder_tree_view, "set_rebuild_callback"):
            self.view.folder_tree_view.set_rebuild_callback(
                self.controller.asset_rebuild_controller.rebuild_assets_in_folder
            )

        if hasattr(self.view.folder_tree_view, "set_open_in_explorer_callback"):
            from core.file_utils import open_path_in_explorer

            self.view.folder_tree_view.set_open_in_explorer_callback(
                lambda path: open_path_in_explorer(path, self.view)
            )

        if hasattr(self.view.folder_tree_view, "set_refresh_folder_callback"):
            self.view.folder_tree_view.set_refresh_folder_callback(
                self.on_folder_refresh_requested
            )

        # Podpięcie sygnału currentChanged po ustawieniu modelu
        if hasattr(self.view.folder_tree_view, "_on_current_folder_changed"):
            sel_model = self.view.folder_tree_view.selectionModel()
            if sel_model:
                sel_model.currentChanged.connect(
                    self.view.folder_tree_view._on_current_folder_changed
                )

        logger.debug("Folder system model connected to view - ETAP 6")

    def on_folder_structure_changed(self, tree_model):
        self.view.folder_tree_view.setModel(tree_model)
        if tree_model.rowCount() > 0:
            root_index = tree_model.index(0, 0)
            self.view.folder_tree_view.expand(root_index)
        logger.debug("Folder structure updated in view")

    def on_folder_clicked(self, folder_path: str):
        logger.info("Folder clicked: %s", folder_path)
        self.model.asset_grid_model.set_current_folder(folder_path)
        self.model.asset_grid_model.scan_folder(folder_path)
        self.controller.control_panel_controller.update_button_states()
        logger.info(f"Emituję sygnał working_directory_changed: {folder_path}")
        self.controller.working_directory_changed.emit(folder_path)
        logger.info("Sygnał working_directory_changed został wyemitowany")

    def on_workspace_folder_clicked(self, folder_path: str):
        logger.info("Workspace folder clicked: %s", folder_path)
        self.model.folder_system_model.set_root_folder(folder_path)
        self.model.asset_grid_model.set_current_folder(folder_path)
        self.model.asset_grid_model.scan_folder(folder_path)
        self.controller.control_panel_controller.update_button_states()

    def on_tree_item_clicked(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            self.model.folder_system_model.on_folder_clicked(folder_path)

    def on_tree_item_expanded(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            self.model.folder_system_model.expand_folder(item)

    def on_tree_item_collapsed(self, index):
        model = self.view.folder_tree_view.model()
        item = model.itemFromIndex(index)
        if item:
            folder_path = item.data(Qt.ItemDataRole.UserRole)
            self.model.folder_system_model.collapse_folder(folder_path)

    def on_collapse_tree_requested(self):
        logger.info("Zwijanie wszystkich elementów drzewa folderów")
        try:
            self.view.folder_tree_view.collapseAll()
            logger.debug("Drzewo folderów zostało zwinięte")
        except Exception as e:
            logger.error(f"Błąd podczas zwijania drzewa folderów: {e}")
        self.controller.control_panel_controller.update_button_states()

    def on_expand_tree_requested(self):
        logger.info("Rozwijanie wszystkich węzłów drzewa folderów")
        try:
            self.view.folder_tree_view.expandAll()
            logger.debug("Pomyślnie rozwinięto wszystkie węzły drzewa")
        except Exception as e:
            logger.error(f"Błąd podczas rozwijania drzewa: {e}")
        self.controller.control_panel_controller.update_button_states()

    def on_folder_refresh_requested(self, folder_path: str):
        """Obsługuje żądanie odświeżenia folderu z menu kontekstowego."""
        logger.info(f"Odświeżanie folderu: {folder_path}")
        try:
            # Odśwież strukturę drzewa folderów
            self.model.folder_system_model.refresh_folder(folder_path)

            # Jeśli to aktualnie wybrany folder, odśwież też siatkę assetów
            current_folder = self.model.asset_grid_model.get_current_folder()
            if current_folder == folder_path:
                self.model.asset_grid_model.scan_folder(folder_path)
                self.controller.control_panel_controller.update_button_states()
                logger.info(f"Odświeżono siatkę assetów dla folderu: {folder_path}")

            logger.debug(f"Pomyślnie odświeżono folder: {folder_path}")
        except Exception as e:
            logger.error(f"Błąd podczas odświeżania folderu {folder_path}: {e}")
