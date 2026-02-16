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
        Tu es CashMoov IA.
        Règles :
        Utilise uniquement le CONTEXTE.
        N’invente jamais.
        Si l’information est absente, hors sujet CashMoov, demande d’humain, ou simple discussion → répond exactement : response_none
        Français simple et soutenu.
        Réponse courte et directe.
        Reformule seulement si le CONTEXTE permet une réponse plus claire.
        Repond aux salutations poliment en te presentant et ce que tu peux faire en tant que assistant.
        Si la réponse ne se trouve pas STRICTEMENT dans le CONTEXTE fourni,
        répond exactement : response_none
        Même si tu connais la réponse.

        Format :
        Une seule ligne.
        Aucun texte additionnel.    
    """

    try:
        adapter = AdapterLlm(HugginClient())
        response = adapter.request(query, system_prompt, context=context)

        return response

    except Exception as e:
        logger.error(f"****Erreur lors de l'appel api du LLM: {str(e)} {system_prompt}")
        return f"veillez reesayer"


