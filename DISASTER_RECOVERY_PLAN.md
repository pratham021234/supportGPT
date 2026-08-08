# SupportGPT Disaster Recovery Plan

## 1. Overview
This document outlines the protocols to restore the SupportGPT platform in the event of a catastrophic failure (e.g., region-wide cloud provider outage, massive data corruption, or ransomware attack).

## 2. Recovery Time Objective (RTO)
- **Target RTO**: 4 Hours for total regional failover.

## 3. Failure Scenarios & Runbooks

### Scenario A: Primary Database Corruption
1. **Declare Incident**: Page on-call Data Engineer.
2. **Halt Traffic**: Route Nginx/Ingress traffic to a static "Maintenance" page to prevent further corruption.
3. **Restore from PITR**: Spin up a new PostgreSQL RDS instance using the latest automated snapshot combined with WAL logs up to 1 minute before the corruption event.
4. **Update Secrets**: Update Kubernetes Secrets/Environment variables to point to the new DB endpoint.
5. **Resume Traffic**: Restore Ingress routing.

### Scenario B: Qdrant Vector Data Loss
1. **Assess Impact**: Relational data is safe, but AI Agents will hallucinate or fail to answer.
2. **Restore Snapshot**: Pull the last nightly snapshot from S3 and mount it to a fresh Qdrant container.
3. **Delta Sync**: If the snapshot is 12 hours old, trigger a background worker script `python scripts/rebuild_vectors.py --since="last_snapshot_time"` to re-embed any newly uploaded documents in PostgreSQL that are missing from Qdrant.

### Scenario C: Region Outage (e.g., us-east-1 goes down)
1. **DNS Failover**: Update Route53/Cloudflare DNS to point to the `us-west-2` standby cluster.
2. **Promote Replicas**: Promote the cross-region PostgreSQL Read Replica to Primary.
3. **Scale Compute**: Scale up the Kubernetes deployment in `us-west-2` from minimum to production capacities.

## 4. Post-Mortem Requirements
Every DR event must be followed by a blameless post-mortem document within 48 hours, tracking Root Cause, Resolution Time, and Action Items to prevent recurrence.
