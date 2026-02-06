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


def normalize_embedding(content: str, *, is_query: bool = False):
    """ "
    Cette fonction nous permet de faire le calcule
    du embedding et la normalisation des vecteurs.
    """
    if not content or not content.strip():
        raise ValueError("Le contenu ne peut pas être vide")

    prefix = "query: " if is_query else "passage: "
    text = prefix + content.strip()

    model, tokenizer = get_model()

    with torch.no_grad():
        inputs = tokenizer(
            text, return_tensors="pt", padding=True, truncation=True, max_length=512
        )
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
    print('************* fin de la normalisation et embeding **********')
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
    Utile pour de longs documents.

    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks if chunks else [text]
