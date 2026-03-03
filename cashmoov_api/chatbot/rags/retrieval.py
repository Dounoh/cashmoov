import logging

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.db.models import F, FloatField
from django.db.models.functions import Cast
from pgvector.django import CosineDistance

from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.tasks import normalize_embedding

from .prompt_llm import llm_humanise

logger = logging.getLogger(__name__)


def search_documents_sync(query_text, top_k=2, min_similarity=0.75):
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
            Document.objects.filter(is_active=True)
            .annotate(
                distance=CosineDistance("embedding", norm_query),
                similarity=1.0 - Cast(F("distance"), FloatField()),
            )
            .filter(similarity__gte=min_similarity)
            .order_by("-similarity")
            .only("title", "content", "source_type")[:top_k]
        )
        
        documents = list(documents)
        if len(documents) == 0:
            logger.info(f"Aucun document pertinent trouvé pour: {query_text}")
            return []

        results = [
            {
                "context": f"{doc.title} :{doc.content}",
            }
            for doc in documents
        ]

        logger.info(f"***Trouvé {len(results)} documents pour: {query_text}")

        return results

    except Exception as e:
        logger.error(f"***Erreur lors de la recherche: {str(e)}")
        return []


async def search_documents(query_text, top_k=3, min_similarity=0.75):
    results = await database_sync_to_async(search_documents_sync)(
        query_text, top_k, min_similarity=min_similarity
    )

    if not results:
        return []

    try:
        resultats_llm = await sync_to_async(llm_humanise)(
            query=query_text, context=results
        )
        return resultats_llm
    except Exception as e:
        logger.error(f"****Erreur LLM: {str(e)}")
        return []
