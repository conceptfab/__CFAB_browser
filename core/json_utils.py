"""
JSON utilities z fallback na standardowy json
Ułatwia migrację i zapewnia kompatybilność
"""

import logging

logger = logging.getLogger(__name__)

try:
    import orjson

    HAS_ORJSON = True
    logger.info("Using orjson for JSON operations")
except ImportError:
    import json

    HAS_ORJSON = False
    logger.warning("orjson not available, falling back to standard json")


def loads(data):
    """
    Uniwersalna funkcja do deserializacji JSON

    Args:
        data: JSON string lub bytes

    Returns:
        dict: Zdekodowane dane
    """
    if HAS_ORJSON:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return orjson.loads(data)
    else:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        return json.loads(data)


def dumps(obj, indent=False):
    """
    Uniwersalna funkcja do serializacji JSON

    Args:
        obj: Obiekt do serializacji
        indent: Czy formatować z wcięciami

    Returns:
        bytes lub str: JSON data
    """
    if HAS_ORJSON:
        options = 0
        if indent:
            options |= orjson.OPT_INDENT_2
        return orjson.dumps(obj, option=options)
    else:
        indent_value = 2 if indent else None
        result = json.dumps(obj, indent=indent_value, ensure_ascii=False)
        return result


def load_from_file(file_path):
    """
    Ładuje JSON z pliku

    Args:
        file_path: Ścieżka do pliku

    Returns:
        dict: Zdekodowane dane lub None w przypadku błędu
    """
    try:
        if HAS_ORJSON:
            with open(file_path, "rb") as f:
                return orjson.loads(f.read())
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except PermissionError as e:
        logger.error(f"Brak uprawnień do odczytu pliku {file_path}: {e}")
        return None
    except FileNotFoundError as e:
        logger.error(f"Plik nie istnieje {file_path}: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Nieprawidłowy format JSON w pliku {file_path}: {e}")
        return None
    except UnicodeDecodeError as e:
        logger.error(f"Błąd kodowania pliku {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas ładowania pliku {file_path}: {e}")
        return None


def save_to_file(obj, file_path, indent=True):
    """
    Zapisuje JSON do pliku

    Args:
        obj: Obiekt do zapisania
        file_path: Ścieżka do pliku
        indent: Czy formatować z wcięciami
    """
    if HAS_ORJSON:
        options = orjson.OPT_INDENT_2 if indent else 0
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(obj, option=options))
    else:
        indent_value = 2 if indent else None
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent_value, ensure_ascii=False)
