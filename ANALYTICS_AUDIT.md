# Analytics Platform Audit

## 1. Existing Functionality

### Database & Models
- **AnalyticsEvent**: Stores raw events (e.g., `RAG_QUERY`, `AI_ESCALATION`, `TICKET_CREATED`).
- **MetricSnapshot**: Stores pre-aggregated metrics over time (daily/weekly).
- **DashboardWidget**: Stores customizable widget definitions.
- **KnowledgeGap**: Stores clusters of failed/low-confidence queries to highlight missing knowledge.
- **CostMetric**: Stores AI token and cost data.

### Services
- **AnalyticsEventService**: Logs raw events.
- **MetricsAggregationService**: Computes basic overview stats (Total Conversations, Total Tickets, AI Resolution Rate).
- **KnowledgeGapService**: Intercepts low-confidence RAG queries and groups them.
- **CostAnalyticsService**: Logs usage metrics.
- **ReportingService**: Basic CSV exporter for Tickets and Knowledge Gaps.

### API Endpoints
- `POST /api/v1/analytics/events`: Logs raw events.
- `GET /api/v1/analytics/dashboard`: Gets high-level metrics.
- `GET /api/v1/analytics/knowledge-gaps`: Lists knowledge gaps.
- `GET /api/v1/analytics/costs`: Sums estimated cost.
- `POST /api/v1/analytics/reports/export`: Generates basic CSVs.

### Frontend
- **Analytics Page (`src/app/dashboard/analytics/page.tsx`)**: Has a basic layout with an Overview Chart and three placeholder lists: Top Questions, Knowledge Gaps, Most Referenced Documents.

---

## 2. Missing Functionality

### Core APIs Required
The user requires the following endpoints which are either missing or need major expansion:
- `GET /analytics/overview` (expand existing)
- `GET /analytics/conversations`
- `GET /analytics/agents`
- `GET /analytics/knowledge`
- `GET /analytics/tickets`
- `GET /analytics/escalations`
- `GET /analytics/costs`
- `GET /analytics/satisfaction`
- `GET /analytics/realtime`

### Intelligence & Insights
- **BusinessInsightsEngine**: Currently, knowledge gaps are logged, but there is no engine proactively generating text recommendations (e.g., "Create API Authentication Guide").
- **Knowledge Intelligence**: No tracking for "Most Referenced Documents" or "Least Used Documents" in a formalized API.
- **Agent Performance**: No endpoints to track AI agent vs Human agent performance explicitly.
- **Cost Analytics Details**: Current cost API only returns a single total. Needs breakdown per model/agent.

### Realtime & Export
- **Realtime Dashboards**: No WebSocket or active connection for live traffic / live agents monitoring.
- **Comprehensive Reporting**: Need PDF/Excel exports, and a wider variety of CSV reports.

## 3. Technical Debt & Needed Improvements
- The frontend currently tries to call `getTopQuestions` and `getMostReferencedDocuments`, but the backend doesn't properly provide these.
- RAG Service logging (done in Phase 6) writes to tables, but the `AnalyticsService` does not cross-reference them optimally.
- We need to build the `BusinessInsightsEngine` to use Gemini to read the aggregated metrics and `KnowledgeGaps` and produce actionable text recommendations.
