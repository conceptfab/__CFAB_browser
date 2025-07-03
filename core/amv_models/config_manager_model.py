import logging
import os
import sys

from PyQt6.QtCore import QObject, pyqtSignal

from core.json_utils import load_from_file

logger = logging.getLogger(__name__)


class ConfigManagerMV(QObject):
    """Model dla zarządzania konfiguracją w architekturze M/V"""

    config_loaded = pyqtSignal(dict)
    config_error = pyqtSignal(str)
    config_reloaded = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._config_cache = None
        self._config_timestamp = None
        self._config_path = "config.json"
        logger.debug("ConfigManagerMV initialized")

    def load_config(self, force_reload=False):
        try:
            if force_reload or not self._is_cache_valid():
                logger.debug("Ładowanie konfiguracji z pliku")
                config = load_from_file(self._config_path)
                if config:
                    self._config_cache = config
                    self._config_timestamp = (
                        os.path.getmtime(self._config_path)
                        if os.path.exists(self._config_path)
                        else 0
                    )
                    self.config_loaded.emit(config)
                    logger.debug("Konfiguracja załadowana pomyślnie")
                else:
                    self._config_cache = self._get_default_config()
                    self._config_timestamp = 0
                    self.config_loaded.emit(self._config_cache)
                    logger.warning("Użyto domyślnej konfiguracji")

            return self._config_cache or self._get_default_config()

        except Exception as e:
            error_msg = f"Błąd ładowania konfiguracji: {e}"
            logger.error(error_msg)
            self.config_error.emit(error_msg)
            return self._get_default_config()

    def reload_config(self):
        config = self.load_config(force_reload=True)
        self.config_reloaded.emit(config)
        return config

    def get_config(self):
        if not self._config_cache:
            return self.load_config()
        return self._config_cache

    def _is_cache_valid(self):
        if not self._config_cache or not os.path.exists(self._config_path):
            return False
        current_timestamp = os.path.getmtime(self._config_path)
        return current_timestamp == self._config_timestamp

    def _get_default_config(self):
        return {
            "thumbnail": 256,
            "logger_level": "INFO",
            "use_styles": True,
            "work_folder1": "",
            "work_folder2": "",
            "work_folder3": "",
            "work_folder4": "",
            "work_folder5": "",
            "work_folder6": "",
            "work_folder7": "",
            "work_folder8": "",
            "work_folder9": "",
        }
