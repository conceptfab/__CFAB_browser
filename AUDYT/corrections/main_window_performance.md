### ⚡ main_window.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Główne Problemy Wydajnościowe:

1.  **Synchroniczne Ładowanie Konfiguracji w Konstruktorze (NISKI PRIORYTET):**
    -   **Problem:** Metoda `_load_config_safe` jest wywoływana bezpośrednio w konstruktorze `MainWindow`. Oznacza to, że operacja odczytu pliku z dysku (`config.json`) odbywa się synchronicznie w głównym wątku UI, zanim okno zostanie w pełni zainicjalizowane i wyświetlone.
    -   **Wpływ:** Chociaż pliki konfiguracyjne są zazwyczaj małe i operacja ta jest bardzo szybka, w skrajnych przypadkach (np. plik na bardzo wolnym dysku sieciowym, uszkodzony dysk) może to nieznacznie opóźnić start aplikacji. Jest to antywzorzec, ponieważ konstruktory powinny być jak najlżejsze i nie powinny wykonywać operacji I/O.
    -   **Rekomendacja (NISKA):** Przenieść ładowanie konfiguracji do osobnego wątku lub zadania asynchronicznego. Można to zrobić na kilka sposobów:
        a)  Uruchomić ładowanie konfiguracji w osobnym wątku zaraz po utworzeniu instancji `MainWindow`, a następnie, po załadowaniu, przekazać ją do okna za pomocą sygnału.
        b)  Jeśli aplikacja używa `asyncio`, można użyć `asyncio.to_thread` do asynchronicznego załadowania konfiguracji.
        c)  W przypadku małych plików konfiguracyjnych, wpływ na wydajność jest minimalny, więc ta optymalizacja ma niski priorytet.

2.  **Potencjalne Opóźnienia przy Tworzeniu Zakładek (ZALEŻNE OD IMPLEMENTACJI ZAKŁADEK):**
    -   **Problem:** Metoda `_createTabs` tworzy instancje `AmvTab`, `PairingTab` i `ToolsTab` synchronicznie. Jeśli konstruktory tych zakładek wykonują długotrwałe operacje (np. ładowanie danych, skanowanie plików, inicjalizacja złożonych widżetów), może to opóźnić wyświetlenie głównego okna aplikacji.
    -   **Wpływ:** W obecnej implementacji `MainWindow` nie jest bezpośrednio odpowiedzialne za te opóźnienia, ale jest ich ofiarą. Problem leży w konstruktorach samych zakładek.
    -   **Rekomendacja (ZALEŻNE):** Upewnić się, że konstruktory wszystkich zakładek są lekkie i nie wykonują żadnych blokujących operacji I/O ani złożonych obliczeń. Długotrwałe inicjalizacje powinny być wykonywane asynchronicznie po wyświetleniu zakładki lub w osobnym wątku.

#### Pozytywne Aspekty:

-   **Brak Blokujących Operacji w Trakcie Działania:** Poza fazą inicjalizacji, `MainWindow` nie wykonuje żadnych operacji, które mogłyby blokować interfejs użytkownika. Jej rola jest głównie koordynacyjna i prezentacyjna.
-   **Efektywne Zarządzanie Sygnałami:** Połączenia sygnałów są wykonywane raz podczas inicjalizacji, co jest wydajne.
