# Multi-Agent Platform Audit

## 1. Existing Functionality

### Models & Schema
- **Agent Models**: Comprehensive SQLAlchemy models exist in `agent.py`, including `Agent`, `AgentPrompt` (system prompt, behavior rules), `AgentModelConfig` (temperature, tokens), `AgentEscalationRule` (confidence thresholds), `AgentKnowledgeScope` (knowledge mapping), and `AgentVersion` (snapshotting).
- **Repositories**: Standard async CRUD repositories for all Agent models are implemented in `agent_repo.py`.

### Services
- **AgentService**: Can create an agent (auto-generating default prompts, model configs, and escalation rules) and publish an agent (serializing its state into an `AgentVersion` snapshot).
- **PromptService**: Can fetch and update `AgentPrompt`.

### API Routes
- **Agents Router**: Currently supports `POST /agents`, `GET /agents`, `POST /{id}/publish`, `PATCH /{id}/prompt`, and `POST /{id}/test`.

---

## 2. Missing Functionality

### Agent Lifecycle & Management
- **Archiving & Deletion**: No `DELETE` or `ARCHIVE` endpoints.
- **Cloning**: Missing `POST /agents/{id}/clone` to duplicate a successful agent.
- **Versioning Rollback**: The `agent_service.restore_version` is just a mock returning `True`. Needs to actually overwrite active configs and missing `POST /agents/{id}/rollback` endpoint.

### Knowledge Assignment
- **Knowledge API**: Missing `POST /agents/{id}/knowledge` to attach specific Documents, Tags, or Sources to `AgentKnowledgeScope`.
- **RAG Enforcement**: The RAG engine (`testing_service.py` / Phase 6) needs to read the agent's `AgentKnowledgeScope` to restrict Qdrant vector retrieval properly instead of querying all workspace data.

### Configuration APIs
- **Model Configs**: No endpoints to edit Temperature, Tokens, Provider, Model.
- **Escalation Configs**: No endpoints to edit Confidence Thresholds, Escalation Messages, or Auto-Handoff settings.

### Agent Routing
- **Agent Router**: No `AgentRouter` exists to dynamically route a customer to the correct agent (e.g., Sales vs. Technical) based on the query. Currently, conversations are statically assigned.

### Safety & Memory
- **Safety Layer**: Missing `AgentSafetyLayer` to protect against Prompt Injection and PII leakage.
- **Memory**: The system currently pulls all conversation history without a specialized memory window context builder.

### Analytics
- **Agent Analytics**: Missing `GET /agents/{id}/analytics` for tracking Resolution Rate, Avg Confidence, Token Usage, etc.

---

## 3. Required Improvements
1. **API Expansion**: Fulfill the missing endpoints (`clone`, `rollback`, `knowledge`, `model`, `escalation`, `analytics`).
2. **Implement Rollback Logic**: Complete the deserialization in `restore_version` to overwrite current settings with the JSONB snapshot.
3. **Build Agent Router**: Create an LLM-powered router to evaluate customer queries and assign the correct agent if one is not already assigned to the conversation.
4. **Build Safety Layer**: Implement prompt validation and PII obfuscation pre/post generation.
5. **RAG Integration**: Ensure `RetrievalService` strictly filters by the `AgentKnowledgeScope` instead of just the workspace.
