from typing import Dict, Any, Tuple
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """
    Abstract base class for all file extractors.
    """
    @abstractmethod
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        """
        Extracts content from a file.
        Returns:
            Tuple containing:
            - raw_text (str): The extracted text content.
            - page_count (int): Number of pages/sections.
            - metadata (dict): Any structural metadata extracted.
        """
        pass
