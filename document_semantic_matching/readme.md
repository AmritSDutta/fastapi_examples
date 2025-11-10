Running test:
    pytest -v

Generating requirement.txt:
>pipreqs . --force --savepath requirements.txt


>docker build -t doc-semantic-matching .

if you are running directly on windows
>docker run -d  -p 8000:8000 -e GEMINI_API_KEY=<yourkey> --name doc-semantic-matching doc-semantic-matching:latest

if you are running pgvector on another docker , grab it's network, and docker name
>docker run -d --name doc-semantic-matching --network <your_pgvector_default_network> -p 8000:8000  -e GEMINI_API_KEY=<yourkey> -e DB_DSN=postgresql://user:password@<your_pgvector_docker_name>:5432/wine_review_gemini  TABLE_NAME=test_test doc-semantic-matching:latest


#### Deployment note: 1

Architecture: Postgres with pgvector runs as its own container (pgvector-postgres-1)
and exposes a dedicated Docker user-defined bridge network (pgvector_default).
This isolates data plane and enables container DNS-based service discovery.

Networking principle: Attach the app container to the same network and use the Postgres container name as the DB host
(e.g., postgresql://user:pass@pgvector-postgres-1:5432/db). Don’t use localhost — inside containers that points to the container itself.

Run pattern (example):

docker run -d \
  --name doc-semantic-matching \
  --network pgvector_default \
  -e DB_DSN="postgresql://user:pass@pgvector-postgres-1:5432/wine_review_gemini" \
  -e GEMINI_API_KEY=... \
  doc-semantic-matching:latest


Or declare both services in docker-compose.yml so Docker Compose wires the pgvector_default network automatically.
Operational hygiene: verify docker network inspect pgvector_default and
docker exec <app> nc -vz pgvector-postgres-1 5432 during smoke tests; add start-up retries
and DSN normalization in app init to tolerate race conditions.

Why this is recommended: user-defined bridge networks provide lightweight isolation, predictable DNS service names,
and straightforward horizontal scaling without sacrificing portability.


#### Deployment note: 2

The pgvector database runs as its own Docker container, exposing a fixed port and
joining a user-defined network used by the application container.

Example command (stand-alone)
docker run -d \
  --name pgvector-postgres-1 \
  --network pgvector_default \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=wine_review_gemini \
  -p 5432:5432 \
  ankane/pgvector:latest


Explanation

--name pgvector-postgres-1 → container hostname that the app uses as its DB host.
--network pgvector_default → shared network so containers discover each other by name.
-p 5432:5432 → binds PostgreSQL to the host for optional external access.
-e POSTGRES_* → initializes credentials and default database.
ankane/pgvector:latest → official lightweight image with the pgvector extension pre-installed.