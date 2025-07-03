import logging
import os
import random
import string
import subprocess
import sys
from typing import List, Tuple

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

logger = logging.getLogger(__name__)


class WorkerManager:
    """Wspólna klasa do zarządzania workerami"""

    @staticmethod
    def handle_progress(button, current, total, message):
        """Wspólna logika obsługi postępu"""
        progress = int((current / total) * 100) if total > 0 else 0
        button.setText(f"{button.text().split('...')[0]}... {progress}%")
        logger.debug(f"Worker progress: {progress}% - {message}")

    @staticmethod
    def handle_finished(button, message, original_text, parent_instance):
        """Wspólna logika obsługi zakończenia"""
        logger.info(f"Operacja zakończona: {message}")
        parent_instance.show_info_message.emit("Sukces", message)
        if parent_instance.current_working_directory:
            parent_instance.scan_working_directory(
                parent_instance.current_working_directory
            )
        WorkerManager.reset_button_state(button, original_text, parent_instance)
        parent_instance.working_directory_changed.emit(
            parent_instance.current_working_directory
        )

    @staticmethod
    def handle_error(button, error_message, original_text, parent_instance):
        """Wspólna logika obsługi błędów"""
        logger.error(f"Błąd operacji: {error_message}")
        parent_instance.show_error_message.emit("Błąd", error_message)
        WorkerManager.reset_button_state(button, original_text, parent_instance)

    @staticmethod
    def reset_button_state(button, original_text, parent_instance):
        """Wspólna logika resetowania stanu przycisku"""
        if button:
            button.setText(original_text)
            parent_instance._update_button_states()


class BaseWorker(QThread):
    """Bazowa klasa dla workerów operacji na plikach."""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._should_stop = False

    def run(self):
        try:
            if not self.folder_path or not os.path.exists(self.folder_path):
                error_msg = f"Nieprawidłowy folder: {self.folder_path}"
                self.error_occurred.emit(error_msg)
                return

            self._run_operation()

        except Exception as e:
            error_msg = f"Błąd podczas operacji: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _run_operation(self):
        """Metoda do nadpisania w klasach pochodnych."""
        raise NotImplementedError(
            "Metoda _run_operation musi być zaimplementowana w klasie pochodnej."
        )

    def stop(self):
        """Bezpiecznie zatrzymuje wątek"""
        self._should_stop = True
        self.quit()
        if not self.wait(3000):
            self.terminate()
            self.wait(2000)


class WebPConverterWorker(BaseWorker):
    """Worker do konwersji plików obrazów na format WebP"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Główna metoda konwersji na WebP"""
        try:
            logger.info(f"Rozpoczęcie konwersji na WebP w folderze: {self.folder_path}")

            files_to_convert = self._find_files_to_convert()

            if not files_to_convert:
                self.finished.emit("Brak plików do konwersji na WebP")
                return

            converted_count = 0
            skipped_count = 0
            error_count = 0

            for i, (original_path, webp_path) in enumerate(files_to_convert):
                try:
                    logger.info(
                        f"[WebP] START iteracja {i+1}/{len(files_to_convert)}: {original_path}"
                    )
                    logger.debug(
                        f"[WebP] {i+1}/{len(files_to_convert)}: {original_path} -> {webp_path}"
                    )

                    logger.info(f"[WebP] Emituję progress_updated dla {original_path}")
                    self.progress_updated.emit(
                        i,
                        len(files_to_convert),
                        f"Konwertowanie: {os.path.basename(original_path)}",
                    )

                    logger.info(f"[WebP] Sprawdzam czy {webp_path} już istnieje")
                    if os.path.exists(webp_path):
                        skipped_count += 1
                        logger.info(f"[WebP] Pomijam (już istnieje): {webp_path}")
                        QThread.msleep(1)
                        continue

                    logger.info(
                        f"[WebP] Rozpoczynam konwersję {original_path} -> {webp_path}"
                    )
                    if self._convert_to_webp(original_path, webp_path):
                        logger.info(
                            f"[WebP] Konwersja udana, usuwam oryginalny plik: {original_path}"
                        )
                        try:
                            os.remove(original_path)
                            logger.info(
                                f"[WebP] Plik {original_path} usunięty pomyślnie"
                            )
                        except Exception as e_rm:
                            logger.error(
                                f"[WebP] Błąd przy usuwaniu pliku {original_path}: {e_rm}"
                            )
                            error_count += 1
                            QThread.msleep(1)
                            continue
                        converted_count += 1
                        logger.info(
                            f"[WebP] Skutecznie skonwertowano: {original_path} -> {webp_path}"
                        )
                    else:
                        error_count += 1
                        logger.error(f"[WebP] Błąd konwersji: {original_path}")

                    logger.info(
                        f"[WebP] END iteracja {i+1}/{len(files_to_convert)}: {original_path}"
                    )
                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"[WebP] Błąd podczas konwersji {original_path}: {e}")
                    QThread.msleep(1)

            logger.info(f"[WebP] Przygotowuję komunikat końcowy")
            message = f"Konwersja zakończona: {converted_count} skonwertowano"
            if skipped_count > 0:
                message += f", {skipped_count} pominięto (już istnieją)"
            if error_count > 0:
                message += f", {error_count} błędów"

            logger.info(f"[WebP] Emituję progress_updated końcowy")
            self.progress_updated.emit(
                len(files_to_convert), len(files_to_convert), "Konwersja zakończona"
            )
            logger.info(f"[WebP] Emituję finished: {message}")
            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Błąd podczas konwersji na WebP: {e}"
            logger.error(f"[WebP] {error_msg}")
            self.error_occurred.emit(error_msg)

    def _find_files_to_convert(self) -> List[Tuple[str, str]]:
        """Znajduje pliki do konwersji na WebP"""
        files_to_convert = []
        supported_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in supported_extensions:
                        # Utwórz nazwę pliku WebP
                        name_without_ext = os.path.splitext(item)[0]
                        webp_filename = f"{name_without_ext}.webp"
                        webp_path = os.path.join(self.folder_path, webp_filename)
                        files_to_convert.append((item_path, webp_path))

            logger.info(f"Znaleziono {len(files_to_convert)} plików do konwersji")
            return files_to_convert

        except Exception as e:
            logger.error(f"Błąd podczas wyszukiwania plików: {e}")
            return []

    def _convert_to_webp(self, input_path: str, output_path: str) -> bool:
        """Konwertuje pojedynczy plik na WebP"""
        try:
            logger.info(f"[WebP] _convert_to_webp START: {input_path} -> {output_path}")

            # Import Pillow tutaj, żeby nie wymagać go globalnie
            logger.info(f"[WebP] Importuję PIL.Image")
            from PIL import Image

            # Otwórz obraz
            logger.info(f"[WebP] Otwieram obraz: {input_path}")
            with Image.open(input_path) as img:
                logger.info(
                    f"[WebP] Obraz otwarty, rozmiar: {img.size}, tryb: {img.mode}"
                )

                # Konwertuj na RGB jeśli to konieczne (WebP nie obsługuje RGBA)
                if img.mode in ("RGBA", "LA", "P"):
                    logger.info(f"[WebP] Konwertuję tryb {img.mode} na RGB")
                    # Utwórz białe tło
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(
                        img, mask=img.split()[-1] if img.mode == "RGBA" else None
                    )
                    img = background
                    logger.info(f"[WebP] Konwersja trybu zakończona")
                elif img.mode != "RGB":
                    logger.info(f"[WebP] Konwertuję tryb {img.mode} na RGB")
                    img = img.convert("RGB")
                    logger.info(f"[WebP] Konwersja trybu zakończona")

                # Zapisz jako WebP z optymalną jakością
                logger.info(f"[WebP] Zapisuję jako WebP: {output_path}")
                img.save(output_path, "WEBP", quality=85, method=6)
                logger.info(f"[WebP] Zapis zakończony pomyślnie")
                return True

        except ImportError:
            logger.error("[WebP] Biblioteka Pillow nie jest zainstalowana")
            return False
        except Exception as e:
            logger.error(f"[WebP] Błąd konwersji {input_path}: {e}")
            return False
        finally:
            logger.info(f"[WebP] _convert_to_webp END: {input_path}")


