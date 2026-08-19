# Disaster Recovery Plan

## 1. Relational Database Failure (PostgreSQL)
**Scenario**: Master DB instance crashes, data corruption, or accidental deletion.
**Prevention**: Enable Point-In-Time-Recovery (PITR) on managed services (Neon/RDS). Daily automated snapshots.
**Recovery Steps**:
1. Identify the timestamp of corruption/failure.
2. Spin up a new PostgreSQL instance using the cloud provider's snapshot restore function.
3. Update `DATABASE_URL` in the environment secrets to point to the new DB instance.
4. Restart the backend services to sever old connection pools.

## 2. Vector Database Failure (Qdrant)
**Scenario**: Qdrant cluster goes offline or collection is corrupted.
**Prevention**: Enable Qdrant Cloud snapshots. Store source documents in S3 so embeddings can be regenerated if necessary.
**Recovery Steps**:
1. Restore Qdrant from the latest snapshot via the Qdrant Cloud console.
2. *If snapshot is unavailable*: Run the backend utility script `python -m app.scripts.rebuild_vectors` which will stream all source documents from S3 and re-embed them via OpenAI/Gemini APIs. Note: This will incur API costs.

## 3. Cache / PubSub Failure (Redis)
**Scenario**: Redis node fails or restarts, losing in-memory cache and websocket routing state.
**Prevention**: Use managed Redis with Multi-AZ failover (e.g., ElastiCache).
**Recovery Steps**:
1. Redis state in SupportGPT is entirely ephemeral (rate limits, active WS connections, celery queues).
2. Simply restart the backend services. Clients will automatically reconnect their websockets, and background tasks will be re-queued by the DB-backed scheduler.

## 4. File Storage Failure (AWS S3)
**Scenario**: Accidental deletion of S3 bucket or regional AWS outage.
**Prevention**: Enable S3 Versioning and Cross-Region Replication (CRR).
**Recovery Steps**:
1. If an object is deleted, restore it via S3 Versioning.
2. If a region goes down, update `AWS_REGION` and `S3_BUCKET_NAME` to the replication target bucket and restart services.
