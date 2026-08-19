# SupportGPT 🚀

SupportGPT is an open-source, enterprise-grade AI customer support platform. It combines a state-of-the-art RAG engine, conversational AI agents, and a robust ticketing/automation system to resolve customer queries instantly and autonomously.

## Features
- **Multi-Agent Architecture**: Create specialized AI agents mapped to specific knowledge domains.
- **RAG Knowledge Base**: Upload PDFs, DOCX, TXT, or crawl websites to construct the vector knowledge graph.
- **Conversation Engine**: Real-time websocket-powered conversational UI.
- **Ticketing & Escalation**: AI automatically escalates low-confidence interactions to human agents via trackable support tickets.
- **Workflow Automation**: IF-THEN triggers (e.g. `If confidence < 0.6 -> Escalate`).
- **Billing & Multi-tenant**: Native Stripe integration mapped to hierarchical Workspaces.

## Tech Stack
- **Frontend**: Next.js 14 (App Router), TailwindCSS, Shadcn/UI, Zustand, React Query.
- **Backend**: FastAPI, SQLAlchemy (Async), PostgreSQL, APScheduler.
- **AI/Vector**: Gemini 1.5, OpenAI embeddings, Qdrant Vector DB.
- **Infrastructure**: Docker, Redis (PubSub/Caching).

## Quickstart

1. Copy `.env.example` to `.env` and fill in your keys (Gemini, Stripe, Postgres).
2. Run `docker compose up --build -d`.
3. The API will be available at `http://localhost:8000`
4. The Dashboard will be available at `http://localhost:3000`

See `DEPLOYMENT_GUIDE.md` for production deployment instructions.
