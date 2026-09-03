from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
)
from app.schemas.risk_intelligence import (
    RiskCategory,
    RiskLevel,
)
from app.services.risk_focus_builder import (
    RiskFocus,
)
from app.services.risk_focus_selector import (
    RiskFocusSelector,
)


def build_focus(
    competency: str,
    level: RiskLevel,
    category: InterviewQuestionCategory,
) -> RiskFocus:
    return RiskFocus(
        competency=competency,
        category=category,
        level=level,
        risk_category=(
            RiskCategory.EVIDENCE_GAP
            if level == RiskLevel.HIGH
            else RiskCategory.LIMITED_EVIDENCE
        ),
        score=1 if level == RiskLevel.HIGH else 2,
        description="Teste",
    )


def test_limits_total_risks():
    focuses = [
        build_focus(
            f"Skill {index}",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        )
        for index in range(10)
    ]

    result = RiskFocusSelector(
        max_total=6,
        max_high=6,
    ).select(focuses)

    assert len(result) == 6


def test_limits_high_risks():
    focuses = [
        build_focus(
            f"High {index}",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        )
        for index in range(10)
    ]

    result = RiskFocusSelector(
        max_high=4,
    ).select(focuses)

    assert len(result) == 4


def test_limits_medium_risks():
    focuses = [
        build_focus(
            f"Medium {index}",
            RiskLevel.MEDIUM,
            InterviewQuestionCategory.HARD_SKILL,
        )
        for index in range(10)
    ]

    result = RiskFocusSelector(
        max_medium=2,
    ).select(focuses)

    assert len(result) == 2


def test_high_risks_are_selected_before_medium():
    focuses = [
        build_focus(
            "Medium",
            RiskLevel.MEDIUM,
            InterviewQuestionCategory.SOFT_SKILL,
        ),
        build_focus(
            "High",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
    ]

    result = RiskFocusSelector(
        max_total=1,
        max_high=1,
    ).select(focuses)

    assert result[0].level == RiskLevel.HIGH


def test_balances_categories_for_same_level():
    focuses = [
        build_focus(
            "Hard 1",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        build_focus(
            "Hard 2",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        build_focus(
            "Soft 1",
            RiskLevel.HIGH,
            InterviewQuestionCategory.SOFT_SKILL,
        ),
        build_focus(
            "AWS",
            RiskLevel.HIGH,
            InterviewQuestionCategory.TECHNOLOGY,
        ),
    ]

    result = RiskFocusSelector(
        max_total=3,
        max_high=3,
    ).select(focuses)

    categories = {
        item.category
        for item in result
    }

    assert (
        InterviewQuestionCategory.HARD_SKILL
        in categories
    )

    assert (
        InterviewQuestionCategory.SOFT_SKILL
        in categories
    )

    assert (
        InterviewQuestionCategory.TECHNOLOGY
        in categories
    )


def test_respects_global_limit_across_levels():
    focuses = [
        build_focus(
            f"High {index}",
            RiskLevel.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        )
        for index in range(4)
    ]

    focuses.extend(
        [
            build_focus(
                f"Medium {index}",
                RiskLevel.MEDIUM,
                InterviewQuestionCategory.SOFT_SKILL,
            )
            for index in range(4)
        ]
    )

    result = RiskFocusSelector(
        max_total=5,
        max_high=4,
        max_medium=2,
    ).select(focuses)

    assert len(result) == 5

    assert (
        sum(
            item.level == RiskLevel.HIGH
            for item in result
        )
        == 4
    )

    assert (
        sum(
            item.level == RiskLevel.MEDIUM
            for item in result
        )
        == 1
    )