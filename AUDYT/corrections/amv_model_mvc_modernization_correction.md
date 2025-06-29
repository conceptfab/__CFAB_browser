### 📄 core/amv_models/amv_model.py - Analiza Modernizacji MVC

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvModel` jest centralnym modelem agregującym. Modernizacja jego struktury w kontekście MVC poprawi modularność, testowalność i elastyczność całej aplikacji.
- **Performance impact:** NISKI. Modernizacja MVC dotyczy głównie struktury kodu i separacji odpowiedzialności, a nie bezpośrednio wydajności.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w modernizacji architektury MVC.
- **Bottlenecks found:**
  - **Bezpośrednie tworzenie instancji modeli:** `AmvModel` bezpośrednio tworzy instancje wszystkich podległych modeli w swoim konstruktorze. Utrudnia to testowanie jednostkowe (ponieważ nie można łatwo podmienić zależności) i zmniejsza elastyczność w konfiguracji aplikacji.
- **Modernization needed:**
  - **Wstrzykiwanie zależności (Dependency Injection):** Zamiast tworzyć instancje modeli w `__init__`, `AmvModel` powinien otrzymywać je jako argumenty konstruktora. To pozwoli na łatwiejsze testowanie (mockowanie zależności) i elastyczność w konfiguracji aplikacji.
  - **Definicja interfejsów (opcjonalnie, ale zalecane):** W połączeniu z implementacją wzorca Repository, można zdefiniować interfejsy dla każdego z tych modeli, a `AmvModel` mógłby przyjmować instancje tych interfejsów. To dodatkowo zwiększy abstrakcję i elastyczność.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
