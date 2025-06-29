### 📄 core/preview_window.py - Analiza Korekcyjna

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `PreviewWindow` odpowiada za wyświetlanie podglądu pojedynczego obrazu. Jego wydajność wpływa na szybkość otwierania podglądów i płynność ich skalowania, co jest ważne dla komfortu użytkownika.
- **Performance impact:** ŚREDNI. Główne potencjalne problemy wydajnościowe wynikają z operacji skalowania dużych obrazów w `resizeEvent`. Nie zidentyfikowano bezpośrednich, poważnych wycieków pamięci, ale optymalizacja zarządzania `QPixmap` może poprawić ogólną wydajność.
- **Modernization priority:** ŚREDNIE - Optymalizacja jest wskazana, ale nie jest krytyczna dla ogólnej funkcjonalności aplikacji w takim stopniu jak inne komponenty UI.
- **Bottlenecks found:**
  - **Skalowanie `QPixmap` w `resizeEvent`:** Metoda `load_image` (wywoływana w `resizeEvent`) skaluje `original_pixmap` za każdym razem, gdy okno zmienia rozmiar. Dla bardzo dużych obrazów i częstych zmian rozmiaru, ta operacja może być kosztowna obliczeniowo i prowadzić do chwilowych zacięć UI.
  - **Potencjalne obciążenie pamięci dla dużych obrazów:** Chociaż `original_pixmap` jest atrybutem instancji i powinien zostać zwolniony po zamknięciu okna, ładowanie bardzo dużych obrazów może chwilowo zwiększyć zużycie pamięci.
- **Modernization needed:**
  - **Optymalizacja skalowania obrazów:** Rozważenie technik takich jak skalowanie obrazu tylko raz do maksymalnego rozmiaru ekranu przy ładowaniu, a następnie używanie tego skalowanego obrazu do dalszych operacji, zamiast skalowania oryginalnego `QPixmap` za każdym razem. Można również rozważyć asynchroniczne skalowanie dla bardzo dużych obrazów.
  - **Zarządzanie pamięcią `QPixmap`:** Upewnienie się, że `QPixmap` są efektywnie zarządzane i zwalniane, gdy okno jest zamykane. W przypadku wielu otwieranych i zamykanych okien podglądu, można rozważyć cache'owanie często używanych `QPixmap`.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
