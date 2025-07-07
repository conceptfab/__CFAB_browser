"""
JSON utilities with fallback to standard json
Facilitates migration and ensures compatibility
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
    Universal function for JSON deserialization

    Args:
        data: JSON string or bytes

    Returns:
        dict: Decoded data
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
    Universal function for JSON serialization

    Args:
        obj: Object to serialize
        indent: Whether to format with indentation

    Returns:
        bytes or str: JSON data
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
    Loads JSON from file

    Args:
        file_path: Path to file

    Returns:
        dict: Decoded data or None on error
    """
    try:
        import os

        # Check the file size before loading (100MB limit)
        file_size = os.path.getsize(file_path)
        max_size = 100 * 1024 * 1024  # 100MB

        if file_size > max_size:
            logger.error(
                f"File {file_path} is too large ({file_size} bytes), limit: {max_size} bytes"
            )
            return None

        if HAS_ORJSON:
            with open(file_path, "rb") as f:
                return orjson.loads(f.read())
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except PermissionError as e:
        logger.error(f"No permissions to read file {file_path}: {e}")
        return None
    except FileNotFoundError as e:
        logger.error(f"File does not exist {file_path}: {e}")
        return None
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid JSON format in file {file_path}: {e}")
        return None
    except UnicodeDecodeError as e:
        logger.error(f"File encoding error {file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while loading file {file_path}: {e}")
        return None


def save_to_file(obj, file_path, indent=True):
    """
    Saves JSON to file

    Args:
        obj: Object to save
        file_path: Path to file
        indent: Whether to format with indentation
    """
    if HAS_ORJSON:
        options = orjson.OPT_INDENT_2 if indent else 0
        with open(file_path, "wb") as f:
            f.write(orjson.dumps(obj, option=options))
    else:
        indent_value = 2 if indent else None
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent_value, ensure_ascii=False)
