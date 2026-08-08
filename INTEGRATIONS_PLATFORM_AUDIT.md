# Integrations Platform Audit

## 1. Existing Functionality

### OAuth Infrastructure
- A basic `OAuth` configuration exists via `authlib` in `backend/app/services/oauth_service.py` to support Google Login (`openid email profile`). 
- This is purely for **authentication** (SSO), not for background API integration or data synchronization (it lacks offline access and robust token management/refresh flows required for service-to-service communication).

### Integration Models
- No central `Integration` or `Connection` models exist in `backend/app/models/` to store third-party credentials, access tokens, refresh tokens, scopes, or sync statuses.

### Ecosystem Connectors
- **Slack, Teams, Discord**: Missing. No capabilities exist for external workflow notifications.
- **HubSpot, Salesforce, Zendesk**: Missing. No capabilities exist for bi-directional data syncing (Contacts, Tickets).
- **Gmail, Outlook**: Missing. No capabilities exist for email-to-ticket creation or thread syncing.
- **Webhooks & Zapier**: Missing. No framework exists to push arbitrary JSON payloads out to Zapier or receive incoming commands securely.

### Sync Engine
- Missing. There is no background worker or CRON job framework dedicated to incremental or full data synchronization with external CRMs or Helpdesks.

### Frontend
- No `/dashboard/settings/integrations` UI exists for Workspace Owners to browse the Marketplace, authorize OAuth apps, or review sync health.

---

## 2. Technical Debt & Requirements

### Connector Framework
We need a unified `BaseConnector` interface that all specific integrations (SlackConnector, HubSpotConnector) inherit from, ensuring consistent methods for `connect`, `disconnect`, `sync`, and `handle_webhook`.

### Credential Security
OAuth tokens for external systems (e.g., Salesforce API keys) must be stored securely. Since we don't have a dedicated secret management engine, we will need to utilize strong encryption at rest (or rely on robust database access controls for the MVP) when storing the `access_token` and `refresh_token` in PostgreSQL.

### Event Bus Bridge
The Integrations platform needs to tap into the `EventBus` established in Phase 11. When a ticket is created, the Event Bus should notify the `SyncEngine` to push that ticket to HubSpot or Slack based on active integrations.

---

## 3. Required Action Plan
1.  **Core Models**: Create `IntegrationConnection` and `IntegrationSyncLog` in `backend/app/models/integration.py`.
2.  **Connector Framework**: Create `backend/app/services/integrations/base.py` and implementations for major providers (Slack, HubSpot, Webhooks).
3.  **Sync Engine**: Build `backend/app/services/integrations/sync_engine.py` to handle data mapping and API retries.
4.  **API & UI**: Build the `/integrations` REST router and the Frontend Integrations Marketplace where users can one-click install apps.
