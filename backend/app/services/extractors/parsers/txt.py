import logging
import chardet
from typing import Dict, Any, Tuple

from app.services.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class TXTExtractor(BaseExtractor):
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        try:
            # Detect encoding
            with open(file_path, "rb") as f:
                raw_data = f.read()
                
            detected = chardet.detect(raw_data)
            encoding = detected.get("encoding", "utf-8") or "utf-8"
            
            try:
                content = raw_data.decode(encoding)
            except UnicodeDecodeError:
                # Fallback
                logger.warning(f"Failed to decode with {encoding}, falling back to utf-8 ignore")
                content = raw_data.decode("utf-8", errors="ignore")
                encoding = "utf-8 (ignore)"
                
            return content, 1, {"encoding": encoding}
        except Exception as e:
            logger.error(f"Failed to parse TXT {file_path}: {str(e)}")
            raise e
