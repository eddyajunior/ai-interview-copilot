import json

from app.schemas.interview_intelligence import (
    InterviewQuestionSet,
)
from app.services.ai_client import AIClient
from app.services.interview_focus_builder import (
    InterviewFocus,
)


class AIInterviewQuestionGenerator:
    def __init__(
        self,
        ai_client: AIClient | None = None,
    ):
        self.ai_client = ai_client or AIClient()
        self.client = self.ai_client.get_client()

    def generate(
        self,
        focuses: list[InterviewFocus],
    ) -> InterviewQuestionSet:
        if not focuses:
            return InterviewQuestionSet(
                questions=[]
            )

        response = self.client.responses.create(
            model=self._get_model(),
            input=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em entrevistas "
                        "técnicas e comportamentais.\n\n"
                        "Sua responsabilidade é SOMENTE formular "
                        "perguntas de entrevista a partir dos focos "
                        "fornecidos.\n\n"
                        "Regras obrigatórias:\n"
                        "- gere exatamente uma pergunta por foco;\n"
                        "- preserve exatamente a competência;\n"
                        "- preserve exatamente a categoria;\n"
                        "- preserve exatamente a prioridade;\n"
                        "- não crie novas competências;\n"
                        "- não remova competências;\n"
                        "- não altere scores;\n"
                        "- não faça recomendação de contratação;\n"
                        "- não conclua ausência de competência pela "
                        "ausência de evidência no currículo;\n"
                        "- perguntas devem buscar exemplos concretos;\n"
                        "- prefira perguntas abertas e situacionais;\n"
                        "- evite perguntas que possam ser respondidas "
                        "apenas com sim ou não;\n"
                        "- o follow-up deve aprofundar a resposta;\n"
                        "- what_to_observe deve orientar objetivamente "
                        "o entrevistador."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(
                        focuses
                    ),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": (
                        "interview_question_set"
                    ),
                    "strict": True,
                    "schema": (
                        InterviewQuestionSet
                        .model_json_schema()
                    ),
                }
            },
        )

        result = InterviewQuestionSet.model_validate_json(
            response.output_text
        )

        self._validate_result(
            focuses,
            result,
        )

        return result

    @staticmethod
    def _build_prompt(
        focuses: list[InterviewFocus],
    ) -> str:
        payload = [
            {
                "competency": focus.competency,
                "category": focus.category.value,
                "priority": focus.priority.value,
                "score": focus.score,
                "reason": focus.reason,
            }
            for focus in focuses
        ]

        return (
            "Gere perguntas de entrevista para os "
            "seguintes focos:\n\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )

    @staticmethod
    def _validate_result(
        focuses: list[InterviewFocus],
        result: InterviewQuestionSet,
    ) -> None:
        if len(result.questions) != len(focuses):
            raise ValueError(
                "A IA deve retornar exatamente "
                "uma pergunta para cada foco."
            )

        expected = {
            (
                focus.competency,
                focus.category.value,
                focus.priority.value,
            )
            for focus in focuses
        }

        returned = {
            (
                question.competency,
                question.category.value,
                question.priority.value,
            )
            for question in result.questions
        }

        if expected != returned:
            raise ValueError(
                "As perguntas retornadas não "
                "correspondem exatamente aos focos "
                "selecionados."
            )

    def _get_model(self) -> str:
        from app.core.settings import settings

        return settings.OPENAI_MODEL