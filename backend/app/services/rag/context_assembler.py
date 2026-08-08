import logging
from typing import List, Dict, Any
import tiktoken

logger = logging.getLogger(__name__)

class ContextAssembler:
    def __init__(self, max_tokens: int = 6000):
        self.max_tokens = max_tokens
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None
            
    def _count_tokens(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        # Fallback approximation (4 chars ~= 1 token)
        return len(text) // 4

    def assemble(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Assembles chunks into a single context string.
        Removes duplicates, enforces a strict token budget.
        """
        if not retrieved_chunks:
            return "No relevant documents found in the knowledge base."
            
        seen_chunks = set()
        context_parts = []
        current_tokens = 0
        
        for hit in retrieved_chunks:
            payload = hit.get("payload", {})
            chunk_id = payload.get("chunk_id", hit.get("id"))
            
            # Deduplicate exact chunk IDs
            if chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk_id)
            
            doc_title = payload.get("document_title", "Unknown Document")
            content = payload.get("content", "").strip()
            if not content:
                continue
                
            chunk_str = (
                f"--- SOURCE ID: {chunk_id} ---\n"
                f"DOCUMENT: {doc_title}\n"
                f"CONTENT:\n{content}\n"
            )
            
            tokens = self._count_tokens(chunk_str)
            if current_tokens + tokens > self.max_tokens:
                logger.warning(f"Context budget exceeded ({current_tokens + tokens} > {self.max_tokens}). Truncating.")
                break
                
            context_parts.append(chunk_str)
            current_tokens += tokens
            
        if not context_parts:
            return "No relevant documents found in the knowledge base."
            
        assembled = "\n".join(context_parts)
        logger.info(f"Assembled context with {len(context_parts)} chunks (~{current_tokens} tokens)")
        return assembled

context_assembler = ContextAssembler()
