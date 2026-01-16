# ============================
# Étape 1: BUILDER
# ============================
FROM python:3.10-slim AS builder

WORKDIR /app

# Outils nécessaires pour compiler certaines dépendances
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

# Installer les dépendances dans /root/.local (isolé)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip wheel setuptools && \
    pip install --user --no-warn-script-location -r requirements.txt


# ============================
# Étape 2: RUNTIME (PRODUCTION)
# ============================
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Dépendances système minimales au runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copier les dépendances depuis le builder
COPY --from=builder /root/.local /root/.local

# Copier le code applicatif
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
