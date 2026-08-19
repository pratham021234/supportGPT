# Deployment Guide

SupportGPT is designed as a modular 12-factor application. It can be deployed on a single VPS via Docker Compose or scaled out using managed cloud providers.

## Recommended Cloud Stack
- **Frontend**: Vercel (or Netlify)
- **Backend**: Railway, Render, or AWS ECS
- **Database**: Neon (Serverless Postgres) or AWS RDS
- **Vector DB**: Qdrant Cloud (Managed)
- **Cache/Queue**: Upstash Redis or AWS ElastiCache
- **Object Storage**: AWS S3

## Single Server (Docker Compose)
Ideal for testing or low-volume MVPs.
1. Provision a Linux VPS (Ubuntu 22.04 LTS).
2. Install Docker and Docker Compose.
3. Clone the repository: `git clone https://github.com/your-org/supportgpt`
4. Copy `.env.example` to `.env` and configure your API keys. Ensure `DATABASE_URL` matches the internal compose network (e.g. `postgresql+asyncpg://postgres:password@postgres:5432/supportgpt`).
5. Run: `docker compose up -d`
6. Reverse proxy `localhost:3000` (frontend) and `localhost:8000` (backend) using Nginx/Caddy.

## Managed Cloud Deployment

### 1. Database Provisioning
- Create a Neon DB project. Note the connection string.
- Create a Qdrant Cloud cluster. Note the URL and API Key.
- Create an Upstash Redis database. Note the connection string.

### 2. Backend (Railway / Render)
- Connect your GitHub repo to Railway.
- Change the root directory to `/backend` or use the `Dockerfile.backend`.
- Add all Environment Variables from your `.env`.
- Deploy. Note the public URL (e.g. `https://api.supportgpt.com`).

### 3. Frontend (Vercel)
- Connect your GitHub repo to Vercel.
- Set the Build Command to `npm run build` and Output Directory to `.next`.
- Add Environment Variables: `NEXT_PUBLIC_API_URL=https://api.supportgpt.com`.
- Deploy.

## CI/CD
The repository includes a GitHub Action `.github/workflows/main.yml`.
This pipeline automatically:
1. Runs Python `flake8` linting.
2. Runs the `pytest` test suite against an in-memory SQLite DB.
3. Scans for security vulnerabilities using Trivy.
4. Builds the Docker images and pushes them to GitHub Container Registry (GHCR) upon a successful merge to `main`.
