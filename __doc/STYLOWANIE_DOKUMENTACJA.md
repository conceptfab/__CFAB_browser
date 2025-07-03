# Dokumentacja Stylowania - CFAB Browser

## Przegląd

Stylowanie w projekcie jest oparte na **dziedziczeniu klas** i **centralnym pliku QSS**. To zapewnia:

- **Spójność** - wszystkie podobne elementy wyglądają identycznie
- **Łatwość modyfikacji** - zmieniasz style w jednym miejscu
- **Automatyczne dziedziczenie** - nowe elementy automatycznie mają odpowiednie style

## Struktura Stylowania

### 1. Klasy Bazowe (`core/base_widgets.py`)

Wszystkie podstawowe style są zdefiniowane w klasach bazowych:

#### BaseWidget

- **Plik**: `core/base_widgets.py` linia 95
- **Użycie**: Główny widget aplikacji
- **Style**: Tło główne, kolor tekstu

#### BaseFrame

- **Plik**: `core/base_widgets.py` linia 10
- **Użycie**: Ramki, panele
- **Style**: Tło, obramowanie, zaokrąglenie

#### BaseButton

- **Plik**: `core/base_widgets.py` linia 35
- **Użycie**: Podstawowe przyciski
- **Style**: Tło, obramowanie, hover, pressed

#### BaseLabel

- **Plik**: `core/base_widgets.py` linia 25
- **Użycie**: Etykiety tekstowe
- **Style**: Kolor tekstu, tło transparentne

#### BaseCheckBox

- **Plik**: `core/base_widgets.py` linia 55
- **Użycie**: Checkboxy
- **Style**: Indicator, checked, hover

### 2. Klasy Specjalizowane

#### ControlButtonBase

- **Plik**: `core/base_widgets.py` linia 207
- **Użycie**: Przyciski kontrolne (Zaznacz wszystkie, Przenieś zaznaczone, etc.)
- **Style**: Kompaktowy, ciemny, z hover efektami

#### PanelButtonBase

- **Plik**: `core/base_widgets.py` linia 246
- **Użycie**: Przyciski panelowe (Zwiń, Rozwiń)
- **Style**: Małe, kompaktowe, z zaokrągleniem

#### StarCheckBoxBase

- **Plik**: `core/base_widgets.py` linia 180
- **Użycie**: Gwiazdki ocen
- **Style**: Bez indicatora, kolor zmienia się na złoty gdy zaznaczone

#### TileBase

- **Plik**: `core/base_widgets.py` linia 110
- **Użycie**: Kafelki assetów
- **Style**: Tło, obramowanie, hover z niebieskim borderem

#### ThumbnailContainerBase

- **Plik**: `core/base_widgets.py` linia 130
- **Użycie**: Kontenery miniatur
- **Style**: Tło ciemne, transparent border, hover z niebieskim borderem

### 3. Centralny Plik QSS (`core/resources/styles.qss`)

Zawiera style dla standardowych widgetów Qt, które nie mają klas bazowych:

#### Główne sekcje:

- **Kolor podstawowy**: `#007ACC` (niebieski)
- **Tło główne**: `#1E1E1E` (ciemne)
- **Tło powierzchni**: `#252526` (ciemniejsze)
- **Obramowanie**: `#3F3F46` (szare)
- **Tekst**: `#CCCCCC` (jasny)

#### Widgety Qt:

- `QMainWindow`, `QDialog` - tło główne
- `QPushButton` - podstawowe przyciski
- `QTabWidget` - zakładki
- `QGroupBox` - grupy
- `QLineEdit`, `QTextEdit`, `QTableWidget` - pola edycji
- `QProgressBar` - pasek postępu
- `QMenu`, `QMenuBar` - menu
- `QScrollBar` - paski przewijania

## Jak Edytować Style

### 1. Zmiana Kolorów Głównych

**Plik**: `core/resources/styles.qss` (linie 8-15)

```css
/*
    primary_color: #007ACC;      <- Kolor główny (niebieski)
    success_color: #10B981;      <- Kolor sukcesu (zielony)
    warning_color: #DC2626;      <- Kolor ostrzeżenia (czerwony)
    background_color: #1E1E1E;   <- Tło główne
    surface_color: #252526;      <- Tło powierzchni
    border_color: #3F3F46;       <- Kolor obramowania
    text_color: #CCCCCC;         <- Kolor tekstu
    selection_color: #264F78;    <- Kolor zaznaczenia
*/
```

### 2. Zmiana Kolorów Okien

**Plik**: `core/resources/styles.qss` (linie 17-20)

```css
QMainWindow,
QDialog {
  background-color: #1e1e1e; /* <- Tło głównego okna */
  color: #cccccc; /* <- Kolor tekstu w oknie */
}
```

### 3. Zmiana Kolorów Zakładek

**Plik**: `core/resources/styles.qss` (linie 70-85)

