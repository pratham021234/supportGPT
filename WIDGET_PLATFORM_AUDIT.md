# Widget Platform Audit

## 1. Existing Functionality

### Models & Schema
- **WidgetConfiguration**: SQLAlchemy model storing `theme`, `primary_color`, `logo_url`, `launcher_text`, `welcome_message`, `position`, `border_radius`. Mapped to Workspace and optionally to Agent.
- **WidgetSession**: SQLAlchemy model tracking public visitor sessions, storing `session_token`, `workspace_id`, and mapping to `customer_id`.

### Services & API
- **WidgetService**: Contains `WidgetConfigurationService` and `WidgetSessionService` to initialize sessions, fetch configurations, and convert a session into a new `Conversation` and `Customer`.
- **Widget API Router**: Includes public routes `GET /config/{agent_id}`, `POST /session`, and `POST /conversations`. It also includes a private admin route `PATCH /settings` to update branding configs.

---

## 2. Missing Functionality

### Frontend Deployment & SDK
- **Embeddable SDK (`widget.js`)**: No static Javascript loader exists. Companies have no way to embed the widget on their websites.
- **Frontend Widget UI**: There is no Chat Widget frontend (e.g., in React/Next.js) for the end-user to interact with. The floating button, chat window, typing indicators, and message lists are completely missing.
- **Mobile Responsiveness**: Since the UI doesn't exist, it cannot be mobile-responsive.

### Frontend Dashboard
- **Widget Builder**: There is no UI in the Dashboard (`frontend/src/app/dashboard/widget-builder`) for companies to configure their theme, color, text, or test their widget in a live preview.

### Realtime Connectivity
- While `realtime_service.py` exists for internal conversations, the widget SDK needs to actually connect to the WebSocket endpoint (`ws://.../api/v1/conversations/{id}/ws`) to stream tokens and handle live typing updates.

### File Attachments & Customer Identity
- **Attachments**: No endpoints or logic for users to upload files via the widget.
- **Identity Context**: No robust SDK method to pass known user identity (`SupportGPT.identify({ email: "..." })`) beyond the basic anonymous session creation.
- **Multi-site & Security**: No logic exists to restrict widget loading to specific whitelisted domains (Origin Validation).

---

## 3. Required Improvements
1. **Build the `widget.js` SDK**: Create a lightweight Vanilla JS loader script that can be embedded on any website.
2. **Build the Chat Widget UI**: Implement an iframe-based or shadow-DOM React component for the chat interface, integrating closely with the WebSocket for streaming.
3. **Build the Widget Builder UI**: Create the admin interface in the Next.js dashboard where users can customize the colors/text and see a live preview.
4. **SDK API Expansion**: Implement window-level methods (`SupportGPT.open()`, `.identify()`) to give host websites programmatic control over the widget.
5. **Security**: Add origin checks to the session initialization to prevent unauthorized embedding of the widget.
