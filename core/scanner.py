import os
import sys
import logging
import importlib.util

logger = logging.getLogger(__name__)

def _load_scanner_rust():
    """
    Attempts to load scanner_rust module using importlib from local __rust directory.
    Falls back to global import if local load fails.
    """
    rust_dir = os.path.join(os.path.dirname(__file__), "__rust")
    
    # 1. Try to load from local __rust directory
    try:
        if os.path.exists(rust_dir):
            # Find the extension file (.pyd on Windows, .so on Linux/macOS)
            ext_file = None
            for f in os.listdir(rust_dir):
                if f.startswith("scanner_rust") and (f.endswith(".pyd") or f.endswith(".so")):
                    ext_file = os.path.join(rust_dir, f)
                    break
            
            if ext_file:
                spec = importlib.util.spec_from_file_location("scanner_rust", ext_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules["scanner_rust"] = module # Register in sys.modules
                    spec.loader.exec_module(module)
                    
                    # Verify content
                    location = getattr(module, '__file__', ext_file)
                    build_info = getattr(module, 'get_build_info', lambda: {})()
                    timestamp = build_info.get('build_timestamp', 'unknown')
                    
                    logger.info(f"🦀 ✅ SUCCESS: Loaded LOCAL Rust scanner from: {location}")
                    print(f"🦀 RUST SCANNER: Using LOCAL version [build: {timestamp}]")
                    return module
    except Exception as e:
        logger.warning(f"Failed to load local scanner_rust: {e}")

    # 2. Fallback to global import
    try:
        import scanner_rust
        location = getattr(scanner_rust, '__file__', 'global site-packages')
        logger.warning(f"🦀 ⚠️ FALLBACK: Using GLOBAL scanner_rust from: {location}")
        return scanner_rust
    except ImportError:
        logger.error("🦀 ❌ ERROR: Could not load scanner_rust module")
        return None

# Load the module
scanner_rust = _load_scanner_rust()

# Define Mock if loading failed
if scanner_rust is None:
    print("💡 TIP: Run 'python rebuild_rust.py' to rebuild the Rust engine.")
    class MockScannerRust:
        def get_build_info(self): return {}
        class RustAssetRepository:
            def find_and_create_assets(self, *args, **kwargs): return []
            def load_existing_assets(self, *args, **kwargs): return []
            def create_single_asset(self, *args, **kwargs): return None
    scanner_rust = MockScannerRust()
    logger.warning("Using mock Rust backend.")

class AssetRepository:
    """
    Wrapper for Rust backend of asset scanner.
    """
    def __init__(self):
        self._rust_repo = scanner_rust.RustAssetRepository()
        self.use_rust = True

    def find_and_create_assets(self, folder_path, progress_callback=None):
        return self._rust_repo.find_and_create_assets(folder_path, progress_callback)

    def load_existing_assets(self, folder_path):
        return self._rust_repo.load_existing_assets(folder_path)

    def _create_single_asset(self, name, archive_path, preview_path, work_folder_path):
        """
        Creates a single asset using Rust backend.
        This method is used by pairing_model.py for manual asset creation.
        """
        try:
            # Use the Rust backend method
            asset_data = self._rust_repo.create_single_asset(
                name, archive_path, preview_path, work_folder_path
            )
            return asset_data
        except Exception as e:
            logger.error(f"Error creating single asset: {e}")
            return None

    def create_thumbnail_for_asset(self, asset_file_path, preview_path):
        """
        Creates thumbnail for an asset using Rust backend.
        """
        try:
            # This would need to be implemented in Rust backend
            # For now, return True as placeholder
            logger.info(f"Creating thumbnail for asset: {asset_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return False
