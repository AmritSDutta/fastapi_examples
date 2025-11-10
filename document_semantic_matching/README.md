# 📘 Document Semantic Matching — FastAPI + pgvector + Gemini GenAI

This service performs **semantic document retrieval** by embedding text data using **Google Gemini GenAI** and storing the resulting vectors in **PostgreSQL with pgvector** for efficient similarity search.

---

## ⚙️ Running Tests

```bash
pytest -v
```

---

## 📦 Generating `requirements.txt`

```bash
pipreqs . --force --savepath requirements.txt
```

---

## 🐳 Docker Build

```bash
docker build -t doc-semantic-matching .
```

---

## 🚀 Running the Container

### 1️⃣ Run directly on Windows (no external pgvector)
```bash
docker run -d   -p 8000:8000   -e GEMINI_API_KEY=<yourkey>   --name doc-semantic-matching   doc-semantic-matching:latest
```

### 2️⃣ Run with external pgvector container
If your **pgvector** instance runs in a separate Docker container, attach the app to the same network:

```bash
docker run -d   --name doc-semantic-matching   --network <your_pgvector_default_network>   -p 8000:8000   -e GEMINI_API_KEY=<yourkey>   -e DB_DSN=postgresql://user:password@<your_pgvector_docker_name>:5432/wine_review_gemini   -e TABLE_NAME=test_test   doc-semantic-matching:latest
```

---

## 🏗️ Deployment Note 1 — Network & Architecture

- **Architecture:** PostgreSQL (with pgvector) runs as an isolated container (`pgvector-postgres-1`) exposing a Docker **user-defined bridge network** (`pgvector_default`).
- **Networking principle:** The FastAPI app container attaches to the same network and connects using the Postgres container name as the hostname.  
  Example DSN:  
  `postgresql://user:pass@pgvector-postgres-1:5432/wine_review_gemini`
- **Important:** Don’t use `localhost` inside containers — it refers to the container itself, not the host.
- **Example run:**
  ```bash
  docker run -d     --name doc-semantic-matching     --network pgvector_default     -e DB_DSN="postgresql://user:pass@pgvector-postgres-1:5432/wine_review_gemini"     -e GEMINI_API_KEY=...     doc-semantic-matching:latest
  ```
- **Operational hygiene:**
  ```bash
  docker network inspect pgvector_default
  docker exec <app> nc -vz pgvector-postgres-1 5432
  ```
- **Why:**  
  User-defined bridge networks provide lightweight isolation, predictable DNS resolution, and easy horizontal scaling without host port conflicts.

---

## 🐘 Deployment Note 2 — pgvector Setup

### Standalone pgvector Deployment
```bash
docker run -d   --name pgvector-postgres-1   --network pgvector_default   -e POSTGRES_USER=user   -e POSTGRES_PASSWORD=password   -e POSTGRES_DB=wine_review_gemini   -p 5432:5432   ankane/pgvector:latest
```

**Explanation**
- `--name pgvector-postgres-1` → hostname used by the FastAPI app.  
- `--network pgvector_default` → shared Docker network for service discovery.  
- `-p 5432:5432` → exposes the database externally for admin access.  
- `-e POSTGRES_*` → initializes credentials and database.  
- `ankane/pgvector:latest` → official image preloaded with the pgvector extension.

---

## 🔮 Deployment Note 3 — Gemini GenAI Vector Embeddings

### 💡 Overview
- **Provider:** Google Cloud’s **Gemini API** (`google-genai` Python SDK)  
- **Purpose:** Convert text into dense vector embeddings that capture semantic similarity.  
- **Usage:** The FastAPI app uses `genai.Client().models.embed_content(...)` for embedding text during both ingestion and retrieval.  
- **Integration:** Embeddings are stored as `vector` columns in PostgreSQL and queried using `<=>` distance metrics.

---

### 🔑 Acquiring a Gemini API Key

1. Visit **[Google AI Studio](https://aistudio.google.com/app/apikey)**  
2. Click **“Create API key”** and copy it securely.  
3. Pass it into Docker via an environment variable:

   ```bash
   docker run -d      --name doc-semantic-matching      --network pgvector_default      -e GEMINI_API_KEY=your_api_key_here      -e DB_DSN="postgresql://user:password@pgvector-postgres-1:5432/wine_review_gemini"      doc-semantic-matching:latest
   ```

4. **Verify API connectivity:**
   ```bash
   docker exec -it doc-semantic-matching python -c    "import google.genai as genai; c=genai.Client(api_key='YOUR_KEY'); print([m.name for m in c.models.list()])"
   ```

---

### 🧠 Notes
- Default embedding model: `models/embedding-001` (or equivalent Gemini variant).  
- Implement exponential backoff for `ResourceExhausted` (quota) errors.  
- For production, store API keys in a secure secret store (Docker secrets, Vault, or GCP Secret Manager).

---

## ✅ Summary

| Component | Description | Example Container Name | Network |
|------------|--------------|------------------------|----------|
| PostgreSQL + pgvector | Vector storage backend | `pgvector-postgres-1` | `pgvector_default` |
| FastAPI App | Semantic search microservice | `doc-semantic-matching` | `pgvector_default` |
| Gemini API | Embedding provider | External service | N/A |

This setup ensures reliable inter-container communication, semantic vector retrieval, and scalable deployment across environments.
