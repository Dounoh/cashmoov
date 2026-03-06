"""
Fonctions de recherche et de récupération de contexte RAG.

Ce module effectue :
- calcul et normalisation des embeddings de requête
- sélection des documents via pgvector (index ivfflat conseillé)
- mise en cache LRU des résultats pour éviter des requêtes identiques
- nettoyage des passages et limitation du nombre de tokens

Tout résultat renvoyé est une simple chaîne de texte, prête à être
jointée au prompt LLM. L'appel au modèle de génération n'est pas effectué
ici ; la fonction `search_documents` ne fait que l'accès synchrone/
async à la DB.
"""

import logging

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from pgvector.django import CosineDistance

from cashmoov_api.chatbot.models import Document
from cashmoov_api.chatbot.tasks import normalize_embedding

from .prompt_llm import llm_humanise

logger = logging.getLogger(__name__)


from functools import lru_cache


def search_documents_sync(query_text, top_k=2, min_similarity=0.2):
    """
    Recherche sémantique des documents les plus pertinents.

    Résultats mis en cache LRU pour éviter des requêtes répétées identiques.
    Voir `_search_documents_cached`.
    """
    return _search_documents_cached(query_text, top_k, min_similarity)


@lru_cache(maxsize=128)
def _search_documents_cached(query_text, top_k, min_similarity):
    # la logique précédente mais sans cache
    if not query_text or not query_text.strip():
        return ""

    try:
        norm_query = normalize_embedding(content=query_text, is_query=True)

        documents = (
            Document.objects.filter(is_active=True)
            .annotate(
                similarity=1.0 - CosineDistance("embedding", norm_query),
            )
            .filter(similarity__gte=min_similarity)
            .order_by("-similarity")
            .only("title", "content", "source_type")[:top_k]
        )
        
        documents = list(documents)
        if not documents:
            logger.info(f"Aucun document pertinent trouvé pour: {query_text}")
            return ""

        contexts = "\n\n".join(f"{doc.title}: {doc.content[:1000]}" for doc in documents)
        logger.info(f"***Trouvé {len(documents)} documents pour: {query_text}")
        return contexts

    except Exception as e:
        logger.error(f"***Erreur lors de la recherche: {str(e)}")
        return ""


async def search_documents(query_text, top_k=2, min_similarity=0.2):
    """Fonction async qui ne fait que la récupération vectorielle.
    L'appel au LLM doit être réalisé dans le consumer / la view afin de
    n'exécuter qu'un seul appel par requête.
    """
    results = await database_sync_to_async(search_documents_sync)(
        query_text, top_k, min_similarity=min_similarity
    )

    # results est désormais une chaîne de contexte ou ''
    return results or ""