class ImageResizerWorker(BaseWorker):
    """Worker do zmniejszania plików obrazów"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message

    def __init__(self, folder_path: str):
        super().__init__(folder_path)

    def _run_operation(self):
        """Główna metoda zmniejszania obrazów"""
        try:
            logger.info(
                f"Rozpoczęcie zmniejszania obrazów w folderze: {self.folder_path}"
            )

            files_to_resize = self._find_files_to_resize()

            if not files_to_resize:
                self.finished.emit("Brak plików do zmniejszenia")
                return

            resized_count = 0
            skipped_count = 0
            error_count = 0

            for i, file_path in enumerate(files_to_resize):
                try:
                    filename = os.path.basename(file_path)
                    logger.info(
                        f"[Resize] START iteracja {i+1}/{len(files_to_resize)}: {filename}"
                    )
                    logger.debug(f"[Resize] {i+1}/{len(files_to_resize)}: {filename}")

                    logger.info(f"[Resize] Emituję progress_updated dla {filename}")
                    self.progress_updated.emit(
                        i, len(files_to_resize), f"Zmniejszanie: {filename}"
                    )

                    logger.info(f"[Resize] Rozpoczynam zmniejszanie: {filename}")
                    if self._resize_image(file_path):
                        resized_count += 1
                        logger.info(f"[Resize] Skutecznie zmniejszono: {filename}")
                    else:
                        skipped_count += 1
                        logger.info(
                            f"[Resize] Pominięto (nie wymaga zmniejszenia): {filename}"
                        )

                    logger.info(
                        f"[Resize] END iteracja {i+1}/{len(files_to_resize)}: {filename}"
                    )
                    QThread.msleep(1)
                except Exception as e:
                    error_count += 1
                    logger.error(f"[Resize] Błąd podczas zmniejszania {filename}: {e}")
                    QThread.msleep(1)

            logger.info(f"[Resize] Przygotowuję komunikat końcowy")
            message = f"Zmniejszanie zakończone: {resized_count} zmniejszono"
            if skipped_count > 0:
                message += f", {skipped_count} pominięto (nie wymagały zmniejszenia)"
            if error_count > 0:
                message += f", {error_count} błędów"

            logger.info(f"[Resize] Emituję progress_updated końcowy")
            self.progress_updated.emit(
                len(files_to_resize), len(files_to_resize), "Zmniejszanie zakończone"
            )
            logger.info(f"[Resize] Emituję finished: {message}")
            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Błąd podczas zmniejszania obrazów: {e}"
            logger.error(f"[Resize] {error_msg}")
            self.error_occurred.emit(error_msg)

    def _find_files_to_resize(self) -> List[str]:
        """Znajduje pliki do zmniejszenia"""
        files_to_resize = []
        supported_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        }

        try:
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    if file_ext in supported_extensions:
                        files_to_resize.append(item_path)

            logger.info(f"Znaleziono {len(files_to_resize)} plików do zmniejszenia")
            return files_to_resize

        except Exception as e:
            logger.error(f"Błąd podczas wyszukiwania plików: {e}")
            return []

    def _resize_image(self, file_path: str) -> bool:
        """Zmniejsza pojedynczy obraz"""
        try:
            logger.info(f"[Resize] _resize_image START: {file_path}")

            # Import Pillow tutaj, żeby nie wymagać go globalnie
            logger.info(f"[Resize] Importuję PIL.Image")
            from PIL import Image

            # Otwórz obraz
            logger.info(f"[Resize] Otwieram obraz: {file_path}")
            with Image.open(file_path) as img:
                logger.info(f"[Resize] Obraz otwarty, rozmiar: {img.size}")

                original_width, original_height = img.size
                new_width, new_height = self._calculate_new_size(
                    original_width, original_height
                )

                logger.info(f"[Resize] Nowy rozmiar: {new_width}x{new_height}")

                # Sprawdź czy zmniejszenie jest potrzebne
                if new_width >= original_width and new_height >= original_height:
                    logger.info(f"[Resize] Zmniejszenie nie jest potrzebne")
                    return False

                # Zmniejsz obraz
                logger.info(f"[Resize] Zmniejszam obraz")
                resized_img = img.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

                # Zapisz z powrotem do tego samego pliku
                logger.info(f"[Resize] Zapisuję zmniejszony obraz: {file_path}")
                resized_img.save(file_path, quality=85, optimize=True)
                logger.info(f"[Resize] Zapis zakończony pomyślnie")
                return True

        except ImportError:
            logger.error("[Resize] Biblioteka Pillow nie jest zainstalowana")
            return False
        except Exception as e:
            logger.error(f"[Resize] Błąd zmniejszania {file_path}: {e}")
            return False
        finally:
            logger.info(f"[Resize] _resize_image END: {file_path}")

    def _calculate_new_size(self, width: int, height: int) -> Tuple[int, int]:
        """Oblicza nowe wymiary według zasad skalowania"""
        # Oblicz różnicę między bokami w procentach
        max_side = max(width, height)
        min_side = min(width, height)
        difference_percent = ((max_side - min_side) / max_side) * 100

        # Jeśli różnica <= 30% (kwadratowy lub prawie kwadratowy)
        if difference_percent <= 30:
            # Skaluj tak, żeby mniejszy bok miał 1024px
            if width <= height:
                # Obraz jest szerszy niż wyższy lub kwadratowy
                new_width = 1024
                new_height = int((height / width) * 1024)
            else:
                # Obraz jest wyższy niż szerszy
                new_height = 1024
                new_width = int((width / height) * 1024)
        else:
            # Różnica > 30% - skaluj tak, żeby większy bok miał 1600px
            if width >= height:
                # Obraz jest szerszy niż wyższy
                new_width = 1600
                new_height = int((height / width) * 1600)
            else:
                # Obraz jest wyższy niż szerszy
                new_height = 1600
                new_width = int((width / height) * 1600)

        # Sprawdź czy nowe wymiary nie są większe od oryginalnych
        if new_width > width or new_height > height:
            return width, height  # Nie powiększaj

        return new_width, new_height


class FileRenamerWorker(BaseWorker):
    """Worker do skracania nazw plików"""

    # Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker
    finished = pyqtSignal(str)  # message
    pairs_found = pyqtSignal(list)  # lista par do wyświetlenia
    user_confirmation_needed = pyqtSignal(list)  # czeka na potwierdzenie użytkownika

    def __init__(self, folder_path: str, max_name_length: int):
        super().__init__(folder_path)
        self.max_name_length = max_name_length
        self.user_confirmed = False
        self.files_info = None

    def confirm_operation(self):
        """Metoda wywoływana po potwierdzeniu przez użytkownika"""
        self.user_confirmed = True

    def _run_operation(self):
        """Główna metoda skracania nazw plików"""
        try:
            logger.info(f"Rozpoczęcie skracania nazw w folderze: {self.folder_path}")

            # Znajdź pary i pliki do skrócenia
            self.files_info = self._analyze_files()

            if not self.files_info["all_files"]:
                self.finished.emit("Brak plików do przetworzenia")
                return

            # Wyślij listę par do wyświetlenia i czekaj na potwierdzenie
            self.user_confirmation_needed.emit(self.files_info["pairs"])

            # Czekaj na potwierdzenie użytkownika
            while not self.user_confirmed:
                self.msleep(100)  # Czekaj 100ms
                if self.isInterruptionRequested():
                    return

            # Teraz rozpocznij skracanie nazw
            self._perform_renaming()

        except Exception as e:
            error_msg = f"Błąd podczas skracania nazw: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _perform_renaming(self):
        """Wykonuje właściwe skracanie nazw"""
        try:
            renamed_count = 0
            error_count = 0

            # Najpierw pary
            if self.files_info["pairs"]:
                self.progress_updated.emit(
                    0, len(self.files_info["pairs"]), "Skracanie nazw par..."
                )
                for i, (archive_file, preview_file) in enumerate(
                    self.files_info["pairs"]
                ):
                    try:
                        # Sprawdź czy nazwa wymaga skrócenia
                        archive_name = os.path.splitext(os.path.basename(archive_file))[
                            0
                        ]
                        if len(archive_name) > self.max_name_length:
                            # Wygeneruj nową nazwę
                            new_name = self._generate_random_name()

                            # Zmień nazwę pliku archiwum
                            if self._rename_file(archive_file, new_name):
                                renamed_count += 1

                            # Zmień nazwę pliku podglądu
                            if self._rename_file(preview_file, new_name):
                                renamed_count += 1

                            logger.info(f"Skrócono parę: {new_name}")
                        else:
                            logger.debug(
                                f"Pominięto parę (nazwa w normie): {archive_name}"
                            )

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["pairs"]),
                            f"Skrócono parę: {new_name if len(archive_name) > self.max_name_length else archive_name}",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Błąd podczas skracania pary: {e}")

            # Potem pliki bez pary
            if self.files_info["unpaired"]:
                self.progress_updated.emit(
                    0,
                    len(self.files_info["unpaired"]),
                    "Skracanie nazw plików bez pary...",
                )
                for i, file_path in enumerate(self.files_info["unpaired"]):
                    try:
                        filename = os.path.basename(file_path)
                        name_without_ext = os.path.splitext(filename)[0]

                        if len(name_without_ext) > self.max_name_length:
                            # Wygeneruj nową nazwę
                            new_name = self._generate_random_name()

                            if self._rename_file(file_path, new_name):
                                renamed_count += 1
                                logger.info(f"Skrócono nazwę: {filename} -> {new_name}")
                        else:
                            logger.debug(f"Pominięto (nazwa w normie): {filename}")

                        self.progress_updated.emit(
                            i + 1,
                            len(self.files_info["unpaired"]),
                            f"Przetwarzanie: {filename}",
                        )

                    except Exception as e:
                        error_count += 1
                        logger.error(f"Błąd podczas skracania {filename}: {e}")

            # Przygotuj komunikat końcowy
            message = f"Skracanie nazw zakończone: {renamed_count} plików skrócono"
            if error_count > 0:
                message += f", {error_count} błędów"

            self.finished.emit(message)

        except Exception as e:
            error_msg = f"Błąd podczas skracania nazw: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def _analyze_files(self) -> dict:
        """Analizuje pliki w folderze i znajduje pary"""
        files_info = {"all_files": [], "pairs": [], "unpaired": []}

        try:
            # Rozszerzenia plików
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

            # Zbierz wszystkie pliki
            archive_files = []
            preview_files = []

            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if os.path.isfile(item_path):
                    file_ext = os.path.splitext(item)[1].lower()
                    name_without_ext = os.path.splitext(item)[0]

                    if file_ext in archive_extensions:
                        archive_files.append((name_without_ext, item_path))
                    elif file_ext in preview_extensions:
                        preview_files.append((name_without_ext, item_path))

            # Znajdź pary (pliki o tej samej nazwie bez rozszerzenia)
            archive_names = {name: path for name, path in archive_files}
            preview_names = {name: path for name, path in preview_files}

            # Znajdź wspólne nazwy (pary)
            common_names = set(archive_names.keys()) & set(preview_names.keys())

            for name in common_names:
                files_info["pairs"].append((archive_names[name], preview_names[name]))

            # Znajdź pliki bez pary
            all_archive_paths = set(archive_names.values())
            all_preview_paths = set(preview_names.values())
            paired_archive_paths = {archive_names[name] for name in common_names}
            paired_preview_paths = {preview_names[name] for name in common_names}

            unpaired_archives = all_archive_paths - paired_archive_paths
            unpaired_images = all_preview_paths - paired_preview_paths

            files_info["unpaired"] = list(unpaired_archives | unpaired_images)
            files_info["all_files"] = list(all_archive_paths | all_preview_paths)

            logger.info(
                f"Znaleziono {len(files_info['pairs'])} par i {len(files_info['unpaired'])} plików bez pary"
            )
            return files_info

        except Exception as e:
            logger.error(f"Błąd podczas analizy plików: {e}")
            return files_info

    def _generate_random_name(self) -> str:
        """Generuje losową nazwę z zestawu 8 cyfr + 8 liter"""
        # Generuj 8 cyfr i 8 liter
        digits = "".join(random.choices(string.digits, k=8))
        letters = "".join(random.choices(string.ascii_uppercase, k=8))

        # Połącz i wymieszaj
        combined = digits + letters
        shuffled = "".join(random.sample(combined, len(combined)))

        return shuffled

    def _rename_file(self, file_path: str, new_name: str) -> bool:
        """Zmienia nazwę pliku zachowując rozszerzenie"""
        try:
            # Pobierz rozszerzenie
            file_dir = os.path.dirname(file_path)
            file_ext = os.path.splitext(file_path)[1]

            # Utwórz nową nazwę z rozszerzeniem
            new_file_path = os.path.join(file_dir, new_name + file_ext)

            # Sprawdź czy nowa nazwa nie istnieje
            if os.path.exists(new_file_path):
                logger.warning(f"Plik o nazwie {new_name + file_ext} już istnieje")
                return False

            # Zmień nazwę
            os.rename(file_path, new_file_path)
            logger.debug(
                f"Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}"
            )
            return True

        except Exception as e:
            logger.error(f"Błąd zmiany nazwy {file_path}: {e}")
            return False


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


class ToolsTab(QWidget):
    # Sygnały
    working_directory_changed = pyqtSignal(str)
    show_info_message = pyqtSignal(str, str)
    show_error_message = pyqtSignal(str, str)

    def __init__(self, config_manager=None):
        super().__init__()
        self.config_manager = config_manager
        self.current_working_directory = None

        # Inicjalizacja workerów
        self.webp_converter = None
        self.asset_rebuilder = None
        self.image_resizer = None
        self.file_renamer = None
        self.remove_worker = None

        # Inicjalizacja UI
        self._setup_ui()

    def _validate_working_directory(self) -> bool:
        """Wspólna walidacja folderu roboczego"""
        logger.debug(f"Walidacja folderu roboczego: {self.current_working_directory}")
        logger.debug(
            f"Folder istnieje: {os.path.exists(self.current_working_directory) if self.current_working_directory else False}"
        )

        if not self.current_working_directory or not os.path.exists(
            self.current_working_directory
        ):
            logger.warning(
                f"Folder roboczy nie jest ustawiony lub nie istnieje: {self.current_working_directory}"
            )
            QMessageBox.warning(
                self, "Błąd", "Folder roboczy nie jest ustawiony lub nie istnieje."
            )
            return False
        return True

    def _handle_worker_lifecycle(self, worker, button, original_text):
        """Jednolita obsługa cyklu życia worker"""
        try:
            # Wyłącz przycisk podczas operacji
            button.setEnabled(False)
            button.setText(f"{original_text}...")

            # Połącz sygnały
            worker.progress_updated.connect(
                lambda c, t, m: self._handle_worker_progress(button, c, t, m)
            )
            worker.finished.connect(
                lambda m: self._handle_worker_finished(button, m, original_text)
            )
            worker.error_occurred.connect(
                lambda e: self._handle_worker_error(button, e, original_text)
            )

            # Uruchom worker
            worker.start()

            logger.info(
                f"Rozpoczęto operację w folderze: {self.current_working_directory}"
            )

        except Exception as e:
            logger.error(f"Błąd podczas rozpoczynania operacji: {e}")
            QMessageBox.critical(self, "Błąd", f"Nie można rozpocząć operacji: {e}")
            self._reset_button_state(button, original_text)

    def _start_operation_with_confirmation(
        self, operation_name: str, description: str, worker_factory
    ):
        """Uniwersalna metoda do rozpoczynania operacji z potwierdzeniem"""
        if not self._validate_working_directory():
            return

        reply = QMessageBox.question(
            self,
            f"Potwierdzenie {operation_name.lower()}",
            f"Czy na pewno chcesz {operation_name.lower()} w folderze:\n{self.current_working_directory}?\n\n{description}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            worker = worker_factory()

            # Mapowanie nazw operacji na nazwy przycisków i pól klasy
            button_mapping = {
                "konwersji na webp": ("webp_button", "webp_converter"),
                "przebudowy assetów": ("rebuild_button", "asset_rebuilder"),
                "zmniejszania obrazów": ("image_resizer_button", "image_resizer"),
                "skracania nazw plików": ("file_renamer_button", "file_renamer"),
                "usuwania prefixu/suffixu": ("remove_button", "remove_worker"),
            }

            button_name, worker_attr = button_mapping.get(
                operation_name.lower(), ("webp_button", "webp_converter")
            )
            logger.debug(
                f"Mapowanie operacji '{operation_name}' na przycisk '{button_name}' i pole '{worker_attr}'"
            )
            button = getattr(self, button_name)
            setattr(self, worker_attr, worker)
            self._handle_worker_lifecycle(worker, button, button.text())

    def _setup_ui(self):
        """Setup user interface for tools tab"""
        # Główny layout poziomy (2 kolumny)
        main_layout = QHBoxLayout()

        # Lewa kolumna - skalowana
        left_column = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Pliki"))

        # Podział kolumny "Pliki" na dwa widoki listy
        files_layout = QHBoxLayout()

        # Lewy widok - pliki archiwum
        self.archive_list = QListWidget()
        self.archive_list.setAlternatingRowColors(True)
        self.archive_list.itemDoubleClicked.connect(self._on_archive_double_clicked)
        files_layout.addWidget(self.archive_list)

        # Prawy widok - pliki podglądów
        self.preview_list = QListWidget()
        self.preview_list.setAlternatingRowColors(True)
        self.preview_list.itemDoubleClicked.connect(self._on_preview_double_clicked)
        files_layout.addWidget(self.preview_list)

        left_layout.addLayout(files_layout)
        left_column.setLayout(left_layout)

        # Prawa kolumna - stała szerokość 175px
        right_column = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Narzędzia"))

        # Przycisk 1 - konwersja na WebP
        self.webp_button = QPushButton("Konwertuj na WebP")
        self.webp_button.clicked.connect(self._on_webp_conversion_clicked)
        right_layout.addWidget(self.webp_button)

        # Przycisk 2 - zmniejszanie obrazów
        self.image_resizer_button = QPushButton("Zmniejsz obrazy")
        self.image_resizer_button.clicked.connect(self._on_image_resizing_clicked)
        right_layout.addWidget(self.image_resizer_button)

        # Przycisk 3 - skracanie nazw plików
        self.file_renamer_button = QPushButton("Skróć nazwy plików")
        self.file_renamer_button.clicked.connect(self._on_file_renaming_clicked)
        right_layout.addWidget(self.file_renamer_button)

        # Przycisk 4 - usuwanie prefixu/suffixu z nazw plików
        self.remove_button = QPushButton("Usuń prefix/suffix")
        self.remove_button.clicked.connect(self._on_remove_clicked)
        right_layout.addWidget(self.remove_button)

        # Rozciągacz
        right_layout.addSpacerItem(
            QSpacerItem(
                20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
            )
        )
        # 5 przycisk na dole - przebudowa assetów
        self.rebuild_button = QPushButton("Przebuduj assety")
        self.rebuild_button.clicked.connect(self._on_rebuild_assets_clicked)
        right_layout.addWidget(self.rebuild_button)
        right_column.setLayout(right_layout)
        right_column.setFixedWidth(175)

        # Dodanie kolumn do głównego layoutu
        main_layout.addWidget(left_column, 1)  # Stretch factor 1 - skalowana
        main_layout.addWidget(right_column, 0)  # Stretch factor 0 - stała szerokość

        self.setLayout(main_layout)
        logger.debug("ToolsTab UI setup completed with 2-column layout")

    def set_working_directory(self, directory_path: str):
        """Ustawia folder roboczy i skanuje pliki"""
        logger.debug(f"ToolsTab.set_working_directory() wywołane z: {directory_path}")

        if not directory_path or not os.path.exists(directory_path):
            logger.warning(f"Nieprawidłowy folder roboczy: {directory_path}")
            self.clear_lists()
            self._update_button_states()
            return

        self.current_working_directory = directory_path
        logger.debug(
            f"Ustawiono current_working_directory: {self.current_working_directory}"
        )

        self.scan_working_directory(directory_path)
        self.working_directory_changed.emit(directory_path)
        self._update_button_states()
        logger.info(f"Ustawiono folder roboczy: {directory_path}")

    def scan_working_directory(self, directory_path: str):
        """Skanuje folder roboczy w poszukiwaniu plików archiwum i podglądów"""
        try:
            if not os.path.exists(directory_path):
                logger.error(f"Folder nie istnieje: {directory_path}")
                return

            # Rozszerzenia plików
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

            # Skanuj pliki
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

            # Sortuj pliki alfabetycznie
            archive_files.sort(key=str.lower)
            preview_files.sort(key=str.lower)

            # Aktualizuj listy
            self._update_archive_list(archive_files)
            self._update_preview_list(preview_files)

            logger.info(
                f"Skanowanie zakończone: {len(archive_files)} archiwów, {len(preview_files)} podglądów"
            )

        except Exception as e:
            logger.error(f"Błąd podczas skanowania folderu {directory_path}: {e}")
            QMessageBox.warning(self, "Błąd", f"Nie można skanować folderu: {e}")

    def _update_archive_list(self, archive_files: list):
        """Aktualizuje listę plików archiwum"""
        self.archive_list.clear()
        for file_name in archive_files:
            item = QListWidgetItem(file_name)
            item.setData(Qt.ItemDataRole.UserRole, file_name)
            self.archive_list.addItem(item)

    def _update_preview_list(self, preview_files: list):
        """Aktualizuje listę plików podglądów"""
        self.preview_list.clear()
        for file_name in preview_files:
            # Pobierz rozdzielczość obrazu
            resolution = self._get_image_resolution(file_name)
            display_text = f"{file_name} - res: {resolution}"

            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, file_name)
            self.preview_list.addItem(item)

    def _get_image_resolution(self, file_name: str) -> str:
        """Pobiera rozdzielczość obrazu w formacie 'szerokość x wysokość'"""
        if not self.current_working_directory:
            return "brak danych"

        file_path = os.path.join(self.current_working_directory, file_name)

        try:
            # Import Pillow tutaj, żeby nie wymagać go globalnie
            from PIL import Image

            with Image.open(file_path) as img:
                width, height = img.size
                return f"{width} x {height}"

        except ImportError:
            logger.warning(
                "Biblioteka Pillow nie jest zainstalowana - nie można odczytać rozdzielczości"
            )
            return "brak Pillow"
        except Exception as e:
            logger.debug(f"Nie można odczytać rozdzielczości {file_name}: {e}")
            return "błąd odczytu"

    def clear_lists(self):
        """Czyści obie listy"""
        self.archive_list.clear()
        self.preview_list.clear()

    def _update_button_states(self):
        """Aktualizuje stan wszystkich przycisków"""
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
        if self.remove_button:
            self.remove_button.setEnabled(has_working_folder)

    def _handle_worker_progress(
        self, button: QPushButton, current: int, total: int, message: str
    ):
        WorkerManager.handle_progress(button, current, total, message)

    def _handle_worker_finished(
        self, button: QPushButton, message: str, original_text: str
    ):
        WorkerManager.handle_finished(button, message, original_text, self)

    def _handle_worker_error(
        self, button: QPushButton, error_message: str, original_text: str
    ):
        WorkerManager.handle_error(button, error_message, original_text, self)

    def _reset_button_state(self, button: QPushButton, original_text: str):
        WorkerManager.reset_button_state(button, original_text, self)

    def closeEvent(self, event):
        """Zatrzymuje wszystkie aktywne wątki przed zniszczeniem"""
        try:
            logger.info("ToolsTab: Zatrzymywanie aktywnych wątków...")

            # Lista wszystkich wątków do zatrzymania
            workers_to_stop = []

            if hasattr(self, "webp_converter") and self.webp_converter:
                workers_to_stop.append(self.webp_converter)
            if hasattr(self, "asset_rebuilder") and self.asset_rebuilder:
                workers_to_stop.append(self.asset_rebuilder)
            if hasattr(self, "image_resizer") and self.image_resizer:
                workers_to_stop.append(self.image_resizer)
            if hasattr(self, "file_renamer") and self.file_renamer:
                workers_to_stop.append(self.file_renamer)
            if hasattr(self, "remove_worker") and self.remove_worker:
                workers_to_stop.append(self.remove_worker)

            # Zatrzymaj wszystkie wątki
            for worker in workers_to_stop:
                if worker and worker.isRunning():
                    logger.info(f"Zatrzymywanie workera: {worker.__class__.__name__}")
                    worker.stop()

            logger.info("ToolsTab: Wszystkie wątki zostały zatrzymane")

        except Exception as e:
            logger.error(f"Błąd podczas zatrzymywania wątków w ToolsTab: {e}")

        # Zaakceptuj zdarzenie zamknięcia
        event.accept()

    def _on_webp_conversion_clicked(self):
        """Obsługuje kliknięcie przycisku konwersji na WebP"""
        logger.debug(
            f"Kliknięto przycisk WebP. Folder roboczy: {self.current_working_directory}"
        )
        logger.debug(f"Przycisk WebP enabled: {self.webp_button.isEnabled()}")

        description = (
            "Ta operacja:\n"
            "• Skonwertuje pliki JPG, PNG, GIF, BMP, TIFF na WebP\n"
            "• Pominie już istniejące pliki WebP\n"
            "• Usunie oryginalne pliki po udanej konwersji\n"
            "• Zoptymalizuje rozmiar plików"
        )
        self._start_operation_with_confirmation(
            "konwersji na WebP",
            description,
            lambda: WebPConverterWorker(self.current_working_directory),
        )

    def _on_rebuild_assets_clicked(self):
        """Obsługuje kliknięcie przycisku przebudowy assetów"""
        description = (
            "Ta operacja:\n"
            "• Usunie wszystkie pliki .asset\n"
            "• Usunie folder .cache\n"
            "• Utworzy nowe assety na podstawie plików archiwum"
        )
        self._start_operation_with_confirmation(
            "przebudowy assetów",
            description,
            lambda: AssetRebuilderWorker(self.current_working_directory),
        )

    def _on_archive_double_clicked(self, item: QListWidgetItem):
        """Obsługuje podwójne kliknięcie na plik archiwum"""
        file_name = item.data(Qt.ItemDataRole.UserRole)
        if not file_name or not self.current_working_directory:
            return

        full_path = os.path.join(self.current_working_directory, file_name)
        if os.path.exists(full_path):
            try:
                # Otwórz archiwum w domyślnej aplikacji
                if sys.platform == "win32":
                    os.startfile(full_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.Popen(["open", full_path])
                else:  # Linux
                    subprocess.Popen(["xdg-open", full_path])
                logger.info(f"Otworzono archiwum: {full_path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania archiwum {full_path}: {e}")
                QMessageBox.warning(self, "Błąd", f"Nie można otworzyć archiwum: {e}")
        else:
            logger.warning(f"Plik nie istnieje: {full_path}")
            QMessageBox.warning(self, "Błąd", f"Plik nie istnieje: {file_name}")

    def _on_preview_double_clicked(self, item: QListWidgetItem):
        """Obsługuje podwójne kliknięcie na plik podglądu"""
        file_name = item.data(Qt.ItemDataRole.UserRole)
        if not file_name or not self.current_working_directory:
            return

        full_path = os.path.join(self.current_working_directory, file_name)
        if os.path.exists(full_path):
            try:
                # Otwórz podgląd w oknie podglądu
                from core.preview_window import PreviewWindow

                # Zabezpieczenie przed wieloma oknami
                if hasattr(self, "preview_window") and self.preview_window:
                    self.preview_window.close()

                self.preview_window = PreviewWindow(full_path, self)
                self.preview_window.show_window()
                logger.info(f"Otworzono podgląd: {full_path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania podglądu {full_path}: {e}")
                QMessageBox.warning(self, "Błąd", f"Nie można otworzyć podglądu: {e}")
        else:
            logger.warning(f"Plik nie istnieje: {full_path}")
            QMessageBox.warning(self, "Błąd", f"Plik nie istnieje: {file_name}")

    def _on_image_resizing_clicked(self):
        """Obsługuje kliknięcie przycisku zmniejszania obrazów"""
        logger.debug(
            f"Kliknięto przycisk Image Resizer. Folder roboczy: {self.current_working_directory}"
        )
        logger.debug(
            f"Przycisk Image Resizer enabled: {self.image_resizer_button.isEnabled()}"
        )

        description = (
            "Ta operacja:\n"
            "• Zmniejszy obrazy o określonych zasadach skalowania\n"
            "• Pominie obrazy, które nie wymagają zmniejszenia\n"
            "• Zoptymalizuje rozmiar plików"
        )
        self._start_operation_with_confirmation(
            "zmniejszania obrazów",
            description,
            lambda: ImageResizerWorker(self.current_working_directory),
        )

    def _on_file_renaming_clicked(self):
        """Obsługuje kliknięcie przycisku skracania nazw plików"""
        if not self._validate_working_directory():
            return

        max_name_length, ok = QInputDialog.getInt(
            self,
            "Limit znaków",
            "Podaj maksymalną długość nazw plików (bez rozszerzenia):",
            16,  # Domyślny limit
            1,  # Minimalny limit
            256,  # Maksymalny limit
            1,  # Krok zmiany
        )

        if ok:
            self._start_file_renaming(max_name_length)

    def _start_file_renaming(self, max_name_length: int):
        """Rozpoczyna skracanie nazw plików"""
        # Utwórz worker do skracania nazw
        self.file_renamer = FileRenamerWorker(
            self.current_working_directory, max_name_length
        )

        # Dodatkowe połączenie sygnału dla potwierdzenia użytkownika
        self.file_renamer.user_confirmation_needed.connect(self._show_pairs_dialog)

        # Użyj wspólnej metody obsługi workerów
        self._handle_worker_lifecycle(
            self.file_renamer, self.file_renamer_button, "Skróć nazwy plików"
        )

    def _on_remove_clicked(self):
        """Obsługuje kliknięcie przycisku usuwania prefixu/suffixu"""
        if not self._validate_working_directory():
            return

        # Stwórz lepszy dialog do wyboru operacji i tekstu
        dialog = QDialog(self)
        dialog.setWindowTitle("Usuwanie prefiksów/sufiksów")
        dialog.setModal(True)
        dialog.resize(450, 200)

        layout = QVBoxLayout(dialog)

        # Sekcja wyboru trybu
        mode_label = QLabel("Wybierz tryb operacji:")
        mode_label.setProperty("class", "mode-label")
        layout.addWidget(mode_label)

        # Radio buttony do wyboru trybu
        mode_layout = QHBoxLayout()

        # Grupa buttonów (tylko jeden może być wybrany)
        button_group = QButtonGroup()

        prefix_radio = QRadioButton("Usuń PREFIX (początek nazwy)")
        suffix_radio = QRadioButton("Usuń SUFFIX (koniec nazwy)")

        # Dodaj do grupy (tylko jeden może być aktywny)
        button_group.addButton(prefix_radio)
        button_group.addButton(suffix_radio)

        # Domyślnie prefix
        prefix_radio.setChecked(True)

        mode_layout.addWidget(prefix_radio)
        mode_layout.addWidget(suffix_radio)
        layout.addLayout(mode_layout)

        # Sekcja wprowadzania tekstu
        text_label = QLabel("Tekst do usunięcia (wielkość liter ma znaczenie):")
        text_label.setProperty("class", "text-label")
        layout.addWidget(text_label)

        # Większe pole tekstowe
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(60)
        text_edit.setPlaceholderText(
            "Wpisz tekst który ma być usunięty z nazw plików..."
        )
        text_edit.setProperty("class", "tool-text")
        layout.addWidget(text_edit)

        # Przykłady
        example_label = QLabel(
            "Przykłady: _8K, _FINAL, temp_, backup_, ' 0' (spacja+zero)"
        )
        example_label.setProperty("class", "example-label")
        layout.addWidget(example_label)

        # Przyciski
        button_layout = QHBoxLayout()
        ok_button = QPushButton("USUŃ")
        cancel_button = QPushButton("Anuluj")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        # Wyświetl dialog
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            # WAŻNE: Nie używamy strip() żeby zachować spacje!
            text_to_remove = text_edit.toPlainText().rstrip(
                "\n\r"
            )  # Usuń tylko nowe linie na końcu
            if not text_to_remove:
                QMessageBox.warning(
                    self, "Błąd", "Proszę wprowadzić tekst do usunięcia."
                )
                return

            selected_mode = "prefix" if prefix_radio.isChecked() else "suffix"
            self._start_remove(text_to_remove, selected_mode)

    def _start_remove(self, text_to_remove: str, mode: str):
        """Rozpoczyna usuwanie prefixu/suffixu z nazw plików"""
        try:
            # Wyłącz przycisk podczas usuwania
            self.remove_button.setEnabled(False)
            self.remove_button.setText("Usuwanie...")

            # Utwórz worker do usuwania
            self.remove_worker = PrefixSuffixRemoverWorker(
                self.current_working_directory, text_to_remove, mode
            )

            # Połącz sygnały
            self.remove_worker.progress_updated.connect(
                lambda c, t, m: self._handle_worker_progress(
                    self.remove_button, c, t, m
                )
            )
            self.remove_worker.finished.connect(
                lambda m: self._handle_worker_finished(
                    self.remove_button, m, "Usuń prefix/suffix"
                )
            )
            self.remove_worker.error_occurred.connect(
                lambda e: self._handle_worker_error(
                    self.remove_button, e, "Usuń prefix/suffix"
                )
            )

            # Uruchom worker
            self.remove_worker.start()

            logger.info(
                f"Rozpoczęto usuwanie {mode} w folderze: {self.current_working_directory}"
            )

        except Exception as e:
            logger.error(f"Błąd podczas rozpoczynania usuwania: {e}")
            QMessageBox.critical(self, "Błąd", f"Nie można rozpocząć usuwania: {e}")
            self._reset_button_state(self.remove_button, "Usuń prefix/suffix")

    def _show_pairs_dialog(self, pairs):
        """Wyświetla okno z listą par, które będą zmieniane"""
        if not pairs:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Pary plików do zmiany nazw")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Nagłówek
        header_label = QLabel(f"Znaleziono {len(pairs)} par plików do przetworzenia:")
        header_label.setProperty("class", "dialog-header")
        layout.addWidget(header_label)

        # Lista par
        list_widget = QListWidget()
        for archive_path, preview_path in pairs:
            archive_name = os.path.basename(archive_path)
            preview_name = os.path.basename(preview_path)
            item_text = f"📦 {archive_name}\n   🖼️ {preview_name}"
            list_widget.addItem(item_text)

        layout.addWidget(list_widget)

        # Przyciski
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Kontynuuj")
        cancel_button = QPushButton("Anuluj")

        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Wyświetl okno
        result = dialog.exec()

        # Jeśli użytkownik anulował, zatrzymaj worker
        if result == QDialog.DialogCode.Rejected:
            if hasattr(self, "file_renamer") and self.file_renamer:
                self.file_renamer.quit()
                if not self.file_renamer.wait(3000):
                    self.file_renamer.terminate()
                    self.file_renamer.wait(2000)
        else:
            # Użytkownik potwierdził - kontynuuj operację
            self.file_renamer.confirm_operation()


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = ToolsTab()
    w.show()
    sys.exit(app.exec())
