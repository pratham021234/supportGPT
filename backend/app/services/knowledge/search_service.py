from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.knowledge import Document, DocumentStatus, KnowledgeTag

class DocumentSearchService:
    @staticmethod
    async def search_documents(
        db: AsyncSession,
        workspace_id: str,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
        source_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        
        stmt = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.is_current_version == True,
            Document.status != DocumentStatus.DELETED
        ).options(selectinload(Document.tags))

        if query:
            stmt = stmt.where(
                or_(
                    Document.title.ilike(f"%{query}%"),
                    Document.original_filename.ilike(f"%{query}%"),
                    Document.file_name.ilike(f"%{query}%")
                )
            )

        if status:
            stmt = stmt.where(Document.status.in_(status))

        if source_id:
            stmt = stmt.where(Document.source_id == source_id)

        if start_date:
            stmt = stmt.where(Document.created_at >= start_date)

        if end_date:
            stmt = stmt.where(Document.created_at <= end_date)
            
        if tags and len(tags) > 0:
            stmt = stmt.join(Document.tags).where(KnowledgeTag.name.in_(tags))

        stmt = stmt.order_by(desc(Document.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        # Using unique() is necessary because of the join with tags and options load
        return list(result.scalars().unique().all())

document_search_service = DocumentSearchService()
