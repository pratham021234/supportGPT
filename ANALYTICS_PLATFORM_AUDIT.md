# Analytics Platform Audit

## 1. Existing Infrastructure

### Database Models
- **AnalyticsEvent**: Stores granular events (`event_type`, `entity_type`, `entity_id`, `metadata`).
- **MetricSnapshot**: Stores pre-aggregated metrics (`metric_name`, `metric_value`, `aggregation_period`).
- **DashboardWidget**: Stores UI configurations for custom dashboards.
- **KnowledgeGap**: Tracks unanswered or low-confidence queries.
- **CostMetric**: Tracks API token usage and estimated costs.

### Backend Services (`analytics_service.py`)
- `AnalyticsEventService`: Can log generic events.
- `MetricsAggregationService`: Has partial implementations for `get_volume_metrics` and `get_dashboard_metrics`, but relies on hardcoded data for resolution rates, customer satisfaction, and trends.
- `KnowledgeIntelligenceEngine`: Sorts mocked referenced documents. Returns gaps for top questions.
- `CostAnalyticsService` and `ReportingService`: Basic implementations exist (CSV export).

### API & Routing (`router.py`)
- The `/analytics` router has many endpoints mapped (`/overview`, `/conversations`, `/tickets`, `/agents`, `/knowledge`), but many just route back to mocked services.
- Real-time WebSocket exists (`/realtime`) but only supports "ping/pong" and lacks active publish/subscribe mechanisms.

### Frontend
- Basic executive dashboard exists at `/dashboard/analytics/page.tsx` using `useAnalyticsOverview`.
- API client `src/lib/api/analytics.ts` defines all hooks and shapes but points to incomplete backends.

---

## 2. Missing & Stubbed Features

### Event Tracking Coverage
- No explicit hooks inside `TicketCreationService`, `ConversationService`, or `AgentService` to automatically trigger `AnalyticsEventService.log_event()`.

### Analytics Modules
- **AI Performance**: Missing endpoints for Confidence Score Distribution and Hallucination Risk.
- **Customer Analytics**: Missing tracking for returning vs. active users.
- **Widget Analytics**: Missing specific funnel metrics for Widget Opens -> Chat Starts -> Tickets Created.

### Data Accuracy (Mock Data)
- **Agent Utilization**: Hardcoded resolution rate (80%) and CSAT (4.5) in `get_agent_summary()`.
- **Knowledge Sources**: Hardcoded to `142` in `get_dashboard_metrics()`.
- **Customer Satisfaction**: Hardcoded to `4.7` in `get_dashboard_metrics()`.

### Reporting & Visualization
- **Date Ranges**: Time range filtering ("7d", "30d", "today") is only partially implemented in backend SQL queries.
- **Exports**: Excel and PDF formats are entirely missing from `export_report`.

---

## 3. Required Action Items
1. **Remove all mocked variables** in `MetricsAggregationService` and replace them with SQL `COUNT` and `AVG` aggregates.
2. **Implement full Date Range filtering** dynamically parsing `7d`, `30d`, etc., into `datetime` bounds for all queries.
3. **Build specialized endpoints**: AI Performance, Widget Funnels, Customer Demographics.
4. **Implement Event Triggers**: Hook `AnalyticsEventService` into core product mutations (e.g. `ticket_created`).
5. **Update Frontend Pages**: Build out the sub-tabs in `/dashboard/analytics/*` using Recharts for comprehensive visualization.
