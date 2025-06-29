### 🚀 tools_tab.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

Klasa `ToolsTab` jest obecnie bardzo prostym widżetem, pełniącym rolę miejsca na przyszłe narzędzia. W związku z tym, w obecnym stanie, **nie ma żadnych pilnych potrzeb modernizacyjnych**. Poniższe propozycje dotyczą przyszłego rozwoju, gdy zostaną dodane rzeczywiste narzędzia.

1.  **Modularna Architektura Narzędzi:**
    -   **Cel:** Umożliwienie łatwego dodawania, usuwania i zarządzania różnymi narzędziami w zakładce.
    -   **Plan Działania:**
        1.  Zdefiniować interfejs (klasę abstrakcyjną) `ITool` z metodami takimi jak `get_name()`, `get_widget()`, `initialize()`, `shutdown()`.
        2.  Każde narzędzie będzie osobną klasą implementującą `ITool`.
        3.  `ToolsTab` będzie pełnił rolę kontenera. Może używać `QStackedWidget` do przełączania się między widżetami narzędzi.
        4.  Narzędzia mogą być ładowane dynamicznie (np. z listy w konfiguracji) lub poprzez system wtyczek (plugin system).

2.  **Wstrzykiwanie Zależności dla Narzędzi:**
    -   **Cel:** Zapewnienie, że narzędzia mają dostęp do potrzebnych im usług (np. `ConfigManager`, `AssetScanner`, `FileOperationsModel`) bez tworzenia ścisłych powiązań.
    -   **Plan Działania:**
        1.  `ToolsTab` (lub dedykowany `ToolsController`) będzie odpowiedzialny za tworzenie instancji narzędzi i wstrzykiwanie im zależności w konstruktorze.
        2.  Można użyć prostego kontenera DI do zarządzania cyklem życia usług i narzędzi.

3.  **Asynchroniczne Wykonywanie Operacji Narzędzi:**
    -   **Cel:** Zapewnienie, że długotrwałe operacje wykonywane przez narzędzia nie blokują interfejsu użytkownika.
    -   **Plan Działania:**
        1.  Wszystkie operacje I/O i złożone obliczenia w narzędziach powinny być wykonywane asynchronicznie (np. za pomocą `QThread` lub `asyncio.to_thread`).
        2.  Narzędzia powinny raportować postęp i błędy za pomocą sygnałów, a `ToolsTab` (lub jego kontroler) powinien wyświetlać odpowiednie wskaźniki UI.

4.  **Pełne Adnotacje Typów:**
    -   **Cel:** Poprawa czytelności i umożliwienie statycznej analizy kodu.
    -   **Plan Działania:**
        1.  Upewnić się, że wszystkie metody i atrybuty mają precyzyjne adnotacje typów.
