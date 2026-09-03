from unittest.mock import Mock

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
)
from app.schemas.interview_intelligence import (
    InterviewQuestion,
    InterviewQuestionCategory,
    InterviewQuestionPriority,
    InterviewQuestionSet,
)
from app.services.interview_intelligence_service import (
    InterviewIntelligenceService,
)


def build_assessment():
    return CandidateAssessment(
        candidate_name="Candidato Teste",
        job_title="Engineering Manager",
        summary="Assessment de teste",
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
            short_term="Validar requisitos.",
            medium_term="Avaliar evolução.",
            long_term="Avaliar aderência futura.",
        ),
    )


def build_question():
    return InterviewQuestion(
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        competency="Arquitetura",
        question=(
            "Conte sobre uma decisão "
            "arquitetural complexa."
        ),
        reason="Validar profundidade.",
        priority=(
            InterviewQuestionPriority.HIGH
        ),
        follow_up=(
            "Quais trade-offs foram avaliados?"
        ),
        what_to_observe=[
            "clareza",
            "trade-offs",
        ],
    )


def test_enriches_assessment_with_questions():
    assessment = build_assessment()

    focus_builder = Mock()
    focus_builder.build.return_value = [
        "focus"
    ]

    focus_selector = Mock()
    focus_selector.select.return_value = [
        "selected-focus"
    ]

    generator = Mock()
    generator.generate.return_value = (
        InterviewQuestionSet(
            questions=[
                build_question()
            ]
        )
    )

    service = InterviewIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        question_generator=generator,
    )

    result = service.enrich(
        assessment
    )

    assert len(result.questions) == 1

    assert (
        result.questions[0].competency
        == "Arquitetura"
    )

    assert (
        result.questions[0].priority
        == InterviewQuestionPriority.HIGH
    )


def test_preserves_original_assessment():
    assessment = build_assessment()

    focus_builder = Mock()
    focus_builder.build.return_value = []

    focus_selector = Mock()
    focus_selector.select.return_value = []

    generator = Mock()
    generator.generate.return_value = (
        InterviewQuestionSet(
            questions=[]
        )
    )

    service = InterviewIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        question_generator=generator,
    )

    result = service.enrich(
        assessment
    )

    assert (
        result.candidate_name
        == assessment.candidate_name
    )

    assert (
        result.adherence_percentage
        == assessment.adherence_percentage
    )

    assert result is not assessment


def test_passes_selected_focuses_to_generator():
    assessment = build_assessment()

    selected_focuses = [
        "focus-a",
        "focus-b",
    ]

    focus_builder = Mock()
    focus_builder.build.return_value = [
        "all-focuses"
    ]

    focus_selector = Mock()
    focus_selector.select.return_value = (
        selected_focuses
    )

    generator = Mock()
    generator.generate.return_value = (
        InterviewQuestionSet(
            questions=[]
        )
    )

    service = InterviewIntelligenceService(
        focus_builder=focus_builder,
        focus_selector=focus_selector,
        question_generator=generator,
    )

    service.enrich(
        assessment
    )

    generator.generate.assert_called_once_with(
        selected_focuses
    )