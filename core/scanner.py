import glob
import json
import os

from core.thumbnail import process_thumbnail


def get_file_size_mb(file_path):
    """
    Zwraca rozmiar pliku w MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)  # Konwersja bajtów na MB
        return round(size_mb, 2)  # Zaokrąglenie do 2 miejsc po przecinku
    except Exception:
        return 0


def create_thumbnail_for_asset(asset_path, image_path):
    """
    Tworzy thumbnail dla pliku asset i aktualizuje plik asset

    Args:
        asset_path (str): Ścieżka do pliku .asset
        image_path (str): Ścieżka do pliku obrazu (preview)

    Returns:
        bool: True jeśli thumbnail został utworzony pomyślnie,
              False w przeciwnym razie
    """
    try:
        # Wywołaj funkcję process_thumbnail
        process_thumbnail(image_path)

        # Jeśli funkcja się wykonała bez błędów, zaktualizuj plik asset
        with open(asset_path, "r", encoding="utf-8") as asset_file:
            asset_data = json.load(asset_file)

        # Ustaw thumbnail na True
        asset_data["thumbnail"] = True

        # Zapisz zaktualizowany plik asset
        with open(asset_path, "w", encoding="utf-8") as asset_file:
            json.dump(asset_data, asset_file, indent=2, ensure_ascii=False)

        return True

    except Exception:
        return False


def create_unpair_files_json(folder_path, archive_by_name, image_by_name, common_names):
    """
    Tworzy plik unpair_files.json z listą plików bez pary

    Args:
        folder_path (str): Ścieżka do folderu
        archive_by_name (dict): Słownik plików archiwum według nazwy
        image_by_name (dict): Słownik plików obrazów według nazwy
        common_names (set): Zbiór nazw plików z parami

    Returns:
        str: Ścieżka do utworzonego pliku lub None w przypadku błędu
    """
    try:
        # Znajdź pliki bez pary
        unpaired_archives = []
        unpaired_previews = []

        # Pliki archiwum bez pary
        for name, archive_path in archive_by_name.items():
            if name not in common_names:
                unpaired_archives.append(os.path.basename(archive_path))

        # Pliki obrazów bez pary
        for name, image_path in image_by_name.items():
            if name not in common_names:
                unpaired_previews.append(os.path.basename(image_path))

        # Utwórz strukturę danych
        unpair_data = {
            "unpaired_archives": unpaired_archives,
            "unpaired_previews": unpaired_previews,
        }

        # Ścieżka do pliku unpair_files.json
        unpair_file_path = os.path.join(folder_path, "unpair_files.json")

        # Zapisz plik JSON
        with open(unpair_file_path, "w", encoding="utf-8") as unpair_file:
            json.dump(unpair_data, unpair_file, indent=2, ensure_ascii=False)

        return unpair_file_path

    except Exception:
        return None


def find_and_create_assets(folder_path, progress_callback=None):
    """
    Szuka par plików o tej samej nazwie w folderze:
    - pliki archiwum: zip, rar, sbsar
    - pliki obrazów: png, jpg, webp

    Dla każdej znalezionej pary tworzy plik .asset w formacie JSON
    Dodatkowo tworzy plik unpair_files.json z listą plików bez pary

    Args:
        folder_path (str): Ścieżka do folderu do skanowania
        progress_callback (callable): Funkcja callback do aktualizacji postępu
                                     Przyjmuje parametry: (current, total, message)
    """

    # Sprawdź czy folder istnieje
    if not os.path.exists(folder_path):
        if progress_callback:
            progress_callback(0, 0, f"Folder {folder_path} nie istnieje!")
        return

    # Definicje rozszerzeń
    archive_extensions = ["*.zip", "*.rar", "*.sbsar"]
    image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.webp"]

    # Znajdź wszystkie pliki archiwum
    archive_files = []
    for ext in archive_extensions:
        archive_files.extend(glob.glob(os.path.join(folder_path, ext)))
        archive_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))

    # Znajdź wszystkie pliki obrazów
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        image_files.extend(glob.glob(os.path.join(folder_path, ext.upper())))

    # Słownik do przechowywania plików według nazwy (bez rozszerzenia)
    archive_by_name = {}
    image_by_name = {}

    # Grupuj pliki archiwum według nazwy
    for archive_file in archive_files:
        name_without_ext = os.path.splitext(os.path.basename(archive_file))[0]
        archive_by_name[name_without_ext] = archive_file

    # Grupuj pliki obrazów według nazwy
    for image_file in image_files:
        name_without_ext = os.path.splitext(os.path.basename(image_file))[0]
        image_by_name[name_without_ext] = image_file

    # Znajdź wspólne nazwy (pary plików)
    common_names = set(archive_by_name.keys()) & set(image_by_name.keys())

    # Oblicz całkowitą liczbę operacji do wykonania
    total_operations = len(common_names)

    if progress_callback:
        progress_callback(
            0,
            total_operations,
            f"Znaleziono {total_operations} par plików do przetworzenia",
        )

    created_assets = []
    current_operation = 0

    # Dla każdej pary utwórz plik .asset
    for name in common_names:
        current_operation += 1

        if progress_callback:
            progress_callback(
                current_operation, total_operations, f"Przetwarzanie: {name}"
            )

        archive_path = archive_by_name[name]
        image_path = image_by_name[name]
        asset_path = os.path.join(folder_path, f"{name}.asset")

        # Utwórz plik .asset w formacie JSON (nadpisuje istniejący)
        try:
            # Pobierz rozmiar pliku archiwum w MB
            archive_size_mb = get_file_size_mb(archive_path)

            asset_data = {
                "name": name,
                "archive": os.path.basename(archive_path),
                "preview": os.path.basename(image_path),
                "size_mb": archive_size_mb,
                "thumbnail": None,
                "stars": None,
                "color": None,
                "meta": {},
            }

            with open(asset_path, "w", encoding="utf-8") as asset_file:
                json.dump(asset_data, asset_file, indent=2, ensure_ascii=False)

            created_assets.append(asset_path)

            # Utwórz thumbnail dla tego asset
            create_thumbnail_for_asset(asset_path, image_path)

        except Exception as e:
            if progress_callback:
                progress_callback(
                    current_operation,
                    total_operations,
                    f"Błąd podczas przetwarzania {name}: {e}",
                )

    # Utwórz plik z plikami bez pary
    if progress_callback:
        progress_callback(
            total_operations, total_operations, "Tworzenie pliku z plikami bez pary..."
        )

    create_unpair_files_json(folder_path, archive_by_name, image_by_name, common_names)

    # Finalne podsumowanie
    if progress_callback:
        progress_callback(
            total_operations,
            total_operations,
            f"Zakończono! Utworzono {len(created_assets)} plików .asset",
        )

    return created_assets


# Przykład użycia
if __name__ == "__main__":
    # Przykład wywołania funkcji
    # find_and_create_assets("ścieżka/do/folderu")
    pass
