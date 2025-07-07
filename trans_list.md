# Lista fraz do tłumaczenia

Pliki posortowane pod względem ilości fraz do tłumaczenia (malejąco).

---

## 1. `core/amv_views/asset_tile_view.py` (54)

### UI Messages (0)

### Logi (3)
- `Shift wciśnięty - blokada podglądu/archiwum, tylko drag and drop`
- `Drag and drop zablokowane podczas ładowania galerii.`
- `Zaktualizowano pasek statusu po zmianie checkboxa dla {self.asset_id}`
- `Nie można zaktualizować paska statusu: {e}`

### Komentarze (51)
- `# Czy kafelek jest zaznaczony`
- `# Dane assetu`
- `# Globalny QThreadPool do zarządzania workerami`
- `# Stałe klasowe`
- `# Dodaj selection_model`
- `# Przypisz selection_model`
- `# Użyj nazwy assetu jako ID`
- `# Odłącz stare połączenie sygnału - bezpieczne odłączenie`
- `# Połączenie już nie istnieje`
- `# Zresetuj stan ładowania miniaturki`
- `# Zaktualizuj dane`
- `# Podłącz nowe połączenie sygnału - tylko jeśli model istnieje`
- `# Natychmiast zaktualizuj UI z nowymi danymi`
- `# DODANO: Ustaw początkowy stan checkboxa na podstawie SelectionModel`
- `# Usunięto podwójne tworzenie thumbnail_container - przeniesione do _setup_ui_without_styles()`
- `# Najpierw utwórz ikonę tekstury!`
- `# Ikona tekstury (16x16px)`
- `# Najpierw utwórz label na nazwę pliku!`
- `# Nazwa pliku (centrum)`
- `# Dodaj label na rozmiar pliku`
- `# Rozmiar pliku (prawy)`
- `# Dodaj label na numer kafelka`
- `# Numer kafelka (lewy)`
- `# Dodaj checkbox`
- `# Checkbox zaznaczenia (prawy)`
- `# DODANO: Połączenie sygnału checkboxa`
- `# Dodaj gwiazdki (5)`
- `# Gwiazdki 1-5 (środek)`
- `# z CSS`
- `# Oblicz szerokość na podstawie kolumn`
- `# ikona(60) + nazwa(136) + rozmiar(60)`
- `# Odstęp przed nazwą pliku`
- `# Ustaw stałe szerokości dla kolumn`
- `# NR do lewej`
- `# Rozciągnij do środka`
- `# Gwiazdki do środka`
- `# Rozciągnij do prawej`
- `# Checkbox do prawej`
- `# Dodaj główny kontener do głównego layoutu`
- `# D&D będzie obsługiwane przez Controller`
- `# Ustaw początkowy stan checkboxa na podstawie SelectionModel`
- `# Wyświetlanie nazwy i rozmiaru pliku`
- `# Ogranicz długość nazwy do 16 znaków`
- `# Sprawdź czy gwiazdki mieszczą się na kafelku`
- `# Krok 1: Spróbuj załadować z cache`
- `# Krok 2: Jeśli nie ma w cache, załaduj asynchronicznie`
- `# Krok 3: Jeśli plik nie istnieje, pokaż placeholder`
- `# Przycinanie do kwadratu`
- `# Szeroki - przytnij od lewej`
- `# Wysoki - przytnij od góry`
- `# Już kwadrat`
- `# Wyświetlanie nazwy folderu`
- `# Ukryj gwiazdki dla folderów`
- `# Załaduj ikonę folderu`
- `# Błąd podczas ładowania ikony {icon_name}: {e}`
- `# Fallback: szary lub żółty prostokąt zależnie od ikony`
- `# Sprawdź, który widget został kliknięty`
- `# Jeśli wciśnięty jest Shift, nie pokazuj podglądu ani archiwum`
- `# Obsługa kliknięć na miniaturkę`
- `# Obsługa kliknięć na nazwę pliku`
- `# Blokada D&D gdy trwa ładowanie galerii`
- `# ZABEZPIECZENIE: Sprawdź czy drag już nie jest w toku`
- `# Sprawdź czy selection_model istnieje`
- `# Pobierz zaznaczone assety z SelectionModel`
- `# Jeśli nie ma zaznaczonych assetów, przeciągnij tylko ten kafelek`
- `# ZABEZPIECZENIE: Sprawdź czy asset_ids są prawidłowe`
- `# Ustaw flagę drag in progress`
- `# Ustaw kursor przeciągania`
- `# Emituj sygnał rozpoczęcia przeciągania`
- `# POPRAWKA: Wykonaj przeciąganie z timeout dla bezpieczeństwa`
- `# Używamy Qt.DropAction.MoveAction | Qt.DropAction.IgnoreAction dla lepszej kompatybilności`
- `# Zawsze wyczyść flagę drag in progress`
- `# Przelicz szerokość kafelka`
- `# Przeładuj UI, aby zastosować nowy rozmiar`
- `# Ustaw flagę blokady przed zmianą stanu`
- `# Odłącz sygnał tymczasowo, aby uniknąć rekurencji`
- `# Ręcznie wywołaj metodę obsługującą zmianę stanu, aby zaktualizować model`
- `# Zawsze usuń flagę blokady`
- `# Zabezpieczenie przed rekurencją podczas programowego ustawiania checkboxa`
- `# DODANO: Wymuszenie aktualizacji paska statusu`
- `# Jeśli kliknięto w ostatnią zaznaczoną gwiazdkę, odznacz wszystkie`
- `# Ustaw nową ocenę`
- `# Oblicz dostępną szerokość dla gwiazdek`
- `# Szerokość kafelka - marginesy - numer - checkbox - odstępy`
- `# Szacowana szerokość 5 gwiazdek (każda ~12px) + odstępy`
- `# 5 gwiazdek po 12px + 4 odstępy po 6px`
- `# Aktualizuj widoczność gwiazdek po zmianie rozmiaru`
- `# Aktualizuj rozmiar miniatury, aby wypełnić dostępną przestrzeń`
- `# Oblicz dostępną przestrzeń dla miniatury`
- `# Odejmij miejsce na tekst i kontrolki`
- `# Użyj mniejszego wymiaru, aby zachować proporcje kwadratu`
- `# Minimalny rozmiar 64px`

