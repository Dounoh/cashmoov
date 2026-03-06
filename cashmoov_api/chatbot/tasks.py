import logging

import numpy as np
import torch
from celery import shared_task

from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.rags.lezy_model import get_model

logger = logging.getLogger(__name__)


# def normalize_embedding(content):
#     """
#     Calcule et normalise l'embedding pour la similarité cosinus.
#     """
#     if not content or not content.strip():
#         raise ValueError("Le contenu ne peut pas être vide")

#     model = get_model()
#     embedding = model.encode(content)
#     norm = embedding / np.linalg.norm(embedding)
#     return norm.tolist()


from functools import lru_cache


def normalize_embedding(content: str, *, is_query: bool = False):
    """ 
    Calcule et normalise l'embedding pour la similarité cosinus.

    Le même texte est utilisé pour la requête et le passage. On évite
    le préfixe "query:/passage" afin de conserver l'espace de vecteurs
    identique pour toutes les entrées.

    Pour les requêtes fréquentes on garde un petit cache LRU afin de
    réduire les calculs CPU/GPU.
    """

    if not content or not content.strip():
        raise ValueError("Le contenu ne peut pas être vide")

    text = content.strip()

    # cache uniquement les embeddings de requêtes, pas ceux des documents
    if is_query:
        return _cached_embedding(text)

    model, tokenizer = get_model()

    with torch.no_grad():
        inputs = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)

    return embedding[0].cpu().numpy().tolist()


@lru_cache(maxsize=256)
def _cached_embedding(text: str):
    """Calcule un embedding et le met en cache (LRU)."""
    model, tokenizer = get_model()
    with torch.no_grad():
        inputs = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
    return embedding[0].cpu().numpy().tolist()


@shared_task
def save_embedding(slug):
    """
    Sauvegarde l'embedding d'un document en base de données.
    Tâche Celery asynchrone.
    """
    try:
        document = Document.objects.get(slug=slug)
    except Document.DoesNotExist:
        logger.error(f"Document avec slug '{slug}' introuvable")
        return {"success": False, "error": "Document not found"}

    try:
        title = document.title or document.content[:100].strip()

        # si le texte est très long, le découper en chunks et créer des
        # documents supplémentaires afin d'améliorer la granularité de la
        # recherche vectorielle. Cela double ou triple le nombre d'entrées
        # mais évite les réponses hors-sujet causées par un long contexte.
        chunks = chunk_text(document.content)
        if len(chunks) > 1:
            # remplacer le contenu du document original par le premier chunk
            document.content = chunks[0]
            document.embedding = normalize_embedding(content=chunks[0])
            document.title = title
            document.save()
            # créer des documents enfants pour les autres morceaux
            for idx, chunk in enumerate(chunks[1:], start=1):
                Document.objects.create(
                    title=f"{title} (part {idx})",
                    content=chunk,
                    embedding=normalize_embedding(content=chunk),
                    embedding_model=document.embedding_model,
                    source_type=document.source_type,
                    is_active=document.is_active,
                )
            logger.info(
                f"Document {slug} découpé en {len(chunks)} parties pour indexation"
            )
            return {"success": True, "slug": slug}

        # sinon traitement normal
        embedding = normalize_embedding(content=document.content)

        document.title = title
        document.embedding = embedding
        document.save()

        logger.info(f"Embedding sauvegardé pour le document: {slug}")
        return {"success": True, "slug": slug}

    except Exception as e:
        logger.error(
            f"Erreur lors de la génération de l'embedding pour {slug}: {str(e)}"
        )
        return {"success": False, "error": str(e)}


def chunk_text(text, chunk_size=500, overlap=100):
    """
    Découpe un texte long en morceaux avec chevauchement.

    Pourquoi ? Les documents volumineux ont tendance à noyer la recherche
    vectorielle : un passage pertinent peut se retrouver noyé dans un long
    texte. En découpant, on crée plusieurs entrées de base, ce qui améliore
    la granularité du RAG. La fonction est utilisée dans le traitement des
    embeddings lors de la sauvegarde d'un Document (voir `save_embedding`).
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks if chunks else [text]
