import pytest
import os
import uuid
from typing import Dict, Any
from app.services.processing.chunker import SemanticChunker
from app.services.extractors.cleaner import TextCleaner
from app.services.processing.metadata import metadata_service
from app.services.processing.validation import file_validation_service
from app.services.processing.versioning import document_versioning_service
from app.services.processing.duplicate import duplicate_document_service

@pytest.mark.asyncio
async def test_text_cleaner():
    dirty_text = "Hello\xa0World \u200B  Multiple   Spaces\n\n\n\nParagraph 2.<script>alert(1)</script>"
    clean_text = TextCleaner.clean(dirty_text)
    assert "World" in clean_text
    assert "Multiple Spaces" in clean_text
    assert "alert" not in clean_text
    assert "\n\n\n" not in clean_text

def test_semantic_chunker():
    chunker = SemanticChunker(model="cl100k_base")
    # Test Paragraph
    text = "Para 1.\n\nPara 2.\n\nPara 3."
    res = chunker.chunk_text(text, strategy="PARAGRAPH", max_tokens=100)
    assert len(res) == 1
    assert "Para 1." in res[0].content
    
    # Test Recursive
    large_text = "Word " * 1200
    res = chunker.chunk_text(large_text, strategy="RECURSIVE", max_tokens=1000, overlap=100)
    assert len(res) > 1
    assert res[0].token_count <= 1000

    # Test Section
    section_text = "# Section 1\nContent A.\n\n# Section 2\nContent B."
    res = chunker.chunk_text(section_text, strategy="SECTION", max_tokens=1000)
    assert len(res) == 1
    assert "Section 1" in res[0].content

def test_metadata_service():
    meta = metadata_service.generate_document_metadata(
        file_name="test.pdf",
        source_type="PDF",
        workspace_id="test_ws",
        extra_meta={"hash": "abc"}
    )
    assert meta["document_name"] == "test.pdf"
    assert meta["source_type"] == "PDF"
    assert meta["workspace_id"] == "test_ws"
    assert meta["hash"] == "abc"
    assert "upload_date" in meta

@pytest.mark.asyncio
async def test_duplicate_document_service():
    # Mocking upload file
    class MockFile:
        async def read(self, size):
            if hasattr(self, 'read_done'):
                return b""
            self.read_done = True
            return b"test content"
        async def seek(self, pos):
            pass
            
    hash_val = await duplicate_document_service.compute_hash(MockFile())
    assert len(hash_val) == 64  # sha256 hex digest length

@pytest.mark.asyncio
async def test_file_validation_service():
    class MockFile:
        def __init__(self, filename, content_type, size):
            self.filename = filename
            self.content_type = content_type
            class F:
                def seek(self, *args): pass
                def tell(self): return size
            self.file = F()
            
        async def read(self, size): return b"ok"
        async def seek(self, pos): pass

    valid_file = MockFile("test.pdf", "application/pdf", 1024)
    res, meta = await file_validation_service.validate(valid_file)
    assert res is True
    assert meta["extension"] == ".pdf"

@pytest.mark.asyncio
async def test_versioning_service():
    class MockResult:
        def __init__(self, val): self.val = val
        def scalars(self): 
            class S: 
                def first(self): return self.val
            return S()
            
    class MockDoc:
        def __init__(self):
            self.metadata_ = {"version": 2}
            
    class MockDB:
        async def execute(self, query):
            return MockResult(MockDoc())
            
    db = MockDB()
    version = await document_versioning_service.get_next_version(db, "ws1", "file.pdf")
    assert version == 3

from app.services.extractors.engine import TXTExtractor, MarkdownExtractor
import tempfile

def test_txt_extractor():
    extractor = TXTExtractor()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
        f.write("Hello Text")
        path = f.name
        
    try:
        content, pages, meta = extractor.extract(path)
        assert content == "Hello Text"
        assert meta["encoding"] == "utf-8"
        assert pages == 1
    finally:
        os.remove(path)

def test_markdown_extractor():
    extractor = MarkdownExtractor()
    md_content = "# Title\n\n```python\nprint(1)\n```"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as f:
        f.write(md_content)
        path = f.name
        
    try:
        content, pages, meta = extractor.extract(path)
        assert content == md_content
        assert meta["headings_count"] == 1
        assert meta["code_blocks_count"] == 1
    finally:
        os.remove(path)
