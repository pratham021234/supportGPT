import tiktoken
from typing import List, Dict, Any

class ChunkResult:
    def __init__(self, content: str, token_count: int, metadata: Dict[str, Any]):
        self.content = content
        self.token_count = token_count
        self.metadata = metadata

class SemanticChunker:
    def __init__(self, model: str = "cl100k_base"):
        try:
            self.tokenizer = tiktoken.get_encoding(model)
        except Exception:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def chunk_text(self, text: str, base_metadata: Dict[str, Any] = None, strategy: str = "PARAGRAPH", max_tokens: int = 1000, overlap: int = 200) -> List[ChunkResult]:
        if base_metadata is None:
            base_metadata = {}
            
        if strategy.upper() == "SECTION":
            return self._chunk_by_separator(text, '\n#', max_tokens, overlap, base_metadata)
        elif strategy.upper() == "RECURSIVE":
            return self._recursive_chunk(text, max_tokens, overlap, base_metadata)
        else:
            # Default to paragraph/semantic
            return self._chunk_by_separator(text, '\n\n', max_tokens, overlap, base_metadata)

    def _recursive_chunk(self, text: str, max_tokens: int, overlap: int, base_metadata: Dict[str, Any]) -> List[ChunkResult]:
        # simplified recursive splitting by progressively smaller delimiters
        delimiters = ['\n\n', '\n', '. ', ' ']
        return self._do_recursive_chunk(text, delimiters, max_tokens, overlap, base_metadata)

    def _do_recursive_chunk(self, text: str, delimiters: List[str], max_tokens: int, overlap: int, base_metadata: Dict[str, Any]) -> List[ChunkResult]:
        if self.count_tokens(text) <= max_tokens:
            return [ChunkResult(content=text, token_count=self.count_tokens(text), metadata=base_metadata.copy())]
            
        if not delimiters:
            # Fallback to token splitting
            encoded = self.tokenizer.encode(text)
            chunks = []
            for i in range(0, len(encoded), max_tokens - overlap):
                slice_text = self.tokenizer.decode(encoded[i:i + max_tokens])
                chunks.append(ChunkResult(content=slice_text, token_count=self.count_tokens(slice_text), metadata=base_metadata.copy()))
            return chunks
            
        delimiter = delimiters[0]
        splits = text.split(delimiter)
        
        chunks = []
        current_chunk_text = ""
        
        for s in splits:
            s_with_delim = s + delimiter if s != splits[-1] else s
            if self.count_tokens(current_chunk_text + s_with_delim) > max_tokens and current_chunk_text:
                chunks.append(ChunkResult(content=current_chunk_text, token_count=self.count_tokens(current_chunk_text), metadata=base_metadata.copy()))
                # simplistic overlap (keep last segment)
                current_chunk_text = s_with_delim
            else:
                current_chunk_text += s_with_delim
                
        if current_chunk_text:
            chunks.append(ChunkResult(content=current_chunk_text, token_count=self.count_tokens(current_chunk_text), metadata=base_metadata.copy()))
            
        # Refine any chunks that are still too large
        final_chunks = []
        for c in chunks:
            if c.token_count > max_tokens:
                final_chunks.extend(self._do_recursive_chunk(c.content, delimiters[1:], max_tokens, overlap, base_metadata))
            else:
                final_chunks.append(c)
                
        return final_chunks

    def _chunk_by_separator(self, text: str, separator: str, max_tokens: int, overlap: int, base_metadata: Dict[str, Any]) -> List[ChunkResult]:
        paragraphs = text.split(separator)
        chunks = []
        current_chunk_text = ""
        
        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean: continue
            
            p_prefix = separator + p_clean if current_chunk_text and separator != '\n#' else p_clean
            if separator == '\n#': p_prefix = p_clean # keep standard for sections
            
            p_tokens = self.count_tokens(p_prefix)
            
            if p_tokens > max_tokens:
                if current_chunk_text:
                    chunks.append(ChunkResult(content=current_chunk_text, token_count=self.count_tokens(current_chunk_text), metadata=base_metadata.copy()))
                    current_chunk_text = ""
                # Split huge section
                encoded = self.tokenizer.encode(p_clean)
                for i in range(0, len(encoded), max_tokens - overlap):
                    slice_text = self.tokenizer.decode(encoded[i:i + max_tokens])
                    chunks.append(ChunkResult(content=slice_text, token_count=self.count_tokens(slice_text), metadata=base_metadata.copy()))
                continue
                
            if self.count_tokens(current_chunk_text + p_prefix) > max_tokens:
                chunks.append(ChunkResult(content=current_chunk_text, token_count=self.count_tokens(current_chunk_text), metadata=base_metadata.copy()))
                # Basic overlap
                overlap_text = current_chunk_text.split(separator)[-1] if current_chunk_text else ""
                current_chunk_text = (overlap_text + separator + p_clean).strip() if overlap_text else p_clean
            else:
                current_chunk_text += p_prefix
                
        if current_chunk_text:
            chunks.append(ChunkResult(content=current_chunk_text, token_count=self.count_tokens(current_chunk_text), metadata=base_metadata.copy()))
            
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i
            
        return chunks

semantic_chunker = SemanticChunker()
