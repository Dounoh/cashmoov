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

    # model_ia = "zai-org/GLM-4.7:novita" 
    model_ia = "meta-llama/Meta-Llama-3-8B-Instruct"

    def request_ia(self, query, system_prompt, context):
        """
        Envoie la question et le contexte au LLM et récupère le JSON complet.
        """

        payload = {
            "model": self.model_ia,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"QUESTION:\n{query}"
                },
                {
                    "role": "user",
                    "content": f"CONTEXTE:\n{context}"
                }
            ],
            "temperature": 0,
            "max_tokens": 256
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
