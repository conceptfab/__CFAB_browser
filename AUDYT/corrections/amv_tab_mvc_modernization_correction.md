### 📄 core/amv_tab.py - Analiza Modernizacji MVC

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvTab` jest główną klasą zakładki AMV, odpowiedzialną za inicjalizację i połączenie komponentów MVC. Modernizacja jej struktury poprawi modularność i testowalność aplikacji.
- **Performance impact:** NISKI. Modernizacja MVC dotyczy głównie struktury kodu i separacji odpowiedzialności, a nie bezpośrednio wydajności.
- **Modernization priority:** ŚREDNIE - Jest to ważny krok w modernizacji architektury MVC, ale nie tak krytyczny jak modernizacja samych modeli i widoków.
- **Bottlenecks found:**
  - **Bezpośrednie tworzenie instancji komponentów MVC:** `AmvTab` bezpośrednio tworzy instancje `AmvModel` i `AmvView` w swoim konstruktorze. Utrudnia to testowanie jednostkowe (ponieważ nie można łatwo podmienić zależności) i zmniejsza elastyczność w konfiguracji aplikacji.
- **Modernization needed:**
  - **Wstrzykiwanie zależności (Dependency Injection):** Zamiast tworzyć instancje `AmvModel` i `AmvView` w `__init__`, powinny one być przekazywane jako argumenty konstruktora. To pozwoli na łatwiejsze testowanie (mockowanie zależności) i elastyczność w konfiguracji aplikacji.
  - **Uproszczenie `__init__`:** Jeśli zależności są wstrzykiwane, konstruktor `AmvTab` staje się prostszy i bardziej czytelny.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
