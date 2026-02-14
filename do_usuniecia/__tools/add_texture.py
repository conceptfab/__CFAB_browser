import os
import sys

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# --- Logika działająca w osobnym wątku, aby nie blokować UI ---


class Worker(QObject):
    """
    Klasa robocza, która wykonuje zadanie w tle.
    """

    progress = pyqtSignal(str)  # Sygnał do wysyłania komunikatów o postępie
    finished = pyqtSignal()  # Sygnał informujący o zakończeniu pracy

    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path
        self.is_running = True

    def run(self):
        """
        Główna metoda wykonująca przeszukiwanie i tworzenie folderów.
        """
        if not os.path.isdir(self.root_path):
            self.progress.emit(
                f"BŁĄD: Podana ścieżka nie jest prawidłowym katalogiem: {self.root_path}"
            )
            self.finished.emit()
            return

        self.progress.emit(f"Rozpoczynam przeszukiwanie od: {self.root_path}")

        # os.walk() przechodzi przez całe drzewo katalogów
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            # Sprawdzamy, czy aktualny katalog nie ma podkatalogów
            # dirnames to lista podkatalogów w dirpath
            if not dirnames:
                # To jest "ostatni" podfolder w tej gałęzi drzewa
                self.progress.emit(f"Znaleziono ostatni podfolder: {dirpath}")
                textures_folder_path = os.path.join(dirpath, "textures")

                # Sprawdzamy, czy folder "textures" już nie istnieje
                if not os.path.exists(textures_folder_path):
                    try:
                        os.makedirs(textures_folder_path)
                        self.progress.emit(f"  -> UTWORZONO: {textures_folder_path}")
                    except OSError as e:
                        self.progress.emit(f"  -> BŁĄD podczas tworzenia folderu: {e}")
                else:
                    self.progress.emit(
                        f"  -> POMINIĘTO (już istnieje): {textures_folder_path}"
                    )

        self.progress.emit("\nPrzeszukiwanie zakończone.")
        self.finished.emit()


# --- Główny interfejs użytkownika ---


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Kreator folderów 'textures'")
        self.setGeometry(100, 100, 600, 400)

        # Główny widget i layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Sekcja wyboru folderu
        selection_layout = QHBoxLayout()
        path_label = QLabel("Katalog główny:")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Wybierz katalog do przeszukania...")
        browse_button = QPushButton("Przeglądaj...")
        browse_button.clicked.connect(self.browse_folder)

        selection_layout.addWidget(path_label)
        selection_layout.addWidget(self.path_edit)
        selection_layout.addWidget(browse_button)

        # Przycisk startu
        self.start_button = QPushButton("Uruchom")
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setProperty("class", "start-button")

        # Pole na dziennik (log)
        log_label = QLabel("Dziennik operacji:")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)

        # Dodawanie widgetów do głównego layoutu
        main_layout.addLayout(selection_layout)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_text_edit)

        # Inicjalizacja wątku
        self.thread = None
        self.worker = None

    def browse_folder(self):
        """
        Otwiera dialog wyboru folderu i ustawia ścieżkę w polu tekstowym.
        """
        directory = QFileDialog.getExistingDirectory(self, "Wybierz katalog główny")
        if directory:
            self.path_edit.setText(directory)

    def start_processing(self):
        """
        Rozpoczyna proces w osobnym wątku.
        """
        root_path = self.path_edit.text()
        if not root_path:
            QMessageBox.warning(self, "Brak ścieżki", "Proszę wybrać katalog główny.")
            return

        self.start_button.setEnabled(False)
        self.log_text_edit.clear()

        # Konfiguracja wątku i pracownika
        self.thread = QThread()
        self.worker = Worker(root_path)
        self.worker.moveToThread(self.thread)

        # Połączenie sygnałów i slotów
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.update_log)
        self.thread.finished.connect(self.on_processing_finished)

        # Start wątku
        self.thread.start()

    def update_log(self, message):
        """
        Dodaje wiadomość do pola dziennika.
        """
        self.log_text_edit.append(message)

    def on_processing_finished(self):
        """
        Wywoływane po zakończeniu pracy wątku.
        """
        self.start_button.setEnabled(True)
        QMessageBox.information(self, "Zakończono", "Operacja została zakończona.")


# --- Uruchomienie aplikacji ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
