import json
import logging

from cashmoov_api.chatbot.rags.utils.adpter_api_llm import AdapterLlm

from .utils.huggin_face_api import HugginClient

logger = logging.getLogger(__name__)


def llm_humanise(query, context=None):
    """
    Génère une réponse humanisée avec le LLM basée sur le contexte RAG.
    """

    system_prompt = f"""
                    MODE QA STRICT. Tu es CashMoov IA. Répond du CONTEXTE; ne rien inventer; response_none si aucune info ou demande humaine; reformule si CONTEXTE utile; français simple; string unique, pas de retour à la ligne pas de \n.
                    """

    try:
        adapter = AdapterLlm(HugginClient())
        response = adapter.request(query, system_prompt, context=context)

        return response

    except Exception as e:
        logger.error(f"****Erreur lors de l'appel api du LLM: {str(e)} {system_prompt}")
        return f"veillez reesayer"
