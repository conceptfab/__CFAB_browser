import importlib.util
import os
import sys

# Dodaj core/__rust do sys.path, jeśli nie ma
rust_dir = os.path.join(os.path.dirname(__file__), "__rust")
if rust_dir not in sys.path:
    sys.path.insert(0, rust_dir)

try:
    import scanner_rust
except ImportError as e:
    raise ImportError("Nie można załadować Rustowego backendu (scanner_rust): {}".format(e))

class AssetRepository:
    """
    Wrapper na Rustowy backend skanera assetów.
    """
    def __init__(self):
        self._rust_repo = scanner_rust.RustAssetRepository()
        self.use_rust = True

    def find_and_create_assets(self, folder_path, progress_callback=None, use_async_thumbnails=False):
        return self._rust_repo.find_and_create_assets(folder_path, progress_callback)

    def load_existing_assets(self, folder_path):
        return self._rust_repo.load_existing_assets(folder_path)
