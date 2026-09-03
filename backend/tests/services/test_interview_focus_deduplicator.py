from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.services.interview_focus_builder import (
    InterviewFocus,
)
from app.services.interview_focus_deduplicator import (
    InterviewFocusDeduplicator,
)


def build_focus(
    competency: str,
    priority: InterviewQuestionPriority,
    score: int,
) -> InterviewFocus:
    return InterviewFocus(
        competency=competency,
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        priority=priority,
        score=score,
        reason="Teste",
        evidence_sources=set(),
    )


def test_removes_strong_lexical_overlap():
    focuses = [
        build_focus(
            "Arquitetura orientada a eventos",
            InterviewQuestionPriority.HIGH,
            1,
        ),
        build_focus(
            (
                "Arquiteturas escaláveis, "
                "resilientes, observáveis e "
                "orientadas a eventos"
            ),
            InterviewQuestionPriority.MEDIUM,
            3,
        ),
    ]

    result = (
        InterviewFocusDeduplicator()
        .deduplicate(focuses)
    )

    assert len(result) == 1

    assert (
        result[0].competency
        == "Arquitetura orientada a eventos"
    )


def test_keeps_higher_priority_focus():
    focuses = [
        build_focus(
            "Arquiteturas orientadas a eventos",
            InterviewQuestionPriority.MEDIUM,
            3,
        ),
        build_focus(
            "Arquitetura orientada a eventos",
            InterviewQuestionPriority.HIGH,
            1,
        ),
    ]

    result = (
        InterviewFocusDeduplicator()
        .deduplicate(focuses)
    )

    assert len(result) == 1

    assert (
        result[0].priority
        == InterviewQuestionPriority.HIGH
    )


def test_keeps_distinct_architecture_topics():
    focuses = [
        build_focus(
            "Arquitetura de software",
            InterviewQuestionPriority.LOW,
            4,
        ),
        build_focus(
            "Arquitetura orientada a eventos",
            InterviewQuestionPriority.HIGH,
            1,
        ),
    ]

    result = (
        InterviewFocusDeduplicator()
        .deduplicate(focuses)
    )

    assert len(result) == 2


def test_does_not_confuse_java_and_javascript():
    focuses = [
        build_focus(
            "Java",
            InterviewQuestionPriority.HIGH,
            1,
        ),
        build_focus(
            "JavaScript",
            InterviewQuestionPriority.HIGH,
            1,
        ),
    ]

    result = (
        InterviewFocusDeduplicator()
        .deduplicate(focuses)
    )

    assert len(result) == 2


def test_keeps_unrelated_competencies():
    focuses = [
        build_focus(
            "DevOps",
            InterviewQuestionPriority.HIGH,
            1,
        ),
        build_focus(
            "Gestão de stakeholders",
            InterviewQuestionPriority.LOW,
            4,
        ),
    ]

    result = (
        InterviewFocusDeduplicator()
        .deduplicate(focuses)
    )

    assert len(result) == 2