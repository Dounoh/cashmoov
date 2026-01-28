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

RUN python -c "import sentence_transformers; model = sentence_transformers.SentenceTransformer('intfloat/multilingual-e5-base'); model.save('/app/local_model')"

COPY . .

EXPOSE 8000 8001

CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
