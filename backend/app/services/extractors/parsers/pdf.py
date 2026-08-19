import pypdf
import logging
from typing import Dict, Any, Tuple

from app.services.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        text_content = []
        metadata = {}
        page_count = 0
        pages_mapping = []
        
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                if reader.is_encrypted:
                    # Try with empty password
                    if not reader.decrypt(""):
                        raise ValueError(f"PDF {file_path} is encrypted and requires a password.")
                        
                page_count = len(reader.pages)
                
                # Extract pypdf metadata
                doc_metadata = reader.metadata
                if doc_metadata:
                    metadata = {
                        "author": doc_metadata.author or "",
                        "title": doc_metadata.title or "",
                        "subject": doc_metadata.subject or "",
                        "creator": doc_metadata.creator or "",
                        "producer": doc_metadata.producer or "",
                        "creationDate": str(doc_metadata.creation_date) if doc_metadata.creation_date else "",
                        "modDate": str(doc_metadata.modification_date) if doc_metadata.modification_date else "",
                        "is_encrypted": reader.is_encrypted,
                        "format": "PDF"
                    }
                else:
                    metadata = {"format": "PDF"}
                
                current_offset = 0
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if not page_text:
                        continue
                        
                    # Calculate offsets
                    start_offset = current_offset
                    end_offset = current_offset + len(page_text)
                    
                    pages_mapping.append({
                        "page_number": page_num + 1,
                        "start_offset": start_offset,
                        "end_offset": end_offset
                    })
                    
                    text_content.append(page_text)
                    current_offset = end_offset + 2 # +2 for \n\n
                    
        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {str(e)}")
            raise e
            
        metadata["pages_mapping"] = pages_mapping
        
        return "\n\n".join(text_content), page_count, metadata
