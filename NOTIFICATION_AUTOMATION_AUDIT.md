# Notification & Automation Platform Audit

## 1. Existing Infrastructure

### Database Models
- **Notification**: Captures user notifications (`title`, `message`, `type`, `status`, `priority`).
- **NotificationPreference**: Tracks user settings (`email_enabled`, `in_app_enabled`, `digest_enabled`).
- **NotificationDelivery**: Tracks delivery status per channel.
- **SystemEvent**: Core event log that drives the Event Bus.
- **AutomationRule**: Stores condition-action JSON configurations for event triggers.
- **WorkflowExecution**: Logs execution results of automation rules.
- **WebhookEndpoint**: Stores external webhook URLs for automated payload deliveries.

### Backend Services
- **Event Bus (`notification_service.py`)**: `EventBusService` exists, running an async queue to dispatch `SystemEvent` records to bound handlers (like Notification processing and Automation rule processing).
- **Automation Engine (`automation_service.py`)**: Includes a lightweight `ConditionEngine` and `ActionEngine` capable of checking conditions and running actions (`CREATE_TICKET`, `SEND_EMAIL`, `SEND_WEBHOOK`).
- **Email Service (`email_service.py`)**: Configured to use Resend but currently lacking rich HTML templates.

### API & Routing
- `/notifications` supports GET (paginated), `/unread`, `/{id}/read`, `/preferences`, and a basic `/ws` WebSocket.
- `/automation` supports GET and POST `/rules`, `/webhooks`, and `/executions`.

### Frontend
- Basic top-nav notification bell exists in `src/components/layout/top-nav.tsx`, but it just streams raw JSON payloads via WebSocket instead of querying standard notification objects.
- Mock Automation dashboard exists at `src/app/dashboard/automation/page.tsx`.

---

## 2. Missing & Stubbed Features

### Notification Center & Real-time Delivery
- The notification bell dropdown does not fetch the actual `Notification` objects from the backend; it only captures live websocket pings.
- Missing `Mark All Read` logic in backend service.

### Automation Workflow Engine
- `automation_service.py` is disconnected from core business logic. We need triggers inside `conversation_service` and `ticket_service` to actually call `event_bus.publish()`.
- Automation `PUT /rules/{id}` update endpoint is missing from `router.py`.

### Email & Scheduled Reports
- No rich `EmailTemplateService` for sending professional invites, ticket summaries, or reports.
- Missing Scheduled Task engine (Celery Beat or APScheduler) to process and send Daily/Weekly/Monthly reports automatically.

### Frontend Integration
- Missing a real notification center view.
- The automation dashboard needs to be wired to the API to allow non-technical admins to build `Trigger -> Condition -> Action` rules.
- Missing Notification Preferences page `/dashboard/settings/notifications`.

---

## 3. Required Action Items
1. **Implement Event Triggers**: Hook `event_bus.publish()` throughout the app (Conversations, Tickets, Knowledge uploads).
2. **Upgrade Email & Templates**: Implement an `EmailTemplateService` using HTML templates for professional correspondence.
3. **Scheduled Jobs Engine**: Implement a background scheduler for Daily/Weekly digests.
4. **Complete APIs**: Add missing update endpoints for rules and bulk read/delete operations.
5. **Frontend Notification Center**: Rewrite the `TopNav` dropdown to use a robust React Query + WebSocket hybrid to show clean UI notifications.
6. **Frontend Automation Builder**: Finalize the drag-and-drop or select-based rule builder in the automation dashboard.
