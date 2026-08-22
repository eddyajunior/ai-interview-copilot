import pytest

from app.schemas.document import (
    DocumentPage,
    DocumentType,
    ParsedDocument,
)
from app.services.job_analyzer import JobAnalyzer


# def test_job_analyzer_returns_job_profile():
#     document = ParsedDocument(
#         filename="vaga_copiada",
#         document_type=DocumentType.RAW_TEXT,
#         content="Senior Software Engineer com Java, AWS e Kafka.",
#         character_count=51,
#         page_count=1,
#         pages=[
#             DocumentPage(
#                 number=1,
#                 content="Senior Software Engineer com Java, AWS e Kafka.",
#             )
#         ],
#     )

#     analyzer = JobAnalyzer()

#     job = analyzer.analyze(document)

#     assert job.title == "Não identificado"
#     assert job.summary == document.content
#     assert job.hard_skills == []
#     assert job.soft_skills == []
#     assert job.technologies == []


def test_job_analyzer_identifies_job_information():
    content = (
        "Senior Software Engineer\n"
        "Buscamos profissional com experiência em Java, AWS e Kafka.\n"
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

    analyzer = JobAnalyzer()

    job = analyzer.analyze(document)

    assert job.title == "Senior Software Engineer"
    assert job.seniority == "senior"

    technologies = [
        requirement.name
        for requirement in job.technologies
    ]

    assert "Java" in technologies
    assert "AWS" in technologies
    assert "Kafka" in technologies

    soft_skills = [
        requirement.name
        for requirement in job.soft_skills
    ]

    assert "Liderança técnica" in soft_skills


def test_job_analyzer_rejects_empty_document():
    document = ParsedDocument(
        filename="vaga_vazia",
        document_type=DocumentType.RAW_TEXT,
        content=" ",
        character_count=1,
        page_count=1,
        pages=[
            DocumentPage(
                number=1,
                content=" ",
            )
        ],
    )

    analyzer = JobAnalyzer()

    with pytest.raises(ValueError):
        analyzer.analyze(document)