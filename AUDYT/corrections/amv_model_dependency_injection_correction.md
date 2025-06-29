### 📄 core/amv_models/amv_model.py - Analiza Dependency Injection

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `AmvModel` jest modelem agregującym, który bezpośrednio tworzy instancje wszystkich swoich podległych modeli. Wprowadzenie Dependency Injection poprawi modularność, testowalność i elastyczność aplikacji, ułatwiając zarządzanie zależnościami.
- **Performance impact:** NISKI. Wprowadzenie Dependency Injection dotyczy głównie struktury kodu i separacji odpowiedzialności, a nie bezpośrednio wydajności.
- **Modernization priority:** WYSOKIE - Jest to kluczowy krok w modernizacji architektury i przygotowaniu aplikacji na przyszłe zmiany w sposobie przechowywania danych i komponentów.
- **Bottlenecks found:**
  - **Brak Dependency Injection:** `AmvModel` jest silnie związany z konkretnymi implementacjami swoich podległych modeli, ponieważ tworzy je bezpośrednio w konstruktorze. To utrudnia:
    - **Testowanie jednostkowe:** Niemożność łatwego podmienienia rzeczywistych zależności na mocki.
    - **Elastyczność:** Zmiana implementacji któregokolwiek z podległych modeli wymagałaby modyfikacji `AmvModel`.
    - **Zarządzanie cyklem życia:** `AmvModel` jest odpowiedzialny za cykl życia swoich zależności.
- **Modernization needed:**
  - **Wstrzykiwanie zależności w konstruktorze:** Zamiast tworzyć instancje wszystkich modeli w `__init__`, `AmvModel` powinien otrzymywać je jako argumenty konstruktora. To pozwoli na łatwiejsze testowanie i elastyczność w konfiguracji aplikacji.
  - **Użycie interfejsów (opcjonalnie, ale zalecane):** Jeśli zdefiniowano interfejsy (np. `IAssetRepository`), `AmvModel` powinien przyjmować instancje tych interfejsów, a nie konkretne implementacje. To dodatkowo zwiększy abstrakcję i elastyczność.
  - **Centralny kontener DI (w przyszłości):** W przyszłości można rozważyć wprowadzenie centralnego kontenera Dependency Injection (np. prostego słownika lub dedykowanej biblioteki), który zarządzałby tworzeniem i wstrzykiwaniem zależności w całej aplikacji.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
