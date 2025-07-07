import os
import sys
import logging

logger = logging.getLogger(__name__)

# ALWAYS prefer the local version of the Rust scanner from core/__rust
rust_dir = os.path.join(os.path.dirname(__file__), "__rust")

# Temporarily remove site-packages from path to force the local version
original_path = sys.path.copy()
# Remove all paths containing site-packages for scanner_rust
sys.path = [p for p in sys.path if 'site-packages' not in p or 'scanner_rust' not in p]

# Add the local folder at the beginning
if rust_dir not in sys.path:
    sys.path.insert(0, rust_dir)

try:
    import scanner_rust
    scanner_location = scanner_rust.__file__
    
    # Pobierz informacje o kompilacji
    build_info = scanner_rust.get_build_info()
    build_timestamp = build_info.get('build_timestamp', 'unknown')
    module_number = build_info.get('module_number', '1')
    
    logger.info(f"🦀 ✅ SUCCESS: Loaded LOCAL Rust scanner engine from: {scanner_location}")
    print(f"🦀 RUST SCANNER: Using LOCAL version from: {scanner_location} [build: {build_timestamp}, module: {module_number}]")
except ImportError as e:
    # Restore the original path in case of error
    sys.path = original_path
    try:
        import scanner_rust
        scanner_location = scanner_rust.__file__
        
        # Pobierz informacje o kompilacji
        build_info = scanner_rust.get_build_info()
        build_timestamp = build_info.get('build_timestamp', 'unknown')
        module_number = build_info.get('module_number', '1')
        
        logger.warning(f"🦀 ⚠️ FALLBACK: Using GLOBAL Rust scanner engine from: {scanner_location}")
        print(f"🦀 RUST SCANNER: FALLBACK - using global version from: {scanner_location} [build: {build_timestamp}, module: {module_number}]")
    except ImportError:
        logger.error(f"🦀 ❌ ERROR: Cannot load any version of scanner_rust: {e}")
        raise ImportError("Cannot load Rust backend (scanner_rust): {}".format(e))

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
