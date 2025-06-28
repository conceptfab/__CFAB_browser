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

        success_messages = []
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
            self.operation_progress.emit(
                i + 1, total_assets, f"Przenoszenie: {asset_name}"
            )
            try:
                # Użyj nowej metody z obsługą konfliktów nazw
                result = self._move_single_asset_with_conflict_resolution(
                    asset_data, asset_name
                )
                if result["success"]:
                    success_messages.append(result["message"])
                    logger.debug(result["message"])
                else:
                    error_messages.append(result["message"])
                    logger.error(result["message"])
            except Exception as e:
                error_msg = f"Błąd przenoszenia assetu {asset_name}: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)

        # Po przeniesieniu assetów, sprawdź i usuń pusty folder .cache w źródle
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

        self.operation_completed.emit(success_messages, error_messages)

    def _generate_unique_asset_name(self, original_name: str) -> str:
        """Generuje unikalną nazwę assetu dodając suffix _01, _02, itd."""
        base_name = original_name
        counter = 1

        while True:
            # Sprawdź czy asset o tej nazwie już istnieje (sprawdź plik .asset)
            test_asset_file = os.path.join(
                self.target_folder_path, f"{base_name}.asset"
            )
            if not os.path.exists(test_asset_file):
                return base_name

            # Jeśli istnieje, spróbuj z sufiksem
            base_name = f"{original_name}_{counter:02d}"
            counter += 1

            # Zabezpieczenie przed nieskończoną pętlą
            if counter > 99:
                logger.warning(f"Osiągnięto maksymalną liczbę prób dla {original_name}")
                return f"{original_name}_{counter}"

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
                    # Zachowaj oryginalne rozszerzenie
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
                    # Zachowaj oryginalne rozszerzenie
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
                self._update_asset_file_after_rename(source_path, target_path)

                # Oznacz jako duplikat z informacją o oryginale
                original_asset_path = os.path.join(
                    self.target_folder_path, f"{original_name}.asset"
                )
                target_asset_path = os.path.join(
                    self.target_folder_path, f"{unique_name}.asset"
                )
                if os.path.exists(original_asset_path):
                    self._mark_asset_as_duplicate(
                        target_asset_path, original_asset_path
                    )

            # Zwróć informację o sukcesie
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

    def _update_asset_file_after_rename(self, original_path, new_path):
        """Aktualizuje plik .asset po zmianie nazwy"""
        try:
            asset_file_path = new_path.replace(os.path.splitext(new_path)[1], ".asset")

            if os.path.exists(asset_file_path):
                # Wczytaj JSON z pliku .asset
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Zaktualizuj ścieżki w asset_data
                original_basename = os.path.splitext(os.path.basename(original_path))[0]
                new_basename = os.path.splitext(os.path.basename(new_path))[0]

                # Aktualizuj wszystkie ścieżki w asset_data
                for key, value in asset_data.items():
                    if isinstance(value, str) and original_basename in value:
                        asset_data[key] = value.replace(original_basename, new_basename)

                # Zapisz zaktualizowany JSON
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, ensure_ascii=False, indent=2)

                logger.debug(f"Zaktualizowano plik .asset: {asset_file_path}")
        except Exception as e:
            logger.error(f"Błąd aktualizacji pliku .asset: {e}")

    def _mark_asset_as_duplicate(self, asset_path, original_asset_path):
        """Oznacza asset jako duplikat z informacją o oryginale"""
        try:
            asset_file_path = asset_path.replace(
                os.path.splitext(asset_path)[1], ".asset"
            )

            if os.path.exists(asset_file_path):
                # Wczytaj JSON z pliku .asset
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Dodaj informacje o duplikacie
                asset_data["duplicate"] = True
                asset_data["original_asset"] = os.path.basename(original_asset_path)
                asset_data["original_path"] = os.path.dirname(original_asset_path)

                # Zapisz zaktualizowany JSON
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, ensure_ascii=False, indent=2)

                logger.info(
                    f"Asset oznaczony jako duplikat: {asset_path} "
                    f"(oryginał: {original_asset_path})"
                )
        except Exception as e:
            logger.error(f"Błąd oznaczania assetu jako duplikat: {e}")

    def remove_duplicate_status(self, asset_path):
        """Usuwa status duplikat z assetu"""
        try:
            asset_file_path = asset_path.replace(
                os.path.splitext(asset_path)[1], ".asset"
            )

            if os.path.exists(asset_file_path):
                # Wczytaj JSON z pliku .asset
                with open(asset_file_path, "r", encoding="utf-8") as f:
                    asset_data = json.load(f)

                # Usuń klucze duplikatu jeśli istnieją
                asset_data.pop("duplicate", None)
                asset_data.pop("original_asset", None)
                asset_data.pop("original_path", None)

                # Zapisz zaktualizowany JSON
                with open(asset_file_path, "w", encoding="utf-8") as f:
                    json.dump(asset_data, f, ensure_ascii=False, indent=2)

                logger.info(f"Usunięto status duplikat z assetu: {asset_path}")
                return True
        except Exception as e:
            logger.error(f"Błąd usuwania statusu duplikat: {e}")
            return False

    def _delete_assets(self):
        """Usuwa zaznaczone assety (wszystkie 4 pliki)."""
        if not self.assets_data:
            self.operation_completed.emit([], [])
            return

        success_messages = []
        error_messages = []
        total_assets = len(self.assets_data)

        for i, asset_data in enumerate(self.assets_data):
            asset_name = asset_data.get("name", "Unknown Asset")
            self.operation_progress.emit(i + 1, total_assets, f"Usuwanie: {asset_name}")
            try:
                files_to_delete = self._get_asset_files_paths(
                    asset_data, self.source_folder_path
                )
                for file_path in files_to_delete:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.debug(f"Usunięto plik: {file_path}")
                success_messages.append(f"Pomyślnie usunięto asset: {asset_name}")
                logger.debug(f"Usunięto asset: {asset_name}")
            except Exception as e:
                error_messages.append(f"Błąd usuwania assetu {asset_name}: {e}")
                logger.error(f"Błąd usuwania assetu {asset_name}: {e}")

        # Po usunięciu assetów, sprawdź i usuń pusty folder .cache
        cache_dir = os.path.join(self.source_folder_path, ".cache")
        if os.path.exists(cache_dir) and not os.listdir(cache_dir):
            try:
                os.rmdir(cache_dir)
                logger.debug(f"Usunięto pusty folder .cache: {cache_dir}")
            except Exception as e:
                logger.warning(
                    f"Nie można usunąć pustego folderu .cache {cache_dir}: {e}"
                )

        self.operation_completed.emit(success_messages, error_messages)

    def _get_asset_files_paths(self, asset_data: dict, folder_path: str) -> list:
        """Zwraca listę pełnych ścieżek do plików assetu (bez thumb)."""
        files = []
        asset_name = asset_data.get("name", "")

        # Plik .asset
        asset_file = os.path.join(folder_path, f"{asset_name}.asset")
        if os.path.exists(asset_file):
            files.append(asset_file)

        # Plik archiwum
        archive_filename = asset_data.get("archive")
        if archive_filename:
            archive_file = os.path.join(folder_path, archive_filename)
            if os.path.exists(archive_file):
                files.append(archive_file)

        # Plik podglądu
        preview_filename = asset_data.get("preview")
        if preview_filename:
            preview_file = os.path.join(folder_path, preview_filename)
            if os.path.exists(preview_file):
                files.append(preview_file)

        return files


