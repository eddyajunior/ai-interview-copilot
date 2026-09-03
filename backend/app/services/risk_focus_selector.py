from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
)
from app.schemas.risk_intelligence import (
    RiskLevel,
)
from app.services.risk_focus_builder import (
    RiskFocus,
)


class RiskFocusSelector:
    def __init__(
        self,
        max_total: int = 6,
        max_high: int = 4,
        max_medium: int = 2,
    ):
        self.max_total = max_total

        self.max_by_level = {
            RiskLevel.HIGH: max_high,
            RiskLevel.MEDIUM: max_medium,
        }

        self.category_order = (
            InterviewQuestionCategory.HARD_SKILL,
            InterviewQuestionCategory.SOFT_SKILL,
            InterviewQuestionCategory.TECHNOLOGY,
            InterviewQuestionCategory.OTHER,
        )

    def select(
        self,
        focuses: list[RiskFocus],
    ) -> list[RiskFocus]:
        selected: list[RiskFocus] = []

        for level in (
            RiskLevel.HIGH,
            RiskLevel.MEDIUM,
        ):
            candidates = [
                focus
                for focus in focuses
                if focus.level == level
            ]

            candidates = self._balance_categories(
                candidates
            )

            available_slots = (
                self.max_total - len(selected)
            )

            if available_slots <= 0:
                break

            level_limit = self.max_by_level[
                level
            ]

            limit = min(
                available_slots,
                level_limit,
            )

            selected.extend(
                candidates[:limit]
            )

        return selected

    def _balance_categories(
        self,
        focuses: list[RiskFocus],
    ) -> list[RiskFocus]:
        grouped = {
            category: [
                focus
                for focus in focuses
                if focus.category == category
            ]
            for category in self.category_order
        }

        balanced: list[RiskFocus] = []

        while any(grouped.values()):
            for category in self.category_order:
                items = grouped[category]

                if items:
                    balanced.append(
                        items.pop(0)
                    )

        return balanced