from app.schemas.candidate_assessment import (
    CandidateAssessment,
    ConfidenceLevel,
    Recommendation,
    SkillAssessment,
    SkillType,
)
from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
)
from app.schemas.risk_intelligence import (
    RiskCategory,
    RiskLevel,
)
from app.services.risk_focus_builder import (
    RiskFocusBuilder,
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


def build_assessment():
    return CandidateAssessment(
        candidate_name="Teste",
        job_title="Engineering Manager",
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
                2,
            ),
            build_skill(
                "Liderança",
                SkillType.SOFT_SKILL,
                3,
            ),
        ],
        technologies=[
            build_skill(
                "AWS",
                SkillType.TECHNOLOGY,
                1,
            ),
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


def test_builds_only_low_evidence_risks():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    assert len(result) == 3


def test_score_one_becomes_high_evidence_gap():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    devops = next(
        item
        for item in result
        if item.competency == "DevOps"
    )

    assert devops.level == RiskLevel.HIGH

    assert (
        devops.risk_category
        == RiskCategory.EVIDENCE_GAP
    )


def test_score_two_becomes_medium_limited_evidence():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    communication = next(
        item
        for item in result
        if item.competency == "Comunicação"
    )

    assert communication.level == RiskLevel.MEDIUM

    assert (
        communication.risk_category
        == RiskCategory.LIMITED_EVIDENCE
    )


def test_score_three_does_not_become_risk():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    assert all(
        item.competency != "Liderança"
        for item in result
    )


def test_score_four_does_not_become_risk():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    assert all(
        item.competency != "Arquitetura"
        for item in result
    )


def test_preserves_category():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    aws = next(
        item
        for item in result
        if item.competency == "AWS"
    )

    assert (
        aws.category
        == InterviewQuestionCategory.TECHNOLOGY
    )


def test_high_risks_are_sorted_first():
    result = RiskFocusBuilder().build(
        build_assessment()
    )

    assert result[0].level == RiskLevel.HIGH
    assert result[1].level == RiskLevel.HIGH
    assert result[2].level == RiskLevel.MEDIUM