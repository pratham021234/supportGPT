import os
import logging
from typing import Dict, Any, Tuple

from app.models.knowledge import SourceType
from app.services.extractors.parsers import (
    PDFExtractor,
    DOCXExtractor,
    TXTExtractor,
    MarkdownExtractor,
    CSVExtractor,
    HTMLExtractor
)

logger = logging.getLogger(__name__)

class DocumentExtractorFactory:
    @staticmethod
    def get_extractor(source_type: str, file_path: str = None):
        """
        Returns the appropriate extractor based on source_type or file extension.
        """
        extractors = {
            SourceType.PDF: PDFExtractor(),
            SourceType.DOCX: DOCXExtractor(),
            SourceType.HTML: HTMLExtractor(),
            SourceType.WEBSITE: HTMLExtractor(),
            SourceType.TXT: TXTExtractor(),
            SourceType.MARKDOWN: MarkdownExtractor(),
            SourceType.FAQ: TXTExtractor(),
            SourceType.ARTICLE: HTMLExtractor(),
            SourceType.SPREADSHEET: CSVExtractor()
        }
        
        # Exact match
        if source_type in extractors:
            return extractors[source_type]
            
        # Extension fallback
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            ext_map = {
                ".pdf": PDFExtractor(),
                ".docx": DOCXExtractor(),
                ".doc": DOCXExtractor(),
                ".html": HTMLExtractor(),
                ".htm": HTMLExtractor(),
                ".txt": TXTExtractor(),
                ".md": MarkdownExtractor(),
                ".markdown": MarkdownExtractor(),
                ".csv": CSVExtractor()
            }
            if ext in ext_map:
                return ext_map[ext]
                
        # Default to TXT
        logger.warning(f"No specific extractor found for source_type={source_type}, file={file_path}. Defaulting to TXT.")
        return TXTExtractor()


class ExtractionService:
    def process_file(self, file_path: str, source_type: str) -> Tuple[str, int, Dict[str, Any]]:
        """
        Routes the file to the appropriate extractor based on source_type.
        """
        extractor = DocumentExtractorFactory.get_extractor(source_type, file_path)
        return extractor.extract(file_path)

extraction_service = ExtractionService()
