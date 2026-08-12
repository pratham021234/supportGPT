from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.knowledge import Document

class DocumentVersioningService:
    @classmethod
    async def get_next_version(
        cls, db: AsyncSession, workspace_id: str, file_name: str
    ) -> int:
        """
        Calculates the next version number for a document based on its file_name.
        """
        query = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.file_name == file_name
        ).order_by(desc(Document.metadata_.op("->>")("version")))
        
        result = await db.execute(query)
        latest_doc = result.scalars().first()
        
        if not latest_doc or not latest_doc.metadata_ or "version" not in latest_doc.metadata_:
            return 1
            
        return int(latest_doc.metadata_.get("version", 0)) + 1
        
document_versioning_service = DocumentVersioningService()
