from typing import Dict, Any

class MetadataExtractionService:
    @staticmethod
    def extract_standard_metadata(raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes metadata extracted from various parsers into a standard schema.
        """
        if not raw_metadata:
            return {}
            
        standardized = {
            "title": raw_metadata.get("title") or raw_metadata.get("document_name") or "",
            "author": raw_metadata.get("author") or raw_metadata.get("creator") or "",
            "language": raw_metadata.get("language") or "",
            "keywords": raw_metadata.get("keywords") or "",
            "creation_date": raw_metadata.get("created") or raw_metadata.get("creationDate") or "",
            "modified_date": raw_metadata.get("modified") or raw_metadata.get("modDate") or "",
            "format": raw_metadata.get("format") or ""
        }
        
        # Merge in original for any extra stuff (pages_mapping, headers, etc.)
        for k, v in raw_metadata.items():
            if k not in standardized:
                standardized[k] = v
                
        return standardized

metadata_extractor_service = MetadataExtractionService()
