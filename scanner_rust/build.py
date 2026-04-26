import os
import sys
import subprocess
import shutil
import zipfile
import platform

# --- Konfiguracja ---
CRATES_DIR = "crates"
TARGET_DIR = "core/__rust"
MODULES = ["scanner", "image_tools", "hash_utils"]
# --------------------

def get_native_ext():
    """Returns the native extension for compiled modules on this platform."""
    if platform.system() == "Windows":
        return ".pyd"
    else:
        return ".so"

def resolve_maturin_command():
    """Find working maturin invocation."""
    # Try bare maturin first
    try:
        subprocess.run(["maturin", "--version"], capture_output=True, check=True)
        return "maturin"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # Fallback to python -m maturin
    try:
        subprocess.run([sys.executable, "-m", "maturin", "--version"], capture_output=True, check=True)
        return f"{sys.executable} -m maturin"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    raise RuntimeError("Could not find maturin. Install with: pip3 install maturin")

def clean_previous_builds(script_dir):
    """Czyści pozostałości po poprzednich kompilacjach."""
    print("🧹 --- Czyszczenie pozostałości po poprzednich kompilacjach ---")
    native_ext = get_native_ext()
    # 1. Usuń pliki .pyd z docelowego katalogu
    target_root_dir = os.path.join(script_dir, '..', TARGET_DIR)
    if os.path.exists(target_root_dir):
        for file in os.listdir(target_root_dir):
            if file.endswith(native_ext):
                file_path = os.path.join(target_root_dir, file)
                try:
                    os.remove(file_path)
                    print(f"🧹 Usunięto: {file}")
                except Exception as e:
                    print(f"⚠️  Nie udało się usunąć {file}: {e}")
    
    # 2. Usuń foldery target w każdym module
    for module in MODULES:
        module_path = os.path.join(script_dir, CRATES_DIR, module)
        target_dir = os.path.join(module_path, "target")
        if os.path.exists(target_dir):
            try:
                shutil.rmtree(target_dir)
                print(f"🧹 Usunięto folder target dla modułu: {module}")
            except Exception as e:
                print(f"⚠️  Nie udało się usunąć target dla {module}: {e}")
    
    # 3. Usuń główny folder target w scanner_rust
    main_target_dir = os.path.join(script_dir, "target")
    if os.path.exists(main_target_dir):
        try:
            shutil.rmtree(main_target_dir)
            print(f"🧹 Usunięto główny folder target")
        except Exception as e:
            print(f"⚠️  Nie udało się usunąć główny folder target: {e}")
    
    print("🧹 --- Czyszczenie zakończone ---\n")

def run_command(command, cwd, manifest_path):
    """Uruchamia polecenie i sprawdza, czy się powiodło."""
    full_command = f"{command} --manifest-path \"{manifest_path}\""
    print(f"[{cwd}]$ {full_command}")
    result = subprocess.run(full_command, cwd=cwd, shell=True, capture_output=True, text=True, encoding='utf-8')
    
    # Zawsze pokazuj wyjście
    print("--- STDOUT ---")
    print(result.stdout)
    print("--- STDERR ---")
    print(result.stderr)
    print("--- END OUTPUT ---")
    
    if result.returncode != 0:
        raise RuntimeError(f"Polecenie nie powiodło się: {full_command}")
    return result

def main():
    """Główna funkcja budująca."""
    print("🦀 --- Rozpoczęcie budowania modułów Rust ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Czyszczenie pozostałości po poprzednich kompilacjach
    clean_previous_builds(script_dir)
    
    # Tworzenie docelowego folderu, jeśli nie istnieje
    target_root_dir = os.path.join(script_dir, '..', TARGET_DIR)
    os.makedirs(target_root_dir, exist_ok=True)
    
    for module in MODULES:
        print(f"\n🦀 --- Budowanie modułu: {module} ---")
        module_path = os.path.join(script_dir, CRATES_DIR, module)
        manifest_path = os.path.join(module_path, "Cargo.toml")
        
        # 1. Budowanie koła (wheel)
        maturin_cmd = resolve_maturin_command()
        run_command(f"{maturin_cmd} build --release", cwd=module_path, manifest_path=manifest_path)
        
        # 2. Znajdowanie pliku .whl
        wheels_dir = os.path.join(script_dir, "target", "wheels")
        if not os.path.exists(wheels_dir):
            raise FileNotFoundError(f"Katalog 'wheels' nie został utworzony dla modułu {module}. Prawdopodobnie wystąpił błąd kompilacji.")
        
        wheel_files = [f for f in os.listdir(wheels_dir) if f.endswith(".whl")]
        if not wheel_files:
            raise FileNotFoundError(f"Nie znaleziono pliku .whl dla modułu {module}")
        latest_wheel = sorted(wheel_files, key=lambda f: os.path.getmtime(os.path.join(wheels_dir, f)), reverse=True)[0]
        wheel_path = os.path.join(wheels_dir, latest_wheel)
        print(f"🦀 Znaleziono koło: {wheel_path}")

        # 3. Rozpakowanie i przeniesienie natywnej biblioteki (.pyd/.so)
        native_ext = get_native_ext()
        lib_final_name = f"{module if module != 'scanner' else 'scanner_rust'}{native_ext}"
        target_lib_path = os.path.join(script_dir, '..', TARGET_DIR, lib_final_name)
        
        temp_unpack_dir = os.path.join(module_path, "target", "temp_unpack")
        if os.path.exists(temp_unpack_dir):
            shutil.rmtree(temp_unpack_dir)
        os.makedirs(temp_unpack_dir)

        with zipfile.ZipFile(wheel_path, 'r') as zf:
            zf.extractall(temp_unpack_dir)
            
        # Znajdź natywny plik (.pyd/.so/.dylib) rekurencyjnie
        native_exts = ('.pyd', '.so', '.dylib')
        native_files = []
        for root, dirs, files in os.walk(temp_unpack_dir):
            native_files.extend([os.path.join(root, f) for f in files if any(f.endswith(ext) for ext in native_exts)])
            
        if not native_files:
            raise FileNotFoundError(f"Nie znaleziono natywnego pliku biblioteki w kole dla modułu {module}")
        
        source_lib = native_files[0]  # Weź pierwszy znaleziony plik
        print(f"🦀 Przenoszenie {source_lib} do {target_lib_path}")
        shutil.move(source_lib, target_lib_path)
        
        # 4. Czyszczenie
        shutil.rmtree(temp_unpack_dir)
        print(f"🦀 Pomyślnie zbudowano i przeniesiono moduł {module}.")

    print("\n🦀 --- Wszystkie moduły zbudowane pomyślnie! ---")

if __name__ == "__main__":
    main() 