class FileOperationsModel(QObject):
    """Model dla operacji na plikach (przenoszenie, usuwanie)"""

    operation_progress = pyqtSignal(int, int, str)  # current, total, message
    operation_completed = pyqtSignal(list, list)  # success_messages, error_messages
    operation_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._current_worker = None
        logger.info("FileOperationsModel initialized")

    def delete_assets(self, assets_data: list, current_folder_path: str):
        """Usuwa zaznaczone assety (wszystkie 4 pliki)."""
        if self._current_worker and self._current_worker.isRunning():
            logger.warning("Operacja już w toku, zatrzymuję poprzednią")
            self.stop_operation()

        self._current_worker = FileOperationsWorker(
            "delete", assets_data, current_folder_path, None
        )
        self._current_worker.operation_progress.connect(self.operation_progress)
        self._current_worker.operation_completed.connect(self.operation_completed)
        self._current_worker.operation_error.connect(self.operation_error)
        self._current_worker.finished.connect(self._on_worker_finished)

        self._current_worker.start()

    def move_assets(
        self, assets_data: list, source_folder_path: str, target_folder_path: str
    ):
        """Przenosi zaznaczone assety do nowego folderu."""
        if self._current_worker and self._current_worker.isRunning():
            logger.warning("Operacja już w toku, zatrzymuję poprzednią")
            self.stop_operation()

        self._current_worker = FileOperationsWorker(
            "move", assets_data, source_folder_path, target_folder_path
        )
        self._current_worker.operation_progress.connect(self.operation_progress)
        self._current_worker.operation_completed.connect(self.operation_completed)
        self._current_worker.operation_error.connect(self.operation_error)
        self._current_worker.finished.connect(self._on_worker_finished)

        self._current_worker.start()

    def stop_operation(self):
        """Zatrzymuje aktywną operację."""
        if self._current_worker:
            if self._current_worker.isRunning():
                self._current_worker.terminate()
                # Sprawdź czy worker nadal istnieje przed wywołaniem wait()
                if self._current_worker:
                    self._current_worker.wait(3000)  # Czekaj maksymalnie 3 sekundy
                logger.info("FileOperationsModel: Operacja zatrzymana")
                # Emituj sygnał completion z pustymi listami żeby kontroler mógł zaktualizować UI
                self.operation_completed.emit([], [])

    def _on_worker_finished(self):
        """Czyści referencję do worker'a po zakończeniu."""
        self._current_worker = None
