import re
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from app.services.processing.chunking.tokenization import token_counter_service

class ChunkData:
    def __init__(self, content: str, token_count: int, character_count: int, metadata: Dict[str, Any]):
        self.content = content
        self.token_count = token_count
        self.character_count = character_count
        self.metadata = metadata

class BaseChunker(ABC):
    @abstractmethod
    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkData]:
        pass

class FixedSizeChunker(BaseChunker):
    """
    Chunks text strictly by token size without overlap (simple split).
    """
    def __init__(self, chunk_size: int = 500):
        self.chunk_size = chunk_size

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkData]:
        if base_metadata is None: base_metadata = {}
        if not text: return []

        encoded = token_counter_service.encode(text)
        chunks = []
        for i in range(0, len(encoded), self.chunk_size):
            slice_text = token_counter_service.decode(encoded[i:i + self.chunk_size])
            chunks.append(ChunkData(
                content=slice_text,
                token_count=token_counter_service.count_tokens(slice_text),
                character_count=len(slice_text),
                metadata=base_metadata.copy()
            ))
        return chunks

class SlidingWindowChunker(BaseChunker):
    """
    Chunks text using a sliding window for token overlap to preserve context.
    """
    def __init__(self, chunk_size: int = 800, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkData]:
        if base_metadata is None: base_metadata = {}
        if not text: return []

        encoded = token_counter_service.encode(text)
        chunks = []
        step = max(1, self.chunk_size - self.overlap)
        
        for i in range(0, len(encoded), step):
            slice_text = token_counter_service.decode(encoded[i:i + self.chunk_size])
            chunks.append(ChunkData(
                content=slice_text,
                token_count=token_counter_service.count_tokens(slice_text),
                character_count=len(slice_text),
                metadata=base_metadata.copy()
            ))
            if i + self.chunk_size >= len(encoded):
                break
        return chunks

class SectionChunker(BaseChunker):
    """
    Chunks text based on markdown/heading sections, falling back to recursive length splitting if a section is too long.
    """
    def __init__(self, max_tokens: int = 1000, overlap: int = 200):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self._fallback_chunker = SlidingWindowChunker(chunk_size=max_tokens, overlap=overlap)

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkData]:
        if base_metadata is None: base_metadata = {}
        if not text: return []

        # Find Markdown style headings or standard document breaks
        sections = re.split(r'(?=\n#{1,6}\s)', text)
        chunks = []
        current_chunk = ""
        current_heading = base_metadata.get("parent_heading", "")

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Check if this section starts with a heading
            match = re.match(r'^(#{1,6})\s+(.+?)(?:\n|$)', section)
            if match:
                current_heading = match.group(2).strip()

            tokens = token_counter_service.count_tokens(section)
            
            # If the section alone is too big, chunk it down with fallback
            if tokens > self.max_tokens:
                # Flush current
                if current_chunk:
                    chunks.append(self._make_chunk(current_chunk, base_metadata, current_heading))
                    current_chunk = ""
                
                # Apply sliding window on this giant section
                sub_chunks = self._fallback_chunker.chunk_text(section, base_metadata)
                for sc in sub_chunks:
                    sc.metadata["parent_heading"] = current_heading
                    chunks.append(sc)
                continue

            # If adding this section exceeds max tokens, flush current
            if token_counter_service.count_tokens(current_chunk + "\n\n" + section) > self.max_tokens:
                chunks.append(self._make_chunk(current_chunk, base_metadata, current_heading))
                current_chunk = section
            else:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section

        if current_chunk:
            chunks.append(self._make_chunk(current_chunk, base_metadata, current_heading))

        return chunks

    def _make_chunk(self, content: str, meta: dict, heading: str) -> ChunkData:
        m = meta.copy()
        if heading:
            m["parent_heading"] = heading
        return ChunkData(
            content=content,
            token_count=token_counter_service.count_tokens(content),
            character_count=len(content),
            metadata=m
        )

class SemanticChunker(BaseChunker):
    """
    Chunks text based on semantic boundaries (paragraphs, sentences).
    """
    def __init__(self, max_tokens: int = 1000, overlap: int = 200):
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.delimiters = ['\n\n', '\n', '. ', ' ']

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkData]:
        if base_metadata is None: base_metadata = {}
        if not text: return []
        return self._recursive_split(text, self.delimiters, base_metadata)

    def _recursive_split(self, text: str, delimiters: List[str], base_metadata: Dict[str, Any]) -> List[ChunkData]:
        token_count = token_counter_service.count_tokens(text)
        if token_count <= self.max_tokens:
            return [ChunkData(content=text, token_count=token_count, character_count=len(text), metadata=base_metadata.copy())]
            
        if not delimiters:
            # Fallback to token splitter
            sw_chunker = SlidingWindowChunker(chunk_size=self.max_tokens, overlap=self.overlap)
            return sw_chunker.chunk_text(text, base_metadata)
            
        delimiter = delimiters[0]
        splits = text.split(delimiter)
        
        chunks = []
        current_chunk_text = ""
        
        for i, s in enumerate(splits):
            s_with_delim = s + delimiter if i < len(splits) - 1 else s
            if not s_with_delim.strip():
                continue

            if token_counter_service.count_tokens(current_chunk_text + s_with_delim) > self.max_tokens and current_chunk_text:
                chunks.append(ChunkData(
                    content=current_chunk_text.strip(), 
                    token_count=token_counter_service.count_tokens(current_chunk_text.strip()), 
                    character_count=len(current_chunk_text.strip()), 
                    metadata=base_metadata.copy()
                ))
                # Simple semantic overlap: keep the last sentence/segment
                overlap_text = current_chunk_text.split(delimiter)[-1] if current_chunk_text else ""
                current_chunk_text = (overlap_text + delimiter + s_with_delim) if overlap_text else s_with_delim
            else:
                current_chunk_text += s_with_delim
                
        if current_chunk_text.strip():
            chunks.append(ChunkData(
                content=current_chunk_text.strip(), 
                token_count=token_counter_service.count_tokens(current_chunk_text.strip()), 
                character_count=len(current_chunk_text.strip()), 
                metadata=base_metadata.copy()
            ))
            
        # Recursive refinement if still too large
        final_chunks = []
        for c in chunks:
            if c.token_count > self.max_tokens:
                final_chunks.extend(self._recursive_split(c.content, delimiters[1:], base_metadata))
            else:
                final_chunks.append(c)
                
        return final_chunks
