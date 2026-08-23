import json

from app.schemas.document import (
    DocumentPage,
    DocumentType,
    ParsedDocument,
)
from app.services.ai_resume_analyzer import AIResumeAnalyzer


class FakeResponse:
    output_text = json.dumps(
        {
            "candidate_name": "João Silva",
            "professional_summary": (
                "Engenheiro de software com experiência "
                "em sistemas distribuídos."
            ),
            "experiences": [
                {
                    "company": "Empresa X",
                    "role": "Senior Software Engineer",
                    "start_date": "2022",
                    "end_date": "2026",
                    "responsibilities": [
                        "Desenvolvimento de microsserviços",
                        "Participação em decisões arquiteturais",
                    ],
                    "achievements": [
                        "Redução de 30% no tempo de processamento"
                    ],
                    "technologies": [
                        "Java",
                        "AWS",
                        "Kafka",
                    ],
                }
            ],
            "education": [],
            "certifications": [],
            "hard_skills": [
                {
                    "skill": "Arquitetura de Software",
                    "evidence": [
                        {
                            "text": "Participação em decisões arquiteturais",
                            "source": "experience",
                            "source_reference": (
                                "Senior Software Engineer - Empresa X"
                            ),
                            "page": 1,
                        }
                    ],
                }
            ],
            "soft_skill_evidences": [],
            "technologies": [
                {
                    "skill": "Kafka",
                    "evidence": [
                        {
                            "text": (
                                "Desenvolvimento de microsserviços "
                                "utilizando Kafka"
                            ),
                            "source": "experience",
                            "source_reference": (
                                "Senior Software Engineer - Empresa X"
                            ),
                            "page": 1,
                        }
                    ],
                }
            ],
            "leadership_evidences": [
                "Atuação como referência técnica do time"
            ],
            "measurable_results": [
                "Redução de 30% no tempo de processamento"
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


def test_ai_resume_analyzer_returns_resume_profile():
    content = (
        "João Silva\n"
        "Senior Software Engineer\n"
        "Experiência com Java, AWS e Kafka."
    )

    document = ParsedDocument(
        filename="curriculo.pdf",
        document_type=DocumentType.PDF,
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

    analyzer = AIResumeAnalyzer(
        ai_client=FakeAIClient()
    )

    resume = analyzer.analyze(document)

    assert resume.candidate_name == "João Silva"
    assert resume.experiences[0].company == "Empresa X"
    assert resume.hard_skills[0].skill == "Arquitetura de Software"
    assert resume.technologies[0].skill == "Kafka"
    assert resume.technologies[0].evidence[0].page == 1


def test_build_document_with_pages_preserves_page_numbers():
    document = ParsedDocument(
        filename="curriculo.pdf",
        document_type=DocumentType.PDF,
        content="Conteúdo página 1\nConteúdo página 2",
        character_count=35,
        page_count=2,
        pages=[
            DocumentPage(
                number=1,
                content="Experiência com Java",
            ),
            DocumentPage(
                number=2,
                content="Experiência com Kafka",
            ),
        ],
    )

    analyzer = AIResumeAnalyzer(
        ai_client=FakeAIClient()
    )

    result = analyzer._build_document_with_pages(
        document
    )

    assert "--- PAGE 1 ---" in result
    assert "Experiência com Java" in result

    assert "--- PAGE 2 ---" in result
    assert "Experiência com Kafka" in result