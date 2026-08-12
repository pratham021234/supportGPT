from app.core.database import Base

# User & Auth
from app.models.user import User
from app.models.auth import RefreshToken, EmailVerification, PasswordReset
from app.models.session import UserSession

# RBAC
from app.models.rbac import (
    Role,
    Permission,
    RolePermission,
    UserWorkspaceRole,
)

# Workspace
from app.models.workspace import (
    Workspace,
    WorkspaceMember,
    WorkspaceInvitation,
    WorkspaceAuditLog,
)

# Ticketing
from app.models.ticket import (
    Ticket,
    TicketComment,
    TicketAssignment,
    TicketActivity,
    SLAConfiguration,
)

# Knowledge Base
from app.models.knowledge import (
    KnowledgeSource,
    Document,
    DocumentPage,
    DocumentChunk,
    FAQ,
    KnowledgeTag,
    DocumentTag,
)

# Conversations
from app.models.conversation import (
    Customer,
    Conversation,
    Message,
    ConversationAssignment,
    ConversationEvent,
    CustomerFeedback,
)

# Handoff
from app.models.handoff import (
    AgentSession,
    AgentPresence,
    AgentQueue,
    QueueAssignment,
    ConversationHandoff,
    AgentPerformance,
)

# Notifications
from app.models.notification import (
    SystemEvent,
    Notification,
    NotificationPreference,
    NotificationDelivery,
)

# Analytics
from app.models.analytics import (
    AnalyticsEvent,
    MetricSnapshot,
    DashboardWidget,
    KnowledgeGap,
    CostMetric,
)

# Agents
from app.models.agent import (
    Agent,
    AgentPrompt,
    AgentVersion,
    AgentKnowledgeScope,
    AgentModelConfig,
    AgentEscalationRule,
)

# Widgets
from app.models.widget import (
    WidgetConfiguration,
    WidgetSession,
)

# Billing
from app.models.billing import (
    Plan,
    Subscription,
    PaymentMethod,
    Invoice,
    Payment,
    Seat,
    UsageRecord,
    SubscriptionStatus,
    BillingCycle,
    InvoiceStatus,
    PaymentStatus,
    SeatStatus,
)

# Automation
from app.models.automation import (
    AutomationRule,
    WorkflowExecution,
    WebhookEndpoint,
)

# Security
from app.models.security import (
    ApiKey,
    SecurityAlert,
)

# Integrations
from app.models.integration import (
    IntegrationConnection,
    IntegrationSyncLog,
)

__all__ = [
    "Base",

    # User/Auth
    "User",
    "RefreshToken",
    "EmailVerification",
    "PasswordReset",
    "UserSession",

    # RBAC
    "Role",
    "Permission",
    "RolePermission",
    "UserWorkspaceRole",

    # Workspace
    "Workspace",
    "WorkspaceMember",
    "WorkspaceInvitation",
    "WorkspaceAuditLog",

    # Ticketing
    "Ticket",
    "TicketComment",
    "TicketAssignment",
    "TicketActivity",
    "SLAConfiguration",

    # Knowledge
    "KnowledgeSource",
    "Document",
    "DocumentPage",
    "DocumentChunk",
    "FAQ",
    "KnowledgeTag",
    "DocumentTag",

    # Conversations
    "Customer",
    "Conversation",
    "Message",
    "ConversationAssignment",
    "ConversationEvent",
    "CustomerFeedback",

    # Handoff
    "AgentSession",
    "AgentPresence",
    "AgentQueue",
    "QueueAssignment",
    "ConversationHandoff",
    "AgentPerformance",

    # Notifications
    "SystemEvent",
    "Notification",
    "NotificationPreference",
    "NotificationDelivery",

    # Analytics
    "AnalyticsEvent",
    "MetricSnapshot",
    "DashboardWidget",
    "KnowledgeGap",
    "CostMetric",

    # Agents
    "Agent",
    "AgentPrompt",
    "AgentVersion",
    "AgentKnowledgeScope",
    "AgentModelConfig",
    "AgentEscalationRule",

    # Widgets
    "WidgetConfiguration",
    "WidgetSession",

    # Billing
    "Plan",
    "Subscription",
    "PaymentMethod",
    "Invoice",
    "Payment",
    "Seat",
    "UsageRecord",
    "SubscriptionStatus",
    "BillingCycle",
    "InvoiceStatus",
    "PaymentStatus",
    "SeatStatus",

    # Automation
    "AutomationRule",
    "WorkflowExecution",
    "WebhookEndpoint",

    # Security
    "ApiKey",
    "SecurityAlert",

    # Integrations
    "IntegrationConnection",
    "IntegrationSyncLog",
]