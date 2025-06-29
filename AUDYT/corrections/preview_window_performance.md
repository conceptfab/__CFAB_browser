### ⚡ preview_window.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Synchroniczne Ładowanie Obrazu (KRYTYCZNY PRIORYTET):**
    -   **Problem:** Metoda `load_image_and_resize` wywołuje `QPixmap(absolute_image_path)`. Ta operacja jest blokująca i odbywa się w głównym wątku UI. Dla dużych plików graficznych (np. tekstury 4K, 8K) ładowanie obrazu może trwać od kilkuset milisekund do kilku sekund, całkowicie zamrażając interfejs użytkownika i powodując wrażenie "zawieszenia się" aplikacji.
    -   **Rekomendacja (KRYTYCZNA):** Ładowanie obrazów musi odbywać się **asynchronicznie w tle**. Należy zaimplementować dedykowany `ImageLoader` (działający na `QThreadPool` lub jako zadanie `asyncio.to_thread`), który będzie ładował obraz w tle. `PreviewWindow` powinien najpierw wyświetlać placeholder (np. pusty ekran lub ikonę ładowania), a następnie wysyłać żądanie załadowania obrazu. Gdy obraz jest gotowy, `ImageLoader` emituje sygnał z gotowym `QPixmap`, a `PreviewWindow` aktualizuje swój `QLabel`.

2.  **Nieefektywne Skalowanie Obrazu:**
    -   **Problem:** W metodzie `load_image` obraz jest skalowany za pomocą `self.original_pixmap.scaled(self.size(), ...)`. Oznacza to, że przy każdej zmianie rozmiaru okna, obraz jest skalowany od nowa z oryginalnego `QPixmap`. Chociaż Qt jest zoptymalizowane, dla bardzo dużych obrazów i częstych zmian rozmiaru, może to być kosztowne.
    -   **Rekomendacja (ŚREDNIA):** Zamiast skalować obraz przy każdej zmianie rozmiaru, można zastosować strategię, w której obraz jest skalowany do rozmiaru okna tylko raz, a następnie, jeśli okno jest powiększane, obraz jest ponownie skalowany z oryginalnego `QPixmap`. Jeśli okno jest zmniejszane, można użyć już przeskalowanej wersji, aby uniknąć ponownego skalowania z pełnej rozdzielczości. Można również rozważyć użycie `QGraphicsView` i `QGraphicsPixmapItem` dla bardziej zaawansowanego zarządzania skalowaniem i panoramowaniem dużych obrazów.

#### Pozytywne Aspekty:

-   **Użycie `Qt.WindowType.WindowStaysOnTopHint` i `Qt.WindowType.Tool`:** Te flagi są prawidłowo użyte do stworzenia okna podglądu, które zachowuje się jak narzędzie i pozostaje na wierzchu, co jest dobrym rozwiązaniem dla tego typu funkcjonalności.
