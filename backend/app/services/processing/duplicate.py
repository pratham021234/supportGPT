import hashlib
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from sqlalchemy import select

from app.models.knowledge import Document
from app.repositories.knowledge_repo import document_repo

class DuplicateDocumentService:
    @classmethod
    async def compute_hash(cls, file: UploadFile) -> str:
        """Computes SHA-256 hash of a file's contents."""
        sha256_hash = hashlib.sha256()
        # Read file in chunks to prevent memory overload
        while chunk := await file.read(4096):
            sha256_hash.update(chunk)
        
        await file.seek(0)
        return sha256_hash.hexdigest()

    @classmethod
    async def check_duplicate(cls, db: AsyncSession, workspace_id: str, file_hash: str) -> Optional[Document]:
        """
        Checks if a document with the same hash exists in the same workspace.
        """
        query = select(Document).where(
            Document.workspace_id == workspace_id,
            Document.metadata_.op("->>")("file_hash") == file_hash
        )
        result = await db.execute(query)
        doc = result.scalars().first()
        return doc

duplicate_document_service = DuplicateDocumentService()
