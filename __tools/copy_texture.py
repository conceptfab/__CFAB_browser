import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLineEdit, QFileDialog, QPlainTextEdit, QLabel
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, Qt

# --- POPRAWIONA KLASA WORKER ---
# Ta wersja szuka plików .rar i folderów na tym samym poziomie.

class Worker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.is_running = True

    def run(self):
        """Główna metoda wykonująca logikę programu."""
        self.progress.emit(f"Rozpoczynam przeszukiwanie folderu: {self.root_path}\n")
        
        try:
            # os.walk() przechodzi przez wszystkie podfoldery
            for dirpath, dirnames, filenames in os.walk(self.root_path):
                if not self.is_running:
                    self.progress.emit("Proces przerwany.")
                    break

                # Znajdujemy tylko pliki .rar w bieżącym folderze
                rar_files = [f for f in filenames if f.lower().endswith('.rar')]
                if not rar_files:
                    continue # Przechodzimy dalej, jeśli nie ma tu plików .rar

                self.progress.emit(f"Sprawdzam folder: {dirpath}")

                # <<< POPRAWNA LOGIKA JEST TUTAJ >>>
                for rar_file in rar_files:
                    # Pobieramy nazwę pliku bez rozszerzenia .rar
                    file_name_without_ext = os.path.splitext(rar_file)[0]
                    
                    # Sprawdzamy, czy w tym samym folderze istnieje katalog o takiej samej nazwie
                    # (ignorujemy wielkość liter dla pewności)
                    matching_folder_name = None
                    for folder_name in dirnames:
                        if folder_name.lower() == file_name_without_ext.lower():
                            matching_folder_name = folder_name
                            break # Znaleziono, więc przerywamy szukanie

                    if matching_folder_name:
                        # --- ZNALEZIONO DOPASOWANIE! ---
                        source_path = os.path.join(dirpath, rar_file)
                        
                        # Folder docelowy (ten o pasującej nazwie)
                        target_folder = os.path.join(dirpath, matching_folder_name)
                        
                        # Folder 'textures' tworzymy wewnątrz folderu docelowego
                        textures_folder_path = os.path.join(target_folder, 'textures')
                        
                        try:
                            # Tworzymy folder 'textures', jeśli nie istnieje
                            os.makedirs(textures_folder_path, exist_ok=True)
                            self.progress.emit(f"  > Utworzono/znaleziono folder: {textures_folder_path}")
                            
                            # Ścieżka docelowa dla pliku .rar
                            destination_path = os.path.join(textures_folder_path, rar_file)
                            
                            # Przenosimy plik
                            shutil.move(source_path, destination_path)
                            self.progress.emit(f"  > PRZENIESIONO: '{rar_file}' -> '{destination_path}'")
                            
                        except OSError as e:
                            self.progress.emit(f"  ! BŁĄD podczas operacji na plikach: {e}")
                        except Exception as e:
                            self.progress.emit(f"  ! Nieoczekiwany błąd: {e}")

        except Exception as e:
            self.progress.emit(f"\nWYSTĄPIŁ KRYTYCZNY BŁĄD: {e}")
        finally:
            self.progress.emit("\nZakończono przeszukiwanie.")
            self.finished.emit()

    def stop(self):
        self.is_running = False

# --- Interfejs użytkownika (UI) - bez zmian ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizator Plików .rar v2")
        self.setGeometry(100, 100, 700, 500)
        self.thread = None
        self.worker = None
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.addWidget(QLabel("1. Wybierz główny folder do przeszukania:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Wybierz folder...")
        self.path_input.setReadOnly(True)
        layout.addWidget(self.path_input)
        self.browse_button = QPushButton("Przeglądaj...")
        layout.addWidget(self.browse_button)
        layout.addWidget(QLabel("\n2. Uruchom proces:"))
        self.start_button = QPushButton("Uruchom proces")
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)
        layout.addWidget(QLabel("\nLogi operacji:"))
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        self.browse_button.clicked.connect(self.select_directory)
        self.start_button.clicked.connect(self.start_processing)
        self.path_input.textChanged.connect(self.update_start_button_state)

    def select_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        if path:
            self.path_input.setText(path)

    def update_start_button_state(self):
        path = self.path_input.text()
        if path and os.path.isdir(path):
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def start_processing(self):
        path = self.path_input.text()
        self.log_output.clear()
        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.thread = QThread()
        self.worker = Worker(root_path=path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_log)
        self.thread.finished.connect(self.on_processing_finished)
        self.thread.start()

    def update_log(self, message):
        self.log_output.appendPlainText(message)

    def on_processing_finished(self):
        self.update_log("----------------\nPROCES ZAKOŃCZONY\n----------------")
        self.browse_button.setEnabled(True)
        self.update_start_button_state()
        self.thread = None
        self.worker = None

    def closeEvent(self, event):
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

# --- Uruchomienie aplikacji ---

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())