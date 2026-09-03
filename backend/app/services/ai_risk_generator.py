import json

from app.core.settings import settings
from app.schemas.risk_intelligence import (
    RiskAssessment,
    RiskAssessmentSet,
)
from app.services.ai_client import AIClient
from app.services.risk_focus_builder import (
    RiskFocus,
)


class AIRiskGenerator:
    def __init__(
        self,
        ai_client: AIClient | None = None,
    ):
        self.ai_client = ai_client or AIClient()
        self.client = self.ai_client.get_client()

    def generate(
        self,
        focuses: list[RiskFocus],
    ) -> list[RiskAssessment]:
        if not focuses:
            return []

        response = self.client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em avaliação "
                        "documental de candidatos.\n\n"
                        "Sua responsabilidade é SOMENTE redigir "
                        "pontos de atenção a partir dos focos "
                        "fornecidos.\n\n"
                        "Regras obrigatórias:\n"
                        "- gere exatamente um item por foco;\n"
                        "- preserve exatamente competency;\n"
                        "- preserve exatamente o nível do risco;\n"
                        "- preserve exatamente a categoria do risco;\n"
                        "- não crie novos riscos;\n"
                        "- não aumente nem reduza severidade;\n"
                        "- não conclua ausência de competência;\n"
                        "- ausência de evidência documental não "
                        "significa ausência da competência;\n"
                        "- descreva o item como ponto que precisa "
                        "ser validado;\n"
                        "- não faça recomendação de contratação;\n"
                        "- validation_question deve ser aberta e "
                        "buscar evidência concreta."
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
                    "name": "risk_assessments",
                    "strict": True,
                    "schema": (
                        RiskAssessmentSet
                        .model_json_schema()
                    ),
                }
            },
        )

        result = (
            RiskAssessmentSet
            .model_validate_json(
                response.output_text
            )
        )

        risks = result.risks

        self._validate_result(
            focuses,
            risks,
        )

        return risks

    @staticmethod
    def _build_prompt(
        focuses: list[RiskFocus],
    ) -> str:
        payload = [
            {
                "competency": focus.competency,
                "level": focus.level.value,
                "risk_category": (
                    focus.risk_category.value
                ),
                "score": focus.score,
                "description": focus.description,
            }
            for focus in focuses
        ]

        return (
            "Redija os pontos de atenção para os "
            "seguintes focos:\n\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )

    @staticmethod
    def _validate_result(
        focuses: list[RiskFocus],
        risks: list[RiskAssessment],
    ) -> None:
        if len(risks) != len(focuses):
            raise ValueError(
                "A IA deve retornar exatamente "
                "um risco para cada foco."
            )

        expected = {
            (
                focus.competency,
                focus.level.value,
                focus.risk_category.value,
            )
            for focus in focuses
        }

        returned = {
            (
                risk.competency,
                risk.level.value,
                risk.category.value,
            )
            for risk in risks
        }

        if expected != returned:
            raise ValueError(
                "Os riscos retornados não "
                "correspondem exatamente aos focos "
                "selecionados."
            )