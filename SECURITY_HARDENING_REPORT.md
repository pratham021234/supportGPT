# SupportGPT Security Hardening Report

## 1. Container & Infrastructure Security
- **Non-Root Execution**: Both `Dockerfile.backend` and `Dockerfile.frontend` have been configured to run under a dedicated `appuser` (UID 1000) rather than root.
- **Immutable Tags**: All base images use specific versions (e.g., `postgres:16`, `python:3.11-slim`) rather than `latest` to prevent unexpected upstream supply chain poisoning.
- **Trivy Scanning**: The `.github/workflows/main.yml` pipeline strictly enforces a filesystem vulnerability scan, failing the build if CRITICAL or HIGH CVEs are detected in dependencies.

## 2. Application Security (API & Frontend)
- **CORS Policies**: Tightly restricted to the exact `FRONTEND_URL` environment variable.
- **Rate Limiting**: Nginx is configured to rate-limit aggressive IPs (`10r/s` with a burst of `20`) to mitigate basic DDoS and brute-force attacks against the API.
- **Security Headers**: Nginx automatically injects `X-Frame-Options`, `X-XSS-Protection`, `X-Content-Type-Options`, and strict `Content-Security-Policy` headers.
- **Authentication**: JWT tokens utilize short lifespans (15 minutes) coupled with securely stored refresh tokens to mitigate token theft.

## 3. Data Protection
- **Secrets Management**: Hardcoded secrets have been stripped. `.env.production` dictates all injection points. In Kubernetes, this translates to utilizing `SealedSecrets` or AWS Secrets Manager.
- **Encryption at Rest**: PostgreSQL storage volumes and Qdrant storage volumes must be encrypted at the block level (e.g., AWS EBS KMS encryption).
- **Encryption in Transit**: Nginx handles SSL termination ensuring all client traffic is forced to TLS 1.3. Internal service-to-service communication is isolated on a private docker/k8s virtual network.

## 4. Audit Logging
Comprehensive `WorkspaceAuditLog` and `TicketAuditLog` tables persistently track access and mutations to sensitive enterprise data, satisfying SOC2/GDPR compliance prerequisites.
