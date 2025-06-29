### 📄 preview_window.py - Analiza Poprawek

**Data analizy:** 29.06.2025

#### Główne Problemy Architektoniczne i Stylistyczne:

1.  **Mieszanie Logiki z Widokiem:**
    -   **Problem:** Klasa `PreviewWindow` jest widokiem, ale zawiera logikę ładowania i skalowania obrazu (`load_image_and_resize`, `load_image`). Widok powinien jedynie wyświetlać dane, które zostały mu dostarczone.
    -   **Rekomendacja:** Wydzielić logikę ładowania i przetwarzania obrazu do osobnej klasy, np. `ImageLoader` lub `ImageProcessor`. `PreviewWindow` powinien przyjmować gotowy `QPixmap` lub zlecać jego załadowanie dedykowanemu serwisowi, a następnie tylko go wyświetlać.

2.  **Hardkodowane Style:**
    -   **Problem:** Style CSS są osadzone bezpośrednio w kodzie za pomocą `setStyleSheet()`. To sprawia, że zarządzanie wyglądem aplikacji jest kłopotliwe i utrudnia tworzenie motywów.
    -   **Rekomendacja:** Przenieść wszystkie style do zewnętrznego pliku QSS (`styles.qss`) i ładować go centralnie w aplikacji. Widżety powinny być stylizowane za pomocą selektorów klas i ID, a nie bezpośrednio w kodzie.

3.  **Brak Jawnego Zarządzania Cyklem Życia Okna:**
    -   **Problem:** Okno podglądu jest tworzone i pokazywane w jednej linii (`PreviewWindow(path, self.view)`), ale nie ma jawnego zarządzania jego cyklem życia (np. zamykania po utracie fokusu, czy po zamknięciu głównego okna).
    -   **Rekomendacja:** Upewnić się, że okno podglądu jest prawidłowo zamykane i zwalniane z pamięci. Można to osiągnąć poprzez:
        -   Użycie `self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)`.
        -   Zarządzanie instancjami okien podglądu w kontrolerze, który będzie odpowiedzialny za ich tworzenie i niszczenie.

4.  **Niejasne Przeznaczenie `parent`:**
    -   **Problem:** Konstruktor przyjmuje `parent`, ale nie jest on w pełni wykorzystywany do zarządzania cyklem życia okna. Okno jest ustawione na `WindowStaysOnTopHint` i `Tool`, co sugeruje, że ma być niezależne.
    -   **Rekomendacja:** Jeśli okno ma być niezależne, `parent` może być `None`. Jeśli ma być zależne, należy upewnić się, że jego cykl życia jest prawidłowo powiązany z rodzicem.
