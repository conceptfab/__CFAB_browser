import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import threading
import struct # Importujemy moduł do pracy na danych binarnych

# --- Konfiguracja oparta na nowej analizie ---

# Sygnatura na początku pliku
MAGIC_NUMBER = b'\x00\x00\x00\x01'

# Stała część nagłówka po stringu i jego terminatorze (w Twojej próbce to '55 50') + 'RIFF'
# Długość stringu + 2 bajty (terminator \x00\x00) + 2 bajty (nieznane pole)
# Nowa metoda nie używa stałego rozmiaru, a oblicza go dynamicznie
POST_STRING_HEADER_BYTES = 4 # 2 bajty na terminator + 2 bajty nieznane

class WebpExtractorApp:
    def __init__(self, master):
        self.master = master
        master.title("Poprawiony Ekstraktor WebP (v2)")
        master.geometry("600x450")
        master.resizable(False, False)

        # Zmienne do przechowywania ścieżek
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()

        # --- Interfejs użytkownika (bez zmian) ---
        input_frame = tk.LabelFrame(master, text=" 1. Wybierz folder z plikami do konwersji ", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")
        tk.Entry(input_frame, textvariable=self.input_path_var, width=60, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Przeglądaj...", command=self.select_input_folder).pack(side="left", padx=(5, 0))

        output_frame = tk.LabelFrame(master, text=" 2. Wybierz folder docelowy ", padx=10, pady=10)
        output_frame.pack(padx=10, pady=10, fill="x")
        tk.Entry(output_frame, textvariable=self.output_path_var, width=60, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(output_frame, text="Przeglądaj...", command=self.select_output_folder).pack(side="left", padx=(5, 0))

        self.convert_button = tk.Button(master, text="3. Rozpocznij konwersję", command=self.start_conversion_thread, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white")
        self.convert_button.pack(pady=10, ipadx=10, ipady=5)

        log_frame = tk.LabelFrame(master, text=" Logi procesu ", padx=10, pady=10)
        log_frame.pack(padx=10, pady=5, fill="both", expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)

    def log(self, message):
        self.master.after(0, self._log_update, message)

    def _log_update(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def select_input_folder(self):
        folder_path = filedialog.askdirectory(title="Wybierz folder źródłowy")
        if folder_path:
            self.input_path_var.set(folder_path)

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Wybierz folder docelowy")
        if folder_path:
            self.output_path_var.set(folder_path)

    def process_file(self, input_path, output_path):
        """
        GŁÓWNA ZMIANA LOGIKI JEST TUTAJ.
        Przetwarza pojedynczy plik, dynamicznie odczytując rozmiar nagłówka.
        """
        try:
            with open(input_path, 'rb') as f_in:
                # 1. Odczytaj pierwsze 8 bajtów, które powinny zawierać magiczną liczbę i długość stringu
                header_prefix = f_in.read(8)
                if len(header_prefix) < 8:
                    self.log(f"POMIJAM: Plik '{os.path.basename(input_path)}' jest za mały.")
                    return

                # 2. Sprawdź magiczną liczbę
                magic = header_prefix[0:4]
                if magic != MAGIC_NUMBER:
                    self.log(f"POMIJAM: Plik '{os.path.basename(input_path)}' ma nieprawidłową sygnaturę początkową.")
                    return
                
                # 3. Odczytaj długość stringa (UTF-16) zapisaną jako 4-bajtowy integer (big-endian)
                string_length_bytes = header_prefix[4:8]
                string_length = struct.unpack('>I', string_length_bytes)[0]
                
                # 4. Oblicz początek danych RIFF (WebP)
                # Offset = 8 bajtów (prefix) + długość_stringa + 4 bajty (stały blok po stringu)
                webp_start_offset = 8 + string_length + POST_STRING_HEADER_BYTES
                
                # 5. Przesuń wskaźnik na początek danych WebP i odczytaj resztę
                f_in.seek(webp_start_offset)
                webp_data = f_in.read()

                # 6. Podstawowa walidacja, czy dane WebP zaczynają się od 'RIFF'
                if len(webp_data) < 4 or webp_data[0:4] != b'RIFF':
                    self.log(f"POMIJAM: Nie znaleziono danych RIFF w pliku '{os.path.basename(input_path)}' po odjęciu nagłówka.")
                    return

            # Zapisz wyodrębnione dane do nowego pliku
            with open(output_path, 'wb') as f_out:
                f_out.write(webp_data)
            
            self.log(f"OK: Przekonwertowano '{os.path.basename(input_path)}'")

        except Exception as e:
            self.log(f"BŁĄD przy przetwarzaniu '{os.path.basename(input_path)}': {e}")


    def conversion_logic(self):
        """Logika konwersji, bez zmian."""
        input_dir = self.input_path_var.get()
        output_dir = self.output_path_var.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Błąd", "Musisz wybrać folder źródłowy i docelowy!")
            self.convert_button.config(state="normal")
            return
        
        if input_dir == output_dir:
            messagebox.showerror("Błąd", "Folder źródłowy i docelowy nie mogą być takie same!")
            self.convert_button.config(state="normal")
            return

        self.log("--- Rozpoczynam konwersję (v2) ---")
        os.makedirs(output_dir, exist_ok=True)
        
        files_to_process = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        
        if not files_to_process:
            self.log("Folder źródłowy jest pusty.")
        else:
            for filename in files_to_process:
                input_path = os.path.join(input_dir, filename)
                # Używamy oryginalnej nazwy pliku jako bazy dla nowego pliku .webp
                output_filename = f"{filename}.webp"
                output_path = os.path.join(output_dir, output_filename)
                
                self.process_file(input_path, output_path)

        self.log("--- Konwersja zakończona ---")
        self.master.after(0, lambda: self.convert_button.config(state="normal"))

    def start_conversion_thread(self):
        """Uruchamia wątek konwersji, bez zmian."""
        self.convert_button.config(state="disabled")
        self.log_text.config(state="normal")
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state="disabled")
        thread = threading.Thread(target=self.conversion_logic)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = WebpExtractorApp(root)
    root.mainloop()