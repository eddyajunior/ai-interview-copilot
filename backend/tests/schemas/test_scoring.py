from app.schemas.scoring import (
    AssessmentStatus,
    EvidenceStrength,
    SCORING_RULES,
    SkillScore,
)


def test_scoring_rules_have_all_scores():
    assert len(SCORING_RULES) == 5

    for score in SkillScore:
        assert score in SCORING_RULES


def test_score_one_means_not_evidenced():
    rule = SCORING_RULES[
        SkillScore.NOT_EVIDENCED
    ]

    assert rule.score == 1
    assert rule.evidence_strength == EvidenceStrength.NONE
    assert rule.status == AssessmentStatus.NOT_EVIDENCED


def test_score_five_requires_strong_evidence():
    rule = SCORING_RULES[
        SkillScore.VERY_STRONG
    ]

    assert rule.score == 5
    assert rule.evidence_strength == EvidenceStrength.HIGH
    assert rule.status == AssessmentStatus.STRONG