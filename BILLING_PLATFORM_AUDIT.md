# Billing & SaaS Platform Audit

## 1. Existing Functionality

### Models
- **Billing Models**: The foundation is robust. We have `Plan`, `Subscription`, `PaymentMethod`, `Invoice`, `Payment`, `Seat`, and `UsageRecord` inside `backend/app/models/billing.py`.
- **Enums**: `SubscriptionStatus`, `BillingCycle`, `InvoiceStatus`, etc., are well defined.

### Services
- **StripeService**: Contains a skeletal mock webhook processor (`process_webhook`) that activates a subscription based on a `checkout.session.completed` event.
- **UsageTrackingService**: Can track raw usage events (e.g., `track_usage`).
- **PlanEnforcementService**: Can evaluate limits dynamically and raise `LimitExceededError` preventing unauthorized operations.

### API Endpoints
- `GET /api/v1/billing/plans`: Returns available plans.
- `GET /api/v1/billing/subscription`: Returns the current workspace subscription.
- `POST /api/v1/billing/usage`: Admin route to log usage (with enforcement checks).
- `POST /api/v1/billing/webhooks/stripe`: Basic Stripe webhook receiver.

---

## 2. Missing Functionality (The Gaps)

### Complete Stripe Integration
- **Stripe SDK**: We are not actually using the `stripe` python SDK. There are no functions to generate checkout sessions (`stripe.checkout.Session.create`), fetch customer portal URLs (`stripe.billing_portal.Session.create`), or manage invoices.
- **Webhook Security**: Webhook signature verification is missing (`stripe_signature`).
- **Idempotency**: Webhook handling is not idempotent, meaning duplicate Stripe events could cause duplicate database actions.

### Trial & Subscription Lifecycle
- **Trials**: Subscriptions default to `TRIAL` status, but there's no backend job or logic that expires trials after 14 days or alerts the user.
- **Upgrade / Downgrade Flows**: No API endpoints exist for the user to explicitly change their plan from the UI (e.g., migrating from Starter to Growth).
- **Cancellations**: No endpoint for a user to cancel their subscription. 

### Frontend
- **Billing Dashboard**: The frontend UI for billing management (`src/app/dashboard/billing*`) is missing. Users have no way to view their current plan, see their usage limits, download past invoices, or update their credit card.

## 3. Technical Debt & Requirements
- **Stripe Keys**: We need environment variables `STRIPE_API_KEY` and `STRIPE_WEBHOOK_SECRET`.
- **Revenue Analytics**: We lack admin analytics for MRR, ARR, and active trials.

## 4. Required Action Plan
We need to flesh out `StripeService` to use the actual `stripe` SDK to build Checkout and Portal sessions. We need to create the `router.py` endpoints for these actions. Finally, we must build the Enterprise Billing Dashboard UI where users can manage their SaaS subscription.
