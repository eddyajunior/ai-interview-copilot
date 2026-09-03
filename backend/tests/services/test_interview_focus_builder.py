from app.schemas.candidate_assessment import (
    CandidateAssessment,
    ConfidenceLevel,
    Recommendation,
    SkillAssessment,
    SkillType,
)
from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.services.interview_focus_builder import (
    InterviewFocusBuilder,
)
from app.schemas.evidence import (
    Evidence,
    EvidenceSource,
)


def build_skill(
    name: str,
    skill_type: SkillType,
    score: int,
) -> SkillAssessment:
    return SkillAssessment(
        name=name,
        type=skill_type,
        score=score,
        evidence=[],
        justification="Teste",
        confidence=ConfidenceLevel.MEDIUM,
        status="compatible",
    )


def build_assessment() -> CandidateAssessment:
    return CandidateAssessment(
        candidate_name="Teste",
        job_title="Gerente de Engenharia",
        summary="Teste",
        adherence_percentage=50.0,
        strengths=[],
        weaknesses=[],
        hard_skills=[
            build_skill(
                "DevOps",
                SkillType.HARD_SKILL,
                1,
            ),
            build_skill(
                "Arquitetura",
                SkillType.HARD_SKILL,
                4,
            ),
        ],
        soft_skills=[
            build_skill(
                "Comunicação",
                SkillType.SOFT_SKILL,
                3,
            )
        ],
        technologies=[
            build_skill(
                "AWS",
                SkillType.TECHNOLOGY,
                2,
            )
        ],
        questions=[],
        risks=[],
        interviewer_comments=[],
        recommendation=Recommendation(
            short_term="Teste",
            medium_term="Teste",
            long_term="Teste",
        ),
    )


def test_builds_focus_for_all_skills():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    assert len(focuses) == 4


def test_score_one_has_high_priority():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    devops = next(
        item
        for item in focuses
        if item.competency == "DevOps"
    )

    assert (
        devops.priority
        == InterviewQuestionPriority.HIGH
    )


def test_score_two_has_high_priority():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    aws = next(
        item
        for item in focuses
        if item.competency == "AWS"
    )

    assert (
        aws.priority
        == InterviewQuestionPriority.HIGH
    )


def test_score_three_has_medium_priority():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    communication = next(
        item
        for item in focuses
        if item.competency == "Comunicação"
    )

    assert (
        communication.priority
        == InterviewQuestionPriority.MEDIUM
    )


def test_score_four_has_low_priority():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    architecture = next(
        item
        for item in focuses
        if item.competency == "Arquitetura"
    )

    assert (
        architecture.priority
        == InterviewQuestionPriority.LOW
    )


def test_high_priorities_are_returned_first():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    assert focuses[0].priority == (
        InterviewQuestionPriority.HIGH
    )

    assert focuses[1].priority == (
        InterviewQuestionPriority.HIGH
    )


def test_preserves_category():
    focuses = (
        InterviewFocusBuilder()
        .build(build_assessment())
    )

    aws = next(
        item
        for item in focuses
        if item.competency == "AWS"
    )

    assert (
        aws.category
        == InterviewQuestionCategory.TECHNOLOGY
    )

def test_preserves_evidence_sources():
    assessment = build_assessment()

    assessment.hard_skills[0].evidence = [
        Evidence(
            text="Experiência com automação.",
            source=EvidenceSource.EXPERIENCE,
            source_reference="Empresa A",
            page=1,
        )
    ]

    focuses = (
        InterviewFocusBuilder()
        .build(assessment)
    )

    devops = next(
        item
        for item in focuses
        if item.competency == "DevOps"
    )

    assert (
        EvidenceSource.EXPERIENCE
        in devops.evidence_sources
    )