from unittest.mock import Mock

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
)
from app.schemas.risk_intelligence import (
    RiskAssessment,
    RiskCategory,
    RiskLevel,
)
from app.services.risk_intelligence_service import (
    RiskIntelligenceService,
)


def build_assessment():
    return CandidateAssessment(
        candidate_name="Teste",
        job_title="Engineering Manager",
        summary="Teste",
        adherence_percentage=50.0,
        strengths=[],
        weaknesses=[],
        hard_skills=[],
        soft_skills=[],
        technologies=[],
        questions=[],
        risks=[],
        interviewer_comments=[],
        recommendation=Recommendation(
            short_term="Teste",
            medium_term="Teste",
            long_term="Teste",
        ),
    )


def build_risk():
    return RiskAssessment(
        competency="DevOps",
        title="DevOps requer validação",
        category=(
            RiskCategory.EVIDENCE_GAP
        ),
        level=RiskLevel.HIGH,
        description=(
            "Não foram encontradas "
            "evidências documentais suficientes."
        ),
        evidence=[],
        validation_question=(
            "Conte sobre sua experiência "
            "prática com DevOps."
        ),
    )


def test_enriches_assessment_with_risks():
    focus_builder = Mock()
    focus_selector = Mock()
    risk_generator = Mock()

    focus_builder.build.return_value = [
        "focus"
    ]

    focus_selector.select.return_value = [
        "selected"
    ]

    risk_generator.generate.return_value = [
        build_risk()
    ]

    service = RiskIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        risk_generator=risk_generator,
    )

    result = service.enrich(
        build_assessment()
    )

    assert len(result.risks) == 1

    assert (
        result.risks[0].competency
        == "DevOps"
    )


def test_preserves_original_assessment():
    assessment = build_assessment()

    focus_builder = Mock()
    focus_selector = Mock()
    risk_generator = Mock()

    focus_builder.build.return_value = []
    focus_selector.select.return_value = []
    risk_generator.generate.return_value = []

    service = RiskIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        risk_generator=risk_generator,
    )

    result = service.enrich(
        assessment
    )

    assert result is not assessment

    assert (
        result.candidate_name
        == assessment.candidate_name
    )

    assert (
        result.job_title
        == assessment.job_title
    )


def test_passes_selected_focuses_to_generator():
    focus_builder = Mock()
    focus_selector = Mock()
    risk_generator = Mock()

    focus_builder.build.return_value = [
        "focus-a",
        "focus-b",
    ]

    focus_selector.select.return_value = [
        "selected-focus",
    ]

    risk_generator.generate.return_value = []

    service = RiskIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        risk_generator=risk_generator,
    )

    service.enrich(
        build_assessment()
    )

    risk_generator.generate.assert_called_once_with(
        [
            "selected-focus",
        ]
    )