FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip wheel setuptools && \
    pip install -r requirements.txt

# Une seule ligne pour télécharger le modèle
RUN python -c "import sentence_transformers; model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2'); model.save('/app/local_model')"

COPY . .

EXPOSE 8000 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]