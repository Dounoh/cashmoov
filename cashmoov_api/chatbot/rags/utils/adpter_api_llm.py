
class AdapterLlm:
    username = "CashMoov IA"

    def __init__(self, client):
        self.client = client

    def request(self, query, system_prompt):
        try:
            resultat = self.client.request_ia(query=query, system_prompt=system_prompt)
        except Exception as e:
            raise Exception(f"Erreur LLM: {str(e)}")
        
        if resultat == 'response_none':
            type = 'response_none'
        else:
            type = 'discussion'

        return {
            "username": self.username,
            "response": resultat,
            "type": type,
            "source": "",
            "destination": ""
        }
