import os
from openai import OpenAI

class DeepSeekClient:
    """
    Le clien api de deepseek 
    """
    
    base_url="https://api.deepseek.com"
    api_key = os.getenv('DEEPSEEK_KEY')
    model_ia ="deepseek-chat"

    def request_ia(self, query, prompt_system):

        client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url
            )

        response = client.chat.completions.create(
            model=self.model_ia,
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": query},
            ],
            stream=False
        )        
        response_text = response.choices[0].message.content

        return response_text
