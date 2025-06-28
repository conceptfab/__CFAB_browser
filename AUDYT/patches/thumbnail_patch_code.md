# PATCH-CODE DLA: core/thumbnail.py

**Powiązany plik z analizą:** `../corrections/thumbnail_correction.md`
**Zasady ogólne:** `../refactoring_rules.md`

---

### PATCH 1: Uściślenie obsługi wyjątków w `_save_thumbnail_atomic`

**Problem:** W bloku `except` podczas czyszczenia pliku tymczasowego użyto ogólnego `except: pass`, co może maskować inne błędy.
**Rozwiązanie:** Zmiana ogólnego `except:` na bardziej specyficzny `except OSError:`, aby obsłużyć błędy operacji na plikach.

```python
# ... istniejący kod ...

    def _save_thumbnail_atomic(
        self,
        img: Image.Image,
        temp_path: Path,
        final_path: Path,
        output_format: str,
        quality: int,
    ):
        """Zapisuje thumbnail atomically z obsługą przezroczystości"""
        try:
            # ... istniejący kod zapisu ...

        except Exception as e:
            # Cleanup temp file
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:  # Zmieniono z ogólnego 'except:'
                    pass
            raise

# ... reszta istniejącego kodu ...
```

---

### PATCH 2: Uściślenie obsługi wyjątków w `_is_cache_valid` (ThumbnailConfigManager)

**Problem:** W metodzie `_is_cache_valid` użyto ogólnego `except: return False`, co może maskować inne błędy.
**Rozwiązanie:** Zmiana ogólnego `except:` na bardziej specyficzny `except OSError:`, aby obsłużyć błędy operacji na plikach.

```python
# ... istniejący kod ...

class ThumbnailConfigManager:
    # ... istniejący kod ...

    def _is_cache_valid(self, config_path):
        """Sprawdza czy cache konfiguracji jest aktualny"""
        if self._cache_settings is None or self._config_timestamp is None:
            return False

        try:
            current_timestamp = config_path.stat().st_mtime
            return current_timestamp == self._config_timestamp
        except OSError:  # Zmieniono z ogólnego 'except:'
            return False

# ... reszta istniejącego kodu ...
```

---

### PATCH 3: Uściślenie obsługi wyjątków w `clear_thumbnail_cache`

**Problem:** W pętli usuwającej pliki w `clear_thumbnail_cache` użyto ogólnego `except Exception as e: logger.warning(...)`, co może maskować inne błędy.
**Rozwiązanie:** Zmiana `except Exception as e:` na bardziej specyficzny `except OSError as e:`, aby obsłużyć błędy operacji na plikach.

```python
# ... istniejący kod ...

def clear_thumbnail_cache(work_folder: str, older_than_days: int = 0) -> int:
    # ... istniejący kod ...

        removed_count = 0
        for thumb_file in cache_dir.glob("*.thumb"):
            try:
                if older_than_days == 0 or thumb_file.stat().st_mtime < cutoff_time:
                    thumb_file.unlink()
                    removed_count += 1
            except OSError as e:  # Zmieniono z 'except Exception as e:'
                logger.warning(f"Could not remove {thumb_file}: {e}")

    # ... reszta istniejącego kodu ...
```

---

## ✅ CHECKLISTA WERYFIKACYJNA (DO WYPEŁNIENIA PRZED WDROŻENIEM)

#### **FUNKCJONALNOŚCI DO WERYFIKACJI:**

- [ ] **Funkcjonalność podstawowa** - czy plik nadal wykonuje swoją główną funkcję.
- [ ] **API kompatybilność** - czy wszystkie publiczne metody/klasy działają jak wcześniej.
- [ ] **Obsługa błędów** - czy mechanizmy obsługi błędów nadal działają.
- [ ] **Walidacja danych** - czy walidacja wejściowych danych działa poprawnie.
- [ ] **Logowanie** - czy system logowania działa bez spamowania.
- [ ] **Konfiguracja** - czy odczytywanie/zapisywanie konfiguracji działa.
- [ ] **Cache** - czy mechanizmy cache działają poprawnie.
- [ ] **Thread safety** - czy kod jest bezpieczny w środowisku wielowątkowym.
- [ ] **Memory management** - czy nie ma wycieków pamięci.
- [ ] **Performance** - czy wydajność nie została pogorszona.

#### **ZALEŻNOŚCI DO WERYFIKACJI:**

- [ ] **Importy** - czy wszystkie importy działają poprawnie.
- [ ] **Zależności zewnętrzne** - czy zewnętrzne biblioteki są używane prawidłowo.
- [ ] **Zależności wewnętrzne** - czy powiązania z innymi modułami działają.
- [ ] **Cykl zależności** - czy nie wprowadzono cyklicznych zależności.
- [ ] **Backward compatibility** - czy kod jest kompatybilny wstecz.
- [ ] **Interface contracts** - czy interfejsy są przestrzegane.
- [ ] **Event handling** - czy obsługa zdarzeń działa poprawnie.
- [ ] **Signal/slot connections** - czy połączenia Qt działają.
- [ ] **File I/O** - czy operacje na plikach działają.

#### **TESTY WERYFIKACYJNE:**

- [ ] **Test jednostkowy** - czy wszystkie funkcje działają w izolacji.
- [ ] **Test integracyjny** - czy integracja z innymi modułami działa.
- [ ] **Test regresyjny** - czy nie wprowadzono regresji.
- [ ] **Test wydajnościowy** - czy wydajność jest akceptowalna.

#### **KRYTERIA SUKCESU:**

- [ ] **WSZYSTKIE CHECKLISTY MUSZĄ BYĆ ZAZNACZONE** przed wdrożeniem.
- [ ] **BRAK FAILED TESTS** - wszystkie testy muszą przejść.
- [ ] **PERFORMANCE BUDGET** - wydajność nie pogorszona o więcej niż 5%.
- [ ] **CODE COVERAGE** - pokrycie kodu nie spadło poniżej 80%.
