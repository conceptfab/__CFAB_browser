### 📊 core/preview_window.py - Analiza Wydajności

**Plik:** `core/preview_window.py`

#### **Zidentyfikowane Bottlenecki Wydajnościowe:**

- **Skalowanie `QPixmap` w `resizeEvent`:**
  - **Opis:** Metoda `load_image` jest wywoływana w `resizeEvent` za każdym razem, gdy okno `PreviewWindow` zmienia rozmiar. Wewnątrz `load_image`, `self.original_pixmap` jest skalowany do aktualnego rozmiaru okna za pomocą `scaled()`. Jeśli `original_pixmap` jest bardzo duży (np. obraz o wysokiej rozdzielczości), operacja skalowania może być kosztowna obliczeniowo.
  - **Wpływ:** Chwilowe zacięcia lub spowolnienia UI podczas zmiany rozmiaru okna podglądu, zwłaszcza dla dużych obrazów i na mniej wydajnych systemach.
  - **Rekomendacja:** Zamiast skalować `original_pixmap` za każdym razem, można rozważyć skalowanie go raz do maksymalnego rozmiaru ekranu (lub nieco większego) przy pierwszym ładowaniu. Następnie, w `resizeEvent`, można skalować już wstępnie przeskalowany `QPixmap`, co jest szybsze niż skalowanie oryginalnego, bardzo dużego obrazu. Alternatywnie, dla bardzo dużych obrazów, można rozważyć asynchroniczne skalowanie, aby nie blokować głównego wątku UI.

- **Potencjalne obciążenie pamięci dla bardzo dużych obrazów:**
  - **Opis:** `self.original_pixmap` przechowuje pełną, nieskalowaną wersję obrazu w pamięci. Jeśli użytkownik otwiera wiele okien podglądu z bardzo dużymi obrazami, może to prowadzić do znacznego zużycia pamięci RAM.
  - **Wpływ:** Wysokie zużycie pamięci, potencjalne spowolnienia systemu lub awarie aplikacji w przypadku wyczerpania pamięci.
  - **Rekomendacja:** Implementacja mechanizmu cache'owania dla `QPixmap` w celu ponownego wykorzystania już załadowanych obrazów. Można również rozważyć ładowanie obrazów w niższej rozdzielczości dla podglądu, jeśli pełna rozdzielczość nie jest wymagana, lub dynamiczne zwalnianie `original_pixmap` po przeskalowaniu do rozmiaru okna, jeśli nie jest już potrzebny.

#### **Rekomendowane Działania Optymalizacyjne:**

1.  **Optymalizacja Skalowania Obrazów:**
    - Przy ładowaniu obrazu w `load_image_and_resize`, przeskalować `original_pixmap` do rozmiaru, który jest wystarczający dla maksymalnego rozmiaru okna podglądu (np. rozmiar ekranu). Następnie, w `load_image` (wywoływanej w `resizeEvent`), skalować już ten wstępnie przeskalowany `QPixmap`.
    - Dla ekstremalnie dużych obrazów, rozważyć użycie `QThreadPool` do asynchronicznego skalowania.
2.  **Zarządzanie Pamięcią `QPixmap`:**
    - Wdrożyć prosty mechanizm cache'owania dla `QPixmap`, aby unikać wielokrotnego ładowania tych samych obrazów.
    - Upewnić się, że `original_pixmap` jest prawidłowo zwalniany, gdy okno `PreviewWindow` jest zamykane (np. poprzez jawne ustawienie `self.original_pixmap = None` w destruktorze lub metodzie `closeEvent`).
3.  **Profilowanie Wydajności:**
    - Użycie narzędzi do profilowania (np. `cProfile`) do pomiaru czasu wykonywania operacji skalowania obrazów i identyfikacji ewentualnych dalszych bottlenecków.
