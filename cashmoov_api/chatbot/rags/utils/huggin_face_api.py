import os
from openai import OpenAI 

class HugginClient:
    """
    Le clien api de deepseek 
    """

    base_url = "https://router.huggingface.co/v1"  
    api_key = os.getenv('HUGGIN_FACE_KEY')
    model_ia = "moonshotai/Kimi-K2-Instruct-0905"

    def request_ia(self, query, prompt_system):
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        completion = client.chat.completions.create(
            model=self.model_ia,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": query},
            ]
        )

        response_text = completion.choices[0].message.content
        return response_text
