# Poprawki do logiki obsługi kliknięć w foldery

## Wprowadzone zmiany

### Plik: `core/folder_scanner_worker.py`

**Metoda: `handle_folder_click`**

Zmieniono logikę decyzyjną zgodnie z wymaganiami użytkownika:

#### Poprzednia logika:

1. Sprawdzała czy są pliki asset
2. Jeśli tak - sprawdzała .cache
3. Jeśli nie - sprawdzała archiwa/podglądy

#### Nowa logika (zgodna z wymaganiami):

**WARUNEK 1**: Jeśli folder zawiera pliki archiwum i podglądy i NIE ma plików asset

- **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety

**WARUNEK 2**: Jeśli folder zawiera pliki archiwum, podglądy i pliki asset

- **Podwarunek 2a**: Jeśli nie ma folderu .cache
  - **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety
- **Podwarunek 2b**: Jeśli jest folder .cache ale zawiera inną liczbę plików thumb niż plików asset
  - **Akcja**: Scanner zaczyna pracę i po sukcesie galeria wyświetla assety
- **Podwarunek 2c**: Jeśli w .cache jest identyczna liczba plików thumb i asset
  - **Akcja**: Galeria wyświetla assety, scanner NIE uruchamia się automatycznie

**Dodatkowy przypadek**: Jeśli folder zawiera tylko pliki asset (bez archiwów/podglądów)

- Stosuje tę samą logikę co Warunek 2

## Szczegóły implementacji

### Zmienione warunki w kodzie:

```python
# LOGIKA DECYZYJNA ZGODNIE Z WYMAGANIAMI
if preview_archive_files and not asset_files:
    # WARUNEK 1: folder zawiera pliki archiwum i podglądy i NIE ma plików asset
    logger.info("Warunek 1: Uruchamiam scanner (brak plików asset)")
    self._run_scanner(folder_path)

elif preview_archive_files and asset_files:
    # WARUNEK 2: folder zawiera pliki archiwum, podglądy i pliki asset
    if not cache_exists:
        # Podwarunek 2a: nie ma folderu .cache - uruchom scanner
        logger.info("Warunek 2a: Uruchamiam scanner (brak .cache)")
        self._run_scanner(folder_path)

    elif cache_thumb_count != len(asset_files):
        # Podwarunek 2b: .cache istnieje ale liczba thumb != liczba asset
        logger.info(f"Warunek 2b: Uruchamiam scanner (thumb: {cache_thumb_count}, asset: {len(asset_files)})")
        self._run_scanner(folder_path)

    else:
        # Podwarunek 2c: .cache istnieje i liczba thumb == liczba asset
        # Galeria wyświetla assety, scanner NIE uruchamia się automatycznie
        logger.info(f"Warunek 2c: Wyświetlam galerię bez scannera (thumb: {cache_thumb_count}, asset: {len(asset_files)})")
        self.assets_folder_found.emit(folder_path)
```

## Zachowana funkcjonalność

- Galeria poprawnie obsługuje sygnał `assets_folder_found`
- `AssetScanner` może wyświetlać assety bez uruchamiania scannera
- `GridManager` poprawnie ustawia `current_folder_path` dla ładowania miniaturek
- Wszystkie pozostałe funkcjonalności pozostają niezmienione

## Testowanie

Aplikacja uruchamia się poprawnie. Logika decyzyjna jest teraz zgodna z wymaganiami użytkownika:

1. **Automatyczne uruchamianie scannera** gdy:

   - Brak plików asset (tylko archiwa/podglądy)
   - Brak folderu .cache
   - Niezgodna liczba miniaturek w .cache

2. **Wyświetlanie galerii bez scannera** gdy:

   - Folder .cache istnieje i ma identyczną liczbę miniaturek co plików asset

3. **Decyzja o uruchomieniu scannera** pozostaje do użytkownika gdy:
   - Wszystkie warunki są spełnione (identyczna liczba miniaturek i assetów)
