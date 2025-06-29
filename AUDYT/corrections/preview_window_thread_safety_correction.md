### 📄 core/preview_window.py - Analiza Thread Safety

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `PreviewWindow` jest oknem dialogowym UI, które wyświetla pojedynczy obraz. Zapewnienie bezpieczeństwa wątkowego jest kluczowe dla responsywności aplikacji, zwłaszcza podczas ładowania dużych obrazów.
- **Performance impact:** ŚREDNI. Główne operacje (ładowanie i skalowanie `QPixmap`) są wykonywane w głównym wątku UI, co może prowadzić do chwilowych zacięć UI dla dużych obrazów. Jest to problem wydajnościowy, który pośrednio wpływa na bezpieczeństwo wątkowe poprzez blokowanie głównego wątku.
- **Modernization priority:** ŚREDNIE - Optymalizacja ładowania obrazów jest wskazana, aby uniknąć blokowania UI.
- **Bottlenecks found:**
  - **Ładowanie `QPixmap` w głównym wątku:** W metodzie `load_image_and_resize`, `self.original_pixmap = QPixmap(absolute_image_path)` jest operacją blokującą, która jest wykonywana w głównym wątku UI. Dla dużych obrazów może to spowodować chwilowe zacięcie interfejsu użytkownika.
- **Modernization needed:**
  - **Asynchroniczne ładowanie obrazów:** Przeniesienie operacji ładowania `QPixmap` do wątku w tle (np. za pomocą `QThreadPool` lub dedykowanego `QThread`). Po załadowaniu i wstępnym przeskalowaniu, gotowy `QPixmap` powinien być przekazany do głównego wątku za pomocą sygnału/slotu w celu wyświetlenia.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
  - **Dokumentacja:** Dodanie komentarzy lub dokumentacji wyjaśniającej, w jaki sposób zapewniono bezpieczeństwo wątkowe w oknie podglądu.