---

## 2. `core/amv_views/folder_tree_view.py` (53)

### UI Messages (5)
- `Ukryj liczniki assetów`
- `Pokaż liczniki assetów`
- `Zliczaj tylko w folderze`
- `Zliczaj rekurencyjnie (+)`
- `Odśwież folder`
- `Otwórz w Eksploratorze`
- `Przebuduj assety`

### Logi (10)
- `contextMenuEvent - pozycja myszy: {event.pos()}`
- `contextMenuEvent - item lub UserRole data jest None`
- `contextMenuEvent - index nie jest valid`
- `Błąd obsługi menu kontekstowego: {e}`
- `Błąd przełączania liczników assetów: {e}`
- `Błąd przełączania trybu rekurencyjnego: {e}`
- `Błąd pobierania stanu liczników assetów: {e}`
- `Błąd pobierania stanu trybu rekurencyjnego: {e}`
- `_open_folder_in_explorer - otrzymana ścieżka: {folder_path}`
- `_open_folder_in_explorer - wywołuję callback z ścieżką: {folder_path}`
- `_open_folder_in_explorer - brak callbacku, używam bezpośredniego otwarcia: {folder_path}`
- `Błąd otwierania folderu w eksploratorze: {e}`
- `Brak callbacku do przebudowy assetów`
- `Błąd wywołania callbacku przebudowy: {e}`
- `Brak callbacku do odświeżania folderu`
- `Błąd wywołania callbacku odświeżania folderu: {e}`

