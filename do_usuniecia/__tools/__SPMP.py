import sys
import os
import struct
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QMessageBox, QCheckBox
)
from PyQt6.QtCore import QThread, pyqtSignal

class ExtractorWorker(QThread):
    """
    Wątek roboczy do obsługi ekstrakcji plików w tle,
    aby uniknąć blokowania interfejsu użytkownika.
    """
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, input_dir, extract_png, only_alpha):
        super().__init__()
        self.input_dir = input_dir
        self.extract_png = extract_png
        self.only_alpha = only_alpha
        self.is_running = True

    def run(self):
        """Główna logika ekstrakcji plików z rekursywnym przeszukiwaniem."""
        total_files_processed = 0
        total_png_extracted = 0
        total_webp_extracted = 0

        try:
            for root, _, files in os.walk(self.input_dir):
                if not self.is_running:
                    break
                self.progress_signal.emit(f"\nPrzeszukiwanie folderu: {root}")
                for filename in files:
                    if not self.is_running:
                        break
                    if filename.lower().endswith('.spsm'):
                        total_files_processed += 1
                        file_path = os.path.join(root, filename)
                        self.progress_signal.emit(f"-> Przetwarzanie: {filename}")
                        
                        try:
                            png_count, webp_count = self.extract_images_from_file(file_path, root)
                            if png_count > 0 or webp_count > 0:
                                log_msg = "  -> Wyodrębniono:"
                                if self.extract_png and png_count > 0:
                                    log_msg += f" {png_count} PNG"
                                if webp_count > 0:
                                    log_msg += f" {webp_count} WebP"
                                self.progress_signal.emit(log_msg)
                            total_png_extracted += png_count
                            total_webp_extracted += webp_count
                        except Exception as e:
                            self.progress_signal.emit(f"  -> Błąd podczas przetwarzania {filename}: {e}")

            summary = (
                f"\nZakończono.\n"
                f"Przetworzono plików: {total_files_processed}\n"
                f"Wyodrębniono plików WebP: {total_webp_extracted}"
            )
            if self.extract_png:
                summary += f"\nWyodrębniono plików PNG: {total_png_extracted}"
            
            self.progress_signal.emit(summary)
        except Exception as e:
            self.error_signal.emit(f"Wystąpił krytyczny błąd: {e}")
        finally:
            self.finished_signal.emit()

    def _has_png_alpha(self, data, start_index):
        """Sprawdza, czy chunk IHDR pliku PNG wskazuje na kanał alfa."""
        # Nagłówek IHDR zaczyna się 8 bajtów po sygnaturze PNG
        # Bajt typu koloru jest na 25. pozycji od początku sygnatury
        color_type_byte_pos = start_index + 25
        if color_type_byte_pos < len(data):
            color_type = data[color_type_byte_pos]
            # Kolor typ 4 = Skala szarości z alfą
            # Kolor typ 6 = RGBA (z alfą)
            if color_type in [4, 6]:
                return True
            # Można by też szukać chunka tRNS dla palet, ale to rzadsze
        return False

    def _has_webp_alpha(self, data, start_index):
        """Sprawdza, czy nagłówek VP8X pliku WebP wskazuje na kanał alfa."""
        # Szukamy chunka 'VP8X', który jest w rozszerzonym formacie WebP
        if data[start_index + 12: start_index + 16] == b'VP8X':
            # Bajt flag jest na 20. pozycji od początku sygnatury RIFF
            flags_byte_pos = start_index + 20
            if flags_byte_pos < len(data):
                flags = data[flags_byte_pos]
                # Czwarty bit od prawej (0x10) oznacza obecność kanału alfa
                return (flags & 0x10) == 0x10
        return False

    def extract_images_from_file(self, file_path, output_dir):
        """Wyodrębnia obrazy z pliku z nową logiką nazewnictwa i filtrowaniem alfa."""
        png_count = 0
        webp_count = 0
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        with open(file_path, 'rb') as f:
            data = f.read()

        png_start_sig = b'\x89PNG\r\n\x1a\n'
        png_end_sig = b'IEND\xaeB`\x82'
        webp_riff_sig = b'RIFF'
        webp_id_sig = b'WEBP'

        # Ekstrakcja plików PNG (jeśli opcja jest zaznaczona)
        if self.extract_png:
            current_pos = 0
            while True:
                start_index = data.find(png_start_sig, current_pos)
                if start_index == -1:
                    break

                # Filtrowanie przezroczystości
                if self.only_alpha and not self._has_png_alpha(data, start_index):
                    current_pos = start_index + 1
                    continue
                
                end_index = data.find(png_end_sig, start_index)
                if end_index == -1:
                    current_pos = start_index + 1
                    continue

                png_data = data[start_index : end_index + 8]
                
                if png_count == 0:
                    output_filename = os.path.join(output_dir, f"{base_name}.png")
                else:
                    output_filename = os.path.join(output_dir, f"{base_name}_{png_count}.png")
                
                with open(output_filename, 'wb') as out_f:
                    out_f.write(png_data)
                
                png_count += 1
                current_pos = end_index + 8

        # Ekstrakcja plików WebP
        current_pos = 0
        while True:
            start_index = data.find(webp_riff_sig, current_pos)
            if start_index == -1:
                break
            
            if data[start_index + 8 : start_index + 12] == webp_id_sig:
                # Filtrowanie przezroczystości
                if self.only_alpha and not self._has_webp_alpha(data, start_index):
                    current_pos = start_index + 1
                    continue
                
                file_size_bytes = data[start_index + 4 : start_index + 8]
                file_size = struct.unpack('<I', file_size_bytes)[0]
                total_chunk_size = 8 + file_size

                webp_data = data[start_index : start_index + total_chunk_size]
                
                if webp_count == 0:
                    output_filename = os.path.join(output_dir, f"{base_name}.webp")
                else:
                    output_filename = os.path.join(output_dir, f"{base_name}_{webp_count}.webp")
                
                with open(output_filename, 'wb') as out_f:
                    out_f.write(webp_data)
                
                webp_count += 1
                current_pos = start_index + total_chunk_size
            else:
                current_pos = start_index + 1

        return png_count, webp_count
    
    def stop(self):
        self.is_running = False

class SpsmExtractorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.input_dir = ""
        self.worker = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ekstraktor obrazów z plików SPSM v3')
        self.setGeometry(300, 300, 600, 450)

        main_layout = QVBoxLayout()
        
        # Sekcja wyboru folderu
        in_folder_layout = QHBoxLayout()
        self.btn_in = QPushButton("Wybierz folder do przeszukania")
        self.btn_in.clicked.connect(self.select_input_folder)
        self.lbl_in = QLabel("Nie wybrano folderu")
        in_folder_layout.addWidget(self.btn_in)
        in_folder_layout.addWidget(self.lbl_in)
        main_layout.addLayout(in_folder_layout)

        # Opcje
        options_layout = QVBoxLayout()
        self.cb_only_alpha = QCheckBox("Wyodrębnij tylko obrazy z przezroczystością (kanał alfa)")
        self.cb_only_alpha.setChecked(True) # Domyślnie zaznaczone
        self.cb_extract_png = QCheckBox("Wyodrębnij również pliki PNG")
        
        options_layout.addWidget(self.cb_only_alpha)
        options_layout.addWidget(self.cb_extract_png)
        main_layout.addLayout(options_layout)

        # Logi
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(QLabel("Logi operacji:"))
        main_layout.addWidget(self.log_area)

        # Przyciski akcji
        action_layout = QHBoxLayout()
        self.btn_start = QPushButton("Rozpocznij ekstrakcję")
        self.btn_start.clicked.connect(self.start_extraction)
        self.btn_start.setStyleSheet("font-weight: bold; padding: 5px;")
        
        action_layout.addStretch(1)
        action_layout.addWidget(self.btn_start)
        action_layout.addStretch(1)
        
        main_layout.addLayout(action_layout)
        
        self.setLayout(main_layout)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Wybierz folder do przeszukania")
        if folder:
            self.input_dir = folder
            self.lbl_in.setText(f"...{folder[-50:]}")

    def start_extraction(self):
        if not self.input_dir:
            QMessageBox.warning(self, "Błąd", "Proszę wybrać folder do przeszukania.")
            return

        if self.worker and self.worker.isRunning():
            return
            
        self.btn_start.setEnabled(False)
        self.log_area.clear()
        
        extract_png_option = self.cb_extract_png.isChecked()
        only_alpha_option = self.cb_only_alpha.isChecked()
        
        self.worker = ExtractorWorker(self.input_dir, extract_png_option, only_alpha_option)
        self.worker.progress_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.extraction_finished)
        self.worker.error_signal.connect(self.show_error)
        self.worker.start()

    def update_log(self, message):
        self.log_area.append(message)
    
    def show_error(self, message):
        QMessageBox.critical(self, "Błąd krytyczny", message)
        self.extraction_finished()

    def extraction_finished(self):
        self.btn_start.setEnabled(True)
        self.worker = None 
        QMessageBox.information(self, "Zakończono", "Proces ekstrakcji został zakończony.")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SpsmExtractorApp()
    ex.show()
    sys.exit(app.exec())