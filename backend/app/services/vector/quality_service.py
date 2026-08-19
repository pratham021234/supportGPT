import logging
from typing import Dict

logger = logging.getLogger(__name__)

class EmbeddingQualityService:
    """Tracks latency, success rates, and errors for embedding providers."""
    
    def __init__(self):
        # In memory tracker for the current worker instance
        self.stats = {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "total_latency_ms": 0,
            "provider_stats": {}
        }
        
    def record_call(self, provider: str, latency_ms: int, success: bool):
        self.stats["total_calls"] += 1
        self.stats["total_latency_ms"] += latency_ms
        
        if success:
            self.stats["success_calls"] += 1
        else:
            self.stats["failed_calls"] += 1
            
        if provider not in self.stats["provider_stats"]:
            self.stats["provider_stats"][provider] = {"success": 0, "failed": 0, "latency": 0}
            
        self.stats["provider_stats"][provider]["latency"] += latency_ms
        if success:
            self.stats["provider_stats"][provider]["success"] += 1
        else:
            self.stats["provider_stats"][provider]["failed"] += 1
            
    def get_analytics(self) -> Dict:
        avg_latency = 0
        if self.stats["total_calls"] > 0:
            avg_latency = self.stats["total_latency_ms"] / self.stats["total_calls"]
            
        return {
            "total_calls": self.stats["total_calls"],
            "success_calls": self.stats["success_calls"],
            "failed_calls": self.stats["failed_calls"],
            "average_latency_ms": round(avg_latency, 2),
            "provider_stats": self.stats["provider_stats"]
        }

embedding_quality_service = EmbeddingQualityService()
