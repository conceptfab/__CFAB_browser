### 🚀 pairing_model.py - Plan Modernizacji

**Data analizy:** 29.06.2025

#### Główne Kierunki Modernizacji:

1.  **Pełna Asynchronizacja Operacji Plikowych:**
    -   **Cel:** Wyeliminowanie wszystkich blokujących operacji I/O z głównego wątku, aby zapewnić pełną responsywność interfejsu.
    -   **Plan Działania:**
        1.  Stworzyć `PairingService`, który będzie zawierał metody asynchroniczne, np. `async def delete_archives_async(archives_to_delete: list[Path])`.
        2.  Wewnątrz tych metod używać `asyncio.to_thread`, aby uruchamiać blokujące funkcje (`os.remove`, `shutil.move`) w puli wątków `asyncio`.
        3.  Kontroler będzie wywoływał te metody asynchroniczne i używał `await` (w połączeniu z `qasync`) lub zarządzał zadaniami (`asyncio.Task`), aby obsłużyć wyniki po ich zakończeniu.
        4.  Należy zaimplementować mechanizm raportowania postępu i błędów oparty na sygnałach lub asynchronicznych kolejkach/callbackach.

2.  **Refaktoryzacja do Architektury Model-Repozytorium-Serwis:**
    -   **Cel:** Wprowadzenie czystej separacji odpowiedzialności, co ułatwi testowanie i utrzymanie kodu.
    -   **Plan Działania:**
        1.  `PairingStateModel(QObject)`: Będzie przechowywać tylko stan (listy plików) i emitować sygnały o jego zmianie. Nie będzie zawierać żadnej logiki I/O.
        2.  `UnpairedFilesRepository`: Będzie miał dwie metody: `async def load() -> PairingState` i `async def save(state: PairingState)`. Będzie odpowiedzialny tylko za serializację/deserializację pliku `unpair_files.json`.
        3.  `PairingService`: Będzie orkiestrował operacje. Np. metoda `pair_files` pobierze stan z modelu, wykona operacje plikowe, a na koniec poinformuje repozytorium o konieczności zapisu nowego stanu.

3.  **Modernizacja Zarządzania Ścieżkami i Danymi:**
    -   **Cel:** Użycie nowoczesnych, obiektowych i bezpiecznych typów.
    -   **Plan Działania:**
        1.  Zastąpić wszystkie stringi przechowujące ścieżki obiektami `pathlib.Path`.
        2.  Zamiast przechowywać listy stringów, `PairingStateModel` będzie przechowywał `list[Path]`.
        3.  Wprowadzić `dataclass` `PairingState` do hermetyzacji list niesparowanych plików, co ułatwi przekazywanie stanu między komponentami.

4.  **Wprowadzenie Jawnego Zarządzania Stanem:**
    -   **Cel:** Uniknięcie wielokrotnych, nieefektywnych zapisów na dysku.
    -   **Plan Działania:**
        1.  Usunąć automatyczne wywoływanie `save_unpair_files()` z metod modyfikujących stan.
        2.  Dodać w interfejsie użytkownika przycisk "Zapisz zmiany", który będzie wywoływał metodę `save` w serwisie/repozytorium.
        3.  Alternatywnie, zaimplementować mechanizm "auto-save" oparty na `QTimer`, który zapisuje zmiany np. 2 sekundy po ostatniej modyfikacji lub podczas zamykania aplikacji.
