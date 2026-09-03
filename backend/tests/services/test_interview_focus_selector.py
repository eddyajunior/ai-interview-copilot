from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.services.interview_focus_builder import (
    InterviewFocus,
)
from app.services.interview_focus_selector import (
    InterviewFocusSelector,
)
from app.schemas.evidence import EvidenceSource


def focus(
    name: str,
    priority: InterviewQuestionPriority,
) -> InterviewFocus:
    return InterviewFocus(
        competency=name,
        category=(
            InterviewQuestionCategory.HARD_SKILL
        ),
        priority=priority,
        score=1,
        reason="Teste",
        evidence_sources=set(),
    )


def test_limits_total_number_of_focuses():
    focuses = [
        focus(
            f"Skill {index}",
            InterviewQuestionPriority.HIGH,
        )
        for index in range(20)
    ]

    result = InterviewFocusSelector(
        max_total=10,
        max_high=10,
    ).select(focuses)

    assert len(result) == 10


def test_limits_high_priority():
    focuses = [
        focus(
            f"High {index}",
            InterviewQuestionPriority.HIGH,
        )
        for index in range(10)
    ]

    result = InterviewFocusSelector(
        max_high=5,
    ).select(focuses)

    assert len(result) == 5


def test_limits_medium_priority():
    focuses = [
        focus(
            f"Medium {index}",
            InterviewQuestionPriority.MEDIUM,
        )
        for index in range(10)
    ]

    result = InterviewFocusSelector(
        max_medium=3,
    ).select(focuses)

    assert len(result) == 3


def test_limits_low_priority():
    focuses = [
        focus(
            f"Low {index}",
            InterviewQuestionPriority.LOW,
        )
        for index in range(10)
    ]

    result = InterviewFocusSelector(
        max_low=2,
    ).select(focuses)

    assert len(result) == 2


def test_prioritizes_high_before_medium():
    focuses = [
        focus(
            "Medium",
            InterviewQuestionPriority.MEDIUM,
        ),
        focus(
            "High",
            InterviewQuestionPriority.HIGH,
        ),
    ]

    result = InterviewFocusSelector().select(
        focuses
    )

    assert (
        result[0].priority
        == InterviewQuestionPriority.HIGH
    )


def test_prioritizes_medium_before_low():
    focuses = [
        focus(
            "Low",
            InterviewQuestionPriority.LOW,
        ),
        focus(
            "Medium",
            InterviewQuestionPriority.MEDIUM,
        ),
    ]

    result = InterviewFocusSelector().select(
        focuses
    )

    assert (
        result[0].priority
        == InterviewQuestionPriority.MEDIUM
    )


def test_respects_global_limit_across_priorities():
    focuses = [
        focus(
            f"High {index}",
            InterviewQuestionPriority.HIGH,
        )
        for index in range(5)
    ]

    focuses.extend(
        [
            focus(
                f"Medium {index}",
                InterviewQuestionPriority.MEDIUM,
            )
            for index in range(5)
        ]
    )

    focuses.extend(
        [
            focus(
                f"Low {index}",
                InterviewQuestionPriority.LOW,
            )
            for index in range(5)
        ]
    )

    result = InterviewFocusSelector(
        max_total=6,
        max_high=5,
        max_medium=3,
        max_low=2,
    ).select(focuses)

    assert len(result) == 6

    assert (
        sum(
            item.priority
            == InterviewQuestionPriority.HIGH
            for item in result
        )
        == 5
    )

    assert (
        sum(
            item.priority
            == InterviewQuestionPriority.MEDIUM
            for item in result
        )
        == 1
    )


def category_focus(
    name: str,
    priority: InterviewQuestionPriority,
    category: InterviewQuestionCategory,
) -> InterviewFocus:
    return InterviewFocus(
        competency=name,
        category=category,
        priority=priority,
        score=1,
        reason="Teste",
        evidence_sources=set(),
    )


