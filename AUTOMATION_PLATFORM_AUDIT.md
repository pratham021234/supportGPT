# Automation Platform Audit

## 1. Existing Functionality

### Models
- **SystemEvent**: Core event log for the Event Bus.
- **Notification**: Stores notification instances (type, status, priority).
- **NotificationPreference**: User preferences for email/in-app/digest.
- **NotificationDelivery**: Tracks delivery status across channels.

### Services
- **EventBus** (`notification_service.py`): Barebones implementation that allows publishing events, but lacks sophisticated routing, trigger evaluation, and webhook firing.
- **NotificationService**: Handles creation and marking notifications as read.
- **PreferenceService**: Simple CRUD for user notification preferences.

### API Endpoints
- `POST /api/v1/notifications/events`: Publishes a system event.
- `GET /api/v1/notifications/`: Gets unread notifications.
- `PATCH /api/v1/notifications/{id}/read`: Marks as read.
- `GET / POST /api/v1/notifications/preferences`: Manages preferences.
- `WS /api/v1/notifications/ws`: A stub WebSocket for realtime toasts.

### Frontend
- Basic notification UI exists, but no Rule Builder or Automation Dashboard.

---

## 2. Missing Functionality

### Automation & Rule Engine
- **Missing Models**: No tables exist for `AutomationRule`, `WorkflowExecution`, or `WebhookEndpoint`.
- **Trigger Engine**: The EventBus doesn't automatically trigger "Rules" when an event occurs.
- **Action Engine**: No system to dynamically execute actions (e.g., `create_ticket`, `send_email`) based on rule conditions.
- **Rule Builder (Frontend)**: Missing the enterprise UI that lets users configure `IF condition THEN action` workflows.

### Advanced Notifications & SLAs
- **Email Delivery**: The system has an `email_service.py`, but it isn't hooked up to the EventBus to send transactional emails automatically when rules trigger.
- **SLA Automation**: No tracking of SLAs or automated escalation of tickets when SLAs breach.
- **Scheduled Jobs**: No `SchedulerService` for recurring jobs or cron jobs.

## 3. Technical Debt & Required Improvements
- **Webhooks**: Need an abstraction layer to fire outgoing webhooks for external integrations.
- **Execution Tracking**: When a rule fires, we need to track it in `WorkflowExecution` so admins can debug why an automation succeeded or failed.
- The `EventBus` needs to be enhanced from a simple logger to a real event router that triggers the `AutomationEngine`.
