import json

from app.schemas.document import (
    DocumentPage,
    DocumentType,
    ParsedDocument,
)
from app.services.ai_job_analyzer import AIJobAnalyzer


class FakeResponse:
    output_text = json.dumps(
        {
            "title": "Senior Software Engineer",
            "seniority": "senior",
            "summary": "Desenvolvimento de sistemas distribuídos.",
            "hard_skills": [
                {
                    "name": "Arquitetura de Software",
                    "importance": "required",
                    "description": None,
                }
            ],
            "soft_skills": [
                {
                    "name": "Liderança técnica",
                    "importance": "desired",
                    "description": None,
                }
            ],
            "technologies": [
                {
                    "name": "Java",
                    "importance": "required",
                    "description": None,
                },
                {
                    "name": "AWS",
                    "importance": "required",
                    "description": None,
                },
                {
                    "name": "Kafka",
                    "importance": "required",
                    "description": None,
                },
            ],
            "responsibilities": [
                "Desenvolver sistemas distribuídos"
            ],
            "differentiators": [
                "Experiência com liderança técnica"
            ],
        }
    )


class FakeResponses:
    def create(self, **kwargs):
        return FakeResponse()


class FakeOpenAIClient:
    responses = FakeResponses()


class FakeAIClient:
    def get_client(self):
        return FakeOpenAIClient()


def test_ai_job_analyzer_returns_job_profile():
    content = (
        "Senior Software Engineer\n"
        "Experiência com Java, AWS e Kafka.\n"
        "Liderança técnica será um diferencial."
    )

    document = ParsedDocument(
        filename="vaga_copiada",
        document_type=DocumentType.RAW_TEXT,
        content=content,
        character_count=len(content),
        page_count=1,
        pages=[
            DocumentPage(
                number=1,
                content=content,
            )
        ],
    )

    analyzer = AIJobAnalyzer(
        ai_client=FakeAIClient()
    )

    job = analyzer.analyze(document)

    assert job.title == "Senior Software Engineer"
    assert job.seniority == "senior"
    assert job.technologies[0].name == "Java"
    assert job.soft_skills[0].name == "Liderança técnica"