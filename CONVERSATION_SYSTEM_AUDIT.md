# Conversation System Audit

## 1. Existing Functionality

### Models
- **Conversations & Messages**: Robust SQLAlchemy schemas in `conversation.py`. Supports tracking statuses (`OPEN`, `ACTIVE`, `ESCALATED`, `RESOLVED`), channels, sender types (Customer, Agent, AI), and timestamps. Includes `ConversationEvent` and `ConversationAssignment`.
- **Tickets & SLAs**: Solid schema in `ticket.py` with tracking for status, priority, and source (e.g., `AI_ESCALATION`). Supports ticket assignments, activities, internal/external comments, and SLA configurations.
- **Handoff & Presence**: Schema in `handoff.py` for `AgentPresence`, queues, and `ConversationHandoff`.

### Services
- **ConversationService**: Can create conversations, update statuses, and log messages.
- **RealtimeService**: Handles WebSockets and delegates RAG execution when a customer messages.
- **HandoffService**: Controls the `is_human_active` flag to pause AI responses.
- **TicketService**: Handles manual creation and AI-escalated ticket creation. Tracks SLA breaches.

### API Routes
- **Conversations**: Basic CRUD (list, get, create). Includes a WebSocket endpoint for chat.
- **Tickets**: Basic CRUD and comments. Includes SLA initialization endpoint.

---

## 2. Missing Functionality

### Workflow Integration
- **Escalation Trigger Execution**: Phase 6 calculates an escalation flag, but it doesn't systematically invoke the `TicketService.create_ai_escalation` or `HandoffService` seamlessly inside the `rag_service.py` lifecycle.
- **Assignment System**: Auto-assignment or manual endpoints (`POST /conversations/{id}/assign`) do not exist. Agent workload isn't effectively balanced yet.
- **Lifecycle Endpoints**: Missing dedicated route actions for resolution, closure, and handoff (`POST /conversations/{id}/escalate`, `POST /conversations/{id}/resolve`, `POST /conversations/{id}/close`).

### Search & Filtering
- **Inbox Queries**: `get_workspace_conversations` is too basic. It lacks filters for status, assigned agents, priorities, or advanced search keywords.

### Customer Satisfaction (CSAT)
- **Ratings**: No models or endpoints exist to capture CSAT (1-5 stars, Helpful/Not Helpful) post-resolution.

### Internal Notes & Attachments
- **Internal Messaging**: No clear separation or endpoint to send internal `SYSTEM` or private notes within a live conversation.
- **Attachments**: Models indicate an `ATTACHMENT` type, but no actual S3 abstraction or storage handler exists in the endpoints.

---

## 3. Required Improvements
1. **API Expansion**: Fulfill the required endpoints listed in Phase 7 (`assign`, `escalate`, `resolve`, `close` for both Conversations and Tickets).
2. **Search Refinement**: Upgrade the `conversation_repo` to support complex queries (status in, assigned to, priority).
3. **RAG Integration Hook**: Modify `rag_service.py` to trigger `ticket_service.create_ai_escalation` and `handoff_service.initiate_handoff` when `escalate` is evaluated as True.
4. **CSAT Models**: Add `CustomerFeedback` model and corresponding endpoints.
5. **Real-time Broadcaster**: Ensure the WebSocket manager broadcasts assignment events and status changes to the frontend UI, not just plain text messages.