### Komentarze (38)
- `"""Widok drzewa folderów z obsługą drag & drop.
Zawiera niestandardowy QTreeView z funkcjonalnością przeciągania assetów."""`
- `# Funkcja do pobierania aktualnego folderu`
- `# Referencja do modelu siatki assetów`
- `# Callback do przebudowy assetów`
- `# Callback do otwierania w eksploratorze`
- `# Callback do odświeżania folderu`
- `# Indeks aktywnego folderu`
- `# Włącz obsługę drop`
- `# Podpięcie sygnałów expanded/collapsed`
- `"""Ustawia modele potrzebne do obsługi drag & drop."""`
- `"""Ustawia callback do przebudowy assetów."""`
- `"""Ustawia callback do otwierania folderu w eksploratorze."""`
- `"""Ustawia callback do odświeżania folderu."""`
- `# Podpinaj sygnał currentChanged z opóźnieniem, by selectionModel już istniał`
- `"""Obsługuje menu kontekstowe dla folderu."""`
- `# Opcja włączania/wyłączania liczników assetów (zawsze dostępna)`
- `# Opcja trybu rekurencyjnego (dostępna gdy liczniki są włączone)`
- `# Separator`
- `# Opcja odświeżenia folderu (na górze)`
- `# Opcja otwarcia w eksploratorze`
- `# Opcja przebudowy assetów`
- `# Pokaż menu`
- `"""Przełącza pokazywanie liczników assetów w folderach"""`
- `# Pobierz aktualny stan`
- `# Poinformuj kontroler o zmianie`
- `"""Przełącza tryb rekurencyjnego zliczania assetów"""`
- `"""Pobiera aktualny stan pokazywania liczników assetów"""`
- `# Domyślnie włączone`
- `"""Pobiera aktualny stan rekurencyjnego zliczania assetów"""`
- `"""Ustawia referencję do kontrolera drzewa folderów"""`
- `"""Otwiera folder w eksploratorze systemu."""`
- `# Fallback - bezpośrednie otwarcie`
- `"""Przebudowuje assety w wybranym folderze."""`
- `"""Odświeża folder."""`
- `"""Obsługuje zdarzenie wejścia przeciąganego elementu."""`
- `"""Obsługuje zdarzenie opuszczenia obszaru przez przeciągany element."""`
- `"""Obsługuje zdarzenie ruchu przeciąganego elementu."""`
- `"""Obsługuje zdarzenie upuszczenia elementu."""`
- `# ZABEZPIECZENIE: Sprawdź czy nie ma już operacji w toku`
- `# REFAKTORYZUJ: wynieś walidację do osobnych metod`
- `# ZABEZPIECZENIE: Dodatkowa walidacja asset_ids`
- `# Pobierz pełne dane assetów z asset_grid_model`
- `"""Sprawdza czy zdarzenie drop jest prawidłowe."""`
- `"""Pobiera informacje o celu drop."""`
- `"""Pobiera pełne dane assetów do przeniesienia."""`
- `"""Sprawdza czy można wykonać operację drop."""`
- `"""Wykonuje operację drop."""`
- `# ZABEZPIECZENIE: Sprawdź ponownie czy modele są dostępne`
- `# ZABEZPIECZENIE: Sprawdź czy foldery istnieją`
- `# Wykonaj operację przenoszenia w osobnym wątku`
- `# Oznacz drop jako zakończony`
- `"""Podświetla folder pod podaną pozycją bez zmiany zaznaczenia roboczego."""`
- `# Najpierw wyczyść poprzednie podświetlenie`
- `"""Czyści podświetlenie folderu docelowego."""`
- `# Przywróć domyślny kolor`
- `# Przywróć ikonę poprzedniemu folderowi`
- `# Ustaw ikonę aktywnego folderu`

---

## 3. `core/tools_tab.py` (29)

### UI Messages (16)
- `Files`
- `Tools`
- `Convert to WebP`
- `Resize Images`
- `Randomize File Names`
- `Shorten File Names`
- `Remove prefix/suffix`
- `Find Duplicates`
- `Rebuild Assets`
- `Character Limit`
- `Enter maximum file name length (without extension):`
- `Remove prefixes/suffixes`
- `Select operation mode:`
- `Remove PREFIX (start of name)`
- `Remove SUFFIX (end of name)`
- `Text to remove (case sensitive):`
- `Enter the text to be removed from file names...`
- `Examples: _8K, _FINAL, temp_, backup_, ' 0' (space+zero)`
- `REMOVE`
- `Cancel`
- `Please enter the text to remove.`
- `Confirm Find Duplicates`
- `Are you sure you want to find duplicates in folder:
{self.current_working_directory}?

Function will compare archive files based on SHA-256 and move newer duplicates along with related files to '__duplicates__' folder.`
- `Pary plików do zmiany nazw`
- `Znaleziono {len(pairs)} par plików do przetworzenia:`
- `Kontynuuj`
- `Pary plików do skrócenia nazw`

### Logi (10)
- `Rozpoczęto usuwanie {mode} w folderze: {self.current_working_directory}`
- `Błąd podczas rozpoczynania usuwania: {e}`
- `Nie można rozpocząć usuwania: {e}`
- `Rozpoczęto szukanie duplikatów w folderze: {self.current_working_directory}`
- `Błąd podczas rozpoczynania szukania duplikatów: {e}`
- `Cannot start finding duplicates: {e}`
- `Emitowano sygnał folder_structure_changed dla: {self.current_working_directory}`
- `Błąd w obsłudze zakończenia znajdowania duplikatów: {e}`

