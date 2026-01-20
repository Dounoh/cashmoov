import os
import requests
import json

class HugginClient:
    """
    Client API pour HuggingFace Inference Router (version requests)
    """

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {os.environ.get('HUGGIN_FACE_KEY')}",
        "Content-Type": "application/json"
    }

    model_ia = "zai-org/GLM-4.7:novita" 

    def request_ia(self, query, system_prompt):
        """
        Envoie la question et le contexte au LLM et récupère le JSON complet.
        """

        payload = {
            "model": self.model_ia,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        }

        response = requests.post(
            self.API_URL,
            headers=self.HEADERS,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"HuggingFace API error: {response.text}")

        data = response.json()

        llm_text = data["choices"][0]["message"]["content"]

        return llm_text
