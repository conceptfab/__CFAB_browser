### 🚀 preview_window.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Asynchroniczne Ładowanie Obrazów:**
    -   **Cel:** Zapewnienie płynności interfejsu użytkownika poprzez przeniesienie operacji ładowania obrazów do wątku roboczego.
    -   **Plan Działania:**
        1.  Stworzyć klasę `ImageLoader` (dziedziczącą z `QObject` lub `QRunnable`), która będzie ładować `QPixmap` w osobnym wątku (np. z `QThreadPool`).
        2.  `ImageLoader` powinien emitować sygnał (np. `image_loaded = pyqtSignal(QPixmap)`) po zakończeniu ładowania.
        3.  `PreviewWindow` powinien wyświetlać placeholder (np. pusty `QLabel` lub ikonę ładowania) i uruchamiać `ImageLoader`.
        4.  Po otrzymaniu sygnału `image_loaded`, `PreviewWindow` aktualizuje swój `QLabel` z załadowanym obrazem.

2.  **Wydzielenie Logiki Skalowania i Pozycjonowania:**
    -   **Cel:** Oddzielenie logiki prezentacji od logiki biznesowej i obliczeń.
    -   **Plan Działania:**
        1.  Stworzyć klasę `ImageDisplayManager` lub `ImageScaler`, która będzie odpowiedzialna za obliczanie optymalnego rozmiaru i pozycji obrazu na podstawie dostępnej przestrzeni i oryginalnego rozmiaru obrazu.
        2.  `PreviewWindow` będzie delegować te obliczenia do `ImageDisplayManager`.

3.  **Użycie `pathlib` dla Ścieżek:**
    -   **Cel:** Modernizacja kodu zgodnie z nowoczesnymi standardami Pythona.
    -   **Plan Działania:**
        1.  Zastąpić stringi reprezentujące ścieżki (`image_path`) obiektami `pathlib.Path`.
        2.  Wszelkie operacje na ścieżkach powinny być wykonywane przy użyciu metod `Path`.

4.  **Centralizacja Stylów QSS:**
    -   **Cel:** Ułatwienie zarządzania wyglądem aplikacji i tworzenia motywów.
    -   **Plan Działania:**
        1.  Usunąć hardkodowane style (`setStyleSheet`) z kodu.
        2.  Zdefiniować style dla `QDialog` i `QLabel` w zewnętrznym pliku QSS (`styles.qss`).
        3.  Upewnić się, że `styles.qss` jest ładowany centralnie w aplikacji (np. w `main_window.py`) i stosowany do całej aplikacji.

5.  **Lepsza Obsługa Błędów dla Użytkownika:**
    -   **Cel:** Informowanie użytkownika o problemach w bardziej czytelny sposób.
    -   **Plan Działania:**
        1.  W przypadku błędu ładowania obrazu, zamiast tylko ustawiać tekst na `QLabel`, wyświetlić `QMessageBox.warning` z informacją o błędzie.
        2.  Można również wyświetlić domyślną ikonę błędu zamiast pustego ekranu.
