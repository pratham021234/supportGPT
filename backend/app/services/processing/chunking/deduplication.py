import hashlib

class ChunkDeduplicationService:
    @staticmethod
    def generate_hash(content: str) -> str:
        """
        Generate a SHA-256 hash of the normalized chunk content.
        """
        # Normalize whitespace and lowercase to handle slight variations
        normalized = " ".join(content.lower().split())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    @staticmethod
    def filter_duplicates(chunks: list) -> list:
        """
        Filters out duplicate chunks within a batch.
        """
        seen_hashes = set()
        unique_chunks = []
        
        for chunk in chunks:
            # Assuming chunk is an object with a 'content' attribute or dict
            content = chunk.content if hasattr(chunk, 'content') else chunk.get('content', '')
            chunk_hash = ChunkDeduplicationService.generate_hash(content)
            
            if chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                unique_chunks.append(chunk)
                
        return unique_chunks

chunk_deduplication_service = ChunkDeduplicationService()
