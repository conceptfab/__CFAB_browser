# CFAB Browser - PyInstaller Build

## Instalacja

1. Uruchom `install_pyinstaller.bat` aby utworzyć skrót na pulpicie
2. Lub przejdź do folderu `_dist/CFAB_Browser/` i uruchom `CFAB_Browser.exe`

## Testowanie

- **Test z konsolą**: Uruchom `test_exe.bat` - pokaże błędy jeśli występują
- **Normalny test**: Przejdź do folderu `_dist/CFAB_Browser/` i kliknij dwukrotnie `CFAB_Browser.exe`

## Wymagania systemowe

- Windows 10/11 (64-bit)
- 4 GB RAM
- 200 MB wolnego miejsca na dysku

## Informacje o buildzie

- **Kompilator**: PyInstaller (alternatywa dla Nuitka)
- **Tryb**: --onedir (kompletny folder z aplikacją)
- **GUI**: --windowed (bez konsoli) lub --console (z konsolą w debug)
- **Lokalizacja**: Folder `_dist/CFAB_Browser/`

## Zalety PyInstaller vs Nuitka

✅ Stabilniejszy z PyQt6
✅ Mniej problemów z reference counting
✅ Szybsza kompilacja
✅ Lepsze wsparcie dla bibliotek GUI

## Rozwiązywanie problemów

### Aplikacja się nie uruchamia
1. Uruchom `test_exe.bat` aby zobaczyć błędy
2. Sprawdź czy folder `_dist/CFAB_Browser/` istnieje
3. Uruchom jako administrator

### Brakuje plików zasobów
1. Sprawdź czy folder `_dist/CFAB_Browser/` zawiera wszystkie pliki
2. W razie potrzeby przekopiuj ręcznie

### Tryb debug
Jeśli aplikacja nie działa, spróbuj skompilować w trybie debug:
```
python build_pyinstaller.py --debug
```

## Wsparcie

W przypadku problemów:
1. Uruchom `test_exe.bat` dla szczegółów błędów
2. Sprawdź logi aplikacji
3. Porównaj z oryginalną wersją Python
