from openai import OpenAI

from app.core.settings import settings


class AIClient:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY não configurada.")

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def get_client(self) -> OpenAI:
        return self.client