### Komentarze (3)
- `# Użytkownik potwierdził - kontynuuj operację`
- `"""Wyświetla okno z listą par, które będą skracane"""`
- `"""Czyści folder roboczy, dezaktywuje przyciski i czyści listy"""`

---

## 4. `core/amv_controllers/handlers/file_operation_controller.py` (27)

### UI Messages (10)
- `Moving Assets`
- `No assets selected for {operation_name.lower()}.`
- `Could not find full data for the selected assets.`
- `Found {len(assets_to_process)} assets, but {missing_count} selected assets are missing data.`
- `Select target folder`
- `Moving assets...`
- `Deleting Assets`
- `Confirm Deletion`
- `Are you sure you want to delete {len(assets_to_delete)} selected assets?
This operation is irreversible!`
- `Deleting assets...`

### Logi (1)
- `Błąd podczas optymalizowanego usuwania assetów: {e}`
- `Błąd odświeżania struktury folderów: {e}`
- `Błąd podczas fallback refresh galerii: {e}`

### Komentarze (16)
- `# OPTYMALIZACJA: Szybkie usuwanie tylko przeniesionych kafelków`
- `# OPTYMALIZACJA: Odłożone odświeżanie struktury folderów`
- `# Użyj QTimer żeby odłożyć odświeżanie struktury folderów`
- `# To pozwoli najpierw zakończyć usuwanie kafelków z galerii`
- `"""OPTYMALIZACJA: Szybkie usuwanie tylko przeniesionych assetów bez przebudowy galerii"""`
- `# Fallback bez mutex jeśli nie istnieje`
- `"""Waliduje dane wejściowe dla optymalizacji"""`
- `# Bezpośrednia aktualizacja bez emitowania sygnałów`
- `"""Aktualizuje listę assetów w kontrolerze"""`
- `"""Aktualizuje placeholder galerii w zależności od stanu assetów"""`
- `"""OPTYMALIZACJA: Szybkie usuwanie kafelków bez reorganizacji layoutu"""`
- `# Jednorazowa aktualizacja layoutu`
- `# Usuń z layoutu`
- `# Zwróć do puli (zamiast deleteLater dla lepszej wydajności)`
- `"""OPTYMALIZACJA: Odłożone odświeżanie struktury folderów"""`
- `# Odśwież tylko strukturę drzewa folderów (dla liczników assetów)`
- `# Odśwież także folder docelowy przy operacjach move`
- `"""Fallback: Pełne odświeżanie galerii w przypadku błędu optymalizacji"""`

---

## 5. `core/amv_models/folder_system_model.py` (21)

### Komentarze (21)
- `# Nowa opcja do pokazywania liczby assetów`
- `# Nowa opcja do rekurencyjnego sumowania assetów`
- `# Cache dla liczb assetów`
- `# Timestampy dla cache`
- `"""Ustawia czy pokazywać liczbę assetów w folderach"""`
- `# Wyczyść cache przy zmianie trybu`
- `# Odśwież drzewo folderów jeśli root folder jest ustawiony`
- `"""Zwraca czy pokazywane są liczby assetów"""`
- `"""Ustawia czy sumować assety z podfolderów rekurencyjnie"""`
- `# Wyczyść cache przy zmianie trybu rekurencyjnego`
- `"""Zwraca czy sumowane są assety rekurencyjnie"""`
- `"""Quickly counts assets in a folder (.asset files) - z cache"""`
- `"""Zwraca liczbę assetów z cache lub oblicza na nowo jeśli potrzeba"""`
- `# Sprawdź czy mamy cache i czy jest aktualny`
- `# Oblicz na nowo i zapisz w cache`
- `"""Zlicza assety bezpośrednio w folderze (bez podfolderów) - zoptymalizowane"""`
- `"""Zlicza assety rekurencyjnie w folderze i wszystkich podfolderach - zoptymalizowane"""`
- `"""Czyści cache liczb assetów"""`
- `"""Czyści cache dla konkretnej ścieżki i jej rodziców"""`
- `"""Formatuje nazwę folderu z liczbą assetów (jeśli włączone)"""`
- `# Wyczyść cache przy zmianie root folder`
- `# Wyczyść cache dla odświeżanego folderu`
- `# Spróbuj odświeżyć cały model jeśli nie znaleziono konkretnego folderu`
- `# Zaktualizuj nazwę folderu z nową liczbą assetów`
- `# Zaktualizuj liczby assetów w każdym folderze podczas odświeżania`

