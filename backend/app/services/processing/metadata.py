from datetime import datetime
from typing import Dict, Any

class MetadataService:
    @classmethod
    def generate_document_metadata(
        cls,
        file_name: str,
        source_type: str,
        workspace_id: str,
        agent_id: str = None,
        tags: list = None,
        categories: list = None,
        language: str = "unknown",
        page_count: int = 0,
        extra_meta: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Standardizes metadata payload for Documents and Chunks.
        """
        meta = {
            "document_name": file_name,
            "source_type": source_type,
            "upload_date": datetime.utcnow().isoformat(),
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "tags": tags or [],
            "categories": categories or [],
            "language": language,
            "page_count": page_count
        }
        
        if extra_meta:
            meta.update(extra_meta)
            
        return meta

metadata_service = MetadataService()