```css
QTabBar::tab {
  background-color: #1e1e1e; /* <- Tło zakładki */
  color: #cccccc; /* <- Kolor tekstu */
  border: 1px solid #3f3f46; /* <- Obramowanie */
}

QTabBar::tab:selected {
  background-color: #252526; /* <- Tło aktywnej zakładki */
  border-bottom-color: #252526;
}
```

### 4. Zmiana Kolorów Pól Edycji

**Plik**: `core/resources/styles.qss` (linie 130-140)

```css
QLineEdit,
QTextEdit,
QTableWidget {
  background-color: #1c1c1c; /* <- Tło pól edycji */
  color: #cccccc; /* <- Kolor tekstu */
  border: 1px solid #3f3f46; /* <- Obramowanie */
}
```

### 5. Zmiana Stylu Przycisków Kontrolnych

**Plik**: `core/base_widgets.py` linia 214

```python
def _apply_control_button_styles(self):
    self.setStyleSheet("""
        ControlButtonBase {
            background-color: #3C3C3C;  # <- Zmień tutaj
            color: #CCCCCC;
            border: 1px solid #555555;
            # ... reszta stylów
        }
    """)
```

### 6. Zmiana Stylu Gwiazdek

**Plik**: `core/base_widgets.py` linia 185

```python
def _apply_star_styles(self):
    self.setStyleSheet("""
        StarCheckBoxBase {
            color: #888888;  # <- Kolor domyślny
            font-size: 14px;
        }
        StarCheckBoxBase:checked {
            color: #FFD700;  # <- Kolor zaznaczonej gwiazdki
        }
    """)
```

### 7. Zmiana Stylu Kafelków

**Plik**: `core/base_widgets.py` linia 115

```python
def _apply_tile_styles(self):
    self.setStyleSheet("""
        TileBase {
            background-color: #252526;  # <- Tło kafelka
            border: 1px solid #3F3F46;  # <- Obramowanie
        }
        TileBase:hover {
            border-color: #007ACC;      # <- Kolor hover
        }
    """)
```

## Dodawanie Nowych Stylów

### 1. Nowa Klasa Bazowa

```python
# W core/base_widgets.py
class CustomButtonBase(BaseButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_custom_styles()

    def _apply_custom_styles(self):
        self.setStyleSheet("""
            CustomButtonBase {
                background-color: #SPECJALNY_KOLOR;
                # ... reszta stylów
            }
        """)
```

### 2. Nowy Styl w QSS

```css
/* W core/resources/styles.qss */
QCustomWidget {
  background-color: #252526;
  color: #cccccc;
  border: 1px solid #3f3f46;
}
```

## Najczęstsze Modyfikacje

### Zmiana Koloru Głównego

1. Edytuj `primary_color` w `core/resources/styles.qss` (linia 9)
2. Zaktualizuj wszystkie wystąpienia `#007ACC` w stylach

### Zmiana Tła Głównego Okna

1. Edytuj `background_color` w `core/resources/styles.qss` (linia 12)
2. Zaktualizuj `QMainWindow, QDialog` (linia 18)

### Zmiana Rozmiaru Czcionki

1. Dla etykiet: `core/base_widgets.py` linia 30 (`font-size: 10px`)
2. Dla przycisków: `core/base_widgets.py` linia 45 (`font-size`)

### Zmiana Padding/Margin

1. Dla przycisków: `core/base_widgets.py` linia 47 (`padding: 4px 12px`)
2. Dla ramek: `core/base_widgets.py` linia 18 (`padding`)

## Debugowanie Stylów

### Sprawdzenie Aktualnego Stylu

```python
print(widget.styleSheet())  # Wyświetla aktualny styl widgetu
```

### Tymczasowe Wyłączenie Stylu

```python
widget.setStyleSheet("")  # Resetuje styl do domyślnego
```

### Sprawdzenie Dziedziczenia

```python
print(type(widget))  # Sprawdza klasę widgetu
```

## Najlepsze Praktyki

1. **Używaj klas bazowych** zamiast inline `setStyleSheet()`
2. **Edytuj style centralnie** w odpowiednich plikach
3. **Testuj zmiany** na różnych widgetach
4. **Zachowaj spójność** kolorów w całej aplikacji
5. **Dokumentuj niestandardowe style** w komentarzach

## Pliki do Edycji

### Główne pliki stylowania:

- `core/base_widgets.py` - Klasy bazowe z wbudowanymi stylami
- `core/resources/styles.qss` - Centralny plik QSS
- `core/amv_views/amv_view.py` - Widok główny (używa klas bazowych)
- `core/amv_views/asset_tile_view.py` - Kafelki assetów (używa klas bazowych)

### Pliki z inline stylami (do refaktoryzacji):

- `core/thumbnail_tile.py` - Stare kafelki (do zamiany na TileBase)
- `core/preview_window.py` - Okno podglądu
- `core/amv_views/preview_tile.py` - Kafelki podglądu
