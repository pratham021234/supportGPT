import tiktoken
from typing import List, Dict, Any

class ChunkResult:
    def __init__(self, content: str, token_count: int, metadata: Dict[str, Any]):
        self.content = content
        self.token_count = token_count
        self.metadata = metadata

class SemanticChunker:
    def __init__(self, max_tokens: int = 1000, overlap: int = 200, model: str = "cl100k_base"):
        self.max_tokens = max_tokens
        self.overlap = overlap
        try:
            self.tokenizer = tiktoken.get_encoding(model)
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[ChunkResult]:
        """
        Splits text into token-aware chunks with overlap.
        Uses a naive paragraph/newline boundary approach first, falling back to strict token splitting if needed.
        """
        if base_metadata is None:
            base_metadata = {}
            
        chunks = []
        
        # 1. Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        current_chunk_text = ""
        current_chunk_tokens = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            p_tokens = self.count_tokens(p)
            
            # If a single paragraph is too big, we split it forcefully by token
            if p_tokens > self.max_tokens:
                # Flush current
                if current_chunk_text:
                    chunks.append(ChunkResult(
                        content=current_chunk_text,
                        token_count=current_chunk_tokens,
                        metadata=base_metadata.copy()
                    ))
                    current_chunk_text = ""
                    current_chunk_tokens = 0
                
                # Split large paragraph
                encoded_p = self.tokenizer.encode(p)
                for i in range(0, len(encoded_p), self.max_tokens - self.overlap):
                    slice_encoded = encoded_p[i:i + self.max_tokens]
                    slice_text = self.tokenizer.decode(slice_encoded)
                    chunks.append(ChunkResult(
                        content=slice_text,
                        token_count=len(slice_encoded),
                        metadata=base_metadata.copy()
                    ))
                continue
                
            # If adding this paragraph exceeds limit, flush current chunk
            if current_chunk_tokens + p_tokens > self.max_tokens:
                chunks.append(ChunkResult(
                    content=current_chunk_text,
                    token_count=current_chunk_tokens,
                    metadata=base_metadata.copy()
                ))
                
                # Overlap logic: keep the last paragraph of the previous chunk if possible
                overlap_text = current_chunk_text.split('\n\n')[-1] if current_chunk_text else ""
                current_chunk_text = overlap_text + "\n\n" + p if overlap_text else p
                current_chunk_tokens = self.count_tokens(current_chunk_text)
            else:
                current_chunk_text = current_chunk_text + "\n\n" + p if current_chunk_text else p
                current_chunk_tokens = self.count_tokens(current_chunk_text)
                
        if current_chunk_text:
            chunks.append(ChunkResult(
                content=current_chunk_text,
                token_count=current_chunk_tokens,
                metadata=base_metadata.copy()
            ))
            
        # Add chunk index to metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i
            
        return chunks

semantic_chunker = SemanticChunker()
