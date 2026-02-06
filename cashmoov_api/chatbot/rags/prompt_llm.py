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
        MODE QA STRICT.

        Tu es CashMoov IA, assistant client CashMoov.

        Règles :
        - Utiliser uniquement les informations du CONTEXTE.
        - Ne jamais inventer ni compléter une information.
        - Si la réponse n’est pas dans le CONTEXTE, répondre exactement : response_none
        - Français simple.
        - Réponse courte, claire, directe.
        - Reformule la question uniquement si tu as des contexts pertinants pour donnee une reponse claire et professionnel.
        - Si tu n'as pas de contexte pour la question repond simplement: response_none.

        Format :
        - Une seule string
        - Aucun retour à la ligne
        - Aucun texte additionnel

    """

    try:
        adapter = AdapterLlm(HugginClient())
        response = adapter.request(query, system_prompt, context=context)

        return response

    except Exception as e:
        logger.error(f"****Erreur lors de l'appel api du LLM: {str(e)} {system_prompt}")
        return f"veillez reesayer"
