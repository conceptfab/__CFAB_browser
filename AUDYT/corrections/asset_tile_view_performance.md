### ⚡ asset_tile_view.py - Analiza Wydajności

**Data analizy:** 29.06.2025

#### Krytyczne Problemy Wydajnościowe:

1.  **Brak Reużywania Obiektów (Object Pooling) - NAJWYŻSZY PRIORYTET:**
    -   **Problem:** Każdy kafelek w siatce jest nową, w pełni zainicjalizowaną instancją `AssetTileView` z wieloma pod-widżetami. Przy siatce zawierającej tysiące elementów, proces tworzenia (`__init__`) i niszczenia (`deleteLater`) tych obiektów podczas przewijania (w obecnej architekturze) jest głównym źródłem problemów z wydajnością i zużyciem pamięci.
    -   **Rekomendacja (KRYTYCZNA):** Ten widok musi zostać przeprojektowany, aby wspierać **wirtualne przewijanie**. Zamiast tworzyć tysiące widżetów, należy stworzyć tylko tyle, ile mieści się na ekranie (+ niewielki bufor). Gdy użytkownik przewija, widżety, które znikają z ekranu, nie są niszczone, lecz przenoszone na drugi koniec i wypełniane nowymi danymi (`update_ui`). To jest wzorzec znany jako **Object Pooling** lub **View Recycling** i jest absolutnie kluczowy dla wydajności.

2.  **Synchroniczne Ładowanie Zasobów I/O w Głównym Wątku:**
    -   **Problem:** Metody `_setup_asset_tile_ui` i `_load_folder_icon` ładują obrazy z dysku (`QPixmap(thumbnail_path)`) w sposób blokujący. Jeśli dysk jest wolny, sieć jest wolna (w przypadku zasobów sieciowych) lub pliki są uszkodzone, operacja ta może zająć dużo czasu, powodując zacinanie się i brak responsywności interfejsu, zwłaszcza podczas szybkiego przewijania.
    -   **Rekomendacja (WYSOKA):** Ładowanie miniatur musi odbywać się **asynchronicznie w tle**. Należy zaimplementować globalny `ThumbnailLoader` (działający na `QThreadPool`), który będzie ładował obrazy w tle. Widok kafelka powinien najpierw wyświetlać placeholder, a następnie wysyłać żądanie załadowania miniatury. Gdy miniatura jest gotowa, `ThumbnailLoader` emituje sygnał z gotowym `QPixmap`, a kafelek aktualizuje swój wygląd.

3.  **Nieefektywne Aktualizacje UI (`update_thumbnail_size`):**
    -   **Problem:** Metoda `update_thumbnail_size` jest wywoływana dla każdego kafelka indywidualnie, gdy zmienia się rozmiar suwaka. Każde wywołanie powoduje zmianę rozmiaru widżetów i pełne odświeżenie UI kafelka (`self.update_ui()`). Dla setek kafelków jest to niepotrzebne obciążenie.
    -   **Rekomendacja (ŚREDNIA):** Zmiana rozmiaru powinna być zarządzana centralnie przez widok siatki (`AssetGridView`). Zamiast iterować po wszystkich kafelkach, `AssetGridView` powinien po prostu zaktualizować swój layout i poinformować widoczne kafelki o nowym rozmiarze. W połączeniu z wirtualnym przewijaniem, problem ten w dużej mierze zniknie, ponieważ aktualizowanych będzie tylko kilka widocznych kafelków.
