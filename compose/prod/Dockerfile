# ============================
# Étape 1: BUILDER
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installation des dépendances + téléchargement du modèle IA
RUN pip install --user --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base').save('/app/local_model')"

# ============================
# Étape 2: RUNTIME
# ============================
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    MODEL_PATH="/app/local_model"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur et son home pour .local
RUN useradd -m -r appuser
USER appuser

# Copier les librairies ET le modèle téléchargé depuis le builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appuser /app/local_model /app/local_model

# Copier le reste du code
COPY --chown=appuser:appuser . .

EXPOSE 8000

# Utiliser uvicorn pour FastAPI (Asynchrone)
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]