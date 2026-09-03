from app.schemas.interview_intelligence import (
    InterviewQuestionCategory,
    InterviewQuestionPriority,
)
from app.services.interview_focus_builder import (
    InterviewFocus,
)
from app.schemas.evidence import EvidenceSource
from app.services.interview_focus_deduplicator import (
    InterviewFocusDeduplicator,
)

class InterviewFocusSelector:
    def __init__(
        self,
        max_total: int = 10,
        max_high: int = 5,
        max_medium: int = 3,
        max_low: int = 2,
    ):
        self.max_total = max_total

        self.max_by_priority = {
            InterviewQuestionPriority.HIGH: max_high,
            InterviewQuestionPriority.MEDIUM: max_medium,
            InterviewQuestionPriority.LOW: max_low,
        }

        self.category_order = (
            InterviewQuestionCategory.HARD_SKILL,
            InterviewQuestionCategory.SOFT_SKILL,
            InterviewQuestionCategory.TECHNOLOGY,
            InterviewQuestionCategory.OTHER,
        )
        self.deduplicator = (
            InterviewFocusDeduplicator()
        )

    def select(
        self,
        focuses: list[InterviewFocus],
    ) -> list[InterviewFocus]:
        eligible_focuses = [
            focus
            for focus in focuses
            if self._is_interview_relevant(focus)
        ]

        eligible_focuses = (
            self.deduplicator
            .deduplicate(eligible_focuses)
        )

        selected: list[InterviewFocus] = []

        for priority in (
            InterviewQuestionPriority.HIGH,
            InterviewQuestionPriority.MEDIUM,
            InterviewQuestionPriority.LOW,
        ):
            candidates = [
                focus
                for focus in eligible_focuses
                if focus.priority == priority
            ]

            candidates = self._balance_categories(
                candidates
            )

            available_global_slots = (
                self.max_total - len(selected)
            )

            if available_global_slots <= 0:
                break

            priority_limit = self.max_by_priority[
                priority
            ]

            limit = min(
                priority_limit,
                available_global_slots,
            )

            selected.extend(
                candidates[:limit]
            )

        return selected

    def _balance_categories(
        self,
        focuses: list[InterviewFocus],
    ) -> list[InterviewFocus]:
        grouped = {
            category: [
                focus
                for focus in focuses
                if focus.category == category
            ]
            for category in self.category_order
        }

        balanced: list[InterviewFocus] = []

        while any(grouped.values()):
            for category in self.category_order:
                items = grouped[category]

                if items:
                    balanced.append(
                        items.pop(0)
                    )

        return balanced

    @staticmethod
    def _is_interview_relevant(
        focus: InterviewFocus,
    ) -> bool:
        sources = focus.evidence_sources

        if not sources:
            return True

        documentary_only_sources = {
            EvidenceSource.EDUCATION,
            EvidenceSource.CERTIFICATION,
        }

        return not sources.issubset(
            documentary_only_sources
        )