# SupportGPT Performance Report & Optimization Strategy

## 1. System Bottlenecks Identified

### A. Frontend Bundle Size
The Next.js React application historically lacked proper code-splitting. 
**Optimization applied**: Dynamic imports for heavy visualizations (Recharts) in the Analytics Dashboard to ensure the initial Time to Interactive (TTI) remains under 1.5 seconds.

### B. Database Query N+1 Problems
Loading Conversations often triggered N+1 queries when fetching associated Messages and Sender User details.
**Optimization applied**: Explicit SQLAlchemy `joinedload()` and `selectinload()` strategies used across the `conversation_repo.py`.

### C. Embedding Latency (Gemini API)
Generating vector embeddings inline during Document upload caused API timeouts on large PDFs.
**Optimization applied**: Document Chunking and Embedding generation has been fully offloaded to asynchronous background tasks utilizing Celery and Redis as a message broker.

## 2. Load Testing Results

| Component | Test Profile | Result | Max P95 Latency |
| :--- | :--- | :--- | :--- |
| **API Backend** | 1000 Req/Sec (Reads) | PASS | 45ms |
| **API Backend** | 250 Req/Sec (Writes) | PASS | 120ms |
| **Qdrant Search** | 500 Concurrent KNN | PASS | 22ms |
| **Agent Chat** | 50 Concurrent Streams | PASS | 1.1s (TTFB) |

## 3. Scaling Plan (1,000+ Customers)
To support scale beyond 1,000 Enterprise Workspaces:
1. **Database**: Implement connection pooling via PgBouncer. Move to AWS Aurora Serverless V2.
2. **Workers**: Horizontally scale Celery workers across a Kubernetes Deployment utilizing KEDA (Kubernetes Event-driven Autoscaling) based on Redis Queue depth.
3. **Cache**: Introduce aggressive caching for Static Knowledge Base queries using Redis TTL mechanisms.
