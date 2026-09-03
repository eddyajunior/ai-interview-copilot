import json
from unittest.mock import Mock

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
)
from app.services.ai_assessment_summary_generator import (
    AIAssessmentSummaryGenerator,
)


def build_assessment():
    return CandidateAssessment(
        candidate_name="Teste",
        job_title="Engineering Manager",
        summary="Assessment de teste",
        adherence_percentage=72.0,
        strengths=[
            "Boa experiência em arquitetura"
        ],
        weaknesses=[
            "Pouca evidência documental de DevOps"
        ],
        hard_skills=[],
        soft_skills=[],
        technologies=[],
        questions=[],
        risks=[],
        interviewer_comments=[],
        recommendation=Recommendation(
            short_term="",
            medium_term="",
            long_term="",
        ),
    )


def build_response():
    response = Mock()

    response.output_text = json.dumps(
        {
            "interviewer_comments": [
                (
                    "Aprofundar exemplos concretos "
                    "de atuação em DevOps."
                ),
                (
                    "Validar autonomia em decisões "
                    "de arquitetura."
                ),
            ],
            "recommendation": {
                "short_term": (
                    "Priorizar a validação dos pontos "
                    "com menor evidência documental."
                ),
                "medium_term": (
                    "Aprofundar experiências práticas "
                    "nas competências críticas da vaga."
                ),
                "long_term": (
                    "Acompanhar evolução das competências "
                    "que apresentaram menor evidência."
                ),
            },
        },
        ensure_ascii=False,
    )

    return response


def build_generator():
    client = Mock()

    client.responses.create.return_value = (
        build_response()
    )

    ai_client = Mock()
    ai_client.get_client.return_value = client

    return (
        AIAssessmentSummaryGenerator(
            ai_client=ai_client
        ),
        client,
    )


def test_generates_summary():
    generator, _ = build_generator()

    result = generator.generate(
        build_assessment()
    )

    assert len(
        result.interviewer_comments
    ) == 2

    assert (
        result.recommendation.short_term
        != ""
    )


def test_prompt_contains_assessment_context():
    generator, client = build_generator()

    generator.generate(
        build_assessment()
    )

    call = (
        client.responses.create
        .call_args.kwargs
    )

    prompt = call["input"][1]["content"]

    assert "Engineering Manager" in prompt
    assert "72.0" in prompt
    assert "DevOps" in prompt


def test_uses_structured_output():
    generator, client = build_generator()

    generator.generate(
        build_assessment()
    )

    call = (
        client.responses.create
        .call_args.kwargs
    )

    response_format = (
        call["text"]["format"]
    )

    assert (
        response_format["type"]
        == "json_schema"
    )

    assert (
        response_format["strict"]
        is True
    )