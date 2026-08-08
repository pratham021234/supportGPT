#!/bin/bash
set -e

# Wait for PostgreSQL
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done
echo "PostgreSQL is ready."

# Wait for Redis (we can just ping it)
until redis-cli -h redis -p 6379 ping | grep -q PONG; do
  echo "Waiting for Redis to be ready..."
  sleep 2
done
echo "Redis is ready."

# Wait for Qdrant
until curl -s http://qdrant:6333/readyz | grep -q "all components are ready"; do
  echo "Waiting for Qdrant to be ready..."
  sleep 2
done
echo "Qdrant is ready."

echo "Applying database migrations..."
alembic upgrade head || {
    echo "Migration failed, falling back to graceful fail."
    exit 1
}
echo "Database migrations complete."

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