---

## 6. `core/amv_views/amv_view.py` (21)

### UI Messages (4)
- `Collapse`
- `Expand`
- `Close panel`
- `Open panel`

### Komentarze (17)
- `# Import tutaj aby uniknąć cyklicznych importów`
- `# Użyj wstrzykniętego widżetu lub utwórz nowy`
- `# Pokaż placeholder`
- `# Pokaż siatkę`
- `# wyrównane z polem tekstowym`
- `# Brak marginesów dla precyzyjnego wyrównania`
- `# Wyrównanie layoutu`
- `# Bez skalowania - CSS kontroluje rozmiar`
- `# Pozwala CSS kontrolować skalowanie`
- `# Usunięto setFixedHeight(14) - CSS kontroluje wysokość (16px)`
- `"""OPTYMALIZACJA: Usuwanie kafelków assetów z galerii bez przebudowy layoutu."""`
- `# Walidacja danych wejściowych`
- `# Wyłącz aktualizacje dla lepszej wydajności`
- `# Znajdź widżety do usunięcia`
- `# Usuń widżety z layoutu`
- `# Ukryj zamiast deleteLater dla lepszej wydajności`
- `# Ponownie włącz aktualizacje`
- `# Jednorazowa aktualizacja widoku`

---

## 7. `core/tools/prefix_suffix_remover_worker.py` (17)

### UI Messages (3)
- `Brak plików do przetworzenia`
- `Przetwarzanie: {filename_with_ext}`
- `Usuwanie {self.mode} zakończone: {renamed_count} plików zmieniono`

### Logi (4)
- `Rozpoczęcie usuwania {self.mode} w folderze: {self.folder_path}`
- `Zmieniono: '{filename_with_ext}' -> '{new_full_filename}'`
- `Błąd podczas przetwarzania {os.path.basename(file_path)}: {e}`
- `Błąd podczas usuwania {self.mode}: {e}`

### Komentarze (10)
- `"""Worker do usuwania prefixu/suffixu z nazw plików"""`
- `# Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker`
- `# "prefix" lub "suffix"`
- `"""Główna metoda usuwania prefixu/suffixu"""`
- `# Znajdź wszystkie pliki w folderze`
- `# Przetwórz pliki`
- `# Sprawdź czy plik pasuje do kryteriów`
- `# Usuń spacje z końca po usunięciu prefix`
- `# Usuń spacje z końca po usunięciu suffix`
- `# Zmień nazwę`
- `# Przygotuj komunikat końcowy`

---

## 8. `core/tools/duplicate_finder_worker.py` (16)

### UI Messages (3)
- `No archive files to check`
- `No duplicates found`
- `Found {len(duplicates)} duplicate groups. Moved {moved_count} files to __duplicates__ folder`

### Logi (1)
- `Rozpoczęcie szukania duplikatów w folderze: {self.folder_path}`

### Komentarze (12)
- `# Log informacyjny o załadowaniu modułu Rust`
- `# Pobierz informacje o kompilacji`
- `"""Worker do znajdowania duplikatów plików na podstawie SHA-256"""`
- `# lista duplikatów do wyświetlenia`
- `"""Główna metoda znajdowania duplikatów"""`
- `# Znajdź pliki archiwum`
- `# Oblicz SHA-256 dla każdego pliku`
- `# Znajdź duplikaty`
- `# Przygotuj listę do przeniesienia (nowsze pliki)`
- `# Przenieś pliki do folderu __duplicates__`

---

## 9. `core/pairing_tab.py` (16)

### UI Messages (11)
- `Create asset`
- `Delete unpaired previews`
- `Delete unpaired archives`
- `Rebuild assets`
- `Open in default program`
- `Confirmation`
- `Are you sure you want to delete ALL unpaired previews from the list and disk?
This operation cannot be undone.`
- `Success`
- `Successfully deleted unpaired previews.`
- `Error`
- `An error occurred while deleting previews. Check logs.`
- `Are you sure you want to delete ALL unpaired archives from the list and disk?
This operation cannot be undone.`
- `Successfully deleted unpaired archives.`
- `An error occurred while deleting archives. Check logs.`
- `Are you sure you want to rebuild all assets in the folder:
{work_folder}?`
- `Process started`
- `Asset rebuild started in folder:
{work_folder}`
- `Rebuild Error`

