# Database Schema Documentation

## ER Overview

The SupportGPT database architecture is grouped into several distinct domains, all anchored to a central multi-tenant `Workspaces` model.

### 1. Identity & Access Management (IAM)
- **Users**: Core identity layer.
- **Workspaces**: Organizational tenant boundaries.
- **WorkspaceMembers**: Maps Users to Workspaces.
- **Roles & Permissions**: Fine-grained access control tables (`roles`, `permissions`, `role_permissions`, `user_workspace_roles`).

### 2. AI Agents & RAG System
- **Agents**: The core AI actors scoped to workspaces.
- **AgentPrompts**, **AgentVersions**, **AgentModelConfigs**, **AgentEscalationRules**, **AgentKnowledgeScopes**: Sub-configurations tightly bound to an Agent via one-to-one or one-to-many relationships.
- **Documents & KnowledgeSources**: Storage entities for Retrieval-Augmented Generation.
- **DocumentChunks**: Atomic text blocks for embedding generation.
- **VectorCollections** & **EmbeddingJobs**: Background processing and vector storage sync states.

### 3. Conversations & Handoffs
- **Customers**: External users interacting with Agents.
- **Conversations**: Grouped interactions between Customers and Agents (or humans).
- **Messages**: Individual payloads within a Conversation.
- **ConversationEvents** & **ConversationHandoffs**: Logging and state tracking for when an AI Agent relinquishes control to a human.

### 4. Ticketing System
- **Tickets**: Tasks or issues escalated from Conversations.
- **TicketActivities**, **TicketAssignments**, **TicketComments**: Auditing and workflow tracking for tickets.

## Index Strategy

High-traffic lookup columns have indices implemented at the SQLAlchemy level:
- Authentication lookups (`users.email`, `refresh_tokens.token`)
- Tenant isolation lookups (`workspace_id` heavily indexed across all tables).
- Natural grouping lookups (`conversation_id`, `customer_id`, `ticket_id`, `agent_id`).

## Enum Strategy

PostgreSQL native ENUMs are employed extensively for state safety:
- `TicketStatus`: OPEN, IN_PROGRESS, RESOLVED, CLOSED
- `ConversationStatus`: OPEN, ACTIVE, WAITING, ESCALATED, RESOLVED, CLOSED
- `AgentStatus`: DRAFT, ACTIVE, ARCHIVED, DISABLED
- `JobStatus`: PENDING, PROCESSING, COMPLETED, FAILED

## Tenant Isolation

`workspace_id` acts as the primary tenant discriminator. Queries spanning business entities (Agents, Tickets, Customers, Knowledge) must filter on `workspace_id`. Cross-workspace querying is explicitly restricted at the API layer.
