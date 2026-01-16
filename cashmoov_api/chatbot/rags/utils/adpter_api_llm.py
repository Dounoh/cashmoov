from .huggin_face_api import HugginClient
from .deepseek_api import DeepSeekClient


class AdpterLlm:
    username = "CashMoov IA"

    def __init__(self,client):
        self.client = client

    def request(self, query, prompt_system):
        resultat = self.client.request_ia(query=query, prompt_system=prompt_system)
    
        return {
        "username": self.username,
        "message": resultat
    }

