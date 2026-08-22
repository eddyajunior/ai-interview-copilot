from pydantic import ValidationError

from app.schemas.candidate_assessment import (
    CandidateAssessment,
    Recommendation,
    SkillAssessment,
    SkillType,
    ConfidenceLevel,
)


def test_candidate_assessment_valid():
    assessment = CandidateAssessment(
        candidate_name="João Silva",
        job_title="Senior Software Engineer",
        summary="Candidato apresenta boa aderência técnica.",
        strengths=["Java", "AWS"],
        weaknesses=["Kafka pouco evidenciado"],
        hard_skills=[
            SkillAssessment(
                name="Java",
                type=SkillType.HARD_SKILL,
                score=5,
                evidence=["8 anos de experiência com Java"],
                justification="Experiência recorrente e diretamente relacionada à vaga.",
                confidence=ConfidenceLevel.HIGH,
                status="aderente",
            )
        ],
        recommendation=Recommendation(
            short_term="Boa capacidade de adaptação.",
            medium_term="Pode ampliar responsabilidades arquiteturais.",
            long_term="Possível evolução como referência técnica.",
        ),
    )

    assert assessment.job_title == "Senior Software Engineer"
    assert assessment.hard_skills[0].score == 5


def test_skill_score_cannot_exceed_five():
    try:
        SkillAssessment(
            name="Java",
            type=SkillType.HARD_SKILL,
            score=6,
            evidence=[],
            justification="Teste",
            confidence=ConfidenceLevel.HIGH,
            status="aderente",
        )

        assert False

    except ValidationError:
        assert True