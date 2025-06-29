### 📄 core/amv_views/preview_gallery_view.py - Analiza Korekcyjna

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `PreviewGalleryView` jest odpowiedzialny za wyświetlanie podglądów zasobów. Jego wydajność ma bezpośredni wpływ na płynność przeglądania i ogólne wrażenia użytkownika, zwłaszcza przy dużej liczbie podglądów i częstych zmianach rozmiaru okna.
- **Performance impact:** KRYTYCZNY. Głównym problemem jest nieefektywne zarządzanie widżetami `PreviewTile`, które są całkowicie usuwane i ponownie tworzone przy każdej zmianie rozmiaru widoku. Prowadzi to do znacznego obciążenia CPU i pamięci, powodując zacięcia UI i spowolnienia.
- **Modernization priority:** KRYTYCZNE - Optymalizacja tego widoku jest niezbędna dla zapewnienia responsywności i stabilności aplikacji.
- **Bottlenecks found:**
  - **Nieefektywne odświeżanie w `resizeEvent`:** Metoda `resizeEvent` wywołuje `set_previews`, co powoduje usunięcie wszystkich istniejących `PreviewTile` (za pomocą `deleteLater()`) i ponowne utworzenie ich od zera. Jest to bardzo kosztowna operacja, która będzie powodować zacięcia UI przy każdej zmianie rozmiaru okna, zwłaszcza gdy galeria zawiera wiele elementów.
  - **Ciągłe tworzenie i niszczenie `PreviewTile`:** W wyniku powyższego, obiekty `PreviewTile` są nieustannie tworzone i niszczone, co obciąża system zarządzania pamięcią i garbage collector Pythona. Każdy `PreviewTile` prawdopodobnie zawiera również `QPixmap`, co dodatkowo zwiększa obciążenie pamięci.
  - **Brak Object Pooling/Virtual Scrolling:** Brak mechanizmu ponownego wykorzystania instancji `PreviewTile` lub renderowania tylko widocznych elementów, co jest kluczowe dla wydajnych galerii.
- **Modernization needed:**
  - **Implementacja Object Pooling lub Virtual Scrolling:** Zamiast usuwać i ponownie tworzyć `PreviewTile` przy każdej zmianie rozmiaru, należy zaimplementować mechanizm ponownego wykorzystania istniejących instancji (object pooling) lub renderowania tylko widocznych elementów (virtual scrolling).
  - **Optymalizacja `resizeEvent`:** Zmiana logiki `resizeEvent`, aby nie wywoływała pełnego przeładowania galerii. Zamiast tego, powinna ona jedynie dostosowywać układ istniejących kafelków lub zarządzać pulą obiektów.
  - **Weryfikacja i optymalizacja `PreviewTile`:** Upewnienie się, że sam `PreviewTile` jest zoptymalizowany pod kątem pamięci (np. poprzez cache'owanie miniatur).
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
