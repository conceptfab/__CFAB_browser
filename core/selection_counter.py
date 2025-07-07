"""
Selection Counter for centralizing asset counting logic.

This module provides business logic for counting selected, visible, and total assets,
separating it from UI presentation concerns.
"""

import logging
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class SelectionCounter:
    """
    Centralized logic for counting different types of assets.
    
    Handles counting of selected, visible, and total assets while filtering
    out special folders and providing consistent results.
    """
    
    def __init__(self, amv_controller):
        """
        Initialize SelectionCounter with AMV controller reference.
        
        Args:
            amv_controller: AMV controller instance for accessing asset data
        """
        self.amv_controller = amv_controller
        logger.debug("SelectionCounter initialized")
    
    def get_selection_summary(self) -> Dict[str, int]:
        """
        Get complete selection summary with all counts.
        
        Returns:
            Dict[str, int]: Dictionary with 'selected', 'visible', 'total' counts
        """
        try:
            summary = {
                'selected': self.count_selected_assets(),
                'visible': self.count_visible_assets(),
                'total': self.count_total_assets()
            }
            
            logger.debug(f"Selection summary: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"Error getting selection summary: {e}")
            return {'selected': 0, 'visible': 0, 'total': 0}
    
    def count_selected_assets(self) -> int:
        """
        Count currently selected assets (excluding special folders).
        
        Returns:
            int: Number of selected assets
        """
        try:
            if not self._validate_controller():
                return 0
            
            asset_grid_controller = self.amv_controller.asset_grid_controller
            
            if not hasattr(asset_grid_controller, "asset_tiles"):
                logger.debug("No asset_tiles found in asset_grid_controller")
                return 0
            
            selected_count = 0
            for tile in asset_grid_controller.asset_tiles:
                if self._is_valid_selected_tile(tile):
                    selected_count += 1
            
            logger.debug(f"Counted {selected_count} selected assets")
            return selected_count
            
        except Exception as e:
            logger.error(f"Error counting selected assets: {e}")
            return 0
    
    def count_visible_assets(self) -> int:
        """
        Count currently visible assets (excluding special folders).
        
        Returns:
            int: Number of visible assets
        """
        try:
            if not self._validate_controller():
                return 0
            
            asset_grid_controller = self.amv_controller.asset_grid_controller
            
            if not hasattr(asset_grid_controller, "asset_tiles"):
                logger.debug("No asset_tiles found for visible count")
                return 0
            
            visible_count = 0
            for tile in asset_grid_controller.asset_tiles:
                if self._is_valid_asset_tile(tile):
                    visible_count += 1
            
            logger.debug(f"Counted {visible_count} visible assets")
            return visible_count
            
        except Exception as e:
            logger.error(f"Error counting visible assets: {e}")
            return 0
    
    def count_total_assets(self) -> int:
        """
        Count total assets from original unfiltered list (excluding special folders).
        
        Returns:
            int: Number of total assets
        """
        try:
            if not self._validate_controller():
                return 0
            
            asset_grid_controller = self.amv_controller.asset_grid_controller
            
            if not hasattr(asset_grid_controller, "get_original_assets"):
                logger.debug("No get_original_assets method found")
                return 0
            
            original_assets = asset_grid_controller.get_original_assets()
            
            if not original_assets:
                logger.debug("No original assets found")
                return 0
            
            total_count = self._count_non_special_assets(original_assets)
            
            logger.debug(f"Counted {total_count} total assets")
            return total_count
            
        except Exception as e:
            logger.error(f"Error counting total assets: {e}")
            return 0
    
    def _validate_controller(self) -> bool:
        """
        Validate that AMV controller and asset grid controller are available.
        
        Returns:
            bool: True if controllers are valid, False otherwise
        """
        if not self.amv_controller:
            logger.debug("No AMV controller available")
            return False
        
        if not hasattr(self.amv_controller, "asset_grid_controller"):
            logger.debug("No asset_grid_controller in AMV controller")
            return False
        
        asset_grid_controller = self.amv_controller.asset_grid_controller
        if not asset_grid_controller:
            logger.debug("asset_grid_controller is None")
            return False
        
        return True
    
    def _is_valid_asset_tile(self, tile) -> bool:
        """
        Check if tile represents a valid asset (not special folder).
        
        Args:
            tile: Asset tile to check
            
        Returns:
            bool: True if tile is valid asset, False otherwise
        """
        try:
            return (
                hasattr(tile, "model")
                and tile.model
                and not getattr(tile.model, 'is_special_folder', False)
            )
        except Exception as e:
            logger.debug(f"Error checking tile validity: {e}")
            return False
    
    def _is_valid_selected_tile(self, tile) -> bool:
        """
        Check if tile represents a valid selected asset.
        
        Args:
            tile: Asset tile to check
            
        Returns:
            bool: True if tile is valid and selected, False otherwise
        """
        try:
            return (
                self._is_valid_asset_tile(tile)
                and hasattr(tile, "is_checked")
                and tile.is_checked()
            )
        except Exception as e:
            logger.debug(f"Error checking selected tile validity: {e}")
            return False
    
    def _count_non_special_assets(self, assets: List[Dict[str, Any]]) -> int:
        """
        Count assets excluding special folders.
        
        Args:
            assets: List of asset dictionaries
            
        Returns:
            int: Number of non-special assets
        """
        try:
            return len([
                asset for asset in assets
                if asset.get("type") != "special_folder"
            ])
        except Exception as e:
            logger.error(f"Error counting non-special assets: {e}")
            return 0
    
    def get_status_text(self, summary: Optional[Dict[str, int]] = None) -> str:
        """
        Generate formatted status text for UI display.
        
        Args:
            summary: Optional pre-calculated summary, if None will calculate
            
        Returns:
            str: Formatted status text
        """
        try:
            if summary is None:
                summary = self.get_selection_summary()
            
            selected = summary.get('selected', 0)
            visible = summary.get('visible', 0)
            total = summary.get('total', 0)
            
            status_text = f"Selected: {selected}"
            
            # Add visibility info if there's filtering
            if visible != total and total > 0:
                status_text += f" (visible: {visible}/{total})"
            
            return status_text
            
        except Exception as e:
            logger.error(f"Error generating status text: {e}")
            return "Selected: 0" 