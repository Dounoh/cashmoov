from cashmoov_api.chatbot.models import Document
from .prompt_llm import llm_humanise
from cashmoov_api.chatbot.tasks import normalize_embedding
from pgvector.django import CosineDistance
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import logging
from django.db.models import F, FloatField
from django.db.models.functions import Cast

logger = logging.getLogger(__name__)

def search_documents_sync(query_text, top_k=5, max_similarity=0.7):
    """
    Recherche sémantique des documents les plus pertinents.
    Cette fonction nous permet de retrouver les 5 documents les plus pertinents
    concernant la question poser par le user et envoyer à LLM pour reformuler et renvoyer le resultat
    """
    if not query_text or not query_text.strip():
        return []
    
    try:

        norm_query = normalize_embedding(content=query_text, is_query=True)
        
        # documents = (
        #     Document.objects
        #     .filter(is_active=True)
        #     .annotate(similarity=CosineDistance('embedding', norm_query))
        #     .filter(similarity__lte=max_similarity)
        #     .order_by('similarity')[:top_k]
        # )

        documents = (
            Document.objects
            .filter(is_active=True)
            .annotate(
                distance=CosineDistance('embedding', norm_query),
                # Utiliser Cast pour convertir en float avant la soustraction
                similarity=1.0 - Cast(F('distance'), FloatField())
            )
            .filter(similarity__gte=0.2)
            .order_by('-similarity')
            .only('title', 'content', 'source_type')[:top_k]
        )
        
        if not documents.exists():
            logger.info(f"Aucun document pertinent trouvé pour: {query_text}")
            return []
        
        results = [{
            'title': doc.title,
            'context': doc.content,
            'similarity_score': float(doc.similarity)
        } for doc in documents]
        
        logger.info(f"Trouvé {len(results)} documents pour: {query_text}")
        
        return results
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {str(e)}")
        return []
    


async def search_documents(query_text, top_k=5, max_similarity=0.7):
    results = await database_sync_to_async(search_documents_sync)(query_text, top_k, max_similarity)

    if not results:
        return []

    try:
        resultats_llm = await sync_to_async(llm_humanise)(query=query_text,context=results)
        return resultats_llm
        # return []
    except Exception as e:
        logger.error(f"Erreur LLM: {str(e)}")
        return []

