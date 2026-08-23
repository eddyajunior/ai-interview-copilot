from openai import OpenAI

from app.core.settings import settings


class AIClient:
    def __init__(
        self,
        api_key: str | None = None,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY não configurada."
            )

        self.client = OpenAI(
            api_key=self.api_key
        )

    def get_client(self) -> OpenAI:
        return self.client