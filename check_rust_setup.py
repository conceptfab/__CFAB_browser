#!/usr/bin/env python3
"""
Skrypt do sprawdzenia kompletności konfiguracji Rust + PyO3 na Windows
Sprawdza wszystkie wymagane narzędzia i biblioteki dla migracji Scanner → Rust
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class Colors:
    """Kolory dla terminala Windows"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Wyświetla nagłówek sekcji"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*50}")
    print(f"{text}")
    print(f"{'='*50}{Colors.RESET}")

def print_success(text: str):
    """Wyświetla komunikat sukcesu"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Wyświetla komunikat błędu"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Wyświetla ostrzeżenie"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Wyświetla informację"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def run_command(command: str, capture_output: bool = True) -> Tuple[bool, str]:
    """
    Uruchamia komendę i zwraca wynik
    
    Args:
        command: Komenda do uruchomienia
        capture_output: Czy przechwytywać output
    
    Returns:
        Tuple (success, output)
    """
    try:
        if platform.system() == "Windows":
            # Na Windows używamy cmd.exe
            result = subprocess.run(
                f"cmd /c {command}",
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
        
        return result.returncode == 0, result.stdout.strip() if capture_output else ""
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)

def check_system_info():
    """Sprawdza informacje o systemie"""
    print_header("INFORMACJE O SYSTEMIE")
    
    print_info(f"System: {platform.system()} {platform.release()}")
    print_info(f"Architektura: {platform.machine()}")
    print_info(f"Python: {sys.version}")
    print_info(f"Ścieżka Python: {sys.executable}")

def check_rust_installation():
    """Sprawdza instalację Rust"""
    print_header("SPRAWDZANIE RUST")
    
    # Sprawdź rustc
    success, output = run_command("rustc --version")
    if success:
        print_success(f"rustc: {output}")
    else:
        print_error("rustc nie jest zainstalowany lub nie jest w PATH")
        return False
    
    # Sprawdź cargo
    success, output = run_command("cargo --version")
    if success:
        print_success(f"cargo: {output}")
    else:
        print_error("cargo nie jest zainstalowany lub nie jest w PATH")
        return False
    
    # Sprawdź rustup
    success, output = run_command("rustup --version")
    if success:
        print_success(f"rustup: {output}")
    else:
        print_warning("rustup nie jest dostępny")
    
    # Sprawdź toolchain
    success, output = run_command("rustup show")
    if success:
        print_success("Toolchain aktywny:")
        for line in output.split('\n')[:5]:  # Pokaż pierwsze 5 linii
            if line.strip():
                print_info(f"  {line}")
    else:
        print_warning("Nie można sprawdzić toolchain")
    
    return True

def check_visual_studio_tools():
    """Sprawdza Visual Studio Build Tools"""
    print_header("SPRAWDZANIE VISUAL STUDIO BUILD TOOLS")
    
    # Sprawdź cl.exe (Microsoft C++ Compiler)
    success, output = run_command("cl")
    if success or "Microsoft" in output:
        print_success("Microsoft C++ Compiler (cl.exe) dostępny")
    else:
        print_error("Microsoft C++ Compiler nie jest dostępny")
        print_info("Zainstaluj Visual Studio Build Tools 2022")
        return False
    
    # Sprawdź link.exe
    success, output = run_command("link")
    if success or "Microsoft" in output:
        print_success("Microsoft Linker (link.exe) dostępny")
    else:
        print_warning("Microsoft Linker może nie być dostępny")
    
    return True

def check_python_packages():
    """Sprawdza pakiety Python"""
    print_header("SPRAWDZANIE PAKIETÓW PYTHON")
    
    required_packages = [
        "maturin",
        "wheel",
        "setuptools",
    ]
    
    optional_packages = [
        "pytest",
        "black",
        "mypy",
    ]
    
    all_good = True
    
    for package in required_packages:
        success, output = run_command(f"pip show {package}")
        if success:
            version_line = [line for line in output.split('\n') if line.startswith('Version:')]
            version = version_line[0].split(':')[1].strip() if version_line else "unknown"
            print_success(f"{package}: {version}")
        else:
            print_error(f"{package} nie jest zainstalowany")
            all_good = False
    
    print_info("\nPakiety opcjonalne:")
    for package in optional_packages:
        success, output = run_command(f"pip show {package}")
        if success:
            version_line = [line for line in output.split('\n') if line.startswith('Version:')]
            version = version_line[0].split(':')[1].strip() if version_line else "unknown"
            print_success(f"{package}: {version}")
        else:
            print_warning(f"{package} nie jest zainstalowany (opcjonalny)")
    
    return all_good

def check_environment_variables():
    """Sprawdza zmienne środowiskowe"""
    print_header("SPRAWDZANIE ZMIENNYCH ŚRODOWISKOWYCH")
    
    # Sprawdź PATH
    path_env = os.environ.get('PATH', '')
    rust_in_path = any('.cargo\\bin' in p for p in path_env.split(';'))
    
    if rust_in_path:
        print_success("Rust tools są w PATH")
    else:
        print_error("Rust tools nie są w PATH")
        cargo_bin = Path.home() / ".cargo" / "bin"
        print_info(f"Dodaj do PATH: {cargo_bin}")
    
    # Sprawdź CARGO_HOME
    cargo_home = os.environ.get('CARGO_HOME')
    if cargo_home:
        print_success(f"CARGO_HOME: {cargo_home}")
    else:
        default_cargo = Path.home() / ".cargo"
        print_info(f"CARGO_HOME używa domyślnej lokalizacji: {default_cargo}")
    
    # Sprawdź RUSTUP_HOME
    rustup_home = os.environ.get('RUSTUP_HOME')
    if rustup_home:
        print_success(f"RUSTUP_HOME: {rustup_home}")
    else:
        print_info("RUSTUP_HOME używa domyślnej lokalizacji")
    
    return rust_in_path

def test_rust_compilation():
    """Testuje kompilację prostego projektu Rust"""
    print_header("TEST KOMPILACJI RUST")
    
    test_dir = Path("test_rust_project")
    
    try:
        # Utwórz testowy projekt
        if test_dir.exists():
            import shutil
            shutil.rmtree(test_dir)
        
        success, output = run_command(f"cargo init --lib {test_dir}")
        if not success:
            print_error("Nie można utworzyć testowego projektu Rust")
            return False
        
        # Dodaj PyO3 do Cargo.toml
        cargo_toml = test_dir / "Cargo.toml"
        with open(cargo_toml, 'a', encoding='utf-8') as f:
            f.write('''
[dependencies]
pyo3 = { version = "0.20", features = ["extension-module"] }

[lib]
name = "test_rust_project"
crate-type = ["cdylib"]
''')
        
        # Utwórz prosty kod PyO3
        lib_rs = test_dir / "src" / "lib.rs"
        with open(lib_rs, 'w', encoding='utf-8') as f:
            f.write('''
use pyo3::prelude::*;

#[pyfunction]
fn hello_rust() -> String {
    "Hello from Rust!".to_string()
}

#[pymodule]
fn test_rust_project(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_rust, m)?)?;
    Ok(())
}
''')
        
        # Spróbuj skompilować
        print_info("Kompilowanie testowego projektu...")
        success, output = run_command(f"cargo build --manifest-path {test_dir}/Cargo.toml")
        if success:
            print_success("Kompilacja Rust zakończona sukcesem")
        else:
            print_error("Błąd kompilacji Rust:")
            print_error(output)
            return False
        
        # Test maturin
        print_info("Testowanie maturin...")
        os.chdir(test_dir)
        success, output = run_command("maturin develop")
        os.chdir("..")
        
        if success:
            print_success("Maturin build zakończony sukcesem")
        else:
            print_error("Błąd maturin build:")
            print_error(output)
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Błąd podczas testowania: {e}")
        return False
    finally:
        # Cleanup
        if test_dir.exists():
            try:
                os.chdir("..")
                import shutil
                shutil.rmtree(test_dir)
            except:
                pass

def test_pyo3_import():
    """Testuje import PyO3"""
    print_header("TEST IMPORTU PyO3")
    
    try:
        # Sprawdź czy można zaimportować maturin
        success, output = run_command("python -c \"import maturin; print('maturin OK')\"")
        if success:
            print_success("Import maturin: OK")
        else:
            print_error("Nie można zaimportować maturin")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Błąd testowania importu: {e}")
        return False

def generate_installation_commands():
    """Generuje komendy instalacji brakujących komponentów"""
    print_header("KOMENDY INSTALACJI")
    
    print_info("Jeśli coś nie działa, użyj poniższych komend:\n")
    
    print("# Instalacja Rust (jeśli brakuje):")
    print("winget install Rust.Rustup")
    print("# LUB pobierz z https://rustup.rs/\n")
    
    print("# Instalacja Visual Studio Build Tools:")
    print("winget install Microsoft.VisualStudio.2022.BuildTools")
    print("# Pamiętaj o instalacji komponentu C++ build tools\n")
    
    print("# Instalacja pakietów Python:")
    print("pip install maturin wheel setuptools pytest\n")
    
    print("# Dodanie Rust do PATH (PowerShell):")
    print("$env:PATH += \";$env:USERPROFILE\\.cargo\\bin\"\n")
    
    print("# Sprawdzenie instalacji:")
    print("rustc --version")
    print("cargo --version")
    print("maturin --version")

def main():
    """Główna funkcja"""
    print_header("CHECKER KONFIGURACJI RUST + PyO3")
    print_info("Sprawdzanie kompletności konfiguracji dla migracji Scanner → Rust")
    
    # Wyniki sprawdzeń
    results = {
        "system_info": True,
        "rust": False,
        "visual_studio": False,
        "python_packages": False,
        "environment": False,
        "rust_compilation": False,
        "pyo3_import": False
    }
    
    # Sprawdzenia
    check_system_info()
    results["rust"] = check_rust_installation()
    results["visual_studio"] = check_visual_studio_tools()
    results["python_packages"] = check_python_packages()
    results["environment"] = check_environment_variables()
    
    # Testy zaawansowane tylko jeśli podstawy działają
    if results["rust"] and results["python_packages"]:
        results["rust_compilation"] = test_rust_compilation()
        results["pyo3_import"] = test_pyo3_import()
    
    # Podsumowanie
    print_header("PODSUMOWANIE")
    
    all_good = True
    for check, status in results.items():
        if check == "system_info":
            continue
        if status:
            print_success(f"{check.replace('_', ' ').title()}: OK")
        else:
            print_error(f"{check.replace('_', ' ').title()}: BŁĄD")
            all_good = False
    
    if all_good:
        print_success("\n🎉 Wszystko jest gotowe do migracji Scanner → Rust!")
        print_info("Możesz rozpocząć tworzenie projektu scanner_rust")
    else:
        print_error("\n❌ Konfiguracja nie jest kompletna")
        print_info("Sprawdź błędy powyżej i zainstaluj brakujące komponenty")
        generate_installation_commands()
    
    return all_good

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nPrzerwano przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print_error(f"Nieoczekiwany błąd: {e}")
        sys.exit(1) 