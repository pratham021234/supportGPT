# Go-Live Checklist

Before onboarding the first paying customer, the operations and engineering team must physically verify the following items in the production environment.

## 1. Security & Keys
- [ ] Ensure all mock `test_secret` strings are purged from the environment.
- [ ] Verify `JWT_SECRET_KEY` is a securely generated 256-bit cryptographically secure string.
- [ ] Verify Stripe is configured to "Live Mode" and real `sk_live_...` and `whsec_...` keys are injected.
- [ ] Verify CORS `allow_origins` in `main.py` only allows the actual production domain, not `*`.

## 2. Infrastructure
- [ ] Database is backed up daily with Point-in-Time-Recovery (PITR) enabled.
- [ ] Redis is operating with Eviction Policy set correctly (e.g. `allkeys-lru`).
- [ ] AWS S3 Bucket has block public access fully enforced. Presigned URLs are working for authorized downloads.
- [ ] Ensure SSL/TLS certificates are active on both the Frontend and Backend load balancers.

## 3. Observability
- [ ] Trigger an intentional 400 Bad Request error and verify it appears in the Sentry dashboard.
- [ ] Trigger an intentional 500 Server Error and verify it triggers an alert/pager to the engineering team.
- [ ] Verify logging output is structured JSON.

## 4. End-to-End Validation
- [ ] Create a live Workspace.
- [ ] Upgrade to a paid plan using a real credit card.
- [ ] Upload a PDF to the Knowledge Base and wait for processing to succeed.
- [ ] Open the chat widget and ask a question. Verify the citation correctly links to the PDF.
- [ ] Hit the rate limits intentionally and verify `429 Too Many Requests` is returned.
- [ ] Assign a conversation to an Agent and verify the WebSocket pushes the assignment notification instantly.
