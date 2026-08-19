import logging
import re
from typing import Dict, Any, Tuple

from app.services.extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

class MarkdownExtractor(BaseExtractor):
    def extract(self, file_path: str) -> Tuple[str, int, Dict[str, Any]]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            # Basic structural extraction
            lines = content.split('\n')
            headings = [line for line in lines if re.match(r'^#{1,6}\s', line)]
            code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
            tables = len(re.findall(r'\|.*\|', content))
            lists = len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE))
            
            metadata = {
                "is_markdown": True,
                "headings_count": len(headings),
                "code_blocks_count": code_blocks,
                "tables_count": tables,
                "lists_count": lists,
            }
            
            # Markdown text is already well-structured for LLMs, so we return it largely as is.
            # Could use markdown-it-py to extract purely text, but raw markdown is often better for code blocks and structure.
            
            return content, 1, metadata
        except Exception as e:
            logger.error(f"Failed to parse Markdown {file_path}: {str(e)}")
            raise e
