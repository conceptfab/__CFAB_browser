import json
import logging
import os
import shutil

from PyQt6.QtCore import QObject, QThread, pyqtSignal

logger = logging.getLogger(__name__)


class FileOperationsWorker(QThread):
    """Worker do wykonywania operacji na plikach w osobnym wątku"""

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(
        self, operation_type, assets_data, source_folder_path, target_folder_path
    ):
        super().__init__()
        self.operation_type = operation_type
        self.assets_data = assets_data
        self.source_folder_path = source_folder_path
        self.target_folder_path = target_folder_path

    def run(self):
        try:
            if self.operation_type == "move":
                self._move_assets()
            elif self.operation_type == "delete":
                self._delete_assets()
        except Exception as e:
            self.operation_error.emit(
                f"Błąd podczas operacji {self.operation_type}: {e}"
            )

    def _move_assets(self):
        """Przenosi zaznaczone assety do nowego folderu."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return
        success_asset_names = []
        error_messages = []
        total_assets = len(self.assets_data)
        if not os.path.exists(self.target_folder_path):
            try:
                os.makedirs(self.target_folder_path)
                logger.debug(f"Utworzono folder docelowy: {self.target_folder_path}")
            except Exception as e:
                self.operation_error.emit(
                    f"Nie można utworzyć folderu docelowego "
                    f"{self.target_folder_path}: {e}"
                )
                return
        for i, asset_data in enumerate(self.assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            logger.debug(f"Processing asset {i}: name='{asset_name}'")
            self.operation_progress.emit(
                i + 1, total_assets, f"Przenoszenie: {asset_name}"
            )
            try:
                result = self._move_single_asset_with_conflict_resolution(
                    asset_data, asset_name
                )
                if result["success"]:
                    success_asset_names.append(asset_name)
                    logger.debug(f"Successfully moved asset: {asset_name}")
                else:
                    error_messages.append(result["message"])
                    logger.error(result["message"])
            except Exception as e:
                error_msg = f"Błąd przenoszenia assetu {asset_name}: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        source_cache_dir = os.path.join(self.source_folder_path, ".cache")
        if os.path.exists(source_cache_dir) and not os.listdir(source_cache_dir):
            try:
                os.rmdir(source_cache_dir)
                logger.debug(
                    f"Usunięto pusty folder .cache w źródle: {source_cache_dir}"
                )
            except Exception as e:
                logger.warning(
                    f"Nie można usunąć pustego folderu .cache w źródle {source_cache_dir}: {e}"
                )
        self.operation_completed.emit(success_asset_names, error_messages)

    def _generate_unique_asset_name(self, original_name: str) -> str:
        """Generuje unikalną nazwę assetu dodając suffix _D_01, _D_02, itd."""
        base_name = original_name
        counter = 1

        while True:
            # Sprawdź czy asset o tej nazwie już istnieje (sprawdź plik .asset)
            test_asset_file = os.path.join(
                self.target_folder_path, f"{base_name}.asset"
            )
            if not os.path.exists(test_asset_file):
                return base_name

            # Jeśli istnieje, spróbuj z sufiksem _D_01, _D_02, itd.
            base_name = f"{original_name}_D_{counter:02d}"
            counter += 1

            # Zabezpieczenie przed nieskończoną pętlą
            if counter > 99:
                logger.warning(f"Osiągnięto maksymalną liczbę prób dla {original_name}")
                return f"{original_name}_D_{counter}"

    def _move_single_asset_with_conflict_resolution(
        self, asset_data: dict, original_name: str
    ) -> dict:
        """
        Przenosi pojedynczy asset z obsługą konfliktów nazw.
        Zwraca dict z kluczami: success (bool), message (str), final_name (str)
        """
        # Wygeneruj unikalną nazwę
        unique_name = self._generate_unique_asset_name(original_name)

        try:
            # Przygotuj mapowanie plików źródłowych na docelowe
            files_to_move = []

            # 1. Plik .asset
            source_asset = os.path.join(
                self.source_folder_path, f"{original_name}.asset"
            )
            target_asset = os.path.join(self.target_folder_path, f"{unique_name}.asset")
            if os.path.exists(source_asset):
                files_to_move.append((source_asset, target_asset))

            # 2. Plik archiwum
            archive_filename = asset_data.get("archive")
            if archive_filename:
                source_archive = os.path.join(self.source_folder_path, archive_filename)
                if os.path.exists(source_archive):
                    archive_ext = os.path.splitext(archive_filename)[1]
                    target_archive = os.path.join(
                        self.target_folder_path, f"{unique_name}{archive_ext}"
                    )
                    files_to_move.append((source_archive, target_archive))

            # 3. Plik podglądu
            preview_filename = asset_data.get("preview")
            if preview_filename:
                source_preview = os.path.join(self.source_folder_path, preview_filename)
                if os.path.exists(source_preview):
                    preview_ext = os.path.splitext(preview_filename)[1]
                    target_preview = os.path.join(
                        self.target_folder_path, f"{unique_name}{preview_ext}"
                    )
                    files_to_move.append((source_preview, target_preview))

            # 4. Plik .thumb w folderze .cache
            source_thumb = os.path.join(
                self.source_folder_path, ".cache", f"{original_name}.thumb"
            )
            if os.path.exists(source_thumb):
                target_cache_dir = os.path.join(self.target_folder_path, ".cache")
                os.makedirs(target_cache_dir, exist_ok=True)
                target_thumb = os.path.join(target_cache_dir, f"{unique_name}.thumb")
                files_to_move.append((source_thumb, target_thumb))

            # Przenieś wszystkie pliki
            moved_files = []
            for source_path, target_path in files_to_move:
                shutil.move(source_path, target_path)
                moved_files.append(target_path)
                logger.debug(f"Przeniesiono: {source_path} -> {target_path}")

            # Jeśli nazwa została zmieniona, zaktualizuj plik .asset
            if unique_name != original_name:
                self._update_asset_file_after_rename(source_asset, target_asset)
                if os.path.exists(source_asset):
                    self._mark_asset_as_duplicate(target_asset, source_asset)

            if unique_name != original_name:
                message = (
                    f"Przeniesiono asset: {original_name} -> {unique_name} "
                    f"(zmieniono nazwę z powodu konfliktu)"
                )
            else:
                message = f"Pomyślnie przeniesiono asset: {original_name}"

            return {"success": True, "message": message, "final_name": unique_name}

        except Exception as e:
            return {
                "success": False,
                "message": f"Błąd przenoszenia assetu {original_name}: {e}",
                "final_name": original_name,
            }

    def _update_asset_file_after_rename(self, original_asset_path, new_asset_path):
        try:
            asset_file_path = new_asset_path
            if os.path.exists(asset_file_path):
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)
                original_basename = os.path.splitext(
                    os.path.basename(original_asset_path)
                )[0]
                new_basename = os.path.splitext(os.path.basename(new_asset_path))[0]

                # Zaktualizuj nazwę w danych assetu
                asset_data["name"] = new_basename

                # Zaktualizuj nazwy plików archiwum i podglądu
                if "archive" in asset_data:
                    archive_ext = os.path.splitext(asset_data["archive"])[1]
                    asset_data["archive"] = f"{new_basename}{archive_ext}"

                if "preview" in asset_data:
                    preview_ext = os.path.splitext(asset_data["preview"])[1]
                    asset_data["preview"] = f"{new_basename}{preview_ext}"

                # Zapisz zaktualizowane dane
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, indent=2, ensure_ascii=False)

                logger.debug(
                    f"Zaktualizowano plik .asset po zmianie nazwy: "
                    f"{original_basename} -> {new_basename}"
                )

        except Exception as e:
            logger.error(f"Błąd podczas aktualizacji pliku .asset: {e}")

    def _mark_asset_as_duplicate(self, asset_path, original_asset_path):
        try:
            if os.path.exists(asset_path):
                with open(asset_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Dodaj informację o duplikacie
                if "meta" not in asset_data:
                    asset_data["meta"] = {}
                asset_data["meta"]["duplicate_of"] = os.path.basename(
                    original_asset_path
                )
                asset_data["meta"]["duplicate_date"] = str(
                    os.path.getctime(original_asset_path)
                )

                # Zapisz zaktualizowane dane
                with open(asset_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, indent=2, ensure_ascii=False)

                logger.debug(f"Oznaczono asset jako duplikat: {asset_path}")

        except Exception as e:
            logger.error(f"Błąd podczas oznaczania assetu jako duplikat: {e}")

    def remove_duplicate_status(self, asset_path):
        try:
            if os.path.exists(asset_path):
                with open(asset_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Usuń informację o duplikacie
                if "meta" in asset_data:
                    if "duplicate_of" in asset_data["meta"]:
                        del asset_data["meta"]["duplicate_of"]
                    if "duplicate_date" in asset_data["meta"]:
                        del asset_data["meta"]["duplicate_date"]

                    # Jeśli meta jest puste, usuń je całkowicie
                    if not asset_data["meta"]:
                        del asset_data["meta"]

                # Zapisz zaktualizowane dane
                with open(asset_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, indent=2, ensure_ascii=False)

                logger.debug(f"Usunięto status duplikatu z assetu: {asset_path}")

        except Exception as e:
            logger.error(f"Błąd podczas usuwania statusu duplikatu: {e}")

    def _delete_assets(self):
        """Usuwa zaznaczone assety."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return

        success_asset_names = []
        error_messages = []
        total_assets = len(self.assets_data)

        for i, asset_data in enumerate(self.assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(i + 1, total_assets, f"Usuwanie: {asset_name}")

            try:
                # Pobierz ścieżki do plików assetu
                asset_files = self._get_asset_files_paths(
                    asset_data, self.source_folder_path
                )

                # Usuń wszystkie pliki
                for file_path in asset_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Usunięto plik: {file_path}")

                success_asset_names.append(asset_name)
                logger.debug(f"Pomyślnie usunięto asset: {asset_name}")

            except Exception as e:
                error_msg = f"Błąd usuwania assetu {asset_name}: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)

        # Usuń pusty folder .cache jeśli istnieje
        cache_dir = os.path.join(self.source_folder_path, ".cache")
        if os.path.exists(cache_dir) and not os.listdir(cache_dir):
            try:
                os.rmdir(cache_dir)
                logger.debug(f"Usunięto pusty folder .cache: {cache_dir}")
            except Exception as e:
                logger.warning(
                    f"Nie można usunąć pustego folderu .cache {cache_dir}: {e}"
                )

        self.operation_completed.emit(success_asset_names, error_messages)

    def _get_asset_files_paths(self, asset_data: dict, folder_path: str) -> list:
        """
        Zwraca listę ścieżek do wszystkich plików związanych z assetem.

        Args:
            asset_data (dict): Dane assetu
            folder_path (str): Ścieżka do folderu zawierającego asset

        Returns:
            list: Lista ścieżek do plików
        """
        asset_name = asset_data.get("name", "")
        files = []

        # 1. Plik .asset
        asset_file = os.path.join(folder_path, f"{asset_name}.asset")
        files.append(asset_file)

        # 2. Plik archiwum
        archive_filename = asset_data.get("archive")
        if archive_filename:
            archive_file = os.path.join(folder_path, archive_filename)
            files.append(archive_file)

        # 3. Plik podglądu
        preview_filename = asset_data.get("preview")
        if preview_filename:
            preview_file = os.path.join(folder_path, preview_filename)
            files.append(preview_file)

        # 4. Plik miniatury w folderze .cache
        cache_dir = os.path.join(folder_path, ".cache")
        thumb_file = os.path.join(cache_dir, f"{asset_name}.thumb")
        files.append(thumb_file)

        return files


class FileOperationsModel(QObject):
    """
    Model dla operacji na plikach (przenoszenie, usuwanie).

    Zarządza operacjami na plikach w osobnym wątku, aby nie blokować UI.
    """

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(self):
        """Inicjalizuje model operacji na plikach."""
        super().__init__()
        self._worker = None

    def move_assets(
        self, assets_data: list, source_folder_path: str, target_folder_path: str
    ):
        """Przenosi assety z folderu źródłowego do docelowego."""
        if self._worker and self._worker.isRunning():
            logger.warning("Operacja już w toku. Zatrzymuję poprzednią operację.")
            self.stop_operation()

        self._worker = FileOperationsWorker(
            "move", assets_data, source_folder_path, target_folder_path
        )
        self._connect_worker_signals()
        self._worker.start()

    def delete_assets(self, assets_data: list, current_folder_path: str):
        """Usuwa zaznaczone assety."""
        if self._worker and self._worker.isRunning():
            logger.warning("Operacja już w toku. Zatrzymuję poprzednią operację.")
            self.stop_operation()

        self._worker = FileOperationsWorker(
            "delete", assets_data, current_folder_path, ""
        )
        self._connect_worker_signals()
        self._worker.start()

    def stop_operation(self):
        """Zatrzymuje bieżącą operację na plikach."""
        if self._worker and self._worker.isRunning():
            logger.info("Zatrzymywanie bieżącej operacji...")
            self._worker.terminate()
            if self._worker:
                self._worker.wait()
            logger.info("Operacja została zatrzymana.")

    def _connect_worker_signals(self):
        """Łączy sygnały workera z sygnałami modelu."""
        self._worker.operation_progress.connect(self.operation_progress.emit)
        self._worker.operation_completed.connect(self.operation_completed.emit)
        self._worker.operation_error.connect(self.operation_error.emit)
        self._worker.finished.connect(self._on_worker_finished)

    def _on_worker_finished(self):
        """Obsługa zakończenia pracy workera."""
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
            logger.debug("Worker został usunięty.")

