# PLM Backend

This backend includes RBAC, Redis-backed refresh tokens, S3 presign support (MinIO), background worker stubs, and integration tests.

Quick start (local dev with optional services):

1) Copy `.env.example` to `.env` and adjust values.
2) Start optional services:
   - docker-compose up -d (mongo, redis, minio, opensearch)
3) Install dependencies and run:
   - pip install -r requirements.txt
   - uvicorn app:app --reload

Running integration tests:

- Uses pytest and testcontainers (requires Docker).
- Run: make test-integration

Runbook: Starting optional services

- To start MinIO: docker-compose up -d minio
- To start OpenSearch: docker-compose up -d opensearch
- Worker: docker-compose up -d worker

Design notes:
- Refresh tokens are rotated and stored in Redis with TTL. If a refresh token is reused (not present), rotation fails and requires re-login.
- Cached project summaries are stored in Redis with short TTL (60s) and invalidated on update.

If significant changes are needed, create PRs scoped per the suggested commits list in the main repo documentation.