# ============================
# Étape 1: BUILDER
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

# Installation des dépendances système nécessaires à la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Installation des dépendances Python dans le dossier .local de root
# + Téléchargement du modèle IA
RUN pip install --user --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-base').save('/app/local_model')"

# ============================
# Étape 2: RUNTIME
# ============================
FROM python:3.10-slim

WORKDIR /app

# Variables d'environnement pour Python et le modèle
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH" \
    MODEL_PATH="/app/local_model"

# Installation des dépendances d'exécution (libpq pour Postgres, netcat pour les healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Création de l'utilisateur non-root
RUN useradd -m -r appuser

# --- CORRECTION DES PERMISSIONS ---
# On donne la propriété du dossier /app à appuser AVANT de basculer
RUN chown -R appuser:appuser /app

USER appuser

# Récupération des fichiers du builder avec les bonnes permissions
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --from=builder --chown=appuser:appuser /app/local_model /app/local_model

# Copie du code source du projet
COPY --chown=appuser:appuser . .

# Création du dossier pour les fichiers statiques (Whitenoise)
RUN mkdir -p /app/staticfiles

EXPOSE 8000

# Utilisation de uvicorn pour l'exécution
# Note : En production, le collectstatic est souvent géré via le docker-compose command
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]