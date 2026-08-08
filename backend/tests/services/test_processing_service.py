import pytest
from app.services.extractors.cleaner import TextCleaner
from app.services.extractors.lang_detect import LanguageDetector
from app.services.processing.chunker import semantic_chunker

def test_text_cleaner():
    raw = "This   is \u200B a test. \n\n\n\n It has   bad spacing."
    cleaned = TextCleaner.clean(raw)
    assert "This is a test." in cleaned
    assert "It has bad spacing." in cleaned
    assert "\u200B" not in cleaned

def test_language_detector():
    text_en = "This is a very long string of english text to ensure it detects the language correctly."
    assert LanguageDetector.detect(text_en) == "en"

def test_semantic_chunker():
    # Generate text that is > 1000 tokens
    # 'test ' is about 1 token
    text = "test " * 1500
    
    chunks = semantic_chunker.chunk_text(text, {"meta": "data"})
    
    # Since 1500 tokens is > 1000 limit, it should be split into 2 chunks
    assert len(chunks) == 2
    assert chunks[0].token_count <= 1000
    assert chunks[1].token_count <= 1000
    assert chunks[0].metadata["meta"] == "data"
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[1].metadata["chunk_index"] == 1

def test_chunker_preserves_paragraphs():
    text = "Paragraph 1\n\nParagraph 2\n\nParagraph 3"
    # set max tokens artificially low for test
    semantic_chunker.max_tokens = 3
    chunks = semantic_chunker.chunk_text(text)
    
    assert len(chunks) > 1
    # Paragraph 1 is intact
    assert "Paragraph 1" in chunks[0].content
