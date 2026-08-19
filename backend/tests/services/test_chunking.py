import pytest
from app.services.processing.chunking.tokenization import token_counter_service
from app.services.processing.chunking.strategies import (
    FixedSizeChunker, SlidingWindowChunker, SectionChunker, SemanticChunker
)
from app.services.processing.chunking.quality import chunk_quality_service, chunk_validation_service
from app.services.processing.chunking.deduplication import chunk_deduplication_service

def test_token_counter():
    text = "Hello world! This is a test."
    count = token_counter_service.count_tokens(text)
    assert count > 0
    assert count < 15
    encoded = token_counter_service.encode(text)
    decoded = token_counter_service.decode(encoded)
    assert decoded == text

def test_fixed_size_chunker():
    chunker = FixedSizeChunker(chunk_size=10)
    text = "Word " * 25 # roughly 26 tokens
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) == 3
    assert chunks[0].token_count == 10
    assert chunks[1].token_count == 10
    assert chunks[2].token_count == 6

def test_sliding_window_chunker():
    chunker = SlidingWindowChunker(chunk_size=10, overlap=5)
    text = "Word " * 20 # 21 tokens
    chunks = chunker.chunk_text(text)
    
    # sequence of tokens
    # c1: 0-10
    # c2: 5-15
    # c3: 10-20
    # c4: 15-21
    assert len(chunks) == 4
    assert chunks[0].token_count == 10

def test_section_chunker():
    chunker = SectionChunker(max_tokens=5)
    text = "# Header 1\nThis is the first section.\n## Header 2\nThis is the second section."
    chunks = chunker.chunk_text(text)
    assert len(chunks) >= 2

def test_semantic_chunker():
    chunker = SemanticChunker(max_tokens=4)
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunker.chunk_text(text)
    # Should split near sentence boundaries
    assert len(chunks) > 1

def test_chunk_quality():
    score = chunk_quality_service.score_chunk("Hello world! This is a good chunk.", 10)
    assert score > 0.0

def test_chunk_validation():
    assert chunk_validation_service.is_valid_chunk("Hello world", 5) == False # < 10 tokens
    assert chunk_validation_service.is_valid_chunk("    ", 15) == False
    assert chunk_validation_service.is_valid_chunk("Valid chunk with enough words.", 15) == True

def test_chunk_deduplication():
    class DummyChunk:
        def __init__(self, content):
            self.content = content

    chunks = [
        DummyChunk("Hello world"),
        DummyChunk("hello world"),
        DummyChunk("hello  world "),
        DummyChunk("Different chunk")
    ]
    
    unique = chunk_deduplication_service.filter_duplicates(chunks)
    assert len(unique) == 2
    assert unique[0].content == "Hello world"
    assert unique[1].content == "Different chunk"
