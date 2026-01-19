from .huggin_face_api import HugginClient
from .deepseek_api import DeepSeekClient


class AdpterLlm:
    """ 
    Cette fonction est un adaptateur des Clients api
    il nous permet de garder le meme syntaxe quelque soit le client api qu'on appel 
    deepseek, chatgpt, hugginface, kimi etc.. 
    il vas retourne le meme resultat sans probleme pour ne pas casser la view
    """
    username = "CashMoov IA"

    def __init__(self,client):
        self.client = client

    def request(self, query, prompt_system):
        resultat = self.client.request_ia(query=query, prompt_system=prompt_system)
    
        return {
        "username": self.username,
        "message": resultat
    }

