import json
import os
import sys

# Dodaj ścieżkę do katalogu głównego projektu
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from core.scanner import find_and_create_assets
except ImportError:
    print("Błąd: Nie można zaimportować modułu scanner")
    sys.exit(1)


def load_config():
    """Pobiera konfigurację z pliku config.json"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku config.json w {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Błąd: Nieprawidłowy format JSON w config.json: {e}")
        return None


def test_scanner():
    """Testuje scanner.py używając ścieżki z config.json"""
    print("=== Test Scanner ===")

    # Pobierz konfigurację
    config = load_config()
    if not config:
        return

    # Pobierz ścieżkę z work_folder1
    folder_path = config.get("work_folder1", {}).get("path", "")

    if not folder_path:
        print("Błąd: Brak ścieżki w work_folder1.path w config.json")
        return

    print(f"Używana ścieżka: {folder_path}")

    # Sprawdź czy ścieżka istnieje
    if not os.path.exists(folder_path):
        print(f"Błąd: Folder {folder_path} nie istnieje!")
        return

    # Uruchom scanner
    print("\nUruchamiam scanner...")
    try:
        created_assets = find_and_create_assets(folder_path)
        assets_count = len(created_assets) if created_assets else 0
        print(f"\nTest zakończony. Utworzono {assets_count} plików asset.")
    except Exception as e:
        print(f"Błąd podczas uruchamiania scanner: {e}")


if __name__ == "__main__":
    test_scanner()
