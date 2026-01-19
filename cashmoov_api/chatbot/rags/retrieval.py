from cashmoov_api.chatbot.models import Document
from .prompt_llm import llm_humanise
from cashmoov_api.chatbot.tasks import normalize_embedding
from pgvector.django import CosineDistance
import logging

logger = logging.getLogger(__name__)

def search_documents(query_text, top_k=5, max_similarity=0.7):
    """
    Recherche sémantique des documents les plus pertinents.
    Cette fonction nous permet de retrouver les 5 documents les plus pertinents
    concernant la question poser par le user et envoyer à LLM pour reformuler et renvoyer le resultat
    """
    if not query_text or not query_text.strip():
        return []
    
    try:

        norm_query = normalize_embedding(content=query_text)
        
        documents = (
            Document.objects
            .filter(is_active=True)
            .annotate(similarity=CosineDistance('embedding', norm_query))
            .filter(similarity__lte=max_similarity)
            .order_by('similarity')[:top_k]
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
        resultats_llm = llm_humanise(results)
        return resultats_llm
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche: {str(e)}")
        return []