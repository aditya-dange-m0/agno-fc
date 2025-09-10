# PLM Backend (Scaffold)

This scaffold provides a production-ready FastAPI backend skeleton for the PLM system.

Run locally with Docker Compose:

1. Copy .env.example to .env and configure values.
2. Start services:

   make up

3. API will be available at http://localhost:8000

Run tests locally:

  make test

Notes:
- Mongo and Redis are provided by docker-compose for local development.
- Attachment presign endpoint is stubbed — configure S3 credentials and implement boto3 presigning for production.
- Refresh tokens are stored in Mongo for the scaffold; in production use Redis with expiry and revocation lists.