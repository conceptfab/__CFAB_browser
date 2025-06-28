# PATCH CODE: amv_controller.py

**Wersja: 1.0**

**Data: 2025-06-28**

**Autor: Gemini**

---

## 🎯 OPIS ZMIAN

1.  **Przeniesienie importu:** Import `PreviewWindow` został przeniesiony na początek pliku.

## 💻 KOD

### Zmiana 1: Przeniesienie importu

**Na początku pliku `amv_controller.py` dodaj:**

```python
from ..thumbnail_tile import PreviewWindow
```

**W metodzie `_on_tile_thumbnail_clicked` usuń lokalny import:**

```python
    def _on_tile_thumbnail_clicked(self, path: str):
        """Obsługuje kliknięcie w miniaturkę kafelka."""
        logger.debug(f"Controller: Thumbnail clicked: {path}")
        if os.path.exists(path):
            try:
                # Otwórz podgląd w dedykowanym oknie aplikacji
                PreviewWindow(path, self.view)
                logger.info(f"Otworzono podgląd w dedykowanym oknie: {path}")
            except Exception as e:
                logger.error(f"Błąd podczas otwierania podglądu {path}: {e}")
                QMessageBox.warning(
                    self.view, "Błąd", f"Nie można otworzyć podglądu: {path}"
                )
        else:
            logger.warning(f"Plik nie istnieje: {path}")
            QMessageBox.warning(self.view, "Błąd", f"Plik nie istnieje: {path}")
```
