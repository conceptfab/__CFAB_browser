### 📄 core/scanner.py - Analiza Korekcyjna

- **Status:** ✅ UKOŃCZONA ANALIZA
- **Data ukończenia:** niedziela, 29 czerwca 2025
- **Business impact:** `scanner.py` jest odpowiedzialny za kluczową logikę biznesową wykrywania i tworzenia assetów oraz zarządzania ich metadanymi. Jego wydajność bezpośrednio wpływa na szybkość ładowania galerii assetów i ogólną responsywność aplikacji podczas skanowania folderów.
- **Performance impact:** WYSOKI. Plik zawiera wiele operacji I/O i CPU-intensywnych, które są blokujące. Chociaż `find_and_create_assets` jest wywoływana w osobnym wątku przez `AssetScannerWorker`, operacje wewnątrz tej funkcji, zwłaszcza tworzenie miniatur, mogą być bardzo czasochłonne i wpływać na ogólny czas skanowania.
- **Modernization priority:** WYSOKIE - Optymalizacja operacji I/O i przetwarzania miniatur jest kluczowa dla poprawy wydajności skanowania i responsywności aplikacji.
- **Bottlenecks found:**
  - **`find_and_create_assets` i `load_existing_assets`:** Te funkcje wykonują wiele operacji I/O (odczyt/zapis plików, listowanie katalogów, sprawdzanie istnienia plików) bezpośrednio w wątku, w którym są wywoływane. Chociaż są one delegowane do `AssetScannerWorker` (QThread), ich wewnętrzna natura blokująca może spowalniać proces skanowania.
  - **`create_thumbnail_for_asset` (i `process_thumbnail` z `core.thumbnail`):** Przetwarzanie obrazów (tworzenie miniatur) jest operacją intensywną zarówno pod kątem I/O (odczyt dużych plików obrazów) jak i CPU (skalowanie, konwersja). Jest to prawdopodobnie największy bottleneck wydajnościowy w tym module.
  - **Operacje na plikach JSON (`load_from_file`, `save_to_file`):** Chociaż dla pojedynczych plików `.asset` nie jest to duży problem, przy dużej liczbie assetów sumaryczny czas odczytu/zapisu metadanych może być znaczący.
- **Modernization needed:**
  - **Asynchroniczne przetwarzanie miniatur:** Przeniesienie `process_thumbnail` do puli wątków (np. `QThreadPool`) lub do osobnego procesu, aby nie blokować wątku skanującego. Można również rozważyć cache'owanie miniatur.
  - **Optymalizacja operacji I/O:** Weryfikacja i optymalizacja wszystkich operacji I/O (np. `os.listdir`, `os.path.exists`, `os.path.getsize`) w celu zminimalizowania ich wpływu na wydajność. Można rozważyć buforowanie wyników lub bardziej efektywne algorytmy.
  - **Wprowadzenie Type Hints:** Dla lepszej czytelności i utrzymania kodu.
