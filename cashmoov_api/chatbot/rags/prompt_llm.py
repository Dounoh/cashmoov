import json
import logging

from cashmoov_api.chatbot.rags.utils.adpter_api_llm import AdapterLlm

from .utils.huggin_face_api import HugginClient

logger = logging.getLogger(__name__)


def llm_humanise(query, context=""):
    """Génère une réponse humanisée basée sur le contexte RAG.

    Le contexte doit être une simple chaîne déjà préparée par la
    fonction de recherche (troncature et concatenation).
    """

    system_prompt = (
        "MODE QA STRICT.\n"
        "Tu es CashMoov IA.\n"
        "Règles : utilise uniquement le CONTEXTE, n’invente jamais.\n"
        "Si l’information est absente ou hors sujet, répond `response_none`.\n"
        "Français simple, réponse courte, une seule ligne.\n"
        "Si la question ne concerne pas CashMoov, précise que tu n’es pas formé.\n"
        "CashMoov ne fait que des trasfert electronique d'argent pas de carte physique ou de crédit.\n"
    )
    try:
        adapter = AdapterLlm(HugginClient())
        response = adapter.request(query, system_prompt, context=context)
        return response
    except Exception as e:
        logger.error(f"****Erreur lors de l'appel api du LLM: {str(e)}")
        return "veillez reesayer"


