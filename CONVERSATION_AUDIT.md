# Conversation System Audit

## Existing Functionality
- **Models**: `Conversation`, `Message`, `Customer`, `ConversationAssignment`, `ConversationEvent`, `CustomerFeedback` are present.
- **WebSockets**: Basic websocket endpoints for chat and agents exist in `router.py`.
- **Services**: `conversation_service.py` provides basic CRUD for conversations and messages.
- **API**: Most required REST endpoints (`POST /conversations`, `GET /conversations`, `POST /conversations/{id}/message`, `POST /conversations/{id}/resolve`, etc.) exist.
- **Real-time**: Basic broadcast mechanisms are implemented in `websocket_manager.py` and `realtime_service.py`.

## Partial Functionality
- **Conversation Model**: Missing `confidence_score` field. `ConversationStatus` is missing `HANDOFF`. 
- **Message Model**: Missing `citations`, `confidence`, and `tokens` fields. `SenderType` uses `AI_AGENT` and `SUPPORT_AGENT` instead of the requested `AI` and `AGENT`.
- **Customer Profile**: Contains `name`, `email`, and `phone`, but lacks explicit `company` and `location` fields (though they could be stuffed in `metadata`). Lacks explicit tracking for satisfaction score aggregates.
- **Internal Notes**: Supported somewhat by `SYSTEM` sender types, but lacks dedicated model/fields for clear separation.

## Missing Functionality
- **Handoff Engine**: Logic to automatically trigger handoff when `confidence < 0.70` or based on escalation rules is stubbed or missing.
- **Agent Takeover**: "Take Over", "Release", and "Transfer" flows are incomplete.
- **Conversation Assignment**: Missing auto/round-robin assignment engines.
- **Conversation Search & Filters**: `conversation_search_service.py` exists but needs to properly implement Message, Tag, and Agent search. Filters are likely partial.
- **Analytics**: `GET /conversations/analytics` endpoint is missing from `router.py`.
- **Timeline**: Chronological unified timeline of events and messages might require a specific endpoint or frontend merging logic.

## Broken Functionality
- Potential schema mismatches for `SenderType` (AI_AGENT vs AI) could break frontend/backend assumptions if not unified.
- Missing Alembic migrations for new fields means database saves will crash if frontend sends `citations` or `confidence` on messages.

## Stub Implementations
- `realtime_service.py` and `conversation_engine.py` appear to have skeleton handlers for incoming messages but likely lack the full RAG integration pipeline mapping (Store Message -> RAG Query -> Store Response -> Store Citations -> Store Confidence).
