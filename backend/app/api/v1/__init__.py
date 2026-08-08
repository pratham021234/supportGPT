from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.auth.oauth import router as oauth_router
from app.api.v1.workspaces.routes import router as workspaces_router
from app.api.v1.team.routes import router as team_router
from app.api.v1.knowledge.router import knowledge_router
from app.api.v1.processing.router import router as processing_router
from app.api.v1.vectors.router import router as vectors_router
from app.api.v1.rag.router import router as rag_router
from app.api.v1.agents.router import router as agents_router
from app.api.v1.conversations.router import router as conversations_router
from app.api.v1.tickets.router import router as tickets_router
from app.api.v1.handoff.router import router as handoff_router
from app.api.v1.analytics.router import router as analytics_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.widget.router import router as widget_router
from app.api.v1.billing.router import router as billing_router
from app.api.v1.automation.router import router as automation_router
from app.api.v1.security.router import router as security_router
from app.api.v1.integrations.router import router as integrations_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(oauth_router)
api_router.include_router(workspaces_router)
api_router.include_router(team_router)
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["Knowledge Base"])
api_router.include_router(processing_router, prefix="/processing", tags=["Document Processing"])
api_router.include_router(vectors_router, prefix="/vectors", tags=["Vectors and Search"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG Engine"])
api_router.include_router(agents_router, prefix="/agents", tags=["AI Agents"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["Tickets"])
api_router.include_router(handoff_router, tags=["Live Agent & Handoff"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics & Intelligence"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications & Events"])
api_router.include_router(widget_router, prefix="/widget", tags=["Embeddable Widget"])
api_router.include_router(billing_router, prefix="/billing", tags=["Billing & Monetization"])
api_router.include_router(automation_router, prefix="/automation", tags=["Automation"])
api_router.include_router(security_router, prefix="/security", tags=["Security & Compliance"])
api_router.include_router(integrations_router, prefix="/integrations", tags=["Integrations & Marketplace"])
