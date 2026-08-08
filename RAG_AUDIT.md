# RAG Audit Report

## 1. Existing Retrieval & Search
- **State**: Basic semantic vector search exists in `backend/app/services/vector/search_service.py` via Qdrant.
- **Deficiencies**: Lacks hybrid search (Keyword + Vector), missing metadata filtering logic for agent-specific knowledge, missing deduplication and score normalization.
- **Action**: Build `RetrievalService` with hybrid strategy and robust metadata filtering.

## 2. Existing LangGraph Scaffolding
- **State**: A basic linear `StateGraph` exists in `backend/app/services/rag/graph.py` with states defined in `state.py` and simple nodes in `nodes.py`. `rag_service.py` orchestrates it.
- **Deficiencies**: 
  - `query_node` is a hardcoded stub (`{"language": "en", "query_type": "GENERAL"}`).
  - `retrieval_node` calls basic semantic search.
  - `context_builder_node` does a simple string join without token budget management or deduplication.
  - `validation_node` uses a naive threshold check.
- **Action**: Implement robust nodes utilizing new service classes (`QueryProcessor`, `ContextAssembler`, `CitationService`, `ConfidenceEngine`, `EscalationService`).

## 3. Existing AI Generation
- **State**: Uses `ChatGoogleGenerativeAI` with Gemini 2.5 Flash and structured outputs (`AnswerOutput`). 
- **Deficiencies**: Lacks robust retry mechanisms, cost monitoring, dynamic provider abstraction, and specific hallucination mitigations beyond a basic prompt.
- **Action**: Build `AnswerGenerationService` to wrap generation with observability, retry policies, and strict citation enforcement.

## 4. Analytics & API
- **State**: Endpoints exist in `backend/app/api/v1/rag/router.py`. Database models for `QueryLog`, `AnswerLog`, `RetrievalLog`, `CitationLog`, `EscalationEvent` exist and are populated synchronously in `rag_service.py`.
- **Deficiencies**: `stream_query` in `rag_service.py` is incomplete and doesn't fully handle state reconstruction or SSE formatting for the frontend.
- **Action**: Implement full SSE support with typing experience tokens in `ResponseFormatter`.

## 5. Summary of Missing Pieces
- `QueryProcessor`: For intent detection and entity extraction.
- `RetrievalService`: For fast, tenant-safe hybrid search.
- `ContextAssembler`: For deduplication and token management.
- `AnswerGenerationService`: For robust Gemini integrations.
- `CitationService`: For source attribution mapping.
- `ConfidenceEngine`: For complex confidence calculations.
- `EscalationService`: For decision logic.
- `ResponseFormatter`: For structuring the final response.
- `EvaluationService`: For measuring framework accuracy.
