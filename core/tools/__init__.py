"""
Tools module for CFAB Browser
Contains all worker classes for file operations
"""

from .base_worker import BaseWorker, BaseToolWorker
from .webp_converter_worker import WebPConverterWorker
from .image_resizer_worker import ImageResizerWorker
from .file_renamer_worker import FileRenamerWorker
from .file_shortener_worker import FileShortenerWorker
from .prefix_suffix_remover_worker import PrefixSuffixRemoverWorker
from .duplicate_finder_worker import DuplicateFinderWorker

__all__ = [
    'BaseWorker',
    'BaseToolWorker',
    'WebPConverterWorker', 
    'ImageResizerWorker',
    'FileRenamerWorker',
    'FileShortenerWorker',
    'PrefixSuffixRemoverWorker',
    'DuplicateFinderWorker'
] 