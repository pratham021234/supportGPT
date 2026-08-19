from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, Tuple

from app.services.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class HTMLExtractor(BaseExtractor):
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f, "html.parser")
                
            # Remove scripts, styles, and non-content tags
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "meta", "link"]):
                element.decompose()
                
            metadata = {
                "title": soup.title.string.strip() if soup.title and soup.title.string else None
            }
            
            # Extract main content if available, else body
            main_content = soup.find("main") or soup.find("article") or soup.find("body") or soup
            
            # Extract headers for structure
            headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            metadata["headings_count"] = len(headings)
            
            # Replace some tags with markdown equivalents for better text representation
            for h in headings:
                level = int(h.name[1])
                h.insert_before("\n\n" + "#" * level + " ")
                h.insert_after("\n\n")
                
            for p in main_content.find_all('p'):
                p.insert_after("\n\n")
                
            text_content = main_content.get_text(separator=" ", strip=True)
            
            return text_content, 1, metadata
        except Exception as e:
            logger.error(f"Failed to parse HTML {file_path}: {str(e)}")
            raise e
