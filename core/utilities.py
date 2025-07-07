"""
Utilities module - common utility functions
"""

import logging
import os

logger = logging.getLogger(__name__)


def clear_thumbnail_cache_after_rebuild(is_error: bool = False):
    """
    Clears RAM cache after asset rebuild.
    Simplified version - removed duplicate logic and excessive logging.
    
    Args:
        is_error (bool): True if clearing after error, False after success
    """
    try:
        from core.thumbnail_cache import thumbnail_cache
        
        thumbnail_cache.clear()
        
        status = "after error" if is_error else "after rebuild"
        logger.info(f"RAM cache cleared {status}")
            
    except Exception as e:
        logger.error(f"Error clearing thumbnail cache: {e}")





def update_main_window_status(widget):
    """
    Updates the status bar in the main window.
    Simplified version with optimized parent traversal.
    """
    try:
        # Optimized parent traversal - limit depth to prevent infinite loops
        current_widget = widget
        max_depth = 10  # Safety limit
        depth = 0
        
        while current_widget and depth < max_depth:
            if hasattr(current_widget, "update_selection_status"):
                current_widget.update_selection_status()
                logger.debug("Updated main window status")
                return  # Exit early on success
            
            current_widget = current_widget.parent()
            depth += 1
        
        # If we reach here, no status updater was found
        logger.debug("No status updater found in widget hierarchy")
        
    except Exception as e:
        logger.debug(f"Exception updating main window status: {e}")
