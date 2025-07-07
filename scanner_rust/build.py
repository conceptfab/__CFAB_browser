import os
import subprocess
import shutil
import zipfile

# --- Konfiguracja ---
CRATES_DIR = "crates"
TARGET_DIR = "core/__rust"
MODULES = ["scanner", "image_tools", "hash_utils"]
# --------------------

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
    print("--- Rozpoczęcie budowania modułów Rust ---")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tworzenie docelowego folderu, jeśli nie istnieje
    target_root_dir = os.path.join(script_dir, '..', TARGET_DIR)
    os.makedirs(target_root_dir, exist_ok=True)
    
    for module in MODULES:
        print(f"\n--- Budowanie modułu: {module} ---")
        module_path = os.path.join(script_dir, CRATES_DIR, module)
        manifest_path = os.path.join(module_path, "Cargo.toml")
        
        # 1. Budowanie koła (wheel)
        run_command("maturin build --release", cwd=module_path, manifest_path=manifest_path)
        
        # 2. Znajdowanie pliku .whl
        wheels_dir = os.path.join(script_dir, "target", "wheels")
        if not os.path.exists(wheels_dir):
            raise FileNotFoundError(f"Katalog 'wheels' nie został utworzony dla modułu {module}. Prawdopodobnie wystąpił błąd kompilacji.")
        
        wheel_files = [f for f in os.listdir(wheels_dir) if f.endswith(".whl")]
        if not wheel_files:
            raise FileNotFoundError(f"Nie znaleziono pliku .whl dla modułu {module}")
        latest_wheel = sorted(wheel_files, key=lambda f: os.path.getmtime(os.path.join(wheels_dir, f)), reverse=True)[0]
        wheel_path = os.path.join(wheels_dir, latest_wheel)
        print(f"Znaleziono koło: {wheel_path}")

        # 3. Rozpakowanie i przeniesienie .pyd
        pyd_final_name = f"{module if module != 'scanner' else 'scanner_rust'}.pyd"
        target_pyd_path = os.path.join(script_dir, '..', TARGET_DIR, pyd_final_name)
        
        temp_unpack_dir = os.path.join(module_path, "target", "temp_unpack")
        if os.path.exists(temp_unpack_dir):
            shutil.rmtree(temp_unpack_dir)
        os.makedirs(temp_unpack_dir)

        with zipfile.ZipFile(wheel_path, 'r') as zf:
            zf.extractall(temp_unpack_dir)
            
        # Znajdź plik .pyd rekurencyjnie
        pyd_files = []
        for root, dirs, files in os.walk(temp_unpack_dir):
            pyd_files.extend([os.path.join(root, f) for f in files if f.endswith('.pyd')])
            
        if not pyd_files:
            raise FileNotFoundError(f"Nie znaleziono pliku .pyd w kole dla modułu {module}")
        
        source_pyd = pyd_files[0]  # Weź pierwszy znaleziony plik .pyd
        print(f"Przenoszenie {source_pyd} do {target_pyd_path}")
        shutil.move(source_pyd, target_pyd_path)
        
        # 4. Czyszczenie
        shutil.rmtree(temp_unpack_dir)
        print(f"Pomyślnie zbudowano i przeniesiono moduł {module}.")

    print("\n--- Wszystkie moduły zbudowane pomyślnie! ---")

if __name__ == "__main__":
    main() 