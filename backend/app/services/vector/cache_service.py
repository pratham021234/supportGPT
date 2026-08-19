import hashlib
import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.vector_repo import embedding_record_repo

logger = logging.getLogger(__name__)

class EmbeddingCacheService:
    def compute_hash(self, text: str) -> str:
        """Compute SHA-256 hash of normalized text for caching."""
        normalized = text.strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    async def get_cached_record(self, db: AsyncSession, chunk_hash: str) -> Optional[str]:
        """Returns the chunk_id if a valid embedding record exists for this hash."""
        record = await embedding_record_repo.get_by_chunk_hash(db, chunk_hash)
        if record:
            return str(record.chunk_id)
        return None

embedding_cache_service = EmbeddingCacheService()
