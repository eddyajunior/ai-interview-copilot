from unittest.mock import Mock

from app.schemas.assessment_summary import (
    AssessmentRecommendation,
    AssessmentSummary,
)
from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
)
from app.services.assessment_summary_service import (
    AssessmentSummaryService,
)


def build_assessment():
    return CandidateAssessment(
        candidate_name="Teste",
        job_title="Engineering Manager",
        summary="Teste",
        adherence_percentage=70.0,
        strengths=[],
        weaknesses=[],
        hard_skills=[],
        soft_skills=[],
        technologies=[],
        questions=[],
        risks=[],
        interviewer_comments=[],
        recommendation=Recommendation(
            short_term="Anterior",
            medium_term="Anterior",
            long_term="Anterior",
        ),
    )


def build_summary():
    return AssessmentSummary(
        interviewer_comments=[
            "Validar experiência prática em DevOps.",
            "Aprofundar decisões de arquitetura.",
        ],
        recommendation=AssessmentRecommendation(
            short_term="Priorizar os pontos de validação.",
            medium_term="Aprofundar competências críticas.",
            long_term="Acompanhar pontos de desenvolvimento.",
        ),
    )


def test_enriches_comments_and_recommendation():
    generator = Mock()
    generator.generate.return_value = (
        build_summary()
    )

    service = AssessmentSummaryService(
        summary_generator=generator
    )

    result = service.enrich(
        build_assessment()
    )

    assert len(
        result.interviewer_comments
    ) == 2

    assert (
        result.recommendation.short_term
        == "Priorizar os pontos de validação."
    )


def test_preserves_original_assessment():
    assessment = build_assessment()

    generator = Mock()
    generator.generate.return_value = (
        build_summary()
    )

    service = AssessmentSummaryService(
        summary_generator=generator
    )

    result = service.enrich(
        assessment
    )

    assert result is not assessment

    assert (
        assessment.interviewer_comments
        == []
    )

    assert (
        result.job_title
        == assessment.job_title
    )

    assert (
        result.adherence_percentage
        == assessment.adherence_percentage
    )


def test_calls_generator_with_assessment():
    assessment = build_assessment()

    generator = Mock()
    generator.generate.return_value = (
        build_summary()
    )

    service = AssessmentSummaryService(
        summary_generator=generator
    )

    service.enrich(
        assessment
    )

    generator.generate.assert_called_once_with(
        assessment
    )