# SupportGPT Infrastructure Setup (Phase 1)

This document provides instructions on how to set up, run, and manage the infrastructure for SupportGPT AI. The project uses Docker Compose to orchestrate the Next.js frontend, FastAPI backend, PostgreSQL, Redis, and Qdrant.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed.
- [Docker Compose](https://docs.docker.com/compose/install/) (V2 recommended) installed.

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in any required variables. Most defaults will work out-of-the-box for local development, but you will need to provide actual values for API keys such as:
   - `GEMINI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `RESEND_API_KEY`

## Setup & Running

To build the images and start all services, simply run:

```bash
docker compose up --build
```

This command will:
1. Start the PostgreSQL database (`postgres`), Redis (`redis`), and Qdrant (`qdrant`) services.
2. Build the backend image, wait for the databases to become healthy, automatically run `alembic upgrade head` to apply database migrations, and then start the FastAPI server on port `8000`.
3. Build the frontend Next.js application image and start it on port `3000`.

### Accessing the Services

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) (Assuming standard FastAPI docs)
- **Backend Health Check:** [http://localhost:8000/health](http://localhost:8000/health) or [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

## Infrastructure Components

- **Frontend**: Next.js 16 app built as a multi-stage Docker image, running on node:22.
- **Backend**: FastAPI app running on Python 3.12 with uvicorn. It checks dependency health before running migrations via `start.sh`.
- **Database (PostgreSQL 16)**: Holds all relational data. Data is persisted in the `postgres_data` volume.
- **Redis 7**: Used for caching and rate limiting. Data is persisted in the `redis_data` volume.
- **Qdrant**: Used as the vector database for RAG operations. Data is persisted in the `qdrant_data` volume on port 6333.
- **Network**: All containers communicate internally over `supportgpt-network`.

## Useful Commands

- **Stop all services gracefully:**
  ```bash
  docker compose down
  ```

- **Stop services and remove persistent volumes (Wipe all data):**
  ```bash
  docker compose down -v
  ```

- **View logs for all services:**
  ```bash
  docker compose logs -f
  ```

- **View logs for a specific service (e.g., backend):**
  ```bash
  docker compose logs -f backend
  ```

## Troubleshooting

- **Backend fails to connect to the database/redis/qdrant on startup:** The backend container (`start.sh`) uses `pg_isready`, `redis-cli`, and `curl` to wait until infrastructure dependencies are fully ready. If it fails, check the logs of the specific failing database service.
- **Missing python packages during build:** If `Dockerfile.backend` fails during `pip install`, ensure the `backend/requirements.txt` is up-to-date with your backend imports.
- **Frontend changes not reflecting:** The frontend container currently uses a production multi-stage build. You will need to rebuild the image (`docker compose up --build frontend`) for changes to apply. For active development, consider running the frontend natively using `npm run dev`.

## Production Workflow

For production deployment:
1. Ensure all secrets in `.env` are secure and not default values.
2. Ensure you have proper proxy configuration (e.g., Nginx, Traefik) if deploying to a VM.
3. Depending on traffic, tweak the `docker-compose.yml` to specify resource limits and restart policies appropriate for your cloud environment.