### Logi (1)
- `Zabezpieczenie przed wieloma oknami`

### Komentarze (4)
- `# Użyj folderu roboczego z modelu zamiast folderu z pliku unpair_files.json`
- `# KATEGORYCZNE CZYSZCZENIE CACHE PAMIĘCI RAM PO PRZEBUDOWIE ASSETÓW!!!`
- `# CATEGORICAL CLEARING OF RAM CACHE EVEN AFTER REBUILD ERROR!!!`

---

## 10. `core/amv_models/asset_grid_model.py` (15)

### Logi (8)
- `WCZYTYWANIE OD NOWA assetów w folderze: %s`
- `Inicjalizacja skanowania...`
- `Skanowanie: {message}`
- `Rozpoczynanie skanowania plików...`
- `Skanowanie zakończone, znaleziono %d assetów`
- `Ładowanie assetów z plików...`
- `WCZYTANO OD NOWA %d assetów z plików .asset`
- `Finalizowanie...`
- `WCZYTYWANIE OD NOWA zakończone, łącznie {len(all_assets)} assetów`
- `Zakończono!`

### Komentarze (7)
- `# Początek - inicjalizacja (0-10%)`
- `# WCZYTAJ OD NOWA - najpierw skanuj i utwórz assety`
- `# Skanuj folder i utwórz nowe assety (10-80%)`
- `# Map scan progress to the 10-80% range`
- `# Ładowanie assetów (80-95%)`
- `# WCZYTAJ OD NOWA - teraz załaduj wszystkie assety z plików .asset`
- `# Finalizacja (95-100%)`

---

## 11. `core/amv_models/workspace_folders_model.py` (14)

### Logi (4)
- `Folder roboczy nie istnieje: {folder_path}`
- `Załadowano {len(self._folders)} folderów roboczych (sortowanie alfabetyczne)`
- `Błąd podczas ładowania folderów roboczych: {e}`

### Komentarze (10)
- `# Przeiteruj przez work_folder1 do work_folder9`
- `# Sprawdź, czy folder istnieje (tylko jeśli ma ścieżkę)`
- `# Ustaw domyślną ikonę jeśli nie ma określonej`
- `# Dodaj wszystkie foldery, nawet puste`
- `# Aktywny tylko jeśli ma ścieżkę i istnieje`
- `# SORTOWANIE ALFABETYCZNE - najpierw aktywne, potem nieaktywne`
- `# Sortuj aktywne foldery alfabetycznie`
- `# Sortuj nieaktywne foldery alfabetycznie`
- `# Puste foldery na końcu`
- `# Złóż wszystko w kolejności: aktywne, nieaktywne, puste`

---

## 12. `core/tools/file_shortener_worker.py` (13)

### UI Messages (5)
- `No files to process`
- `Shortening pair names...`
- `Shortened pair: {archive_name[:20]}...`
- `Shortening unpaired file names...`
- `Processing: {filename[:20]}...`
- `Name shortening completed: {shortened_count} files shortened`

### Logi (3)
- `Zmieniono nazwę: {os.path.basename(file_path)} -> {new_name + file_ext}`
- `Błąd podczas zmiany nazwy {file_path}: {e}`

### Komentarze (5)
- `# Zmieniono nazwę sygnału na 'finished' zgodnie z BaseWorker`
- `# lista par do wyświetlenia`
- `# czeka na potwierdzenie użytkownika`
- `"""Zmienia nazwę pliku zachowując rozszerzenie"""`
- `# Pobierz rozszerzenie`
- `# Utwórz nową nazwę z rozszerzeniem`
- `# Zmień nazwę`

---

## 13. `core/amv_models/drag_drop_model.py` (12)

### Logi (1)
- `Porównanie ścieżek: norm_target='{norm_target}', norm_current='{norm_current}'`

