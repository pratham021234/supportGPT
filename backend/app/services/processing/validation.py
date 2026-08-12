import os
from typing import Tuple, Dict, Any
from fastapi import UploadFile
from app.core.exceptions import BadRequestException

class FileValidationService:
    ALLOWED_EXTENSIONS = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".markdown": "text/markdown",
        ".csv": "text/csv"
    }
    
    MAX_FILE_SIZE_MB = 50
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    @classmethod
    async def validate(cls, file: UploadFile) -> Tuple[bool, Dict[str, Any]]:
        """
        Validates a file upload based on extension, mime type, size, and corruption.
        Raises BadRequestException on failure to align with strict validation goals.
        """
        # 1. Empty Check
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        
        if size == 0:
            raise BadRequestException("File is empty.")
            
        if size > cls.MAX_FILE_SIZE_BYTES:
            raise BadRequestException(f"File exceeds maximum allowed size of {cls.MAX_FILE_SIZE_MB}MB.")
            
        # 2. Extension Check
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise BadRequestException(f"Unsupported file extension: {ext}. Allowed: {list(cls.ALLOWED_EXTENSIONS.keys())}")
            
        # 3. Mime Type Validation
        expected_mime = cls.ALLOWED_EXTENSIONS[ext]
        content_type = file.content_type
        if content_type and content_type != "application/octet-stream" and expected_mime != content_type:
            # Fallback check, sometimes browsers send wrong mime types for MD or CSV
            if ext not in [".md", ".markdown", ".csv", ".txt"]:
                raise BadRequestException(f"Mime type mismatch. Expected {expected_mime}, got {content_type}")
                
        # 4. Corruption Check (Basic)
        # Attempt to read a small chunk to ensure it's readable
        try:
            chunk = await file.read(1024)
            if not chunk:
                 raise BadRequestException("File appears to be corrupted or unreadable.")
            await file.seek(0)
        except Exception as e:
            raise BadRequestException(f"File read error: {str(e)}")
            
        return True, {
            "size": size,
            "extension": ext,
            "mime_type": content_type or expected_mime
        }

file_validation_service = FileValidationService()
