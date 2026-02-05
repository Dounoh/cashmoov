class AdapterLlm:
    """
    L'adapteur des different api pour garder le meme format de reponse retourner
    dans les autres fonctions (Design adpter).
    """

    username = "CashMoov IA"

    def __init__(self, client):
        self.client = client

    def request(self, query, system_prompt, context):
        try:
            resultat = self.client.request_ia(query=query, system_prompt=system_prompt, context=context)
        except Exception as e:
            raise Exception(f"Erreur LLM: {str(e)}")

        if resultat == "response_none":
            type = "response_none"
        else:
            type = "discussion"

        return {
            "username": self.username,
            "message": resultat,
            "type": type,
            "source": "",
            "destination": "",
        }
