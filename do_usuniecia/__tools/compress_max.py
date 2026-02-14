import sys
import os
import zipfile

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import QObject, QThread, pyqtSignal

# --- Klasa robocza (Worker) do obsługi kompresji w osobnym wątku ---
# Dzięki temu interfejs graficzny nie będzie się zawieszał podczas pracy.

class Worker(QObject):
    """
    Obsługuje logikę kompresji plików w tle, aby nie blokować UI.
    """
    # Sygnały wysyłane do głównego wątku (UI)
    progress = pyqtSignal(str)  # Sygnał do aktualizacji logu z postępem
    finished = pyqtSignal()     # Sygnał informujący o zakończeniu pracy

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        """Główna metoda wykonująca pracę."""
        self.progress.emit(f"Rozpoczynam przeszukiwanie folderu: {self.folder_path}\n")
        
        file_count = 0
        for root, dirs, files in os.walk(self.folder_path):
            if not self.is_running:
                break
            
            for filename in files:
                if not self.is_running:
                    break

                if filename.lower().endswith('.max'):
                    file_count += 1
                    max_file_path = os.path.join(root, filename)
                    # Nazwa pliku ZIP będzie taka sama jak pliku MAX, ale z rozszerzeniem .zip
                    zip_file_path = os.path.splitext(max_file_path)[0] + '.zip'
                    
                    self.progress.emit(f"Znaleziono plik: {max_file_path}")

                    try:
                        self.progress.emit(" -> Rozpoczynam kompresję...")
                        
                        # Tworzenie archiwum ZIP z maksymalną kompresją
                        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                            # 'arcname' zapewnia, że w pliku zip nie będzie całej ścieżki do pliku
                            zf.write(max_file_path, arcname=filename)
                        
                        self.progress.emit(f" -> Kompresja do pliku {zip_file_path} zakończona pomyślnie.")
                        
                        # Jeśli kompresja się udała, usuwamy oryginalny plik .max
                        self.progress.emit(" -> Usuwam oryginalny plik .max...")
                        os.remove(max_file_path)
                        self.progress.emit(" -> Oryginalny plik usunięty.\n")

                    except Exception as e:
                        self.progress.emit(f" -> BŁĄD! Nie udało się przetworzyć pliku {filename}. Powód: {e}\n")

        if file_count == 0:
            self.progress.emit("Nie znaleziono żadnych plików *.max w wybranym folderze i podfolderach.")

        self.finished.emit() # Wyślij sygnał o zakończeniu pracy

    def stop(self):
        """Metoda do zatrzymania pętli."""
        self.is_running = False

# --- Główna klasa aplikacji (Interfejs graficzny) ---

class MaxZipperApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kompresor plików .max")
        self.setGeometry(100, 100, 700, 500)

        # Zmienne stanu
        self.folder_path = None
        self.thread = None
        self.worker = None

        # Układ i widgety
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Etykieta i przycisk do wyboru folderu
        self.folder_label = QLabel("Nie wybrano folderu")
        self.layout.addWidget(self.folder_label)

        self.select_folder_button = QPushButton("Wybierz Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_button)

        # Przycisk do rozpoczęcia kompresji
        self.start_button = QPushButton("Rozpocznij Kompresję")
        self.start_button.clicked.connect(self.start_compression)
        self.start_button.setEnabled(False) # Domyślnie wyłączony
        self.layout.addWidget(self.start_button)

        # Pole tekstowe na logi
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Tutaj pojawią się informacje o postępie operacji...")
        self.layout.addWidget(self.log_output)

    def select_folder(self):
        """Otwiera dialog wyboru folderu i zapisuje ścieżkę."""
        path = QFileDialog.getExistingDirectory(self, "Wybierz folder do przeszukania")
        if path:
            self.folder_path = path
            self.folder_label.setText(f"Wybrany folder: {self.folder_path}")
            self.start_button.setEnabled(True) # Włącz przycisk po wybraniu folderu
            self.log_output.clear()

    def start_compression(self):
        """Uruchamia proces kompresji w osobnym wątku."""
        if not self.folder_path:
            return

        # Zablokuj przyciski, aby zapobiec ponownemu uruchomieniu
        self.start_button.setEnabled(False)
        self.select_folder_button.setEnabled(False)
        self.log_output.clear()

        # Konfiguracja wątku i workera
        self.thread = QThread()
        self.worker = Worker(self.folder_path)
        self.worker.moveToThread(self.thread)

        # Połączenie sygnałów i slotów
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_compression_finished)
        self.worker.progress.connect(self.update_log)

        # Rozpoczęcie wątku
        self.thread.start()

    def update_log(self, message):
        """Dodaje wiadomość do pola z logami."""
        self.log_output.append(message)

    def on_compression_finished(self):
        """Metoda wywoływana po zakończeniu pracy workera."""
        self.log_output.append("\n--- Operacja zakończona! ---")

        # Sprzątanie po wątku
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        
        self.thread = None
        self.worker = None

        # Odblokowanie przycisków
        self.start_button.setEnabled(True)
        self.select_folder_button.setEnabled(True)

        # Wyświetlenie komunikatu o zakończeniu
        QMessageBox.information(self, "Zakończono", "Przetwarzanie plików zostało zakończone.")

    def closeEvent(self, event):
        """Obsługa zamknięcia okna w trakcie działania wątku."""
        if self.thread and self.thread.isRunning():
            self.log_output.append("\n--- Przerywanie operacji... ---")
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

# --- Główny punkt wejścia do programu ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaxZipperApp()
    window.show()
    sys.exit(app.exec())