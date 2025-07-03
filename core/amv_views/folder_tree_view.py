"""
Widok drzewa folderów z obsługą drag & drop.
Zawiera niestandardowy QTreeView z funkcjonalnością przeciągania assetów.
"""

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu, QTreeView

from core.file_utils import open_path_in_explorer

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
        self.open_in_explorer_callback = None  # Callback do otwierania w eksploratorze
        self.refresh_folder_callback = None  # Callback do odświeżania folderu

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

    def set_open_in_explorer_callback(self, callback):
        """Ustawia callback do otwierania folderu w eksploratorze."""
        self.open_in_explorer_callback = callback

    def set_refresh_folder_callback(self, callback):
        """Ustawia callback do odświeżania folderu."""
        self.refresh_folder_callback = callback

    def contextMenuEvent(self, event):
        """Obsługuje menu kontekstowe dla folderu."""
        try:
            index = self.indexAt(event.pos())
            logger.debug(
                f"contextMenuEvent - index: {index}, isValid: {index.isValid()}"
            )
            logger.debug(f"contextMenuEvent - pozycja myszy: {event.pos()}")

            if index.isValid():
                item = self.model().itemFromIndex(index)
                logger.debug(f"contextMenuEvent - item: {item}")
                logger.debug(
                    f"contextMenuEvent - item text: {item.text() if item else 'None'}"
                )

                if item and item.data(Qt.ItemDataRole.UserRole):
                    folder_path = item.data(Qt.ItemDataRole.UserRole)
                    logger.debug(f"contextMenuEvent - folder_path: {folder_path}")
                    logger.debug(
                        f"contextMenuEvent - item row: {item.row()}, column: {item.column()}"
                    )

                    # Utwórz menu kontekstowe
                    menu = QMenu(self)

                    # Opcja odświeżenia folderu (na górze)
                    refresh_folder_action = QAction("Odśwież folder", self)
                    refresh_folder_action.triggered.connect(
                        lambda checked, path=folder_path: self._refresh_folder(path)
                    )
                    menu.addAction(refresh_folder_action)

                    # Separator
                    menu.addSeparator()

                    # Opcja otwarcia w eksploratorze
                    open_in_explorer_action = QAction("Otwórz w Eksploratorze", self)
                    open_in_explorer_action.triggered.connect(
                        lambda checked, path=folder_path: self._open_folder_in_explorer(
                            path
                        )
                    )
                    menu.addAction(open_in_explorer_action)

                    # Separator
                    menu.addSeparator()

                    # Opcja przebudowy assetów
                    rebuild_action = QAction("Przebuduj assety", self)
                    rebuild_action.triggered.connect(
                        lambda checked, path=folder_path: self._rebuild_assets_in_folder(
                            path
                        )
                    )
                    menu.addAction(rebuild_action)

                    # Pokaż menu
                    menu.exec(event.globalPos())
                else:
                    logger.warning(
                        "contextMenuEvent - item lub UserRole data jest None"
                    )
                    if item:
                        logger.warning(
                            f"contextMenuEvent - UserRole data: {item.data(Qt.ItemDataRole.UserRole)}"
                        )
            else:
                logger.warning("contextMenuEvent - index nie jest valid")

        except Exception as e:
            logger.error(f"Błąd obsługi menu kontekstowego: {e}")

    def _open_folder_in_explorer(self, folder_path: str):
        """Otwiera folder w eksploratorze systemu."""
        logger.debug(f"_open_folder_in_explorer - otrzymana ścieżka: {folder_path}")
        try:
            if self.open_in_explorer_callback:
                logger.debug(
                    f"_open_folder_in_explorer - wywołuję callback z ścieżką: {folder_path}"
                )
                self.open_in_explorer_callback(folder_path)
            else:
                logger.debug(
                    f"_open_folder_in_explorer - brak callbacku, używam bezpośredniego otwarcia: {folder_path}"
                )
                # Fallback - bezpośrednie otwarcie
                open_path_in_explorer(folder_path, self)
        except Exception as e:
            logger.error(f"Błąd otwierania folderu w eksploratorze: {e}")

    def _rebuild_assets_in_folder(self, folder_path: str):
        """Przebudowuje assety w wybranym folderze."""
        try:
            if self.rebuild_callback:
                self.rebuild_callback(folder_path)
            else:
                logger.warning("Brak callbacku do przebudowy assetów")
        except Exception as e:
            logger.error(f"Błąd wywołania callbacku przebudowy: {e}")

    def _refresh_folder(self, folder_path: str):
        """Odświeża folder."""
        try:
            if self.refresh_folder_callback:
                self.refresh_folder_callback(folder_path)
            else:
                logger.warning("Brak callbacku do odświeżania folderu")
        except Exception as e:
            logger.error(f"Błąd wywołania callbacku odświeżania folderu: {e}")

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
                        target_path,
                        (
                            self.current_folder_path_getter()
                            if self.current_folder_path_getter
                            else None
                        ),
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

                        # Sprawdź, czy nie próbujemy przenieść do tego samego folderu roboczego
                        current_folder_path = None
                        if self.current_folder_path_getter:
                            current_folder_path = self.current_folder_path_getter()
                            logger.debug(
                                f"Current folder path: '{current_folder_path}'"
                            )
                            logger.debug(f"Target folder path: '{target_folder_path}'")

                        if self.drag_drop_model and self.drag_drop_model.validate_drop(
                            target_folder_path,
                            (
                                self.current_folder_path_getter()
                                if self.current_folder_path_getter
                                else None
                            ),
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

                            logger.debug(f"[DROP DEBUG] asset_ids: {asset_ids}")
                            logger.debug(f"[DROP DEBUG] source_folder_path: {current_folder_path}")
                            logger.debug(f"[DROP DEBUG] target_folder_path: {target_folder_path}")

                            if not asset_ids or not all(asset_ids):
                                logger.error(f"[DROP ERROR] asset_ids is empty or contains empty values: {asset_ids}")
                            if not current_folder_path:
                                logger.error(f"[DROP ERROR] current_folder_path is empty or None!")
                            if not target_folder_path:
                                logger.error(f"[DROP ERROR] target_folder_path is empty or None!")

                            if (
                                assets_to_move
                                and self.file_operations_model
                                and self.current_folder_path_getter
                                and asset_ids
                                and all(asset_ids)
                                and current_folder_path
                                and target_folder_path
                            ):
                                source_folder_path = current_folder_path
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
                                    f"[DROP ERROR] Missing required models: assets_to_move={len(assets_to_move)}, file_operations_model={self.file_operations_model is not None}, current_folder_path_getter={self.current_folder_path_getter is not None}, asset_ids={asset_ids}, current_folder_path={current_folder_path}, target_folder_path={target_folder_path}"
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
