# Plan migracji do Rusta

1.  **Stworzenie nowego modułu `tools`**: Wewnątrz `scanner_rust/src` utworzę nowy plik `tools.rs`, w którym umieszczę wszystkie nowe funkcje pomocnicze. Pozwoli to na oddzielenie nowej logiki od istniejącego skanera.

2.  **Obliczanie SHA-256**:

    - Do `Cargo.toml` dodam bibliotekę `sha2` do wydajnego obliczania hashy.
    - W `tools.rs` zaimplementuję funkcję `calculate_sha256(path: &str) -> String`.
    - W Pythonie (`duplicate_finder_worker.py`) zastąpię istniejącą implementację wywołaniem nowej funkcji z Rusta.

3.  **Przetwarzanie obrazów (Skalowanie i konwersja WebP)**:

    - Wykorzystam istniejącą w projekcie bibliotekę `image`.
    - W `tools.rs` zaimplementuję dwie funkcje:
      - `resize_image(path: &str)`: odtworzy logikę skalowania z `image_resizer_worker.py`.
      - `convert_to_webp(input_path: &str, output_path: &str)`: odtworzy logikę konwersji z `webp_converter_worker.py`.
    - Zaktualizuję odpowiednie workery w Pythonie, aby korzystały z nowych, szybszych funkcji.

4.  **Budowanie modułu**: Po zaimplementowaniu zmian, przebuduję moduł Rusta za pomocą istniejącego skryptu `build.bat`, aby zmiany były dostępne w Pythonie.
