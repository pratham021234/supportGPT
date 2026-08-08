# Knowledge Base Audit

## Existing Functionality
- **Models**: The database schema in `backend/app/models/` contains comprehensive models for Knowledge Base elements:
  - `KnowledgeSource`, `Document`, `DocumentPage`, `DocumentChunk`, `FAQ`, `KnowledgeTag`, `DocumentTag` in `knowledge.py`.
  - `VectorCollection`, `EmbeddingJob`, `SearchEvent` in `vector.py`.
  - `ProcessingJob`, `ExtractionResult` in `processing.py`.
- **API Shell**: Some basic router endpoints are scaffolded in `backend/app/api/v1/knowledge/`, `backend/app/api/v1/processing/`, and `backend/app/api/v1/vectors/`.
- **Integrations**: Dependencies like `qdrant-client` and `redis` are present in the `requirements.txt`.

## Missing Functionality
- **File Upload System**: API and logic for multipart file uploads, size limits, format checks, and S3/local storage.
- **Extraction Services**: Missing integrations for `PyMuPDF` (PDF), `python-docx` (DOCX), and `BeautifulSoup` (Website crawling). These dependencies are currently missing from `requirements.txt`.
- **Text Cleaning & Preprocessing**: Missing pipeline for normalizing text, removing boilerplate, and deduplicating content.
- **Chunking Engine**: No robust `ChunkService` using recursive character splitting, semantic hooks, or token awareness.
- **Metadata Generation**: Missing extraction of page numbers, headings, source types, and other contextual information.
- **Embedding System**: Need to implement `EmbeddingService` using `google-generativeai` with batching, retries, and rate limiting.
- **Vector Storage Ops**: Missing CRUD and semantic search logic for Qdrant (namespaces, workspace isolation).
- **Asynchronous Processing Pipeline**: Celery is not installed or configured. The async job status tracking (Queued -> Extracting -> Chunking -> Embedding -> Indexing) needs an orchestrator.
- **Analytics & Health endpoints**: `GET /knowledge/health` is missing.
- **Search System**: `GET /knowledge/search` is missing the underlying implementation connecting Postgres metadata and Qdrant similarities.

## Broken Flows & Required Fixes
- **Dependencies**: Need to add `celery`, `pymupdf`, `python-docx`, `beautifulsoup4`, `markdown`, and `httpx` (or `requests`) for crawling.
- **Qdrant**: Needs initialization logic (collection management).
- **Processing Jobs**: Needs worker configuration (Celery + Redis backend/broker) to handle long-running document extractions and embeddings asynchronously.
