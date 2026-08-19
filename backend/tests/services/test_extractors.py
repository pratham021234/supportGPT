import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from app.services.extractors.engine import DocumentExtractorFactory
from app.services.extractors.parsers.txt import TXTExtractor
from app.services.extractors.parsers.csv_parser import CSVExtractor
from app.services.extractors.parsers.html_parser import HTMLExtractor
from app.services.extractors.parsers.markdown_parser import MarkdownExtractor
from app.services.extractors.metadata import metadata_extractor_service

def test_txt_extractor():
    extractor = TXTExtractor()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
        f.write("Hello World")
        temp_path = f.name
        
    try:
        text, pages, meta = extractor.extract(temp_path)
        assert text == "Hello World"
        assert pages == 1
        assert "utf-8" in meta["encoding"].lower() or "ascii" in meta["encoding"].lower()
    finally:
        os.remove(temp_path)

def test_csv_extractor():
    extractor = CSVExtractor()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
        f.write("name,age\nAlice,30\nBob,25")
        temp_path = f.name
        
    try:
        text, pages, meta = extractor.extract(temp_path)
        assert "name: Alice, age: 30" in text
        assert "name: Bob, age: 25" in text
        assert meta["row_count"] == 2
    finally:
        os.remove(temp_path)

def test_markdown_extractor():
    extractor = MarkdownExtractor()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
        f.write("# Header\n\nSome text\n\n- Item 1\n- Item 2\n\n```python\nprint('code')\n```")
        temp_path = f.name
        
    try:
        text, pages, meta = extractor.extract(temp_path)
        assert "# Header" in text
        assert meta["headings_count"] == 1
        assert meta["lists_count"] == 2
        assert meta["code_blocks_count"] == 1
    finally:
        os.remove(temp_path)

def test_html_extractor():
    extractor = HTMLExtractor()
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
        f.write("<html><head><title>Test HTML</title><script>alert('bad');</script></head><body><h1>Main Title</h1><p>Content goes here.</p></body></html>")
        temp_path = f.name
        
    try:
        text, pages, meta = extractor.extract(temp_path)
        assert "Main Title" in text
        assert "Content goes here." in text
        assert "alert('bad');" not in text
        assert meta["title"] == "Test HTML"
    finally:
        os.remove(temp_path)

def test_metadata_extraction():
    raw_meta = {
        "document_name": "Test File",
        "author": "Alice",
        "keywords": "test, doc",
        "unknown_field": "preserved"
    }
    std = metadata_extractor_service.extract_standard_metadata(raw_meta)
    
    assert std["title"] == "Test File"
    assert std["author"] == "Alice"
    assert std["keywords"] == "test, doc"
    assert std["unknown_field"] == "preserved"
