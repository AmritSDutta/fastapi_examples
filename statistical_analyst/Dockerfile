# Dockerfile — containerized Gradio + Gemini UI (production-ready, minimal)
FROM python:3.11-slim

# System deps for common wheels and Google libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application sources
COPY . /app

# Non-root runtime user for safer execution
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860

EXPOSE 7860

WORKDIR /app
CMD ["python", "-m", "app.analyst_gradio_ui"]
