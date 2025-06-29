"""
Abstrakcyjne interfejsy dla wzorca Repository w aplikacji CFAB Browser.

Ten moduł definiuje interfejsy dla różnych typów repozytoriów używanych w aplikacji,
zapewniając separację odpowiedzialności i ułatwiając testowanie.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class IAssetRepository(ABC):
    """
    Abstrakcyjny interfejs dla repozytorium assetów.

    Definiuje operacje związane z wyszukiwaniem, tworzeniem i ładowaniem assetów.
    """

    @abstractmethod
    def find_and_create_assets(
        self,
        folder_path: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        use_async_thumbnails: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Wyszukuje i tworzy assety w określonym folderze.

        Args:
            folder_path: Ścieżka do folderu do skanowania
            progress_callback: Opcjonalna funkcja callback do raportowania postępu
            use_async_thumbnails: Czy używać asynchronicznego generowania miniatur

        Returns:
            Lista słowników reprezentujących znalezione assety
        """
        pass

    @abstractmethod
    def load_existing_assets(self, folder_path: str) -> List[Dict[str, Any]]:
        """
        Ładuje istniejące assety z określonego folderu.

        Args:
            folder_path: Ścieżka do folderu

        Returns:
            Lista słowników reprezentujących załadowane assety
        """
        pass

    @abstractmethod
    def create_thumbnail_for_asset(
        self, asset_path: str, image_path: str, async_mode: bool = False
    ) -> Optional[str]:
        """
        Tworzy miniaturę dla assetu.

        Args:
            asset_path: Ścieżka do pliku assetu
            image_path: Ścieżka do obrazu podglądu
            async_mode: Czy używać trybu asynchronicznego

        Returns:
            Ścieżka do utworzonej miniatury lub None przy błędzie
        """
        pass


class IFileOperationsRepository(ABC):
    """
    Abstrakcyjny interfejs dla repozytorium operacji na plikach.

    Definiuje operacje związane z przenoszeniem, usuwaniem i zarządzaniem plikami assetów.
    """

    @abstractmethod
    def move_assets(
        self,
        assets_data: List[Dict[str, Any]],
        source_folder_path: str,
        target_folder_path: str,
    ) -> None:
        """
        Przenosi assety z folderu źródłowego do docelowego.

        Args:
            assets_data: Lista danych assetów do przeniesienia
            source_folder_path: Ścieżka do folderu źródłowego
            target_folder_path: Ścieżka do folderu docelowego
        """
        pass

    @abstractmethod
    def delete_assets(
        self, assets_data: List[Dict[str, Any]], current_folder_path: str
    ) -> None:
        """
        Usuwa assety z określonego folderu.

        Args:
            assets_data: Lista danych assetów do usunięcia
            current_folder_path: Ścieżka do folderu zawierającego assety
        """
        pass

    @abstractmethod
    def stop_operation(self) -> None:
        """
        Zatrzymuje bieżącą operację na plikach.
        """
        pass
