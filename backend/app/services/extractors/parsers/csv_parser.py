import csv
import logging
import chardet
from typing import Dict, Any, Tuple

from app.services.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class CSVExtractor(BaseExtractor):
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        text_content = []
        metadata = {}
        
        try:
            # Detect encoding
            with open(file_path, "rb") as f:
                raw_data = f.read(10000) # Read chunk for detection
            detected = chardet.detect(raw_data)
            encoding = detected.get("encoding", "utf-8") or "utf-8"
            
            row_count = 0
            headers = []
            
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                # Try to sniff dialect
                sample = f.read(1024)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    reader = csv.reader(f, dialect)
                except csv.Error:
                    reader = csv.reader(f)
                    
                for i, row in enumerate(reader):
                    if not row:
                        continue
                    if i == 0:
                        headers = row
                        metadata["headers"] = headers
                    else:
                        # Serialize row into a readable format for LLMs
                        if headers and len(headers) == len(row):
                            row_text = ", ".join(f"{headers[j]}: {row[j]}" for j in range(len(row)))
                        else:
                            row_text = ", ".join(row)
                        text_content.append(row_text)
                        row_count += 1
            
            metadata["row_count"] = row_count
            metadata["encoding"] = encoding
            
            return "\n".join(text_content), 1, metadata
        except Exception as e:
            logger.error(f"Failed to parse CSV {file_path}: {str(e)}")
            raise e
