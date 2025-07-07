"""
Prefix Suffix Remover Worker module for CFAB Browser
Removes prefixes or suffixes from file names
"""

import logging
import os
from PyQt6.QtCore import pyqtSignal

from .base_worker import BaseWorker

logger = logging.getLogger(__name__)


class PrefixSuffixRemoverWorker(BaseWorker):
    """Worker do usuwania prefixu/suffixu z nazw plików"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str, text_to_remove: str, mode: str):
        super().__init__(folder_path)
        self.text_to_remove = text_to_remove
        self.mode = mode  # "prefix" lub "suffix"

    def _run_operation(self):
        """Główna metoda usuwania prefixu/suffixu"""
        try:
            logger.info(
                f"Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}"
            )

            # Znajdź wszystkie pliki w folderze
            files_to_process = []
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    files_to_process.append(item_path)

            if not files_to_process:
                self.finished.emit("Brak plików do przetworzenia")
                return

            # Przetwórz pliki
            renamed_count = 0
            error_count = 0

            for i, file_path in enumerate(files_to_process):
                try:
                    filename_with_ext = os.path.basename(file_path)
                    filename_base, file_extension = os.path.splitext(filename_with_ext)
                    new_filename_base = None

                    # Sprawdź czy plik pasuje do kryteriów
                    if self.mode == "prefix" and filename_base.startswith(
                        self.text_to_remove
                    ):
                        new_filename_base = filename_base.removeprefix(
                            self.text_to_remove
                        ).rstrip()  # Usuń spacje z końca po usunięciu prefix
                    elif self.mode == "suffix" and filename_base.endswith(
                        self.text_to_remove
                    ):
                        new_filename_base = filename_base.removesuffix(
                            self.text_to_remove
                        ).rstrip()  # Usuń spacje z końca po usunięciu suffix

                    if new_filename_base is not None and new_filename_base:
                        new_full_filename = new_filename_base + file_extension
                        new_file_path = os.path.join(
                            self.folder_path, new_full_filename
                        )

                        # Sprawdź czy nowa nazwa nie istnieje
                        if os.path.exists(new_file_path):
                            logger.warning(
                                f"Plik o nazwie '{new_full_filename}' już istnieje. Pomijam."
                            )
                            continue

                        # Zmień nazwę
                        os.rename(file_path, new_file_path)
                        renamed_count += 1
                        logger.info(
                            f"Zmieniono: '{filename_with_ext}' -> '{new_full_filename}'"
                        )

                    self.progress_updated.emit(
                        i + 1,
                        len(files_to_process),
                        f"Przetwarzanie: {filename_with_ext}",
                    )

                except Exception as e:
                    error_count += 1
                    logger.error(
                        f"Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}"
                    )

            # Przygotuj komunikat końcowy
            message = (
                f"Usuwanie {self.mode} zakończone: {renamed_count} plików zmieniono"
            )
            if error_count > 0:
                message += f", {error_count} błędów"

            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Błąd podczas usuwania {self.mode}: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg) 