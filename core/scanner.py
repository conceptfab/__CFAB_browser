import os
import sys
import logging

logger = logging.getLogger(__name__)

# ZAWSZE preferuj lokalną wersję Rust scannera z core/__rust
rust_dir = os.path.join(os.path.dirname(__file__), "__rust")

# Usuń site-packages z path tymczasowo aby wymusić lokalną wersję
original_path = sys.path.copy()
# Usuń wszystkie ścieżki zawierające site-packages dla scanner_rust
sys.path = [p for p in sys.path if 'site-packages' not in p or 'scanner_rust' not in p]

# Dodaj lokalny folder na początek
if rust_dir not in sys.path:
    sys.path.insert(0, rust_dir)

try:
    import scanner_rust
    scanner_location = scanner_rust.__file__
    logger.info(f"🦀 ✅ SUKCES: Załadowano LOKALNY silnik Rust scanner z: {scanner_location}")
    print(f"🦀 RUST SCANNER: Używam LOKALNEJ wersji z: {scanner_location}")
except ImportError as e:
    # Przywróć oryginalną ścieżkę w przypadku błędu
    sys.path = original_path
    try:
        import scanner_rust
        scanner_location = scanner_rust.__file__
        logger.warning(f"🦀 ⚠️ FALLBACK: Używam GLOBALNEGO silnika Rust scanner z: {scanner_location}")
        print(f"🦀 RUST SCANNER: FALLBACK - używam globalnej wersji z: {scanner_location}")
    except ImportError:
        logger.error(f"🦀 ❌ BŁĄD: Nie można załadować żadnej wersji scanner_rust: {e}")
        raise ImportError("Nie można załadować Rustowego backendu (scanner_rust): {}".format(e))

class AssetRepository:
    """
    Wrapper na Rustowy backend skanera assetów.
    """
    def __init__(self):
        self._rust_repo = scanner_rust.RustAssetRepository()
        self.use_rust = True

    def find_and_create_assets(self, folder_path, progress_callback=None):
        return self._rust_repo.find_and_create_assets(folder_path, progress_callback)

    def load_existing_assets(self, folder_path):
        return self._rust_repo.load_existing_assets(folder_path)
