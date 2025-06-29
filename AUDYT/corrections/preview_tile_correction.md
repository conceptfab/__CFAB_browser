### 📄 preview_tile.py - Analiza Poprawek

**Data analizy:** 29.06.2025

#### Główne Problemy Architektoniczne i Stylistyczne:

1.  **Naruszenie Zasady Pojedynczej Odpowiedzialności (SRP):**
    -   **Problem:** Klasa `PreviewTile` jest odpowiedzialna za zbyt wiele: tworzenie wszystkich swoich sub-widżetów, ładowanie obrazów, obsługę zdarzeń myszy i zarządzanie stanem zaznaczenia. Powinna być odpowiedzialna wyłącznie za prezentację danych.
    -   **Rekomendacja:**
        -   Przenieść logikę ładowania obrazów do dedykowanego serwisu (`ImageLoader`).
        -   Przenieść logikę zarządzania zaznaczeniem do `SelectionModel` (lub jego rozszerzenia). Widok powinien jedynie emitować sygnał o zmianie stanu checkboxa, a kontroler powinien aktualizować model.

2.  **Hardkodowane Style:**
    -   **Problem:** Style CSS są osadzone bezpośrednio w kodzie za pomocą `setStyleSheet()`. To sprawia, że zarządzanie wyglądem aplikacji i jej motywami jest kłopotliwe.
    -   **Rekomendacja:** Przenieść wszystkie style do zewnętrznego pliku QSS (`styles.qss`) i ładować go centralnie w aplikacji. Widżety powinny być stylizowane za pomocą selektorów klas i ID, a nie bezpośrednio w kodzie.

3.  **Brak Hermetyzacji Danych:**
    -   **Problem:** `file_path` i `file_name` są przechowywane jako oddzielne atrybuty. `file_name` jest pochodną `file_path`.
    -   **Rekomendacja:** Przechowywać tylko `file_path` (jako `pathlib.Path`), a `file_name` obliczać dynamicznie za pomocą `path.name`.

4.  **Niespójna Obsługa Zdarzeń:**
    -   **Problem:** Niektóre zdarzenia są obsługiwane przez reimplementację `mousePressEvent`, a inne przez podłączanie do sygnałów (`stateChanged.connect`).
    -   **Rekomendacja:** Ujednolicić podejście. Preferowane jest używanie sygnałów, ponieważ promuje to luźne powiązania. Jeśli konieczna jest reimplementacja `mouse...Event`, powinna ona jedynie emitować odpowiedni sygnał, a cała logika powinna być w slocie podłączonym do tego sygnału.