### Komentarze (11)
- `# Lista ID assetów przeciąganych`
- `# Czy upuszczenie jest możliwe`
- `# Ścieżka docelowa, lista ID przeniesionych assetów`
- `# NOWE: zabezpieczenie przed rekurencją`
- `# ZABEZPIECZENIE: Sprawdź czy operacja już nie jest w toku`
- `# Normalizuj ścieżki do porównania`
- `# Przykład: Nie zezwalaj na upuszczanie do folderów tekstur`
- `# ZABEZPIECZENIE: Sprawdź czy asset_ids są prawidłowe`
- `# ZABEZPIECZENIE: Sprawdź czy target_path jest prawidłowy`
- `# Wyczyść po zakończeniu operacji`
- `# W przypadku błędu, wyczyść stan`

---

## 14. `core/scanner.py` (11)

### Logi (4)
- `🦀 ✅ SUKCES: Załadowano LOKALNY silnik Rust scanner z: {scanner_location}`
- `🦀 RUST SCANNER: Używam LOKALNEJ wersji z: {scanner_location} [build: {build_timestamp}, module: {module_number}]`
- `🦀 ⚠️ FALLBACK: Używam GLOBALNEGO silnika Rust scanner z: {scanner_location}`
- `🦀 RUST SCANNER: FALLBACK - używam globalnej wersji z: {scanner_location} [build: {build_timestamp}, module: {module_number}]`
- `🦀 ❌ BŁĄD: Nie można załadować żadnej wersji scanner_rust: {e}`

### Komentarze (7)
- `# ZAWSZE preferuj lokalną wersję Rust scannera z core/__rust`
- `# Usuń site-packages z path tymczasowo aby wymusić lokalną wersję`
- `# Usuń wszystkie ścieżki zawierające site-packages dla scanner_rust`
- `# Dodaj lokalny folder na początek`
- `# Pobierz informacje o kompilacji`
- `# Przywróć oryginalną ścieżkę w przypadku błędu`
- `# Nie można załadować Rustowego backendu (scanner_rust): {}`
- `"""Wrapper na Rustowy backend skanera assetów."""`

---

## 15. `core/amv_models/file_operations_model.py` (9)

### Logi (1)
- `Błąd przenoszenia assetu {original_name}: {e}`

### Komentarze (8)
- `# 1. Plik .asset`
- `# 2. Plik archiwum`
- `# 3. Plik podglądu`
- `# 4. Plik miniatury w folderze .cache`
- `# Przechowuj folder docelowy`
- `# Zapisz folder docelowy`
- `# Zwraca folder docelowy ostatniej operacji move`
- `# Wyczyść folder docelowy przy delete`

---

## Pozostałe pliki

- **`core/tools/file_renamer_worker.py` (8)**: 5 UI, 3 komentarze
- **`core/workers/asset_rebuilder_worker.py` (8)**: 5 UI, 1 log, 2 komentarze
- **`core/amv_controllers/handlers/folder_tree_controller.py` (8)**: 2 logi, 6 komentarzy
- **`core/tools/image_resizer_worker.py` (7)**: 4 UI, 3 komentarze
- **`core/tools/webp_converter_worker.py` (7)**: 4 UI, 3 komentarze
- **`core/json_utils.py` (6)**: 5 logów, 1 komentarz
- **`core/amv_views/preview_tile.py` (6)**: 6 komentarzy
- **`core/amv_controllers/amv_controller.py` (5)**: 5 komentarzy
- **`core/amv_controllers/handlers/asset_grid_controller.py` (5)**: 5 komentarzy
- **`core/amv_models/pairing_model.py` (5)**: 5 komentarzy
- **`core/amv_tab.py` (5)**: 5 komentarzy
- **`core/performance_monitor.py` (5)**: 5 komentarzy
- **`core/utilities.py` (5)**: 2 logi, 3 komentarze
- **`core/amv_models/config_manager_model.py` (4)**: 4 logi
- **`core/rules.py` (4)**: 4 komentarze
- **`core/main_window.py` (4)**: 4 UI
- **`core/preview_window.py` (3)**: 1 UI, 1 log, 1 komentarz
- **`core/amv_controllers/handlers/asset_rebuild_controller.py` (2)**: 2 komentarze
- **`core/amv_models/selection_model.py` (2)**: 2 komentarze
- **`core/selection_counter.py` (2)**: 2 UI
- **`core/workers/worker_manager.py` (2)**: 2 UI
- **`core/amv_controllers/handlers/signal_connector.py` (1)**: 1 komentarz
- **`core/amv_views/preview_gallery_view.py` (1)**: 1 komentarz
