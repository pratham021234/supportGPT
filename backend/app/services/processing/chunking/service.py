import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.knowledge_repo import document_chunk_repo, DocumentChunkInternalCreate
from app.services.processing.chunking.strategies import (
    FixedSizeChunker, SlidingWindowChunker, SectionChunker, SemanticChunker, ChunkData
)
from app.services.processing.chunking.quality import chunk_quality_service, chunk_validation_service
from app.services.processing.chunking.deduplication import chunk_deduplication_service

logger = logging.getLogger(__name__)

class ChunkingService:
    def __init__(self):
        self.strategies = {
            "FIXED": FixedSizeChunker,
            "SLIDING_WINDOW": SlidingWindowChunker,
            "SECTION": SectionChunker,
            "SEMANTIC": SemanticChunker
        }

    def select_strategy(self, file_type: str, requested_strategy: str = None) -> Any:
        if requested_strategy and requested_strategy.upper() in self.strategies:
            return self.strategies[requested_strategy.upper()]()
            
        # Smart defaults based on file type
        if file_type in ["PDF", "DOCX", "MARKDOWN", "MD"]:
            return SectionChunker()
        return SemanticChunker()

    def process_and_store(
        self, 
        db: AsyncSession, 
        workspace_id: str, 
        document_id: str, 
        text: str, 
        file_type: str, 
        base_metadata: Dict[str, Any] = None,
        strategy_name: str = None
    ) -> List[Any]:
        """
        Orchestrates the entire chunking flow.
        """
        logger.info(f"Chunking document {document_id} with strategy {strategy_name or 'AUTO'}")
        
        # 1. Strategy Selection
        chunker = self.select_strategy(file_type, strategy_name)
        
        # 2. Chunk Generation
        meta = base_metadata.copy() if base_metadata else {}
        meta.update({
            "workspace_id": workspace_id,
            "document_id": document_id,
            "file_type": file_type
        })
        raw_chunks = chunker.chunk_text(text, meta)
        
        # 3. Validation & Quality
        valid_chunks = []
        for c in raw_chunks:
            if chunk_validation_service.is_valid_chunk(c.content, c.token_count):
                c.metadata["quality_score"] = chunk_quality_service.score_chunk(c.content, c.token_count)
                valid_chunks.append(c)
                
        # 4. Deduplication
        unique_chunks = chunk_deduplication_service.filter_duplicates(valid_chunks)
        
        return unique_chunks

    async def save_chunks(self, db: AsyncSession, workspace_id: str, document_id: str, chunks: List[ChunkData]):
        """
        Deletes existing chunks for the document and inserts the new ones.
        """
        await document_chunk_repo.delete_by_document(db, document_id)
        
        for i, chunk in enumerate(chunks):
            # inject index
            chunk.metadata["chunk_index"] = i
            
            chunk_in = DocumentChunkInternalCreate(
                workspace_id=workspace_id,
                document_id=document_id,
                chunk_index=i,
                content=chunk.content,
                token_count=chunk.token_count,
                character_count=chunk.character_count,
                section=chunk.metadata.get("section"),
                page_number=chunk.metadata.get("page_number"),
                parent_heading=chunk.metadata.get("parent_heading"),
                chunk_type="TEXT",
                metadata_=chunk.metadata
            )
            await document_chunk_repo.create(db, obj_in=chunk_in)

chunking_service = ChunkingService()
