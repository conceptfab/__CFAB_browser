"""
Widok drzewa folderów z obsługą drag & drop.
Zawiera niestandardowy QTreeView z funkcjonalnością przeciągania assetów.
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QTreeView

logger = logging.getLogger(__name__)


class CustomFolderTreeView(QTreeView):
    """
    Niestandardowy widok drzewa folderów z obsługą drag & drop i menu
    kontekstowego. Obsługuje przeciąganie assetów między folderami oraz
    przebudowę assetów.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlighted_index = None
        self.drag_drop_model = None
        self.file_operations_model = None
        self.current_folder_path_getter = (
            None  # Funkcja do pobierania aktualnego folderu
        )
        self.asset_grid_model = None  # Referencja do modelu siatki assetów
        self.rebuild_callback = None  # Callback do przebudowy assetów

        # Włącz obsługę drop
        self.setAcceptDrops(True)

    def set_models(
        self,
        drag_drop_model,
        file_operations_model,
        current_folder_path_getter,
        asset_grid_model=None,
    ):
        """Ustawia modele potrzebne do obsługi drag & drop."""
        self.drag_drop_model = drag_drop_model
        self.file_operations_model = file_operations_model
        self.current_folder_path_getter = current_folder_path_getter
        self.asset_grid_model = asset_grid_model

    def set_rebuild_callback(self, callback):
        """Ustawia callback do przebudowy assetów."""
        self.rebuild_callback = callback

    def contextMenuEvent(self, event):
        """Obsługuje menu kontekstowe dla folderu."""
        try:
            index = self.indexAt(event.pos())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    folder_path = item.data(Qt.ItemDataRole.UserRole)

                    # Utwórz menu kontekstowe
                    menu = QMenu(self)

                    rebuild_action = QAction("Przebuduj assety", self)
                    rebuild_action.triggered.connect(
                        lambda: self._rebuild_assets_in_folder(folder_path)
                    )
                    menu.addAction(rebuild_action)

                    # Pokaż menu
                    menu.exec(event.globalPos())

        except Exception as e:
            logger.error(f"Błąd obsługi menu kontekstowego: {e}")

    def _rebuild_assets_in_folder(self, folder_path: str):
        """Przebudowuje assety w wybranym folderze."""
        try:
            if self.rebuild_callback:
                self.rebuild_callback(folder_path)
            else:
                logger.warning("Brak callbacku do przebudowy assetów")
        except Exception as e:
            logger.error(f"Błąd wywołania callbacku przebudowy: {e}")

    def dragEnterEvent(self, event):
        """Obsługuje zdarzenie wejścia przeciąganego elementu."""
        logger.debug(f"dragEnterEvent triggered - mimeData: {event.mimeData().text()}")
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            event.acceptProposedAction()
            pos = event.position().toPoint()
            logger.debug(f"Accepting drag at position: {pos}")
            self._highlight_folder_at_position(pos)
        else:
            logger.debug("Ignoring drag - invalid mime data")
            event.ignore()

    def dragLeaveEvent(self, event):
        """Obsługuje zdarzenie opuszczenia obszaru przez przeciągany element."""
        logger.debug("dragLeaveEvent triggered")
        self._clear_folder_highlight()

    def dragMoveEvent(self, event):
        """Obsługuje zdarzenie ruchu przeciąganego elementu."""
        logger.debug(
            f"dragMoveEvent triggered at position: {event.position().toPoint()}"
        )
        if event.mimeData().hasText() and event.mimeData().text().startswith(
            "application/x-cfab-asset"
        ):
            index = self.indexAt(event.position().toPoint())
            if index.isValid():
                item = self.model().itemFromIndex(index)
                if item and item.data(Qt.ItemDataRole.UserRole):
                    target_path = item.data(Qt.ItemDataRole.UserRole)
                    logger.debug(f"Valid target path: {target_path}")
                    if self.drag_drop_model and self.drag_drop_model.validate_drop(
                        target_path
                    ):
                        event.acceptProposedAction()
                        self._highlight_folder_at_position(event.position().toPoint())
                        logger.debug("Drag move accepted and highlighted")
                    else:
                        event.ignore()
                        self._clear_folder_highlight()
                        logger.debug("Drag move rejected - validation failed")
                else:
                    event.ignore()
                    self._clear_folder_highlight()
                    logger.debug("Drag move rejected - invalid item")
            else:
                event.ignore()
                self._clear_folder_highlight()
                logger.debug("Drag move rejected - invalid index")
        else:
            event.ignore()
            self._clear_folder_highlight()
            logger.debug("Drag move rejected - invalid mime data")

    def dropEvent(self, event):
        """Obsługuje zdarzenie upuszczenia elementu."""
        try:
            logger.debug(f"DropEvent triggered - mimeData: {event.mimeData().text()}")

            if event.mimeData().hasText() and event.mimeData().text().startswith(
                "application/x-cfab-asset"
            ):
                index = self.indexAt(event.position().toPoint())
                if index.isValid():
                    item = self.model().itemFromIndex(index)
                    if item and item.data(Qt.ItemDataRole.UserRole):
                        target_folder_path = item.data(Qt.ItemDataRole.UserRole)
                        logger.debug(f"Target folder path: {target_folder_path}")

                        if self.drag_drop_model and self.drag_drop_model.validate_drop(
                            target_folder_path
                        ):
                            asset_ids_str = (
                                event.mimeData()
                                .text()
                                .replace("application/x-cfab-asset,", "")
                            )
                            asset_ids = asset_ids_str.split(",")
                            logger.debug(f"Asset IDs to move: {asset_ids}")

                            # Pobierz pełne dane assetów z asset_grid_model
                            assets_to_move = []
                            if self.asset_grid_model:
                                all_assets = self.asset_grid_model.get_assets()
                                logger.debug(f"All assets count: {len(all_assets)}")
                                assets_to_move = [
                                    asset
                                    for asset in all_assets
                                    if asset.get("name") in asset_ids
                                ]
                                logger.debug(
                                    f"Assets to move count: {len(assets_to_move)}"
                                )
                            else:
                                logger.error("asset_grid_model is None!")

                            if (
                                assets_to_move
                                and self.file_operations_model
                                and self.current_folder_path_getter
                            ):
                                source_folder_path = self.current_folder_path_getter()
                                logger.debug(
                                    f"Source folder path: {source_folder_path}"
                                )

                                if source_folder_path:
                                    # Wykonaj operację przenoszenia w osobnym wątku
                                    self.file_operations_model.move_assets(
                                        assets_to_move,
                                        source_folder_path,
                                        target_folder_path,
                                    )
                                    self.drag_drop_model.complete_drop(
                                        target_folder_path, asset_ids
                                    )
                                    event.acceptProposedAction()
                                    logger.info(f"Drop completed successfully")
                                else:
                                    logger.error("Source folder path is empty!")
                                    event.ignore()
                            else:
                                logger.error(
                                    f"Missing required models: assets_to_move={len(assets_to_move)}, file_operations_model={self.file_operations_model is not None}, current_folder_path_getter={self.current_folder_path_getter is not None}"
                                )
                                event.ignore()
                        else:
                            logger.error(
                                f"Drag drop validation failed for: {target_folder_path}"
                            )
                            event.ignore()
                    else:
                        logger.error("Invalid item or no UserRole data")
                        event.ignore()
                else:
                    logger.error("Invalid index")
                    event.ignore()
                self._clear_folder_highlight()
            else:
                logger.error("Invalid mime data")
                event.ignore()
                self._clear_folder_highlight()
        except Exception as e:
            logger.error(f"Error in dropEvent: {e}")
            event.ignore()
            self._clear_folder_highlight()

    def _highlight_folder_at_position(self, pos):
        """Podświetla folder pod podaną pozycją."""
        try:
            index = self.indexAt(pos)
            if index.isValid():
                # Wyczyść poprzednie podświetlenie
                if self._highlighted_index and self._highlighted_index.isValid():
                    # Usuń zaznaczenie z poprzedniego elementu
                    self.selectionModel().clearSelection()

                # Ustaw nowe podświetlenie
                self._highlighted_index = index
                # Zaznacz nowy element
                self.setCurrentIndex(index)
                self.selectionModel().select(
                    index, self.selectionModel().SelectionFlag.Select
                )

                # Wymuś odświeżenie widoku
                self.viewport().update()
                logger.debug(f"Highlighted folder at position: {pos}")
            else:
                logger.debug(f"No valid index at position: {pos}")
        except Exception as e:
            logger.error(f"Error highlighting folder at position {pos}: {e}")

    def _clear_folder_highlight(self):
        """Czyści podświetlenie folderu."""
        try:
            if self._highlighted_index and self._highlighted_index.isValid():
                # Usuń zaznaczenie
                self.selectionModel().clearSelection()
                self.viewport().update()
                logger.debug("Cleared folder highlight")
            self._highlighted_index = None
        except Exception as e:
            logger.error(f"Error clearing folder highlight: {e}")
            self._highlighted_index = None
