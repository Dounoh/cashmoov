from celery import shared_task
import numpy as np
from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.rags.lezy_model import get_model
import logging
logger = logging.getLogger(__name__)


def normalize_embedding(content):
    """
    Calcule et normalise l'embedding pour la similarité cosinus.
    """
    if not content or not content.strip():
        raise ValueError("Le contenu ne peut pas être vide")
    
    model = get_model()
    embedding = model.encode(content)
    norm = embedding / np.linalg.norm(embedding)
    return norm.tolist()


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
        # Prendre un titre plus long si nécessaire
        title = document.title or document.content[:100].strip()
        
        # Générer l'embedding
        embedding = normalize_embedding(content=document.content)
        
        # Sauvegarder
        document.title = title
        document.embedding = embedding
        document.save()
        
        logger.info(f"Embedding sauvegardé pour le document: {slug}")
        return {"success": True, "slug": slug}
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'embedding pour {slug}: {str(e)}")
        return {"success": False, "error": str(e)}
    


def chunk_text(text, chunk_size=500, overlap=100):
    """
    Découpe un texte long en morceaux avec chevauchement.
    Utile pour de longs documents.
    
    Args:
        text: Texte à découper
        chunk_size: Taille des morceaux en mots
        overlap: Chevauchement entre morceaux en mots
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks if chunks else [text]