import hashlib
import os

class DocumentFingerprintService:
    @staticmethod
    def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
        """Computes the SHA256 checksum of a file on disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")
            
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    @staticmethod
    def compute_content_hash(content: bytes) -> str:
        """Computes the SHA256 checksum of raw byte content."""
        sha256_hash = hashlib.sha256()
        sha256_hash.update(content)
        return sha256_hash.hexdigest()

    @staticmethod
    def compute_text_hash(text: str) -> str:
        """Computes the SHA256 checksum of a text string."""
        return DocumentFingerprintService.compute_content_hash(text.encode("utf-8"))

fingerprint_service = DocumentFingerprintService()
