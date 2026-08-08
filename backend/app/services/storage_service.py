import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import aiofiles

class StorageService:
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, workspace_id: str, document_id: str) -> str:
        """
        Saves an uploaded file locally.
        Simulates S3 key generation like: {workspace_id}/{document_id}/{filename}
        """
        if not file.filename:
            file.filename = "unnamed_file"

        # Sanitize filename (basic)
        safe_filename = "".join([c for c in file.filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_', '-')]).rstrip()
        
        # Create directory for the document
        doc_dir = self.upload_dir / workspace_id / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        file_path = doc_dir / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024):  # read in 1MB chunks
                await out_file.write(content)
                
        return str(file_path)

    async def delete_file(self, storage_path: str) -> bool:
        """
        Deletes a file given its storage path.
        """
        file_path = Path(storage_path)
        if file_path.exists() and file_path.is_file():
            # In a real S3 implementation, this would be an API call
            os.remove(file_path)
            # Also try to clean up the empty directory
            try:
                os.rmdir(file_path.parent)
            except OSError:
                pass # Directory not empty
            return True
        return False

storage_service = StorageService()
