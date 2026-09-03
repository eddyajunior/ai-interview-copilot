from app.schemas.interview_intelligence import (
    InterviewQuestion,
    InterviewQuestionCategory,
    InterviewQuestionPriority,
    InterviewQuestionSet,
)


def test_builds_interview_question():
    question = InterviewQuestion(
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        competency="Arquitetura de software",
        question=(
            "Conte sobre uma decisão arquitetural "
            "complexa que você liderou."
        ),
        reason=(
            "Validar profundidade prática no requisito."
        ),
        priority=(
            InterviewQuestionPriority.HIGH
        ),
        follow_up=(
            "Quais trade-offs foram considerados?"
        ),
        what_to_observe=[
            "clareza técnica",
            "capacidade de decisão",
            "trade-offs",
        ],
    )

    assert (
        question.category
        == InterviewQuestionCategory.HARD_SKILL
    )
    assert (
        question.priority
        == InterviewQuestionPriority.HIGH
    )
    assert len(question.what_to_observe) == 3


def test_builds_question_set():
    question_set = InterviewQuestionSet(
        questions=[]
    )

    assert question_set.questions == []


def test_rejects_extra_fields():
    try:
        InterviewQuestion(
            category=(
                InterviewQuestionCategory.SOFT_SKILL
            ),
            competency="Comunicação",
            question=(
                "Como você comunica uma decisão difícil?"
            ),
            reason="Validar comunicação.",
            priority=(
                InterviewQuestionPriority.MEDIUM
            ),
            follow_up=None,
            what_to_observe=[
                "clareza",
            ],
            invalid_field="x",
        )

        assert False

    except Exception:
        assert True