from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    chunk_id: str = Field(description="The UUID of the chunk that supports this claim.")
    claim: str = Field(description="The specific claim or sentence in the answer that this chunk supports.")
    document_title: Optional[str] = Field(default=None, description="The title of the source document.")

class AnswerOutput(BaseModel):
    answer: str = Field(description="The generated answer to the user's query.")
    citations: List[Citation] = Field(description="A list of citations mapping claims to source chunks.")
    confidence_score: float = Field(description="A score from 0.0 to 100.0 indicating confidence in the answer's accuracy.")

class RAGState(BaseModel):
    # Inputs
    workspace_id: str
    user_id: Optional[str] = None
    query: str
    
    # Query Understanding
    language: str = "en"
    query_type: str = "GENERAL"
    keywords: List[str] = Field(default_factory=list)
    agent_routing: str = "SUPPORT"
    
    # Retrieval
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Context Assembly
    context_str: str = ""
    
    # Generation
    answer: str = ""
    citations: List[Citation] = Field(default_factory=list)
    
    # Validation & Confidence
    confidence_score: float = 0.0
    
    # Escalation
    escalate: bool = False
    
    # Logging
    latency_ms: int = 0
