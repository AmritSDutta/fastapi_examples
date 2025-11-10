FROM python:3.11-slim

# install build deps to compile psycopg2 (libpq + python headers + build tools)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