def test_balances_categories_with_same_priority():
    focuses = [
        category_focus(
            "Hard 1",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "Hard 2",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "Hard 3",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "Soft 1",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.SOFT_SKILL,
        ),
        category_focus(
            "AWS",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.TECHNOLOGY,
        ),
    ]

    result = InterviewFocusSelector(
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


def test_priority_is_more_important_than_category_balance():
    focuses = [
        category_focus(
            "Hard high",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "Soft medium",
            InterviewQuestionPriority.MEDIUM,
            InterviewQuestionCategory.SOFT_SKILL,
        ),
    ]

    result = InterviewFocusSelector(
        max_total=1,
        max_high=1,
    ).select(focuses)

    assert len(result) == 1

    assert (
        result[0].priority
        == InterviewQuestionPriority.HIGH
    )


def test_round_robin_prevents_single_category_domination():
    focuses = [
        category_focus(
            f"Hard {index}",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        )
        for index in range(5)
    ]

    focuses.extend(
        [
            category_focus(
                "Comunicação",
                InterviewQuestionPriority.HIGH,
                InterviewQuestionCategory.SOFT_SKILL,
            ),
            category_focus(
                "AWS",
                InterviewQuestionPriority.HIGH,
                InterviewQuestionCategory.TECHNOLOGY,
            ),
        ]
    )

    result = InterviewFocusSelector(
        max_total=5,
        max_high=5,
    ).select(focuses)

    assert any(
        item.category
        == InterviewQuestionCategory.SOFT_SKILL
        for item in result
    )

    assert any(
        item.category
        == InterviewQuestionCategory.TECHNOLOGY
        for item in result
    )

def test_excludes_education_only_focus():
    item = category_focus(
        "Formação superior",
        InterviewQuestionPriority.MEDIUM,
        InterviewQuestionCategory.HARD_SKILL,
    )

    item.evidence_sources = {
        EvidenceSource.EDUCATION
    }

    result = InterviewFocusSelector().select(
        [item]
    )

    assert result == []


def test_excludes_certification_only_focus():
    item = category_focus(
        "Certificação AWS",
        InterviewQuestionPriority.MEDIUM,
        InterviewQuestionCategory.TECHNOLOGY,
    )

    item.evidence_sources = {
        EvidenceSource.CERTIFICATION
    }

    result = InterviewFocusSelector().select(
        [item]
    )

    assert result == []


def test_excludes_education_and_certification_only():
    item = category_focus(
        "Formação e certificação",
        InterviewQuestionPriority.MEDIUM,
        InterviewQuestionCategory.HARD_SKILL,
    )

    item.evidence_sources = {
        EvidenceSource.EDUCATION,
        EvidenceSource.CERTIFICATION,
    }

    result = InterviewFocusSelector().select(
        [item]
    )

    assert result == []


def test_keeps_focus_with_experience_evidence():
    item = category_focus(
        "Arquitetura",
        InterviewQuestionPriority.MEDIUM,
        InterviewQuestionCategory.HARD_SKILL,
    )

    item.evidence_sources = {
        EvidenceSource.EDUCATION,
        EvidenceSource.EXPERIENCE,
    }

    result = InterviewFocusSelector().select(
        [item]
    )

    assert len(result) == 1


def test_keeps_focus_without_evidence():
    item = category_focus(
        "DevOps",
        InterviewQuestionPriority.HIGH,
        InterviewQuestionCategory.HARD_SKILL,
    )

    item.evidence_sources = set()

    result = InterviewFocusSelector().select(
        [item]
    )

    assert len(result) == 1

def test_deduplicates_before_applying_global_limit():
    focuses = [
        category_focus(
            "Arquitetura orientada a eventos",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            (
                "Arquiteturas escaláveis, "
                "resilientes, observáveis e "
                "orientadas a eventos"
            ),
            InterviewQuestionPriority.MEDIUM,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "DevOps",
            InterviewQuestionPriority.HIGH,
            InterviewQuestionCategory.HARD_SKILL,
        ),
        category_focus(
            "AWS",
            InterviewQuestionPriority.MEDIUM,
            InterviewQuestionCategory.TECHNOLOGY,
        ),
    ]

    result = InterviewFocusSelector(
        max_total=3,
        max_high=2,
        max_medium=2,
        max_low=0,
    ).select(focuses)

    assert len(result) == 3

    competencies = {
        item.competency
        for item in result
    }

    assert (
        "Arquitetura orientada a eventos"
        in competencies
    )

    assert (
        "DevOps"
        in competencies
    )

    assert "AWS" in competencies