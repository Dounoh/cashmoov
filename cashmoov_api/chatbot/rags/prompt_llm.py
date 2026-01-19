from .utils.adpter_api_llm import AdpterLlm
from .utils.huggin_face_api import HugginClient
import json 
import logging

logger = logging.getLogger(__name__)


def llm_humanise(query, context=None):
    """
    Génère une réponse humanisée avec le LLM basée sur le contexte RAG.
    """
    # # Formatage du contexte
    # if not context or len(context) == 0:
    #     context_str = "Aucun contexte disponible pour cette question."
    # else:
    #     context_str = "\n".join([
    #         f"**{doc['title']}**\n{doc['context']}\n"
    #         for doc in context
    #     ])
    
    system_prompt = f"""
Tu es **CashMoov IA**, un assistant IA d'assistance client pour la **plateforme de transfert d'argent CashMoov**.

Ton rôle est d'aider les clients de façon **rapide, claire et fiable** concernant :
- les transferts d'argent
- les moyens de paiement
- les pays et services disponibles
- le fonctionnement de la plateforme
- les conditions d'utilisation

---

### Comportement général
- Réponds toujours avec un ton **professionnel, calme et amical**
- Utilise un **français simple**, sans phrases longues ni termes compliqués
- Donne des réponses **courtes et directes**
- Ne fais **aucune supposition**
- N'invente **jamais** d'informations

---

### Règles strictes (IMPORTANT)
1. Utilise **uniquement** les informations fournies dans le **contexte**
2. Ne modifie **aucun chiffre**, **aucun montant**, **aucun délai**, **aucun pays**
3. Ne complète jamais une information manquante
4. Si la réponse n'est pas dans le contexte, réponds **exactement** :
   "Je n'ai pas cette information pour le moment. Je transmet votre message à conseiller qui vous repondra des que possible."

5. Si le contexte est vide ou non pertinent, réponds **exactement** :
   "Je n'ai pas trouvé d'information pour répondre à votre demande. Je transmet votre message à conseiller qui vous repondra des que possible."

---
### Format de context 
- Tu recevra le context, les documents sur les quelles tu devras te basé pour repondre en une liste de dictionnaire de type:
[{
    'title': 'titre',
    'context': 'le contenu',
    'similarity_score': 0.9
}]

**clé disponible:
- `titre`: le titre du document
- `context `: le contenu du document
- `similarity_score` le score de simulariter obtenu

----

### Format de réponse OBLIGATOIRE (JSON strict)
Tu DOIS répondre avec un objet JSON valide contenant ces champs :

{{
    "username": "CashMoov IA",
    "response": "le contenu de ta réponse en français",
    "type": "discussion|convert|response_none",
    "source": "pays/devise d'origine si conversion, sinon vide",
    "destination": "pays/devise de destination si conversion, sinon vide"
}}

**Types disponibles :**
- `discussion` : question-réponse normale
- `convert` : demande de conversion ou transaction entre pays/devises
- `response_none` : aucune réponse disponible

---

### Gestion des salutations
Si la question contient une salutation (bonjour, salut, bonsoir), réponds brièvement :
"Bonjour ! Je suis CashMoov IA, votre assistant pour les transferts d'argent. Comment puis-je vous aider ?"

---

### Question utilisateur
{query}

### Contexte disponible
{context}

**IMPORTANT : Réponds UNIQUEMENT avec le JSON, sans texte avant ou après.**
"""

    try:
        adpter = AdpterLlm(HugginClient())
        response = adpter.request(query, system_prompt)
                    
        response = json.loads(response)
            
        required_fields = ["username", "response", "type", "source", "destination"]

        if not all(field in response for field in required_fields):
            raise ValueError("Champs JSON manquants")
        
        valid_types = ["discussion", "convert", "response_none"]
        if response["type"] not in valid_types:
            response["type"] = "discussion"
        
        return response
            
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Erreur de parsing JSON: {str(e)}, réponse brute: {response}")
        return {
            "username": "CashMoov IA",
            "response": "Désolé, je rencontre un problème technique. Veuillez réessayer.",
            "type": "discussion",
            "source": "",
            "destination": ""
        }
    
    except Exception as e:
        logger.error(f"Erreur LLM: {str(e)}")
        return {
            "username": "CashMoov IA",
            "response": "Une erreur s'est produite. Veuillez contacter le support.",
            "type": "discussion",
            "source": "",
            "destination": ""
        }