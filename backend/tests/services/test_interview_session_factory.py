from app.schemas.candidate_assessment import (
    CandidateAssessment,
)
from app.schemas.interview_intelligence import (
    InterviewQuestion,
)
from app.schemas.interview_session import (
    InterviewEvidenceStrength,
    InterviewQuestionStatus,
    InterviewResponseEvaluation,
)
from app.services.interview_session_factory import (
    InterviewSessionFactory,
)


def build_assessment() -> CandidateAssessment:
    return CandidateAssessment(
        candidate_name="Candidato Teste",
        job_title="Engineering Manager",
        summary="Resumo do assessment.",
        adherence_percentage=75.0,
        strengths=[],
        weaknesses=[],
        hard_skills=[],
        soft_skills=[],
        technologies=[],
        questions=[
            InterviewQuestion(
                category="hard_skill",
                competency="Arquitetura",
                question=(
                    "Conte sobre uma decisão "
                    "arquitetural complexa."
                ),
                reason=(
                    "Validar experiência arquitetural."
                ),
                priority="high",
                follow_up=None,
                what_to_observe=[
                    "Clareza dos trade-offs",
                ],
            ),
            InterviewQuestion(
                category="soft_skill",
                competency="Liderança",
                question=(
                    "Como você conduz conflitos "
                    "técnicos no time?"
                ),
                reason=(
                    "Validar capacidade de liderança."
                ),
                priority="medium",
                follow_up=None,
                what_to_observe=[
                    "Capacidade de mediação",
                ],
            ),
        ],
        risks=[],
        interviewer_comments=[],
        recommendation={
            "short_term": "Validar competências.",
            "medium_term": "Consolidar avaliação.",
            "long_term": "Acompanhar evolução.",
        },
    )


def test_creates_session_from_assessment():
    assessment = build_assessment()

    factory = InterviewSessionFactory()

    session = factory.create(assessment)

    assert session.candidate_name == (
        assessment.candidate_name
    )

    assert session.job_title == (
        assessment.job_title
    )

    assert len(session.questions) == 2


def test_preserves_question_order():
    assessment = build_assessment()

    session = InterviewSessionFactory().create(
        assessment
    )

    assert session.questions[0].question_index == 0
    assert session.questions[0].competency == (
        "Arquitetura"
    )

    assert session.questions[1].question_index == 1
    assert session.questions[1].competency == (
        "Liderança"
    )


def test_questions_start_pending_and_not_evaluated():
    assessment = build_assessment()

    session = InterviewSessionFactory().create(
        assessment
    )

    for question in session.questions:
        assert question.status == (
            InterviewQuestionStatus.PENDING
        )

        assert question.evaluation == (
            InterviewResponseEvaluation.NOT_EVALUATED
        )

        assert question.evidence_strength == (
            InterviewEvidenceStrength.NOT_EVALUATED
        )

        assert question.interviewer_notes is None
        assert question.response_summary is None


def test_creates_session_without_questions():
    assessment = build_assessment()
    assessment.questions = []

    session = InterviewSessionFactory().create(
        assessment
    )

    assert session.questions == []