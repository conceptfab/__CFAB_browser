import os
import shutil
import subprocess


def clean_pycache():
    print("Czyszczenie folderów __pycache__...")
    for root, dirs, files in os.walk(os.getcwd()):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"Usunięto: {pycache_path}")
            except OSError as e:
                print(f"Błąd podczas usuwania {pycache_path}: {e}")
    print("Czyszczenie zakończone.")


def run_cfab_browser():
    print("Uruchamianie cfab_browser.py...")
    try:
        subprocess.run(["python", "cfab_browser.py"], check=True)
        print("cfab_browser.py zakończył działanie.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas uruchamiania cfab_browser.py: {e}")
    except FileNotFoundError:
        print(
            "Błąd: Nie znaleziono interpretera 'python'. "
            "Upewnij się, że Python jest zainstalowany i dodany do PATH."
        )


if __name__ == "__main__":
    clean_pycache()
    run_cfab_browser()