# SupportGPT Enterprise Backup Strategy

## 1. Recovery Point Objective (RPO)
- **Target RPO**: 1 Hour for relational data (PostgreSQL), 24 Hours for vector indexes (Qdrant).

## 2. PostgreSQL Backup Procedures
- **Daily Full Backups**: Automated `pg_dump` jobs running at 02:00 UTC, exporting encrypted compressed `.sql.gz` files to AWS S3 / Google Cloud Storage.
- **Continuous Archiving**: Write-Ahead Logging (WAL) shipping enabled (e.g., using WAL-G or pgBackRest) to allow Point-In-Time-Recovery (PITR) with an RPO of 5 minutes.
- **Retention Policy**: 
  - Daily backups: 30 days
  - Weekly backups: 12 weeks
  - Monthly backups: 7 years (Compliance requirement)

## 3. Vector Database (Qdrant) Backups
- **Daily Snapshots**: Automated Qdrant Collection Snapshots triggered via API at 03:00 UTC.
- **Storage**: Snapshots moved to cold cloud storage.
- **Rebuilding Strategy**: In extreme disaster scenarios, Qdrant can be fully reconstructed by re-embedding PostgreSQL document chunks if snapshots are corrupted, sacrificing compute time for data integrity.

## 4. Object Storage (S3 / Attachments)
- **Versioning**: Enabled on all S3 buckets preventing accidental deletion of Customer attachments.
- **Cross-Region Replication (CRR)**: Critical buckets replicated from `us-east-1` to `us-west-2`.

## 5. Verification
- **Automated Restores**: On the 1st of every month, a CI/CD job will pull the latest Postgres and Qdrant backups, spin up a transient Docker environment, run health checks, and tear it down, alerting DevOps upon failure.
