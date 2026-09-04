import json

from app.core.settings import settings
from app.schemas.assessment_summary import (
    AssessmentSummary,
)
from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.services.ai_client import AIClient


class AIAssessmentSummaryGenerator:
    def __init__(
        self,
        ai_client: AIClient | None = None,
    ):
        self.ai_client = ai_client or AIClient()
        self.client = self.ai_client.get_client()

    def generate(
        self,
        assessment: CandidateAssessment,
    ) -> AssessmentSummary:
        response = self.client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "Você é um especialista em apoio "
                        "a entrevistas de seleção.\n\n"
                        "Sua responsabilidade é produzir "
                        "comentários objetivos para o "
                        "entrevistador e recomendações de "
                        "curto, médio e longo prazo a partir "
                        "do assessment fornecido.\n\n"
                        "Regras obrigatórias:\n"
                        "- utilize somente informações "
                        "presentes no assessment;\n"
                        "- não altere scores;\n"
                        "- não altere o percentual de aderência;\n"
                        "- não crie competências;\n"
                        "- não crie novas experiências;\n"
                        "- não crie novos riscos;\n"
                        "- não faça decisão de contratação;\n"
                        "- não classifique competências com ausência ou baixa evidência "
                        "documental como pontos de desenvolvimento, gaps de competência "
                        "ou necessidades de capacitação;\n"
                        "- no longo prazo, não presuma necessidade de desenvolvimento "
                        "para competências apenas não evidenciadas no currículo; "
                        "nesses casos, recomende validação ou acompanhamento;\n"
                        "- ausência ou baixa evidência documental não significa ausência "
                        "da competência;\n"
                        "- enquanto a competência não tiver sido efetivamente avaliada, "
                        "trate-a apenas como ponto de validação, confirmação ou "
                        "acompanhamento;\n"
                        "- recomendações de desenvolvimento só podem ser feitas quando "
                        "existir evidência explícita no assessment de uma limitação, "
                        "necessidade de evolução ou competência efetivamente avaliada;\n"
                        "- ausência de evidência documental "
                        "não significa ausência de competência;\n"
                        "- comentários devem orientar a condução "
                        "da entrevista;\n"
                        "- evite repetir literalmente perguntas "
                        "já existentes;\n"
                        "- considere strengths, weaknesses, "
                        "skills, questions e risks;\n"
                        "- short_term deve orientar a entrevista "
                        "atual;\n"
                        "- medium_term deve indicar aspectos que "
                        "merecem aprofundamento caso o processo "
                        "continue;\n"
                        "- long_term deve indicar pontos de "
                        "desenvolvimento ou acompanhamento, "
                        "sem assumir contratação."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(
                        assessment
                    ),
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "assessment_summary",
                    "strict": True,
                    "schema": (
                        AssessmentSummary
                        .model_json_schema()
                    ),
                }
            },
        )

        return (
            AssessmentSummary
            .model_validate_json(
                response.output_text
            )
        )

    @staticmethod
    def _build_prompt(
        assessment: CandidateAssessment,
    ) -> str:
        payload = {
            "candidate_name": (
                assessment.candidate_name
            ),
            "job_title": assessment.job_title,
            "summary": assessment.summary,
            "adherence_percentage": (
                assessment.adherence_percentage
            ),
            "strengths": assessment.strengths,
            "weaknesses": assessment.weaknesses,
            "hard_skills": [
                {
                    "name": item.name,
                    "score": item.score,
                    "confidence": (
                        item.confidence.value
                    ),
                    "status": item.status,
                    "justification": (
                        item.justification
                    ),
                }
                for item in assessment.hard_skills
            ],
            "soft_skills": [
                {
                    "name": item.name,
                    "score": item.score,
                    "confidence": (
                        item.confidence.value
                    ),
                    "status": item.status,
                    "justification": (
                        item.justification
                    ),
                }
                for item in assessment.soft_skills
            ],
            "technologies": [
                {
                    "name": item.name,
                    "score": item.score,
                    "confidence": (
                        item.confidence.value
                    ),
                    "status": item.status,
                    "justification": (
                        item.justification
                    ),
                }
                for item in assessment.technologies
            ],
            "questions": [
                {
                    "competency": (
                        question.competency
                    ),
                    "priority": (
                        question.priority.value
                    ),
                    "category": (
                        question.category.value
                    ),
                    "reason": question.reason,
                }
                for question in assessment.questions
            ],
            "risks": [
                {
                    "competency": (
                        risk.competency
                    ),
                    "level": risk.level.value,
                    "category": (
                        risk.category.value
                    ),
                    "description": (
                        risk.description
                    ),
                }
                for risk in assessment.risks
            ],
        }

        return (
            "Produza os comentários e recomendações "
            "para o seguinte assessment:\n\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
        )